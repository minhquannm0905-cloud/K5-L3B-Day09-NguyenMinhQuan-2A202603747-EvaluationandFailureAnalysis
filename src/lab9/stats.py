"""Statistics students implement (M2 judge calibration, M4 paired bootstrap).

Rules: a judge is a classifier -- measure it like one. A higher mean is not
"better" until the paired CI of the difference excludes 0.
Reference values to self-check are in tests/test_lab9_stats.py.
"""

from __future__ import annotations

from collections.abc import Sequence

POS = "FAIL"   # the judge's job is to FIND failures, so FAIL is the positive class


def confusion(human: Sequence[str], judge: Sequence[str]) -> dict[str, int]:
    """tp/fp/fn/tn with FAIL as positive."""
    if len(human) != len(judge):
        raise ValueError("human and judge must have the same length")

    result = {"tp": 0, "fp": 0, "fn": 0, "tn": 0}

    for human_label, judge_label in zip(human, judge):
        if human_label == "FAIL" and judge_label == "FAIL":
            result["tp"] += 1
        elif human_label == "PASS" and judge_label == "FAIL":
            result["fp"] += 1
        elif human_label == "FAIL" and judge_label == "PASS":
            result["fn"] += 1
        elif human_label == "PASS" and judge_label == "PASS":
            result["tn"] += 1
        else:
            raise ValueError(
                f"labels must be PASS or FAIL: {human_label!r}, {judge_label!r}"
            )

    return result

def precision_recall(
    human: Sequence[str],
    judge: Sequence[str],
) -> tuple[float, float]:
    cm = confusion(human, judge)

    precision_denominator = cm["tp"] + cm["fp"]
    recall_denominator = cm["tp"] + cm["fn"]

    precision = (
        cm["tp"] / precision_denominator
        if precision_denominator
        else 0.0
    )
    recall = (
        cm["tp"] / recall_denominator
        if recall_denominator
        else 0.0
    )

    return precision, recall


def cohen_kappa(human: Sequence[str], judge: Sequence[str]) -> float:
    """Cohen's kappa with FAIL as the positive class."""
    cm = confusion(human, judge)
    total = sum(cm.values())

    if total == 0:
        raise ValueError("cannot compute kappa for empty input")

    observed_agreement = (cm["tp"] + cm["tn"]) / total

    human_fail_rate = (cm["tp"] + cm["fn"]) / total
    human_pass_rate = (cm["tn"] + cm["fp"]) / total
    judge_fail_rate = (cm["tp"] + cm["fp"]) / total
    judge_pass_rate = (cm["tn"] + cm["fn"]) / total

    expected_agreement = (
        human_fail_rate * judge_fail_rate
        + human_pass_rate * judge_pass_rate
    )

    if expected_agreement == 1.0:
        raise ValueError("cohen kappa is undefined")

    return (
        observed_agreement - expected_agreement
    ) / (1.0 - expected_agreement)

def rogan_gladen(
    observed_rate: float,
    sensitivity: float,
    specificity: float,
) -> float:
    """Correct an observed rate for classifier error."""
    denominator = sensitivity + specificity - 1.0

    if denominator == 0.0:
        raise ValueError("judge has no discriminative signal")

    corrected = (
        observed_rate + specificity - 1.0
    ) / denominator

    return min(1.0, max(0.0, corrected))


def paired_bootstrap(
    a: Sequence[float],
    b: Sequence[float],
    *,
    n_resamples: int = 1000,
    rng: int = 2027,
    confidence: float = 0.95,
) -> tuple[float, float, float]:
    """Return mean(a)-mean(b) and its paired percentile CI."""
    import numpy as np
    from scipy.stats import bootstrap

    if len(a) != len(b):
        raise ValueError("paired samples must have the same length")
    if not a:
        raise ValueError("paired samples must not be empty")

    a_values = np.asarray(a, dtype=float)
    b_values = np.asarray(b, dtype=float)

    if np.array_equal(a_values, b_values):
        return 0.0, 0.0, 0.0

    def mean_difference(
        x: np.ndarray,
        y: np.ndarray,
        axis: int = -1,
    ) -> np.ndarray:
        return np.mean(x - y, axis=axis)

    result = bootstrap(
        (a_values, b_values),
        mean_difference,
        paired=True,
        vectorized=True,
        n_resamples=n_resamples,
        method="percentile",
        confidence_level=confidence,
        rng=np.random.default_rng(rng),
    )

    delta = float(np.mean(a_values) - np.mean(b_values))
    low = float(result.confidence_interval.low)
    high = float(result.confidence_interval.high)

    return delta, low, high


def pass_at_k(n: int, c: int, k: int) -> float:
    """Probability that AT LEAST ONE of k trials drawn from n (c of them passing) passes.
    Unbiased estimator (Chen et al. 2021): 1 - C(n-c, k) / C(n, k). Raise ValueError if k > n."""
    # TODO M6
    raise NotImplementedError


def pass_hat_k(n: int, c: int, k: int) -> float:
    """pass^k (tau-bench, Yao et al. 2024): probability that ALL k trials drawn from n pass.
    Unbiased estimator: C(c, k) / C(n, k). Raise ValueError if k > n.
    pass^k <= pass@1 <= pass@k; a reliable agent keeps pass^k close to pass@1."""
    # TODO M6
    raise NotImplementedError
