#!/usr/bin/env python3
"""Reprodução do baseline publicado REGAL/xNetMF dentro da fonte (B08).

O código oficial é executado **sem modificações** (commit fixado) em um
ambiente separado e pinado (numpy/scipy/networkx/scikit-learn), porque o
`alignments.py` original importa sklearn, que não faz parte do lock do projeto.
Este módulo apenas orquestra a execução, lê a saída oficial e registra a
paridade com o artefato público do próprio repositório (embeddings de
referência) e o status da paridade numérica contra a publicação.

Supervisão declarada: o mapeamento verdadeiro do benchmark é usado somente
para pontuar (avaliação), nunca como entrada do método; o núcleo xNetMF/REGAL
é não supervisionado. A variante com atributos fica em trilho separado e não é
executada aqui. Nenhum dado além da fonte e do benchmark público entra.
"""

import argparse
import hashlib
import json
import re
import resource
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "data" / "raw" / "vendor" / "regal-42ed9083"
VENV_PY = ROOT / ".local" / "regal-venv" / "bin" / "python"
TARBALL = ROOT / "data" / "raw" / "vendor" / "regal-42ed9083.tar.gz"
PIP_REPORT = ROOT / "data" / "raw" / "vendor" / "regal-venv-pip-report.json"

REGAL_COMMIT = "42ed9083f51ad481dc7d7acfb488b390e2013050"
REGAL_LICENSE = "MIT"
BENCHMARK_EDGES = "data/arenas_combined_edges.txt"
BENCHMARK_MAPPING = "data/arenas_edges-mapping-permutation.txt"
REFERENCE_EMBEDDING = "emb/arenas990-1.emb.npy"
INCONSISTENT_EMBEDDING = "emb/arenas990-1.emb"
PAPER_V1_SHA256 = "5146b029c0864f5ffdb2f1b60ca96c69c40f1ce735d5d4f1a74c0281d847d07b"
PAPER_V3_SHA256 = "f0057edca4d052c29455eb78662bc018b73de015fefe309aefc7a4db07e17997"
PAPER_V1 = ROOT / "data" / "raw" / "vendor" / "papers" / "regal-v1.pdf"
PAPER_V3 = ROOT / "data" / "raw" / "vendor" / "papers" / "regal-v3.pdf"
ACCURACY_TOLERANCE = 0.002
EMBEDDING_MEAN_ABS_TOLERANCE = 1e-4
VENDOR_FILES = (
    "regal.py",
    "xnetmf.py",
    "config.py",
    "alignments.py",
    "license.txt",
    BENCHMARK_EDGES,
    BENCHMARK_MAPPING,
    REFERENCE_EMBEDDING,
    INCONSISTENT_EMBEDDING,
)
SCORE_RE = re.compile(r"^score top(\d+): ([0-9]+\.[0-9]+)$", re.M)


class RegalError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while block := handle.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def parse_scores(stdout: str) -> dict[str, float]:
    scores = {f"top{number}": float(value) for number, value in SCORE_RE.findall(stdout)}
    if "top1" not in scores:
        raise RegalError("saída oficial sem 'score top1'")
    return scores


def artifact_parity(
    run_accuracy: float,
    reference_accuracy: float,
    run_sha256: str,
    reference_sha256: str,
    max_abs_diff: float,
    mean_abs_diff: float,
) -> dict:
    delta = abs(run_accuracy - reference_accuracy)
    identical = run_sha256 == reference_sha256
    reproduced = identical or (delta <= ACCURACY_TOLERANCE and mean_abs_diff <= EMBEDDING_MEAN_ABS_TOLERANCE)
    return {
        "status": "reproduzido" if reproduced else "divergente",
        "run_accuracy": round(run_accuracy, 6),
        "reference_accuracy": round(reference_accuracy, 6),
        "delta_accuracy": round(delta, 6),
        "run_sha256": run_sha256,
        "reference_sha256": reference_sha256,
        "hash_identical": identical,
        "max_abs_diff": round(max_abs_diff, 6),
        "mean_abs_diff": round(mean_abs_diff, 6),
        "tolerance_accuracy": ACCURACY_TOLERANCE,
        "tolerance_mean_abs": EMBEDDING_MEAN_ABS_TOLERANCE,
    }


def published_parity() -> dict:
    return {
        "status": "não verificável numericamente",
        "numeric_reference": None,
        "reason": (
            "a publicação (arXiv:1802.06257v3 / CIKM 2018) reporta acurácia apenas "
            "graficamente na Figura 4; a Tabela 4 contém tempos e a Tabela 5 contém "
            "datasets, sem valor numérico de acurácia por dataset"
        ),
        "checked_sources": [
            {
                "source": "arXiv:1802.06257v3 / DOI 10.1145/3269206.3271788",
                "location": "Tabela 4 (runtime), Tabela 5 (datasets), acurácia somente na Figura 4",
                "sha256": PAPER_V3_SHA256,
            },
            {
                "source": "arXiv:1802.06257v1 (título anterior, case study do mirrored Karate)",
                "location": "seção 6.1: único valor numérico público (79,4%, REGAL-xNetMF) com instância não especificada (permutação e par conectado ausentes)",
                "sha256": PAPER_V1_SHA256,
            },
        ],
    }


def _run(command: list[str], cwd: Path) -> tuple[str, str, float]:
    started = time.perf_counter()
    completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    seconds = time.perf_counter() - started
    if completed.returncode != 0:
        raise RegalError(f"comando falhou ({completed.returncode}): {' '.join(command)}\n{completed.stderr[-500:]}")
    return completed.stdout, completed.stderr, seconds


def _score_embeddings(embedding: Path, mapping: str = BENCHMARK_MAPPING) -> dict:
    script = (
        "import json, pickle, sys\n"
        "import numpy as np\n"
        "sys.path.insert(0, '.')\n"
        "import alignments as al\n"
        "path, mapping = sys.argv[1], sys.argv[2]\n"
        "emb = np.load(path) if path.endswith('.npy') else np.asarray(pickle.load(open(path, 'rb'), encoding='latin1'))\n"
        "true = pickle.load(open(mapping, 'rb'), encoding='latin1')\n"
        "true = {int(k): int(v) for k, v in true.items()}\n"
        "emb1, emb2 = al.get_embeddings(emb)\n"
        "similarity = al.get_embedding_similarities(emb1, emb2)\n"
        "score, correct = al.score_alignment_matrix(similarity, topk=1, true_alignments=true)\n"
        "print(json.dumps({'accuracy': float(score), 'correct': len(correct), 'pairs': int(emb.shape[0] // 2)}))\n"
    )
    stdout, _, _ = _run([str(VENV_PY), "-c", script, str(embedding), str(mapping)], cwd=VENDOR)
    return json.loads(stdout.strip().splitlines()[-1])


def _embedding_diff(first: Path, second: Path) -> dict:
    import numpy as np

    left = np.load(first)
    right = np.load(second)
    if left.shape != right.shape:
        raise RegalError(f"shapes divergentes: {left.shape} vs {right.shape}")
    delta = np.abs(left - right)
    return {"max_abs_diff": float(delta.max()), "mean_abs_diff": float(delta.mean())}


def _environment(versions: tuple[str, ...] = ("numpy", "scipy", "networkx", "scikit-learn")) -> dict:
    script = "import json, importlib.metadata as m, sys; print(json.dumps({'python': sys.version.split()[0], 'packages': {n: m.version(n) for n in %r}}))" % (list(versions),)
    stdout, _, _ = _run([str(VENV_PY), "-c", script], cwd=VENDOR)
    data = json.loads(stdout.strip().splitlines()[-1])
    wheels = []
    if PIP_REPORT.exists():
        report = json.loads(PIP_REPORT.read_text(encoding="utf-8"))
        for item in report.get("install", []):
            hashes = item.get("download_info", {}).get("archive_info", {}).get("hashes", {})
            wheels.append(
                {
                    "name": item.get("metadata", {}).get("name"),
                    "version": item.get("metadata", {}).get("version"),
                    "sha256": hashes.get("sha256"),
                    "url": item.get("download_info", {}).get("url"),
                }
            )
    data["wheels"] = wheels
    return data


def run(workdir: Path, report_path: Path) -> dict:
    for path in (VENDOR, VENV_PY, TARBALL, PIP_REPORT, PAPER_V1, PAPER_V3):
        if not path.exists():
            raise RegalError(f"dependência de reprodução ausente: {path}")
    if sha256_file(PAPER_V1) != PAPER_V1_SHA256 or sha256_file(PAPER_V3) != PAPER_V3_SHA256:
        raise RegalError("hash das fontes da publicação diverge do fixado")
    workdir.mkdir(parents=True, exist_ok=True)
    run_embedding = workdir / "regal-shipped.npy"
    stdout, stderr, seconds = _run(
        [str(VENV_PY), "regal.py", "--input", BENCHMARK_EDGES, "--output", str(run_embedding)],
        cwd=VENDOR,
    )
    scores = parse_scores(stdout)
    run_score = _score_embeddings(run_embedding)
    reference = _score_embeddings(VENDOR / REFERENCE_EMBEDDING)
    inconsistent = _score_embeddings(VENDOR / INCONSISTENT_EMBEDDING)
    diff = _embedding_diff(run_embedding, VENDOR / REFERENCE_EMBEDDING)
    peak_child_rss_mib = round(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1024, 1)
    if round(scores["top1"], 6) != round(run_score["accuracy"], 6):
        raise RegalError("acurácia do stdout diverge da repontuação do embedding")
    report = {
        "schema": "b08-regal-reproduction",
        "vendor": {
            "repository": "https://github.com/GemsLab/REGAL",
            "commit": REGAL_COMMIT,
            "license": REGAL_LICENSE,
            "tarball_url": f"https://codeload.github.com/GemsLab/REGAL/tar.gz/{REGAL_COMMIT}",
            "tarball_sha256": sha256_file(TARBALL),
            "files": {name: sha256_file(VENDOR / name) for name in VENDOR_FILES},
            "access_date": "2026-09-15",
        },
        "repro_environment": _environment(),
        "supervised_inputs": {
            "declared": True,
            "usage": "mapeamento verdadeiro do benchmark usado somente para pontuar; xNetMF/REGAL é não supervisionado",
            "mapping_convention": "valores são índices locais do grafo 2 (0..n/2-1), conforme score_alignment_matrix do código oficial",
            "attributed_variant": "não executada (trilho separado, informação extra)",
        },
        "command": {
            "run": f"{VENV_PY} regal.py --input {BENCHMARK_EDGES} --output {run_embedding}",
            "cwd": str(VENDOR),
            "adaptation": "nenhuma no código oficial; ambiente separado fornece sklearn exigido por alignments.py",
        },
        "scores": scores,
        "recomputed": {
            "run": {**run_score, "accuracy": round(run_score["accuracy"], 6)},
            "reference_npy": {**reference, "accuracy": round(reference["accuracy"], 6)},
            "reference_pickle": {**inconsistent, "accuracy": round(inconsistent["accuracy"], 6)},
        },
        "artifact_parity": artifact_parity(
            run_score["accuracy"],
            reference["accuracy"],
            sha256_file(run_embedding),
            sha256_file(VENDOR / REFERENCE_EMBEDDING),
            diff["max_abs_diff"],
            diff["mean_abs_diff"],
        ),
        "reference_pickle_artifact": {
            "status": "inconsistente com a partição",
            "accuracy": round(inconsistent["accuracy"], 6),
            "reason": "emb/arenas990-1.emb (pickle) não reproduz a partição; não é referência válida",
        },
        "published_parity": published_parity(),
        "resources": {"seconds": round(seconds, 3), "peak_child_rss_mib": peak_child_rss_mib, "device": "cpu"},
        "stderr_digest": hashlib.sha256(stderr.encode("utf-8")).hexdigest(),
        "stdout_digest": hashlib.sha256(stdout.encode("utf-8")).hexdigest(),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def check_report(path: Path) -> list[str]:
    failures: list[str] = []
    if not path.exists():
        return [f"relatório ausente: {path}"]
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("schema") != "b08-regal-reproduction":
        failures.append("schema divergente")
    vendor = report.get("vendor", {})
    if vendor.get("commit") != REGAL_COMMIT:
        failures.append("commit do vendor divergente do fixado")
    if vendor.get("license") != REGAL_LICENSE:
        failures.append("licença do vendor deve ser MIT")
    if not re.fullmatch(r"[0-9a-f]{64}", str(vendor.get("tarball_sha256", ""))):
        failures.append("tarball sem sha256")
    for name, digest in vendor.get("files", {}).items():
        if not re.fullmatch(r"[0-9a-f]{64}", str(digest)):
            failures.append(f"arquivo do vendor sem sha256 válido: {name}")
    if len(vendor.get("files", {})) < len(VENDOR_FILES):
        failures.append("lista de arquivos do vendor incompleta")
    environment = report.get("repro_environment", {})
    for package in ("numpy", "scipy", "networkx", "scikit-learn"):
        if not environment.get("packages", {}).get(package):
            failures.append(f"versão ausente no ambiente de reprodução: {package}")
    wheel_hashes = environment.get("wheels", [])
    if len(wheel_hashes) < 4:
        failures.append("hashes de wheel insuficientes no ambiente de reprodução")
    for wheel in wheel_hashes:
        if not re.fullmatch(r"[0-9a-f]{64}", str(wheel.get("sha256", ""))):
            failures.append(f"wheel sem sha256 válido: {wheel.get('name')}")
    scores = report.get("scores", {})
    top1 = float(scores.get("top1", -1))
    if not 0.0 <= top1 <= 1.0:
        failures.append("score top1 fora de [0,1]")
    recomputed = report.get("recomputed", {})
    for key in ("run", "reference_npy", "reference_pickle"):
        entry = recomputed.get(key, {})
        if not 0.0 <= float(entry.get("accuracy", -1)) <= 1.0:
            failures.append(f"acurácia inválida em recomputed.{key}")
        pairs = int(entry.get("pairs", -1))
        correct = int(entry.get("correct", -1))
        if pairs <= 0 or not 0 <= correct <= pairs:
            failures.append(f"contagens inválidas em recomputed.{key}")
        expected = round(float(entry.get("accuracy", 0.0)) * pairs)
        if abs(correct - expected) > 1:
            failures.append(f"acurácia e contagem incoerentes em recomputed.{key}")
    if round(float(recomputed.get("run", {}).get("accuracy", -1)), 6) != round(top1, 6):
        failures.append("stdout e repontuação do embedding divergem")
    parity = report.get("artifact_parity", {})
    status = parity.get("status")
    delta = float(parity.get("delta_accuracy", 1.0))
    mean_diff = float(parity.get("mean_abs_diff", 1.0))
    identical = bool(parity.get("hash_identical"))
    reproduced = identical or (delta <= ACCURACY_TOLERANCE and mean_diff <= EMBEDDING_MEAN_ABS_TOLERANCE)
    if status not in ("reproduzido", "divergente"):
        failures.append("status de paridade de artefato inválido")
    elif status == "reproduzido" and not reproduced:
        failures.append("paridade de artefato declarada sem satisfazer o critério")
    elif status == "divergente" and reproduced:
        failures.append("paridade de artefato satisfeita mas declarada divergente")
    if float(parity.get("tolerance_accuracy", -1)) != ACCURACY_TOLERANCE:
        failures.append("tolerância de acurácia divergente da declarada")
    if float(parity.get("tolerance_mean_abs", -1)) != EMBEDDING_MEAN_ABS_TOLERANCE:
        failures.append("tolerância de embedding divergente da declarada")
    pickle_artifact = report.get("reference_pickle_artifact", {})
    if pickle_artifact.get("status") != "inconsistente com a partição":
        failures.append("artefato pickle inconsistente não foi sinalizado")
    if float(pickle_artifact.get("accuracy", 1.0)) >= 0.01:
        failures.append("artefato pickle deveria ter acurácia desprezível")
    published = report.get("published_parity", {})
    if published.get("status") != "não verificável numericamente":
        failures.append("paridade publicada deve ser declarada não verificável numericamente")
    if published.get("numeric_reference") is not None:
        failures.append("paridade publicada sem referência numérica não pode declarar valor")
    if len(published.get("checked_sources", [])) < 2:
        failures.append("fontes verificadas da paridade publicada insuficientes")
    for source in published.get("checked_sources", []):
        if not re.fullmatch(r"[0-9a-f]{64}", str(source.get("sha256", ""))):
            failures.append("fonte da paridade publicada sem sha256")
    declared = report.get("supervised_inputs", {})
    if not declared.get("declared"):
        failures.append("inputs supervisionados não foram declarados")
    if "somente para pontuar" not in str(declared.get("usage", "")):
        failures.append("uso do mapeamento verdadeiro deve ser limitado à avaliação")
    if not (ROOT / "artifacts" / "reports" / "B08-REGAL.md").exists():
        failures.append("relatório Markdown ausente")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run", "check"))
    parser.add_argument("--workdir", type=Path, default=ROOT / "runs" / "b08")
    parser.add_argument("--report", type=Path, default=ROOT / "artifacts" / "reports" / "B08-REGAL.json")
    args = parser.parse_args()
    try:
        if args.command == "run":
            report = run(args.workdir, args.report)
            print(json.dumps({"scores": report["scores"], "artifact_parity": report["artifact_parity"], "published_parity": report["published_parity"]["status"], "resources": report["resources"]}, ensure_ascii=False, sort_keys=True))
        else:
            failures = check_report(args.report)
            if failures:
                for failure in failures:
                    print(f"FALHA: {failure}")
                return 1
            print("OK: registro B08 validado (vendor, ambiente, paridade e honestidade)")
    except (RegalError, FileNotFoundError, json.JSONDecodeError) as error:
        print(f"FALHA: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
