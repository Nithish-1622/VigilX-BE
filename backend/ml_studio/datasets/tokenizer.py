from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class DatasetTokenStats:
    total_samples: int
    min_tokens: int
    max_tokens: int
    avg_tokens: float
    p95_tokens: int
    exceeds_max_len_count: int


def estimate_token_count(text: str) -> int:
    """
    Fast character/word heuristic token count estimation.
    Averages ~4 characters per token for English/code/Hindi-transliterated text.
    """
    if not text:
        return 0
    words = len(text.split())
    chars = len(text)
    # Hybrid heuristic: max of (word_count * 1.3, char_count / 4)
    return int(max(words * 1.3, chars / 4.0))


def analyze_sequence_lengths(
    rows: list[dict[str, str]],
    max_seq_length: int = 512,
) -> DatasetTokenStats:
    """
    Calculate token sequence length statistics across a dataset.
    Sequence length per row = token_count(prompt) + token_count(completion).
    """
    if not rows:
        return DatasetTokenStats(
            total_samples=0,
            min_tokens=0,
            max_tokens=0,
            avg_tokens=0.0,
            p95_tokens=0,
            exceeds_max_len_count=0,
        )

    lengths: list[int] = []
    exceeds_count = 0

    for r in rows:
        prompt = r.get("prompt", "")
        completion = r.get("completion", "")
        length = estimate_token_count(prompt) + estimate_token_count(completion)
        lengths.append(length)
        if length > max_seq_length:
            exceeds_count += 1

    lengths.sort()
    n = len(lengths)
    p95_idx = int(math.ceil(0.95 * n)) - 1
    p95_idx = max(0, min(n - 1, p95_idx))

    return DatasetTokenStats(
        total_samples=n,
        min_tokens=lengths[0],
        max_tokens=lengths[-1],
        avg_tokens=sum(lengths) / float(n),
        p95_tokens=lengths[p95_idx],
        exceeds_max_len_count=exceeds_count,
    )


def truncate_row(row: dict[str, str], max_seq_length: int = 512) -> dict[str, str]:
    """
    Truncate prompt and completion if combined sequence length exceeds max_seq_length.
    Preserves completion as priority.
    """
    new_row = dict(row)
    prompt = new_row.get("prompt", "")
    completion = new_row.get("completion", "")

    p_tokens = estimate_token_count(prompt)
    c_tokens = estimate_token_count(completion)

    if (p_tokens + c_tokens) <= max_seq_length:
        return new_row

    # Allow prompt to take up to 60% of max_seq_length, completion the rest
    max_p_chars = int(max_seq_length * 0.6 * 4)
    max_c_chars = int(max_seq_length * 0.4 * 4)

    if len(prompt) > max_p_chars:
        new_row["prompt"] = prompt[:max_p_chars] + "... [truncated]"
    if len(completion) > max_c_chars:
        new_row["completion"] = completion[:max_c_chars] + "... [truncated]"

    return new_row
