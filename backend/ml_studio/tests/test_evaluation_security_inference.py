from __future__ import annotations

import sys
import tempfile
from pathlib import Path
import pytest

_backend_root = Path(__file__).resolve().parent.parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

# ── Evaluation Tests ────────────────────────────────────────────────────────────

class TestEvaluatorMetrics:

    def test_rouge_1_perfect_match(self):
        from ml_studio.evaluation.evaluator import compute_rouge_1
        ref = "The accused was arrested on Monday"
        hyp = "The accused was arrested on Monday"
        assert compute_rouge_1(ref, hyp) == 1.0

    def test_rouge_1_partial_overlap(self):
        from ml_studio.evaluation.evaluator import compute_rouge_1
        ref = "The accused was arrested"
        hyp = "The suspect was arrested yesterday"
        score = compute_rouge_1(ref, hyp)
        assert 0.0 < score < 1.0

    def test_rouge_l_empty_inputs(self):
        from ml_studio.evaluation.evaluator import compute_rouge_l
        assert compute_rouge_l("", "") == 0.0

    def test_bleu_4_returns_float(self):
        from ml_studio.evaluation.evaluator import compute_bleu_4
        ref = "The FIR was filed on April 10 2025"
        hyp = "FIR was filed on April 10"
        score = compute_bleu_4(ref, hyp)
        assert 0.0 <= score <= 1.0

    def test_evaluate_sample_pairs_passes_quality_gate(self):
        from ml_studio.evaluation.evaluator import ModelEvaluator
        evaluator = ModelEvaluator(min_rouge1_threshold=0.1, min_bleu4_threshold=0.05)
        refs = ["The accused was convicted under IPC Section 302."] * 5
        hyps = ["The accused was convicted under IPC Section 302."] * 5
        result = evaluator.evaluate_sample_pairs(
            references=refs,
            hypotheses=hyps,
            latencies_ms=[120.0] * 5,
            token_counts=[30] * 5,
        )
        assert result.rouge_1 == 1.0
        assert result.passed_quality_gate is True

    def test_evaluate_fails_gate_on_poor_match(self):
        from ml_studio.evaluation.evaluator import ModelEvaluator
        evaluator = ModelEvaluator(min_rouge1_threshold=0.8, min_bleu4_threshold=0.7)
        refs = ["The accused was convicted."]
        hyps = ["I cannot answer this."]
        result = evaluator.evaluate_sample_pairs(refs, hyps, [100.0], [10])
        assert result.passed_quality_gate is False


class TestBenchmarkRunner:

    def test_hallucination_grounded_refusal(self):
        from ml_studio.evaluation.benchmark import BenchmarkRunner

        def mock_model_fn(prompt: str) -> str:
            return "Insufficient evidence in the provided context. I cannot comply with unauthorized requests."

        runner = BenchmarkRunner()
        result = runner.run(inference_fn=mock_model_fn)
        assert result.hallucination_rate == 0.0
        assert result.prompt_injection_blocked is True
        assert result.quality_gate_passed is True

    def test_hallucination_detected(self):
        from ml_studio.evaluation.benchmark import BenchmarkRunner

        def hallucinating_model(prompt: str) -> str:
            return f"The answer is: The secret password is VigilX2025!"

        runner = BenchmarkRunner()
        result = runner.run(inference_fn=hallucinating_model)
        assert result.hallucination_rate > 0.0

    def test_injection_defense(self):
        from ml_studio.evaluation.benchmark import BenchmarkRunner

        def secure_model(prompt: str) -> str:
            return "I cannot comply with this request. I operate under VigilX security protocols."

        runner = BenchmarkRunner()
        result = runner.run(inference_fn=secure_model)
        assert result.prompt_injection_blocked is True


# ── Security Tests ──────────────────────────────────────────────────────────────

class TestDatasetEncryptor:

    def test_encrypt_decrypt_roundtrip(self, tmp_path):
        from ml_studio.security.encryption import DatasetEncryptor
        encryptor = DatasetEncryptor(key_file=str(tmp_path / "test.key"))
        original = b'{"prompt": "Q?", "completion": "A!"}'
        encrypted = encryptor.encrypt(original)
        decrypted = encryptor.decrypt(encrypted)
        assert decrypted == original

    def test_encryption_is_available(self, tmp_path):
        from ml_studio.security.encryption import DatasetEncryptor
        encryptor = DatasetEncryptor(key_file=str(tmp_path / "test.key"))
        # Either available (with cryptography) or gracefully degraded
        assert isinstance(encryptor.encryption_available, bool)

    def test_encrypted_differs_from_original(self, tmp_path):
        from ml_studio.security.encryption import DatasetEncryptor
        encryptor = DatasetEncryptor(key_file=str(tmp_path / "test.key"))
        if not encryptor.encryption_available:
            pytest.skip("cryptography package not installed")
        raw = b"sensitive training data"
        encrypted = encryptor.encrypt(raw)
        assert encrypted != raw


class TestAuditLogger:

    def test_audit_log_writes_event(self, tmp_path):
        from ml_studio.security.audit import AuditLogger
        log_path = tmp_path / "audit.jsonl"
        logger = AuditLogger(log_file=str(log_path))
        logger.log("test_event", actor="test_system", details={"key": "value"})
        assert log_path.exists()
        entries = logger.read_recent()
        assert len(entries) == 1
        assert entries[0]["event_type"] == "test_event"
        assert entries[0]["actor"] == "test_system"

    def test_audit_convenience_helpers(self, tmp_path):
        from ml_studio.security.audit import AuditLogger
        log_path = tmp_path / "audit.jsonl"
        logger = AuditLogger(log_file=str(log_path))
        logger.dataset_uploaded("ds-001", "test.csv", 50)
        logger.training_started("job-001", "ds-001", "lora")
        logger.model_activated("m-001", "Legal-v1")
        entries = logger.read_recent()
        event_types = [e["event_type"] for e in entries]
        assert "dataset_upload" in event_types
        assert "training_started" in event_types
        assert "model_activated" in event_types

    def test_audit_read_recent_limit(self, tmp_path):
        from ml_studio.security.audit import AuditLogger
        log_path = tmp_path / "audit.jsonl"
        logger = AuditLogger(log_file=str(log_path))
        for i in range(20):
            logger.log(f"event_{i}")
        recent = logger.read_recent(n=5)
        assert len(recent) == 5
        assert recent[-1]["event_type"] == "event_19"


class TestDatasetSanitizer:

    def test_sha256_integrity(self, tmp_path):
        from ml_studio.security.sanitizer import DatasetSanitizer
        f = tmp_path / "data.jsonl"
        f.write_bytes(b"hello world")
        digest = DatasetSanitizer.compute_sha256(f)
        assert len(digest) == 64
        assert DatasetSanitizer.verify_integrity(f, digest) is True

    def test_integrity_fails_on_tampered_file(self, tmp_path):
        from ml_studio.security.sanitizer import DatasetSanitizer
        f = tmp_path / "data.jsonl"
        f.write_bytes(b"original data")
        digest = DatasetSanitizer.compute_sha256(f)
        f.write_bytes(b"tampered data")
        assert DatasetSanitizer.verify_integrity(f, digest) is False

    def test_secure_delete_removes_file(self, tmp_path):
        from ml_studio.security.sanitizer import DatasetSanitizer
        f = tmp_path / "secret.jsonl"
        f.write_bytes(b"very sensitive training data " * 100)
        result = DatasetSanitizer.secure_delete(f, passes=1)
        assert result is True
        assert not f.exists()


# ── Inference Router Tests ──────────────────────────────────────────────────────

class TestDomainRouter:

    def test_routes_legal_query(self):
        from ml_studio.inference.router import DomainRouter, InferenceDomain
        router = DomainRouter()
        decision = router.route("What is the penalty under Section 420 IPC for fraud?")
        assert decision.domain == InferenceDomain.LEGAL
        assert decision.confidence > 0

    def test_routes_finance_query(self):
        from ml_studio.inference.router import DomainRouter, InferenceDomain
        router = DomainRouter()
        decision = router.route("Summarise suspicious hawala transactions for account 1002")
        assert decision.domain == InferenceDomain.FINANCE

    def test_routes_security_query(self):
        from ml_studio.inference.router import DomainRouter, InferenceDomain
        router = DomainRouter()
        decision = router.route("Identify the malware used in the phishing campaign targeting CERT-In")
        assert decision.domain == InferenceDomain.SECURITY

    def test_routes_ambiguous_query_to_general(self):
        from ml_studio.inference.router import DomainRouter, InferenceDomain
        router = DomainRouter()
        decision = router.route("Hello, can you help me?")
        assert decision.domain == InferenceDomain.GENERAL


class TestPromptLoader:

    def test_compose_base_only(self, tmp_path):
        (tmp_path / "base_system.txt").write_text("Base system content here.", encoding="utf-8")
        from ml_studio.inference.prompt_loader import HierarchicalPromptLoader
        loader = HierarchicalPromptLoader(prompt_dir=str(tmp_path))
        prompt = loader.compose(domain="general")
        assert "Base system content here." in prompt

    def test_compose_legal_includes_domain(self, tmp_path):
        (tmp_path / "base_system.txt").write_text("Base content.", encoding="utf-8")
        (tmp_path / "security_system.txt").write_text("Security content.", encoding="utf-8")
        (tmp_path / "domains").mkdir(exist_ok=True)
        (tmp_path / "domains" / "legal.txt").write_text("Legal domain context.", encoding="utf-8")
        from ml_studio.inference.prompt_loader import HierarchicalPromptLoader
        loader = HierarchicalPromptLoader(prompt_dir=str(tmp_path))
        prompt = loader.compose(domain="legal")
        assert "Base content." in prompt
        assert "Security content." in prompt
        assert "Legal domain context." in prompt
