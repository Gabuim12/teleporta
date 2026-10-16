<p align="center"><img src="web/logo.svg" width="72" alt="Teleporta"></p>

<h1 align="center">Teleporta</h1>

<p align="center">Passe fotos, vídeos e arquivos entre o celular e o PC pelo Wi-Fi.<br>Sem cabo, sem nuvem, sem recompressão.</p>

---

## O que é

O Teleporta roda um servidor pequeno no seu computador e mostra um **QR code**. Você aponta a câmera do celular, abre a página no navegador e envia os arquivos direto para uma pasta do PC. **O celular não precisa instalar nada.** Também funciona no sentido contrário: arraste arquivos no painel do PC e baixe no celular.

- Funciona **só na rede local**: os arquivos não passam pela internet nem por servidor de terceiros.
- **Qualidade original**: nada é recomprimido, e a data original da foto é preservada.
- Painel em **português e inglês**, com modo claro e escuro.

## Como funciona

```
 Celular (navegador)                         PC (Teleporta)
 ───────────────────      Wi-Fi / LAN      ───────────────────────────
  lê o QR code / PIN  ─────────────────▶   servidor HTTP (Python)
  envia arquivos (PUT) ────────────────▶   grava em Downloads/Teleporta/Recebidos
  baixa arquivos (GET) ◀────────────────   serve Downloads/Teleporta/Para o celular
  texto e links        ◀───────────────▶   painel em http://localhost:8765
```

1. O PC gera um **PIN de 6 dígitos** e um token. O QR code abre `/auth?t=<token>` no celular.
2. O servidor cria uma sessão (cookie `HttpOnly`, `SameSite=Strict`) e libera a página do celular.
3. Os uploads chegam como um fluxo de bytes e são gravados em um arquivo `.part`. Ele só vira o arquivo final quando termina, então não aparece arquivo pela metade.

### Segurança

- O painel do PC (`/api/info`, lista de recebidos, configurações, licença) só responde a `localhost`, com checagem de `Host` e `Origin`. Isso barra ataques vindos de outros sites e DNS rebinding.
- O celular só entra com o PIN ou o QR code. Depois de 5 erros de PIN, o IP fica bloqueado por 1 minuto.
- Nomes de arquivo são sanitizados (sem `..`, sem nomes reservados do Windows) e todo acesso a arquivo é confinado à pasta escolhida.
- Em redes públicas, prefira não usar.

## Grátis e Pro

| | Grátis | Pro |
|---|:---:|:---:|
| Celular → PC e PC → celular | ✓ | ✓ |
| Texto e links entre os aparelhos | ✓ | ✓ |
| Arquivos por dia | 30 | ilimitado |
| Organizar recebidos por data da foto ou por tipo | | ✓ |
| Pareamento fixo (escaneia uma vez só) | | ✓ |
| Baixar vários arquivos em ZIP | | ✓ |
| Histórico e estatísticas | | ✓ |

O Pro ainda **não está à venda**. A licença é uma chave assinada com Ed25519, verificada offline pelo próprio app (`licenca.py`). A ferramenta que emite as chaves não faz parte deste repositório.

## Baixar

Pacotes na página de [Releases](https://github.com/Gabuim12/teleporta/releases).

- **Windows**: baixe `Teleporta-Windows.zip`, extraia e abra `Teleporta.exe`. O executável **não tem assinatura digital**, então o Windows pode avisar "protegeu seu computador" (Mais informações → Executar assim mesmo) ou bloqueá-lo, conforme a configuração do Smart App Control.
- **Mac**: baixe `Teleporta-Mac.zip` e siga o `LEIA-ME.txt`. Roda via script e precisa de Python 3.

Esta é uma versão **beta**.

## Rodar pelo código-fonte

Requer Python 3. Testado no 3.14.

```bash
pip install -r requirements.txt
python teleporta.py
```

Opções: `--porta`, `--pasta` (onde salvar), `--pasta-envio`, `--ip` (força o IP da rede) e `--sem-navegador`. Os dados do app (configuração, histórico) ficam em `~/.teleporta` (ou em `TELEPORTA_HOME`).

### Gerar o executável

```powershell
.\empacotar.ps1 -Teste
```

Gera `dist\release\Teleporta-Windows.zip` e `Teleporta-Mac.zip` com o PyInstaller.

## Estrutura

```
teleporta.py   servidor HTTP, rotas e regras do plano
licenca.py     verificação offline da chave de licença (Ed25519)
dados.py       configuração, histórico e contagem diária
web/           painel do PC, tela do celular, login (HTML, CSS e JS puros)
site/          página de apresentação (publicada na Vercel)
empacotar.ps1  gera os pacotes de Windows e Mac
```

Dependências: `qrcode` e `cryptography`. Todo o resto é biblioteca padrão do Python.

---

### English

**Teleporta** moves photos, videos and files between your phone and PC over your local Wi-Fi: no cable, no cloud, no recompression. The PC runs a tiny server and shows a QR code; the phone scans it and uploads straight to a folder, with nothing to install on the phone. A Pro tier (not for sale yet) adds unlimited files, auto-sorting, fixed pairing, ZIP download and history. Run it with `pip install -r requirements.txt && python teleporta.py`. Beta software; the Windows build is unsigned.

---

© 2026 Teleporta. Todos os direitos reservados.
