# Proveniência, manifestos e download idempotente (R03)

Implementado em 2026-09-14. Torna toda entrada de dados identificável e
reobtível: cada arquivo bruto tem manifesto versionado com URL pública, release,
licença, data de acesso, tamanho e checksums, e o download é idempotente, com
retomada segura e verificação antes de promover o arquivo final. Nenhuma
credencial, URL assinada ou token é registrado.

## 1. Schema

- Contrato legível: `schemas/manifest.schema.json` (JSON Schema draft 2020-12),
  com `schema_version`, `dataset`, `release`, `source_page` (https ou DOI),
  `license` (`CC-BY-4.0`, `CC-BY-4.0-restricted`, `CC-BY-4.0-annotations-unclear`)
  e `files`.
- Cada arquivo exige `path` (relativo, sob `data/raw/`), `url` (https sem
  credenciais embutidas), `bytes`, `sha256` e `accessed_at` (AAAA-MM-DD);
  `md5_official` e `notes` são opcionais.
- URLs com parâmetros de assinatura/credencial (`X-Amz-*`, `X-Goog-*`, `token`,
  `sig`, `expires` e afins) são rejeitadas pelo validador e pelo downloader.

## 2. Validador

```bash
python3 tools/manifest.py validate --check-files   # estrutura + bytes/sha256 no disco
python3 tools/manifest.py validate                 # só estrutura (CI sem dados brutos)
python3 tools/manifest.py validate --schema-only   # confere o arquivo de schema
```

O módulo `tools/manifest.py` implementa as mesmas regras do schema em Python
(sem dependências externas), calcula SHA-256/MD5 em blocos e reporta falhas por
campo. Os quatro manifestos versionados passam com `--check-files` enquanto as
amostras de D09 estiverem em `data/raw/spikes/`.

## 3. Download idempotente

```bash
python3 tools/download.py --manifest data/manifests/flywire-783.json \
    --path data/raw/spikes/flywire_proofread_root_ids_783.npy
python3 tools/download.py --path data/raw/spikes/x.bin --url https://... \
    --bytes 1234 --sha256 <64 hex> --record --manifest data/manifests/novo.json
```

- **Idempotente**: se o arquivo existe e confere em tamanho e SHA-256, não faz
  nenhuma requisição e retorna `skipped`.
- **Nunca sobrescreve divergente**: arquivo existente com tamanho ou hash
  diferente gera erro; o arquivo não é tocado.
- **Retomada segura**: usa `.part`, envia `Range` e só continua com resposta
  `206 Partial Content`; se o servidor ignorar o `Range` (200), recomeça do zero.
- **Interrupção**: mantém o `.part` para retomar; transferência incompleta nunca
  é promovida a arquivo final.
- **Verificação final**: tamanho e SHA-256 são conferidos antes de `os.replace`;
  divergência remove o `.part` e falha.
- **Limites e termos**: somente https (http apenas em `localhost` de teste);
  `--max-bytes` bloqueia arquivos acima do teto; nenhum cabeçalho de
  autenticação é usado; nenhum bypass de termos é automatizado.

## 4. Manifestos versionados

| Manifesto | Dataset/release | Arquivos |
|---|---|---|
| `data/manifests/flywire-783.json` | FlyWire/FAFB v783 | 2 |
| `data/manifests/manc-v1.0.json` | MANC v1.0 (bucket flat) | 2 |
| `data/manifests/mcns-v1.0.json` | MCNS `male-cns:v1.0` | 1 |
| `data/manifests/banc-888.json` | BANC v888 | 1 |

Os dados brutos continuam fora do Git; os manifestos (versionados) são a fonte
de proveniência e permitem reobter cada amostra.

## 5. Testes

```bash
.venv/bin/python -m pytest tests/ -q
```

24 casos em `tests/test_manifest.py` e `tests/test_download.py`, com servidor
HTTP local (fixture pequena de 64 KiB): manifesto válido/inválido, URLs com
credencial, download novo, idempotência sem nova requisição, arquivo divergente
protegido, retomada com `Range` 206, servidor sem `Range`, interrupção com
`.part` preservado, checksum divergente e teto `--max-bytes`.

## 6. Limitações

- A retomada não detecta mudança remota na mesma URL; a verificação de SHA-256
  no fim é a salvaguarda.
- Datasets sem checksum oficial (MCNS) dependem do SHA-256 local registrado.
- Os manifestos cobrem as amostras de D09, não os releases completos; a
  ingestão integral reutiliza o mesmo schema e ferramenta (H02/H03).
- O schema é validado por implementação própria; se dependências externas forem
  aprovadas no futuro, `jsonschema` pode verificar o contrato diretamente.
- Validação: `python3 tools/validate_research.py`.
