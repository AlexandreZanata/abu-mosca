import hashlib
import http.server
import sys
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import download as d  # noqa: E402

PAYLOAD = bytes(range(256)) * 256  # 64 KiB determinístico


class Handler(http.server.BaseHTTPRequestHandler):
    payload = PAYLOAD
    support_range = True
    fail_after = None
    count = 0
    bytes_sent = 0
    last_range = None

    def log_message(self, *args):  # silencia o servidor no pytest
        pass

    def do_GET(self):
        type(self).count += 1
        type(self).last_range = self.headers.get("Range")
        data = type(self).payload
        start = 0
        if self.headers.get("Range") and type(self).support_range:
            start = int(self.headers["Range"].split("=")[1].split("-")[0])
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{len(data) - 1}/{len(data)}")
        else:
            self.send_response(200)
        body = data[start:]
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if type(self).fail_after is not None and len(body) > type(self).fail_after:
            self.wfile.write(body[: type(self).fail_after])
            self.wfile.flush()
            self.connection.close()
        else:
            self.wfile.write(body)
            type(self).bytes_sent += len(body)


@pytest.fixture()
def server():
    Handler.payload = PAYLOAD
    Handler.support_range = True
    Handler.fail_after = None
    Handler.count = 0
    Handler.bytes_sent = 0
    Handler.last_range = None
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}/fixture.bin"
    httpd.shutdown()
    thread.join(timeout=5)


@pytest.fixture()
def area(tmp_path, monkeypatch):
    monkeypatch.setattr(d, "ROOT", tmp_path)
    return tmp_path


def entry(url: str, digest: str = None) -> dict:
    return {
        "path": "data/raw/spikes/fixture.bin",
        "url": url,
        "bytes": len(PAYLOAD),
        "sha256": digest or hashlib.sha256(PAYLOAD).hexdigest(),
        "accessed_at": "2026-09-14",
    }


def dest(area: Path) -> Path:
    return area / "data" / "raw" / "spikes" / "fixture.bin"


def test_download_novo(server, area):
    result = d.download_entry(entry(server))
    assert result["status"] == "downloaded"
    assert dest(area).read_bytes() == PAYLOAD
    assert Handler.bytes_sent == len(PAYLOAD)


def test_download_idempotente_nao_repete(server, area):
    d.download_entry(entry(server))
    requests_before = Handler.count
    result = d.download_entry(entry(server))
    assert result["status"] == "skipped"
    assert result["transferred"] == 0
    assert Handler.count == requests_before


def test_arquivo_divergente_nao_e_sobrescrito(server, area):
    path = dest(area)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"conteudo errado")
    with pytest.raises(d.DownloadError):
        d.download_entry(entry(server))
    assert path.read_bytes() == b"conteudo errado"
    assert Handler.count == 0


def test_retomada_com_range(server, area):
    path = dest(area)
    path.parent.mkdir(parents=True, exist_ok=True)
    half = len(PAYLOAD) // 2
    path.with_suffix(".bin.part").write_bytes(PAYLOAD[:half])
    result = d.download_entry(entry(server))
    assert result["status"] == "resumed"
    assert result["transferred"] == len(PAYLOAD) - half
    assert Handler.last_range == f"bytes={half}-"
    assert path.read_bytes() == PAYLOAD
    assert not path.with_suffix(".bin.part").exists()


def test_sem_range_recomeca(server, area):
    Handler.support_range = False
    path = dest(area)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.with_suffix(".bin.part").write_bytes(PAYLOAD[:100])
    result = d.download_entry(entry(server))
    assert result["status"] == "downloaded"
    assert result["transferred"] == len(PAYLOAD)
    assert path.read_bytes() == PAYLOAD


def test_checksum_divergente_falha_e_limpa_part(server, area):
    with pytest.raises(d.DownloadError, match="sha256"):
        d.download_entry(entry(server, digest="0" * 64))
    assert not dest(area).exists()
    assert not dest(area).with_suffix(".bin.part").exists()


def test_interrupcao_preserva_part_para_retomada(server, area):
    Handler.fail_after = 1024
    with pytest.raises(d.DownloadError, match="retomada"):
        d.download_entry(entry(server))
    part = dest(area).with_suffix(".bin.part")
    assert part.exists() and part.stat().st_size == 1024
    Handler.fail_after = None
    result = d.download_entry(entry(server))
    assert result["status"] == "resumed"
    assert dest(area).read_bytes() == PAYLOAD


def test_url_com_credencial_e_recusada_sem_requisicao(server, area):
    bad = server + "?X-Goog-Signature=abc"
    with pytest.raises(d.DownloadError, match="credencial"):
        d.download_entry(entry(bad))
    assert Handler.count == 0


def test_limite_max_bytes_bloqueia(server, area):
    with pytest.raises(d.DownloadError, match="max-bytes"):
        d.download_entry(entry(server), max_bytes=1024)
    assert Handler.count == 0
