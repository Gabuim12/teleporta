"""Licença Pro do Teleporta: chaves assinadas (Ed25519), conferidas offline.

Só quem tem a chave privada (vendedor/gerar_chave.py) consegue criar chaves válidas.
"""
import base64
import json

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

PUBLIC_KEY = "WmQa7K/1I3RkEvXhQUJ7PzPQT8hvRM4XoJB+tnHGVkM="

# Troque pelo link da sua página de pagamento (Kiwify, Hotmart, Mercado Pago, Stripe, Gumroad…).
# O empacotar.ps1 se recusa a gerar o pacote enquanto isto ainda for o texto de exemplo.
BUY_URL = "https://SEU-LINK-DE-PAGAMENTO"


def _b64d(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def verify(key):
    """Devolve {'e': email, 'p': 'pro', 't': data} se a chave for autêntica, senão None."""
    try:
        prefix, payload_b64, sig_b64 = "".join((key or "").split()).split(".")
        if prefix != "TLP1":
            return None
        payload = _b64d(payload_b64)
        Ed25519PublicKey.from_public_bytes(base64.b64decode(PUBLIC_KEY)).verify(_b64d(sig_b64), payload)
        data = json.loads(payload)
        return data if isinstance(data, dict) and data.get("p") == "pro" else None
    except (ValueError, TypeError, InvalidSignature):
        return None
