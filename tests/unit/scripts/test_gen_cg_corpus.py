"""Gate for the Context Grounding corpus generator (scripts/gen_cg_corpus.py).

The corpus docs are what the BAA-corpus / ClaimTelemetry-corpus indexes ingest.
They must embed the EXACT seeded Data Fabric terms (retrieval answers must match
the structured records), stay IP-safe, and the committed files must match the
generator output byte-for-byte (reproducibility / no silent drift).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CORPUS_DIR = REPO_ROOT / "data" / "context-grounding"

FORBIDDEN = (
    "zelis", "aetna", "cigna", "unitedhealth", "cotiviti", "optum",
    "change healthcare", "wex ", "rivet", "bcbs", "hartley", "zipp", "zapp",
)


def _load_script(name: str):
    path = REPO_ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace("-", "_").removesuffix(".py"), path)
    assert spec is not None, f"cannot load {path}"
    assert spec.loader is not None, f"cannot load {path}"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestBaaDocs:
    def test_one_doc_per_seed_baa_with_exact_terms(self) -> None:
        gen = _load_script("gen_cg_corpus.py")
        seed = _load_script("seed_data_fabric.py")
        docs = gen.build_baa_docs()
        assert set(docs) == {f"{bid}.txt" for (bid, *_rest) in seed.BAAS}
        providers = {pid: name for (pid, name, *_r) in seed.PROVIDERS}
        for (bid, prov, ver, notif, consult, permitted, forbidden, indem, law) in seed.BAAS:
            text = docs[f"{bid}.txt"]
            assert providers[prov] in text, f"{bid}: provider display name missing"
            assert f"{notif} hours" in text, f"{bid}: notification window missing"
            for term in permitted:
                assert term in text, f"{bid}: permitted disclosure {term!r} missing"
            for term in forbidden:
                assert term in text, f"{bid}: forbidden disclosure {term!r} missing"
            assert indem in text, f"{bid}: indemnification clause missing"
            assert law in text, f"{bid}: governing law missing"
            assert (f"version {ver}" in text) or (ver in text), f"{bid}: version missing"
            if consult:
                assert "pre-disclosure consultation" in text.lower(), (
                    f"{bid}: pre-disclosure consultation requirement missing"
                )

    def test_epsilon_is_strictest(self) -> None:
        gen = _load_script("gen_cg_corpus.py")
        text = gen.build_baa_docs()["baa-epsilon.txt"]
        assert "pediatric" in text.lower()
        assert "federal_regulator" in text  # epsilon forbids federal disclosure


class TestTelemetryDocs:
    def test_one_doc_per_provider_with_seeded_profile(self) -> None:
        gen = _load_script("gen_cg_corpus.py")
        seed = _load_script("seed_data_fabric.py")
        docs = gen.build_telemetry_docs()
        assert set(docs) == {f"telemetry-{pid}.txt" for (pid, *_r) in seed.PROVIDERS}
        for (pid, name, _v, _h, _npi, monthly_vol, *_r) in seed.PROVIDERS:
            text = docs[f"telemetry-{pid}.txt"]
            hourly_base = max(1, monthly_vol // (30 * 24))
            assert name in text, f"{pid}: provider display name missing"
            assert str(hourly_base) in text, f"{pid}: baseline hourly volume missing"
            assert "35%" in text, f"{pid}: suppression magnitude missing"
            assert "0.75" in text, f"{pid}: anomaly score floor missing"
            assert "2026-01" in text, f"{pid}: telemetry window missing"


class TestCorpusHygiene:
    def test_ip_safety(self) -> None:
        gen = _load_script("gen_cg_corpus.py")
        for fname, text in {**gen.build_baa_docs(), **gen.build_telemetry_docs()}.items():
            low = text.lower()
            for tok in FORBIDDEN:
                assert tok not in low, f"{fname}: forbidden token {tok!r}"

    def test_committed_files_match_generator(self) -> None:
        gen = _load_script("gen_cg_corpus.py")
        expected = {
            CORPUS_DIR / "baa-corpus" / n: t for n, t in gen.build_baa_docs().items()
        } | {
            CORPUS_DIR / "claimtelemetry-corpus" / n: t
            for n, t in gen.build_telemetry_docs().items()
        }
        for path, text in expected.items():
            assert path.is_file(), f"missing committed corpus doc {path} — run scripts/gen_cg_corpus.py"
            assert path.read_text() == text, f"{path} drifted from generator output — regenerate"
