#!/usr/bin/env python3
"""Download idempotente com retomada segura e verificação de checksum (R03).

Regras: só https (http apenas em localhost de teste), nunca usa ou registra
credenciais, não sobrescreve arquivo existente divergente, retoma `.part` apenas
quando o servidor confirma `206 Partial Content` e sempre confere tamanho/checksum
antes de promover o arquivo final.
"""

import argparse
import http.client
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from manifest import (  # noqa: E402
    FORBIDDEN_QUERY_KEYS,
    FORBIDDEN_QUERY_PREFIXES,
    ROOT,
    SHA256_RE,
    check_files,
    file_digest,
    load,
    validate_manifest,
)

CHUNK = 1 << 20
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
USER_AGENT = "crossconnectome-mu/R03 (+proveniencia; contato: repositorio local)"


class DownloadError(RuntimeError):
    pass


def check_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme == "https":
        pass
    elif parsed.scheme == "http" and parsed.hostname in LOCAL_HOSTS:
        pass
    else:
        raise DownloadError(f"URL não permitida (somente https): {url}")
    if parsed.username or parsed.password:
        raise DownloadError("URL com credenciais embutidas é proibida")
    for key, _ in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True):
        lowered = key.lower()
        if lowered in FORBIDDEN_QUERY_KEYS or lowered.startswith(FORBIDDEN_QUERY_PREFIXES):
            raise DownloadError(f"URL com parâmetro de credencial/assinatura '{key}' é proibida")


def expected_bytes(entry: dict) -> int:
    value = entry.get("bytes")
    if not isinstance(value, int) or value < 1:
        raise DownloadError("entrada sem 'bytes' válido")
    return value


def verify_file(path: Path, entry: dict) -> None:
    size = path.stat().st_size
    if size != expected_bytes(entry):
        raise DownloadError(f"tamanho divergente: {size} != {entry['bytes']}")
    digest = file_digest(path)
    if digest != entry["sha256"]:
        raise DownloadError(f"sha256 divergente: {digest} != {entry['sha256']}")


def download_entry(
    entry: dict,
    max_bytes: int | None = None,
    timeout: int = 30,
) -> dict:
    url = str(entry["url"])
    check_url(url)
    dest = ROOT / str(entry["path"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        verify_file(dest, entry)
        return {"status": "skipped", "path": str(dest), "bytes": dest.stat().st_size, "transferred": 0}
    part = dest.with_suffix(dest.suffix + ".part")
    limit = expected_bytes(entry)
    if max_bytes is not None and limit > max_bytes:
        raise DownloadError(f"arquivo excede --max-bytes ({limit} > {max_bytes})")

    headers = {"User-Agent": USER_AGENT, "Accept-Encoding": "identity"}
    offset = part.stat().st_size if part.exists() else 0
    resumed = offset > 0
    if resumed:
        headers["Range"] = f"bytes={offset}-"
    request = urllib.request.Request(url, headers=headers, method="GET")
    started = time.perf_counter()
    transferred = 0
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", response.getcode())
            if status == 206 and resumed:
                mode = "ab"
            elif status == 200:
                mode = "wb"
                offset = 0
                resumed = False
            else:
                raise DownloadError(f"resposta inesperada do servidor: {status}")
            with part.open(mode) as handle:
                while block := response.read(CHUNK):
                    handle.write(block)
                    transferred += len(block)
                    if limit is not None and part.stat().st_size > limit:
                        handle.close()
                        part.unlink(missing_ok=True)
                        raise DownloadError("download excedeu o tamanho esperado declarado")
    except urllib.error.HTTPError as error:
        raise DownloadError(f"HTTP {error.code} ao baixar {url}") from error
    except (
        urllib.error.URLError,
        TimeoutError,
        ConnectionError,
        http.client.HTTPException,
    ) as error:
        raise DownloadError(f"interrompido ({error}); '.part' preservado para retomada") from error

    size = part.stat().st_size
    if size < limit:
        raise DownloadError(
            f"transferência incompleta ({size}/{limit} bytes); '.part' preservado para retomada"
        )
    if size > limit:
        part.unlink(missing_ok=True)
        raise DownloadError(f"tamanho excedente recebido ({size} > {limit})")
    try:
        verify_file(part, entry)
    except DownloadError:
        part.unlink(missing_ok=True)
        raise
    os.replace(part, dest)
    return {
        "status": "resumed" if resumed else "downloaded",
        "path": str(dest),
        "bytes": dest.stat().st_size,
        "transferred": transferred,
        "seconds": round(time.perf_counter() - started, 3),
    }


def entry_from_args(args: argparse.Namespace) -> dict:
    return {
        "path": args.path,
        "url": args.url,
        "bytes": args.bytes,
        "sha256": args.sha256,
        "md5_official": args.md5_official,
        "accessed_at": time.strftime("%Y-%m-%d", time.gmtime()),
    }


def record_entry(manifest_path: Path, entry: dict) -> None:
    payload = load(manifest_path)
    paths = {item["path"] for item in payload["files"]}
    if entry["path"] in paths:
        raise DownloadError(f"manifesto já contém '{entry['path']}'")
    payload["files"].append(entry)
    failures = validate_manifest(payload, manifest_path.name)
    if failures:
        raise DownloadError("; ".join(failures))
    temp = manifest_path.with_suffix(".json.tmp")
    temp.write_text(
        __import__("json").dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temp, manifest_path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, help="manifesto com a entrada desejada")
    parser.add_argument("--path", help="caminho relativo da entrada no manifesto")
    parser.add_argument("--url")
    parser.add_argument("--bytes", type=int)
    parser.add_argument("--sha256")
    parser.add_argument("--md5-official", default=None)
    parser.add_argument("--max-bytes", type=int, default=None)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--record", action="store_true", help="adiciona a entrada ao manifesto após sucesso")
    args = parser.parse_args()
    try:
        if args.manifest is not None:
            payload = load(args.manifest)
            failures = validate_manifest(payload, args.manifest.name)
            if failures:
                raise DownloadError("; ".join(failures))
            if args.path is None:
                raise DownloadError("--path obrigatório com --manifest")
            entry = next((item for item in payload["files"] if item["path"] == args.path), None)
            if entry is None:
                raise DownloadError(f"entrada '{args.path}' não encontrada em {args.manifest.name}")
        else:
            if not (args.path and args.url and args.bytes and args.sha256):
                raise DownloadError("modo avulso exige --path --url --bytes --sha256")
            if not SHA256_RE.match(args.sha256):
                raise DownloadError("--sha256 deve ter 64 hexadecimais minúsculos")
            entry = entry_from_args(args)
        result = download_entry(entry, max_bytes=args.max_bytes, timeout=args.timeout)
        print(
            f"{result['status']}: {entry['path']} ({result['bytes']} bytes, "
            f"{result['transferred']} transferidos, {result.get('seconds', 0)} s)"
        )
        if args.record:
            if args.manifest is None:
                raise DownloadError("--record exige --manifest")
            record_entry(args.manifest, entry)
            print(f"registrado em {args.manifest}")
        return 0
    except DownloadError as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
