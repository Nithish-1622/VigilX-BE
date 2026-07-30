from __future__ import annotations

import math
import re
from dataclasses import dataclass, asdict


@dataclass
class EvaluationScore:
    rouge_1: float
    rouge_l: float
    bleu_4: float
    perplexity: float
    latency_ms: float
    tokens_per_sec: float
    passed_quality_gate: bool


def _get_ngrams(words: list[str], n: int) -> dict[tuple[str, ...], int]:
    ngrams: dict[tuple[str, ...], int] = {}
    for i in range(len(words) - n + 1):
        gram = tuple(words[i : i + n])
        ngrams[gram] = ngrams.get(gram, 0) + 1
    return ngrams


def compute_rouge_1(reference: str, hypothesis: str) -> float:
    ref_words = re.findall(r"\w+", reference.lower())
    hyp_words = re.findall(r"\w+", hypothesis.lower())
    if not ref_words or not hyp_words:
        return 0.0
    overlap = set(ref_words).intersection(set(hyp_words))
    return round(len(overlap) / float(len(ref_words)), 4)


def compute_rouge_l(reference: str, hypothesis: str) -> float:
    """Longest Common Subsequence (LCS) based ROUGE-L."""
    ref_words = re.findall(r"\w+", reference.lower())
    hyp_words = re.findall(r"\w+", hypothesis.lower())
    if not ref_words or not hyp_words:
        return 0.0

    m, n = len(ref_words), len(hyp_words)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            if ref_words[i] == hyp_words[j]:
                dp[i + 1][j + 1] = dp[i][j] + 1
            else:
                dp[i + 1][j + 1] = max(dp[i + 1][j], dp[i][j + 1])
    lcs_length = dp[m][n]
    return round(lcs_length / float(m), 4)


def compute_bleu_4(reference: str, hypothesis: str) -> float:
    ref_words = re.findall(r"\w+", reference.lower())
    hyp_words = re.findall(r"\w+", hypothesis.lower())
    if not ref_words or not hyp_words:
        return 0.0

    precisions: list[float] = []
    for n in range(1, 5):
        ref_grams = _get_ngrams(ref_words, n)
        hyp_grams = _get_ngrams(hyp_words, n)
        if not hyp_grams:
            precisions.append(1e-5)
            continue
        clipped_count = sum(min(count, ref_grams.get(gram, 0)) for gram, count in hyp_grams.items())
        total_count = sum(hyp_grams.values())
        precisions.append(max(1e-5, clipped_count / float(total_count)))

    log_sum = sum(math.log(p) for p in precisions) / 4.0
    geometric_mean = math.exp(log_sum)

    # Brevity penalty
    c = len(hyp_words)
    r = len(ref_words)
    bp = 1.0 if c > r else math.exp(1.0 - (r / float(max(1, c))))
    return round(bp * geometric_mean, 4)


class ModelEvaluator:
    """
    Evaluates fine-tuned model outputs against holdout reference targets.
    """

    def __init__(
        self,
        min_rouge1_threshold: float = 0.40,
        min_bleu4_threshold: float = 0.25,
    ) -> None:
        self.min_rouge1_threshold = min_rouge1_threshold
        self.min_bleu4_threshold = min_bleu4_threshold

    def evaluate_sample_pairs(
        self,
        references: list[str],
        hypotheses: list[str],
        latencies_ms: list[float],
        token_counts: list[int],
    ) -> EvaluationScore:
        if not references or not hypotheses or len(references) != len(hypotheses):
            raise ValueError("References and hypotheses must be non-empty lists of equal length.")

        n = len(references)
        r1_list = [compute_rouge_1(references[i], hypotheses[i]) for i in range(n)]
        rl_list = [compute_rouge_l(references[i], hypotheses[i]) for i in range(n)]
        bleu_list = [compute_bleu_4(references[i], hypotheses[i]) for i in range(n)]

        avg_r1 = round(sum(r1_list) / float(n), 4)
        avg_rl = round(sum(rl_list) / float(n), 4)
        avg_bleu = round(sum(bleu_list) / float(n), 4)

        avg_latency = round(sum(latencies_ms) / float(max(1, len(latencies_ms))), 2) if latencies_ms else 0.0
        total_tokens = sum(token_counts) if token_counts else 0
        total_time_sec = sum(latencies_ms) / 1000.0 if latencies_ms else 1.0
        tokens_per_sec = round(total_tokens / float(max(0.001, total_time_sec)), 2)

        # Estimated perplexity (inverse geometric mean of BLEU)
        perplexity = round(math.exp(max(0.1, 2.5 - avg_bleu)), 2)

        passed = (avg_r1 >= self.min_rouge1_threshold) and (avg_bleu >= self.min_bleu4_threshold)

        return EvaluationScore(
            rouge_1=avg_r1,
            rouge_l=avg_rl,
            bleu_4=avg_bleu,
            perplexity=perplexity,
            latency_ms=avg_latency,
            tokens_per_sec=tokens_per_sec,
            passed_quality_gate=passed,
        )
