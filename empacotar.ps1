# Gera os pacotes em dist\release: Teleporta-Windows.zip e Teleporta-Mac.zip (suba como Release no GitHub).
# Uso: .\empacotar.ps1          (recusa gerar enquanto houver links de exemplo "SEU-...")
#      .\empacotar.ps1 -Teste   (ignora a checagem, só para testar o pacote)
param([switch]$Teste)
$ErrorActionPreference = "Continue"  # o pip escreve avisos em stderr; falhas reais são checadas por $LASTEXITCODE
Set-Location $PSScriptRoot
function Check($what) { if ($LASTEXITCODE -ne 0) { throw "Falhou: $what" } }

if (-not $Teste) {
    $pend = Select-String -Path licenca.py, site\index.html -Pattern "SEU-" | ForEach-Object { "$($_.Filename):$($_.LineNumber)  $($_.Line.Trim())" }
    if ($pend) { throw "Troque os textos de exemplo antes de empacotar:`n$($pend -join "`n")" }
}

python -m pip install -q --disable-pip-version-check -r requirements.txt pyinstaller
Check "instalar dependências"

$build = Join-Path $env:TEMP "pyi-build"
python -m PyInstaller --onefile --name Teleporta --add-data "$((Resolve-Path web).Path);web" `
    --distpath dist --workpath $build --specpath $build teleporta.py | Out-Null
Check "PyInstaller"
Remove-Item -Recurse -Force $build

$out = "dist\release"
New-Item -ItemType Directory -Force $out | Out-Null

$steps = @"
1. {ABRIR}
2. {REDE}
3. No celular, no MESMO Wi-Fi, abra a camera e aponte para o QR code que aparece na tela
   (no Samsung, se a camera nao ler, abra o Chrome e digite o endereco e o PIN mostrados na tela)
4. Toque em "Escolher fotos, videos ou arquivos" e envie
   Para mandar do computador para o celular, arraste os arquivos para "Enviar para o celular"

Os arquivos ficam em: Downloads/Teleporta/Recebidos
Deixe a janela aberta enquanto estiver transferindo. Feche quando terminar.
Chave do Pro: cole na aba "Plano" do painel.
"@

# --- Windows ---
$stage = Join-Path $env:TEMP "pacote\Teleporta"
New-Item -ItemType Directory -Force $stage | Out-Null
Copy-Item dist\Teleporta.exe $stage
$win = "TELEPORTA - passa arquivos entre o celular e o PC`r`n`r`n" + $steps.
    Replace("{ABRIR}", 'De dois cliques em Teleporta.exe (se o Windows avisar "protegeu seu computador": Mais informacoes > Executar assim mesmo)').
    Replace("{REDE}", 'Se o Windows perguntar sobre o firewall, clique em "Permitir acesso"')
Set-Content -Encoding UTF8 "$stage\LEIA-ME.txt" $win
Compress-Archive -Path $stage -DestinationPath "$PWD\$out\Teleporta-Windows.zip" -Force
Remove-Item -Recurse -Force (Split-Path $stage)

# --- Mac ---
$mac = "TELEPORTA (Mac) - passa arquivos entre o celular e o Mac`n`n" + $steps.
    Replace("{ABRIR}", 'Abra o app Terminal, digite  bash  (com um espaco), arraste o arquivo iniciar.command para a janela e aperte Enter (na primeira vez o Mac pode pedir para instalar as Ferramentas de Linha de Comando: aceite, espere e repita)').
    Replace("{REDE}", 'Se o Mac perguntar sobre conexoes de rede, clique em Permitir').Replace("`r`n", "`n")
$macPy = @'
import sys, zipfile, pathlib
out, readme = sys.argv[1], pathlib.Path(sys.argv[2]).read_bytes()
launcher = b'#!/bin/bash\ncd "$(dirname "$0")"\n[ -d .venv ] || python3 -m venv .venv\n.venv/bin/pip install -q -r requirements.txt\n.venv/bin/python teleporta.py\n'
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for name in ["teleporta.py", "licenca.py", "dados.py", "requirements.txt"]:
        z.write(name, f"Teleporta/{name}")
    for f in pathlib.Path("web").iterdir():
        z.write(f, f"Teleporta/web/{f.name}")
    for name, data, mode in [("iniciar.command", launcher, 0o755), ("LEIA-ME.txt", readme, 0o644)]:
        i = zipfile.ZipInfo(f"Teleporta/{name}"); i.external_attr = mode << 16; i.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(i, data)
'@
$readme = Join-Path $env:TEMP "leiame-mac.txt"
[IO.File]::WriteAllText($readme, $mac, (New-Object Text.UTF8Encoding $false))
$macPy | python - "$PWD\$out\Teleporta-Mac.zip" $readme
Remove-Item $readme

Get-ChildItem $out\*.zip | Select-Object Name, @{n = 'MB'; e = { [math]::Round($_.Length / 1MB, 1) } }
