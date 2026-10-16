"""Dados persistentes do Teleporta: configuração, histórico e contagem diária (plano grátis)."""
import json
import os
import threading
import time
from pathlib import Path

HOME = Path(os.environ.get("TELEPORTA_HOME") or Path.home() / ".teleporta")
FREE_DAILY = 30  # arquivos por dia no plano grátis
HISTORY_MAX = 1000


def today():
    return time.strftime("%Y-%m-%d")


class Store:
    lock = threading.RLock()
    cfg = {}
    history = []

    @classmethod
    def load(cls):
        HOME.mkdir(parents=True, exist_ok=True)
        cls.cfg = cls._read("config.json", {})
        cls.history = cls._read("history.json", [])

    @staticmethod
    def _read(name, default):
        try:
            data = json.loads((HOME / name).read_text(encoding="utf-8"))
            return data if isinstance(data, type(default)) else default
        except (OSError, ValueError):
            return default

    @staticmethod
    def _write(name, data):
        tmp = HOME / (name + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        tmp.replace(HOME / name)

    @classmethod
    def save(cls):
        with cls.lock:
            cls._write("config.json", cls.cfg)

    # ---- contagem diária ----
    @classmethod
    def used_today(cls):
        u = cls.cfg.get("usage", {})
        return u.get("n", 0) if u.get("day") == today() else 0

    @classmethod
    def bump(cls):
        with cls.lock:
            cls.cfg["usage"] = {"day": today(), "n": cls.used_today() + 1}
            cls.save()

    # ---- histórico ----
    @classmethod
    def log(cls, direction, name, size, device):
        """direction: 'in' (celular -> PC) ou 'out' (PC -> celular)."""
        with cls.lock:
            cls.history.append({"t": time.time(), "d": direction, "n": name, "s": size, "dev": device})
            del cls.history[:-HISTORY_MAX]
            cls._write("history.json", cls.history)

    @classmethod
    def stats(cls):
        with cls.lock:
            items = list(cls.history)
        days = {}
        for i in range(13, -1, -1):
            days[time.strftime("%Y-%m-%d", time.localtime(time.time() - i * 86400))] = [0, 0]
        total = {"in": 0, "out": 0, "files": len(items)}
        for it in items:
            total[it["d"]] += it["s"]
            d = days.get(time.strftime("%Y-%m-%d", time.localtime(it["t"])))
            if d:
                d[0] += 1
                d[1] += it["s"]
        return {
            "total": total,
            "days": [{"day": k, "files": v[0], "bytes": v[1]} for k, v in days.items()],
            "items": list(reversed(items[-100:])),
        }
