#!/usr/bin/env python3
"""Gera os ativos de marca (logos, ícones, favicon, imagem de compartilhamento) a partir de brand/identidade.png.

  python brand/gerar_ativos.py

Saídas: brand/*.png|ico, web/*.png (app) e site/*.png (página de apresentação).
Requer Pillow e numpy. As fontes brand/_*.ttf só servem para a imagem de compartilhamento.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
BRAND, WEB, SITE = ROOT / "brand", ROOT / "web", ROOT / "site"
SRC = Image.open(BRAND / "identidade.png").convert("RGB")

NAVY = (6, 17, 37)  # #061125
ORANGE_A, ORANGE_B = (254, 166, 3), (254, 60, 5)  # gradiente do ícone laranja da prancha
MUTED_ON_DARK = (167, 179, 207)


def to_rgba(box, strength=0.5):
    """Recorta sobre fundo branco e devolve RGBA (fundo vira transparente, cores preservadas)."""
    p = np.asarray(SRC.crop(box)).astype(float) / 255
    dist = 1 - p.min(axis=2)  # distância ao branco
    floor = 0.07  # o fundo da prancha tem um ruído leve; abaixo disso é transparente
    alpha = np.clip((dist - floor) / (strength - floor), 0, 1)
    a3 = alpha[..., None]
    fg = np.where(a3 > 0.001, (p - (1 - a3)) / np.maximum(a3, 0.001), 0).clip(0, 1)
    out = np.dstack([fg, alpha])
    return Image.fromarray((out * 255).round().astype("uint8"), "RGBA")


def trim(im, pad=6):
    x0, y0, x1, y1 = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))


def recolor_for_dark(im):
    """Texto escuro vira branco e a tagline cinza vira cinza-claro; laranja, violeta e azul ficam iguais."""
    a = np.asarray(im).astype(float) / 255
    rgb, alpha = a[..., :3], a[..., 3]
    sat = rgb.max(axis=2) - rgb.min(axis=2)
    lum = rgb.mean(axis=2)
    neutral = sat < 0.16
    out = rgb.copy()
    out[neutral & (lum < 0.30)] = 1.0
    out[neutral & (lum >= 0.30)] = np.array(MUTED_ON_DARK) / 255
    return Image.fromarray((np.dstack([out, alpha]) * 255).round().astype("uint8"), "RGBA")


def resize_w(im, w):
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def save(im, *paths, **kw):
    for p in paths:
        im.save(p, optimize=True, **kw)
        print("ok", p.relative_to(ROOT), im.size)


def erase_blue(im, left_limit):
    """Apaga os quadradinhos azuis (a 'nuvem de dados') à esquerda da porta, mantendo nuvem e porta."""
    a = np.asarray(im).copy().astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    blue = (b - r > 60) & (g < 190) & (a[..., 3] > 0)
    blue[:, left_limit:] = False  # a ponta violeta da nuvem fica intacta
    # engorda a máscara para levar junto as bordas suavizadas dos quadradinhos
    mask = Image.fromarray((blue * 255).astype("uint8")).filter(ImageFilter.MaxFilter(7))
    erase = np.asarray(mask) > 0
    erase[:, left_limit:] = False
    a[erase, 3] = 0
    return Image.fromarray(a.astype("uint8"), "RGBA")


# ---------- logos ----------
logo = trim(to_rgba((295, 66, 1495, 318)))
logo_tag = trim(to_rgba((295, 66, 1495, 360)))
mark = trim(to_rgba((295, 66, 700, 318)))
# a porta começa em x=455 na prancha (x=165 no recorte); tudo à esquerda disso, em azul, é a nuvem de dados
door_cloud = trim(erase_blue(to_rgba((295, 66, 700, 318)), left_limit=164))

logo_w, logo_tag_w = recolor_for_dark(logo), recolor_for_dark(logo_tag)

save(resize_w(logo, 720), BRAND / "logo.png")
save(resize_w(logo_w, 720), BRAND / "logo-branca.png")
save(resize_w(logo_tag, 1000), BRAND / "logo-tagline.png")
save(resize_w(logo_tag_w, 1000), BRAND / "logo-tagline-branca.png")
save(resize_w(mark, 480), BRAND / "simbolo.png")
# app (cabeçalho, ~30px de altura)
save(resize_w(logo, 360), WEB / "logo.png")
save(resize_w(logo_w, 360), WEB / "logo-branca.png")
# site
save(resize_w(logo, 720), SITE / "logo.png")
save(resize_w(logo_w, 720), SITE / "logo-branca.png")
save(resize_w(door_cloud.resize((door_cloud.width * 2, door_cloud.height * 2), Image.LANCZOS), 640), SITE / "porta.png")


# ---------- ícones do app ----------
def rounded_mask(size, radius_ratio=0.225, ss=4):
    big = Image.new("L", (size * ss, size * ss), 0)
    ImageDraw.Draw(big).rounded_rectangle((0, 0, size * ss - 1, size * ss - 1), radius=int(size * ss * radius_ratio), fill=255)
    return big.resize((size, size), Image.LANCZOS)


def gradient(size, a, b):
    t = (np.add.outer(np.arange(size), np.arange(size)) / (2 * (size - 1)))[..., None]
    arr = np.array(a) * (1 - t) + np.array(b) * t
    return Image.fromarray(arr.round().astype("uint8"), "RGB").convert("RGBA")


def app_icon(size, dark=False):
    base = Image.new("RGBA", (size, size), NAVY + (255,)) if dark else gradient(size, ORANGE_A, ORANGE_B)
    if dark:
        glyph = mark
    else:  # silhueta branca do símbolo
        glyph = Image.new("RGBA", mark.size, (255, 255, 255, 0))
        glyph.putalpha(mark.getchannel("A"))
        white = Image.new("RGBA", mark.size, (255, 255, 255, 255))
        white.putalpha(mark.getchannel("A"))
        glyph = white
    g = resize_w(glyph, round(size * 0.66))
    base.alpha_composite(g, ((size - g.width) // 2, (size - g.height) // 2))
    base.putalpha(rounded_mask(size))
    return base


icon = app_icon(1024)
icon_dark = app_icon(1024, dark=True)
save(icon.resize((512, 512), Image.LANCZOS), BRAND / "icone-512.png")
save(icon_dark.resize((512, 512), Image.LANCZOS), BRAND / "icone-escuro-512.png")
save(icon.resize((192, 192), Image.LANCZOS), WEB / "icon.png", SITE / "icon.png")
save(icon.resize((180, 180), Image.LANCZOS), SITE / "apple-touch-icon.png")
icon.resize((256, 256), Image.LANCZOS).save(BRAND / "teleporta.ico", sizes=[(s, s) for s in (16, 24, 32, 48, 64, 128, 256)])
print("ok brand/teleporta.ico")

# ---------- imagem de compartilhamento (1200x630) ----------
og = Image.new("RGBA", (1200, 630), NAVY + (255,))
glow = Image.new("RGBA", (1200, 630), (0, 0, 0, 0))
ImageDraw.Draw(glow).ellipse((250, 40, 950, 560), fill=(255, 106, 0, 46))
og.alpha_composite(glow.filter(ImageFilter.GaussianBlur(90)))
lg = resize_w(logo_w, 860)
og.alpha_composite(lg, ((1200 - lg.width) // 2, 175))
font = ImageFont.truetype(str(BRAND / "_Inter-500.ttf"), 26)
tag, track = "DADOS EM MOVIMENTO. RESULTADOS MAIS RÁPIDOS.", 7
w = sum(font.getlength(c) + track for c in tag) - track
d, x = ImageDraw.Draw(og), (1200 - w) / 2
for c in tag:
    d.text((x, 440), c, font=font, fill=MUTED_ON_DARK)
    x += font.getlength(c) + track
save(og.convert("RGB"), BRAND / "og.png", SITE / "og.png")
