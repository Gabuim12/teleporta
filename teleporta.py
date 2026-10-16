#!/usr/bin/env python3
"""Teleporta: passa fotos, vídeos e arquivos entre celular e PC pela rede local.

O PC roda um servidor pequeno e mostra um QR code. O celular escaneia, abre no navegador
e os arquivos vão direto para uma pasta do PC: sem nuvem, sem cabo, sem recompressão.
"""
import argparse
import io
import json
import mimetypes
import os
import re
import secrets
import socket
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
import zipfile
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

import qrcode
import qrcode.image.svg

import licenca
from dados import FREE_DAILY, Store

WEB_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).parent)) / "web"  # _MEIPASS: dentro do .exe
STATIC_FILES = {
    "style.css": "text/css; charset=utf-8",
    "app.js": "text/javascript; charset=utf-8",
    "logo.png": "image/png",
    "logo-branca.png": "image/png",
    "icon.png": "image/png",
    "outfit.woff2": "font/woff2",
    "inter.woff2": "font/woff2",
}
CHUNK = 1024 * 1024
ONLINE_WINDOW = 15
NOTES_MAX = 40
NOTE_LEN = 20000

mimetypes.add_type("image/heic", ".heic")
mimetypes.add_type("image/heif", ".heif")
mimetypes.add_type("video/quicktime", ".mov")

BAD_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
RESERVED = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
TYPE_FOLDERS = [
    ("Fotos", {".jpg", ".jpeg", ".png", ".heic", ".heif", ".gif", ".webp", ".bmp", ".dng", ".raw"}),
    ("Videos", {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm", ".3gp"}),
    ("Audios", {".mp3", ".m4a", ".wav", ".aac", ".flac", ".ogg", ".opus"}),
    ("Documentos", {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".csv", ".odt", ".rtf"}),
]


class State:
    pin = f"{secrets.randbelow(10**6):06d}"
    token = secrets.token_urlsafe(16)
    sessions = {}  # sid -> {"seen": ts, "name": str}
    fails = {}  # ip -> (count, locked_until)
    notes = []  # textos e links trocados (só em memória)
    license = None  # dados da licença Pro, se válida
    lock = threading.Lock()
    received = Path()
    outbox = Path()
    host = "127.0.0.1"
    port = 8765


# ---------- plano / licença ----------
def is_pro():
    return State.license is not None


def plan_info():
    used = Store.used_today()
    pro = is_pro()
    return {
        "pro": pro,
        "email": State.license.get("e") if pro else None,
        "used": used,
        "limit": None if pro else FREE_DAILY,
        "remaining": None if pro else max(0, FREE_DAILY - used),
        "buy_url": licenca.BUY_URL,
    }


def session_ttl():
    return 30 * 86400 if (is_pro() and Store.cfg.get("fixed")) else 12 * 3600


def persist_sessions():
    if is_pro() and Store.cfg.get("fixed"):
        with State.lock:
            Store.cfg["sessions"] = dict(State.sessions)
        Store.save()


# ---------- utilitários ----------
def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def open_path(path):
    """Abre arquivo ou pasta no app padrão do sistema."""
    if sys.platform == "win32":
        os.startfile(path)
    else:
        subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", str(path)])


def device_name(ua):
    for needle, label in (("iPhone", "iPhone"), ("iPad", "iPad"), ("Android", "Android"),
                          ("Windows", "Windows"), ("Macintosh", "Mac"), ("Linux", "Linux")):
        if needle in (ua or ""):
            return label
    return "Dispositivo"


def safe_name(raw):
    name = BAD_CHARS.sub("_", unquote(raw or "").replace("\\", "/").split("/")[-1]).strip(" .")
    if not name:
        name = "arquivo"
    p = Path(name)
    stem, ext = p.stem[:150], p.suffix[:16]
    if stem.upper() in RESERVED:
        stem = "_" + stem
    name = stem + ext
    if name.lower().endswith(".part"):
        name += ".file"
    return name


def organized_dir(base, name, mtime_ms):
    """Pro: guarda em subpastas por data da foto ou por tipo. Grátis: tudo na mesma pasta."""
    mode = Store.cfg.get("organize", "off") if is_pro() else "off"
    if mode == "date":
        ts = mtime_ms / 1000 if 0 < mtime_ms / 1000 <= time.time() else time.time()
        sub = time.strftime("%Y-%m-%d", time.localtime(ts))
    elif mode == "type":
        ext = Path(name).suffix.lower()
        sub = next((folder for folder, exts in TYPE_FOLDERS if ext in exts), "Outros")
    else:
        return base
    d = base / sub
    d.mkdir(exist_ok=True)
    return d


def reserve_path(directory, name):
    """Escolhe um nome livre ('foto (1).jpg') e já cria o .part para ninguém pegar o mesmo."""
    p = Path(name)
    with State.lock:
        n = 0
        while True:
            candidate = directory / (name if n == 0 else f"{p.stem} ({n}){p.suffix}")
            part = candidate.with_name(candidate.name + ".part")
            if not candidate.exists() and not part.exists():
                part.touch()
                return candidate, part
            n += 1


def list_dir(directory, limit=60):
    items = []
    for p in directory.rglob("*"):
        try:
            if not p.is_file():
                continue
            st = p.stat()
        except OSError:
            continue
        rel = p.relative_to(directory).as_posix()
        partial = rel.endswith(".part")
        rel = rel[:-5] if partial else rel
        items.append({
            "name": rel,
            "title": rel.rsplit("/", 1)[-1],
            "folder": rel.rsplit("/", 1)[0] if "/" in rel else "",
            "size": st.st_size,
            "mtime": st.st_mtime,
            "partial": partial,
        })
    items.sort(key=lambda i: -i["mtime"])
    return items[:limit]


def child_file(directory, name):
    """Arquivo dentro de `directory` (aceita subpastas), nunca fora dele."""
    try:
        p = (directory / unquote(name)).resolve()
    except (OSError, ValueError):
        return None
    return p if directory in p.parents and p.is_file() else None


def build_zip(base, names):
    tmp = tempfile.SpooledTemporaryFile(max_size=64 * 1024 * 1024)
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_STORED, allowZip64=True) as z:
        for n in names:
            f = child_file(base, n)
            if f and not f.name.endswith(".part"):
                z.write(f, f.relative_to(base).as_posix())
    size = tmp.tell()
    tmp.seek(0)
    return tmp, size


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "Teleporta"
    timeout = 120

    def log_message(self, *args):
        pass

    # ---------- helpers ----------
    def _ip(self):
        return self.client_address[0]

    def _is_local(self):
        """Só o próprio PC, e só via localhost (barra ataques de outros sites / DNS rebinding)."""
        if self._ip() not in ("127.0.0.1", "::1"):
            return False
        host = (self.headers.get("Host") or "").lower()
        if host not in (f"localhost:{State.port}", f"127.0.0.1:{State.port}"):
            return False
        origin = self.headers.get("Origin")
        return origin is None or urlparse(origin).netloc.lower() == host

    def _sid(self):
        c = SimpleCookie(self.headers.get("Cookie", ""))
        return c["sid"].value if "sid" in c else None

    def _is_authed(self):
        sid = self._sid()
        now = time.time()
        with State.lock:
            s = State.sessions.get(sid)
            if s is None or now - s["seen"] > session_ttl():
                State.sessions.pop(sid, None)
                return False
            s["seen"] = now
            self._device = s["name"]
        return True

    def _new_session(self):
        sid = secrets.token_urlsafe(24)
        with State.lock:
            State.sessions[sid] = {"seen": time.time(), "name": device_name(self.headers.get("User-Agent"))}
        persist_sessions()
        return sid

    def _cookie(self, sid):
        return f"sid={sid}; Path=/; HttpOnly; SameSite=Strict; Max-Age={session_ttl()}"

    def _send(self, status, body=b"", ctype="text/plain; charset=utf-8", headers=None):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in {"Cache-Control": "no-store", **(headers or {})}.items():
            self.send_header(k, v)
        self.end_headers()
        if body and self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, obj, status=200, headers=None):
        self._send(status, json.dumps(obj).encode(), "application/json", headers)

    def _redirect(self, where, headers=None):
        self._send(303, b"", headers={"Location": where, **(headers or {})})

    def _query(self):
        return parse_qs(urlparse(self.path).query)

    def _body_json(self, limit=NOTE_LEN * 4):
        try:
            raw = self.rfile.read(min(int(self.headers.get("Content-Length", "0")), limit))
            data = json.loads(raw or b"{}")
            return data if isinstance(data, dict) else {}
        except (ValueError, OSError):
            return {}

    def _send_file(self, path, attachment, cache=False):
        """Envia o arquivo, com suporte a Range (o Safari precisa disso para tocar vídeo). True se terminou."""
        size = path.stat().st_size
        start, end, status = 0, size - 1, 200
        m = re.fullmatch(r"bytes=(\d*)-(\d*)", self.headers.get("Range", ""))
        if m and (m[1] or m[2]) and size:
            if m[1]:
                start = int(m[1])
                end = min(int(m[2]), size - 1) if m[2] else size - 1
            else:
                start = max(0, size - int(m[2]))
            if start > end:
                return self._send(416, b"", headers={"Content-Range": f"bytes */{size}"}) or False
            status = 206
        ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        disp = "attachment" if attachment else "inline"
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(end - start + 1 if size else 0))
        self.send_header("Accept-Ranges", "bytes")
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Disposition", f"{disp}; filename*=UTF-8''{quote(path.name)}")
        self.send_header("Cache-Control", "private, max-age=3600" if cache else "no-store")
        self.end_headers()
        try:
            with open(path, "rb") as f:
                f.seek(start)
                left = end - start + 1 if size else 0
                while left > 0 and (chunk := f.read(min(CHUNK, left))):
                    self.wfile.write(chunk)
                    left -= len(chunk)
        except (BrokenPipeError, ConnectionError, TimeoutError):
            self.close_connection = True
            return False
        return True

    def _guard(self, local_only=False):
        ok = self._is_local() if local_only else (self._is_local() or self._is_authed())
        if not ok:
            self._send(403 if local_only else 401, b"nao autorizado")
        return ok

    def _who(self):
        return "PC" if self._is_local() else getattr(self, "_device", "Dispositivo")

    def _pro_only(self):
        if not is_pro():
            self._json({"ok": False, "error": "pro"}, 402)
            return False
        return True

    def _receive_file(self, directory, direction, count=False):
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self._send(411, b"Content-Length obrigatorio")
            return
        try:
            mtime_ms = int(self.headers.get("X-Last-Modified", "0"))
        except ValueError:
            mtime_ms = 0
        name = safe_name(self._query().get("name", [""])[0])
        directory = organized_dir(directory, name, mtime_ms) if direction == "in" else directory
        final, part = reserve_path(directory, name)
        remaining = length
        try:
            with open(part, "wb") as f:
                while remaining:
                    chunk = self.rfile.read(min(CHUNK, remaining))
                    if not chunk:
                        raise ConnectionError("conexao interrompida")
                    f.write(chunk)
                    remaining -= len(chunk)
            part.replace(final)
        except (OSError, TimeoutError):
            part.unlink(missing_ok=True)
            self.close_connection = True
            return
        try:  # preserva a data original da foto quando o navegador informa
            if 0 < mtime_ms / 1000 <= time.time():
                os.utime(final, (mtime_ms / 1000, mtime_ms / 1000))
        except OSError:
            pass
        if count:
            Store.bump()
        Store.log(direction, final.name, length, self._who() if direction == "in" else "PC")
        self._json({"ok": True, "name": final.name, "size": length})

    # ---------- GET ----------
    def do_GET(self):
        url = urlparse(self.path)
        path = url.path

        if path == "/":
            if self._is_local():
                return self._page("pc.html")
            if self._is_authed():
                return self._page("phone.html")
            return self._page("login.html")

        if path == "/auth":
            token = self._query().get("t", [""])[0]
            if secrets.compare_digest(token, State.token):
                return self._redirect("/", {"Set-Cookie": self._cookie(self._new_session())})
            return self._redirect("/")

        if path.startswith("/static/"):
            name = path[len("/static/"):]
            if name in STATIC_FILES:
                # CSS e JS mudam com o app (revalidar); fontes e imagens quase nunca (cache de 1 dia)
                cache = "no-cache" if name.endswith((".css", ".js")) else "public, max-age=86400"
                return self._send(200, (WEB_DIR / name).read_bytes(), STATIC_FILES[name], {"Cache-Control": cache})
            return self._send(404, b"nao encontrado")

        if path == "/qr.svg":
            if not self._guard(local_only=True):
                return
            auth_url = f"http://{State.host}:{State.port}/auth?t={State.token}"
            buf = io.BytesIO()
            qrcode.make(auth_url, image_factory=qrcode.image.svg.SvgPathImage, border=1).save(buf)
            return self._send(200, buf.getvalue(), "image/svg+xml")

        if path == "/api/info":
            if not self._guard(local_only=True):
                return
            now = time.time()
            with State.lock:
                devices = sorted({s["name"] for s in State.sessions.values() if now - s["seen"] < ONLINE_WINDOW})
            return self._json({
                "url": f"http://{State.host}:{State.port}",
                "pin": State.pin,
                "received_dir": str(State.received),
                "outbox_dir": str(State.outbox),
                "devices": devices,
                "plan": plan_info(),
                "organize": Store.cfg.get("organize", "off"),
                "fixed": bool(Store.cfg.get("fixed")),
            })

        if path == "/api/ping":  # celular: "estou aqui" + situação do plano
            if not self._guard():
                return
            return self._json({"host": socket.gethostname(), "plan": plan_info()})

        if path == "/api/received":
            if not self._guard(local_only=True):
                return
            return self._json(list_dir(State.received))

        if path == "/api/outbox":
            if not self._guard():
                return
            return self._json({"host": socket.gethostname(), "files": list_dir(State.outbox, 200)})

        if path == "/api/notes":
            if not self._guard():
                return
            with State.lock:
                return self._json(list(reversed(State.notes)))

        if path == "/api/history":
            if not self._guard(local_only=True) or not self._pro_only():
                return
            return self._json(Store.stats())

        if path == "/api/zip":
            q = self._query()
            which = q.get("which", [""])[0]
            if which == "received":
                if not self._guard(local_only=True):
                    return
                base = State.received
            elif which == "outbox":
                if not self._guard():
                    return
                base = State.outbox
            else:
                return self._send(404, b"nao encontrado")
            if not self._pro_only():
                return
            names = q.get("n") or [i["name"] for i in list_dir(base, 100000) if not i["partial"]]
            tmp, size = build_zip(base, names)
            stamp = time.strftime("%Y-%m-%d_%H%M")
            try:
                self.send_response(200)
                self.send_header("Content-Type", "application/zip")
                self.send_header("Content-Length", str(size))
                self.send_header("Content-Disposition", f"attachment; filename=\"teleporta_{stamp}.zip\"")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                while chunk := tmp.read(CHUNK):
                    self.wfile.write(chunk)
            except (BrokenPipeError, ConnectionError, TimeoutError):
                self.close_connection = True
            finally:
                tmp.close()
            return

        if path.startswith("/files/received/"):
            if not self._guard(local_only=True):
                return
            f = child_file(State.received, path[len("/files/received/"):])
            return self._send_file(f, attachment=False, cache=True) if f else self._send(404, b"nao encontrado")

        if path.startswith("/download/"):
            if not self._guard():
                return
            f = child_file(State.outbox, path[len("/download/"):])
            if not f:
                return self._send(404, b"nao encontrado")
            attachment = self._query().get("inline", ["0"])[0] != "1"
            if attachment and plan_info()["remaining"] == 0:
                return self._json({"ok": False, "error": "limit"}, 402)
            if self._send_file(f, attachment=attachment) and attachment and not self.headers.get("Range"):
                Store.bump()
                Store.log("out", f.name, f.stat().st_size, self._who())
            return

        self._send(404, b"nao encontrado")

    def _page(self, name):
        self._send(200, (WEB_DIR / name).read_bytes(), "text/html; charset=utf-8")

    # ---------- POST ----------
    def do_POST(self):
        path = urlparse(self.path).path

        if path == "/login":
            ip = self._ip()
            now = time.time()
            with State.lock:
                count, locked_until = State.fails.get(ip, (0, 0))
            if now < locked_until:
                return self._json({"ok": False, "error": "locked", "wait": int(locked_until - now)}, 429)
            pin = str(self._body_json(1024).get("pin", ""))
            if secrets.compare_digest(pin, State.pin):
                with State.lock:
                    State.fails.pop(ip, None)
                return self._json({"ok": True}, headers={"Set-Cookie": self._cookie(self._new_session())})
            count += 1
            with State.lock:
                State.fails[ip] = (0, now + 60) if count >= 5 else (count, 0)
            return self._json({"ok": False, "error": "pin"}, 401)

        if path == "/api/open":
            if not self._guard(local_only=True):
                return
            q = self._query()
            base = State.outbox if q.get("which", [""])[0] == "outbox" else State.received
            name = q.get("name", [""])[0]
            target = child_file(base, name) if name else base
            if target:
                open_path(target)
            return self._json({"ok": bool(target)})

        if path == "/api/notes":
            if not self._guard():
                return
            text = str(self._body_json().get("text", "")).strip()[:NOTE_LEN]
            if not text:
                return self._json({"ok": False}, 400)
            with State.lock:
                State.notes.append({"id": secrets.token_hex(6), "t": time.time(), "from": self._who(), "text": text})
                del State.notes[:-NOTES_MAX]
            return self._json({"ok": True})

        if path == "/api/license":
            if not self._guard(local_only=True):
                return
            key = str(self._body_json(8192).get("key", ""))
            data = licenca.verify(key)
            if not data:
                return self._json({"ok": False}, 400)
            State.license = data
            Store.cfg["license"] = "".join(key.split())
            Store.save()
            return self._json({"ok": True, "email": data.get("e")})

        if path == "/api/settings":
            if not self._guard(local_only=True) or not self._pro_only():
                return
            body = self._body_json()
            if body.get("organize") in ("off", "date", "type"):
                Store.cfg["organize"] = body["organize"]
            if "fixed" in body:
                if body["fixed"]:
                    Store.cfg["fixed"] = True
                    Store.cfg["pair"] = {"pin": State.pin, "token": State.token}
                else:
                    Store.cfg["fixed"] = False
                    Store.cfg.pop("pair", None)
                    Store.cfg.pop("sessions", None)
            Store.save()
            persist_sessions()
            return self._json({"ok": True})

        self._send(404, b"nao encontrado")

    # ---------- PUT ----------
    def do_PUT(self):
        path = urlparse(self.path).path
        if path == "/api/upload":  # celular -> PC
            if not self._guard():
                return
            if plan_info()["remaining"] == 0:
                self.close_connection = True
                return self._json({"ok": False, "error": "limit"}, 402)
            self._receive_file(State.received, "in", count=True)
        elif path == "/api/outbox-upload":  # PC -> celular (arquivos que o PC oferece)
            if self._guard(local_only=True):
                self._receive_file(State.outbox, "out")
        else:
            self._send(404, b"nao encontrado")

    # ---------- DELETE ----------
    def do_DELETE(self):
        path = urlparse(self.path).path
        for prefix, base in (("/api/outbox/", State.outbox), ("/api/received/", State.received)):
            if path.startswith(prefix):
                if not self._guard(local_only=True):
                    return
                f = child_file(base, path[len(prefix):])
                if f:
                    f.unlink()
                return self._json({"ok": bool(f)})
        if path.startswith("/api/notes/"):
            if not self._guard():
                return
            nid = path[len("/api/notes/"):]
            with State.lock:
                State.notes[:] = [n for n in State.notes if n["id"] != nid]
            return self._json({"ok": True})
        self._send(404, b"nao encontrado")


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = False


def load_state():
    """Carrega licença e, no Pro com pareamento fixo, o PIN/token e os celulares já conectados."""
    Store.load()
    State.license = licenca.verify(Store.cfg.get("license", ""))
    if is_pro() and Store.cfg.get("fixed") and Store.cfg.get("pair"):
        State.pin = Store.cfg["pair"]["pin"]
        State.token = Store.cfg["pair"]["token"]
        State.sessions = {k: v for k, v in Store.cfg.get("sessions", {}).items()
                          if isinstance(v, dict) and time.time() - v.get("seen", 0) < session_ttl()}


def main():
    # No Windows o terminal pode não ser UTF-8; evita erro ao imprimir acentos.
    sys.stdout.reconfigure(errors="replace")
    downloads = Path.home() / "Downloads" / "Teleporta"
    ap = argparse.ArgumentParser(description="Passa arquivos entre celular e PC pela rede local.")
    ap.add_argument("--porta", type=int, default=8765)
    ap.add_argument("--pasta", type=Path, default=downloads / "Recebidos", help="onde salvar o que chega do celular")
    ap.add_argument("--pasta-envio", type=Path, default=downloads / "Para o celular", help="arquivos que o celular pode baixar")
    ap.add_argument("--ip", default=None, help="força o IP da rede (se o detectado estiver errado)")
    ap.add_argument("--sem-navegador", action="store_true")
    args = ap.parse_args()

    load_state()
    State.received, State.outbox = args.pasta.resolve(), args.pasta_envio.resolve()
    State.received.mkdir(parents=True, exist_ok=True)
    State.outbox.mkdir(parents=True, exist_ok=True)
    State.host = args.ip or lan_ip()

    server = None
    for port in range(args.porta, args.porta + 10):
        try:
            server = Server(("0.0.0.0", port), Handler)
            State.port = port
            break
        except OSError:
            continue
    if server is None:
        sys.exit(f"Não consegui abrir nenhuma porta entre {args.porta} e {args.porta + 9}.")

    print("\n  Teleporta  celular <-> PC" + ("   [PRO]" if is_pro() else ""))
    print(f"  Painel no PC:   http://localhost:{State.port}")
    print(f"  Endereço rede:  http://{State.host}:{State.port}")
    print(f"  PIN:            {State.pin}")
    print(f"  Recebidos em:   {State.received}")
    print(f"  Para o celular:  {State.outbox}")
    print("\n  Deixe esta janela aberta. Ctrl+C para encerrar.\n")
    if State.host == "127.0.0.1":
        print("  AVISO: não achei sua rede Wi-Fi. Conecte o PC ao Wi-Fi ou use --ip.\n")

    if not args.sem_navegador:
        threading.Timer(0.5, webbrowser.open, args=(f"http://localhost:{State.port}/",)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Encerrado.")


if __name__ == "__main__":
    main()
