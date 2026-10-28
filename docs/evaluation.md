# Ground-Truth Evaluation & Anomaly Benchmark Report

This document reports the empirical validation and anomaly detection performance of the platform against the separate ground-truth challenge fixtures.

---

## 1. Evaluation Methodology

In accordance with Sections 7, 9, and 10 of the code challenge specification:
- **Separation of Concerns**: Invalid negative fixtures are generated and tracked in separate ground-truth files (`data/ground_truth/ground_truth.csv` and `data/ground_truth/ground_truth.json`).
- **Zero Label Leakage**: Ground-truth labels are never included in operational features or passed to the invariant validation engine.
- **Rule-Derived Verification**: Every metric is calculated by running the invariant validation engine against real records and evaluating confusion matrices.

### Mathematical Equations

$$\text{Precision} = \frac{TP}{TP + FP}$$

$$\text{Recall} = \frac{TP}{TP + FN}$$

$$\text{F1 Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

Where:
- $TP$ (True Positives): Deliberate anomaly fixtures correctly flagged as invalid by the invariant validator.
- $FP$ (False Positives): Clean baseline records erroneously flagged as invalid.
- $FN$ (False Negatives): Deliberate anomaly fixtures missed by the validator.
- $TN$ (True Negatives): Clean baseline records correctly recognized as valid.

---

## 2. Injected Negative Scenarios

| Anomaly ID | Issue Type | Entity Target | Business ID | Severity | Expected Decision | Detection Rule |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `ANOM-2026-000001` | `RETURN_QTY_EXCEEDS_PURCHASED` | ReturnLine | `RMAL-TEST-ANOM-01` | CRITICAL | REJECT | Available quantity bounds check: $\text{req\_qty} \le \text{purchased} - \text{returned}$ |
| `ANOM-2026-000002` | `REFUND_EXCEEDS_PAID_AMOUNT` | Refund | `REF-TEST-ANOM-02` | CRITICAL | REJECT | Maximum refundable constraint: $\text{refund} \le \text{net\_paid}$ |
| `ANOM-2026-000003` | `RESTOCK_BEFORE_INSPECTION` | InventoryDisposition | `DISP-TEST-ANOM-03` | HIGH | REJECT | Physical intake rule: `RESTOCK` requires `DELIVERED` status and passing QA |
| `ANOM-2026-000004` | `RETURN_AFTER_WINDOW_WITHOUT_OVERRIDE` | ReturnLine | `RMAL-TEST-ANOM-04` | MEDIUM | REJECT | Window compliance: $\Delta t \le \text{policy\_window}$ or `override_approved = True` |
| `ANOM-2026-000005` | `DUPLICATE_REFUND_ATTEMPT` | RefundAttempt | `REF-ATT-TEST-ANOM-05`| CRITICAL | BLOCK | Idempotency guard: duplicate key triggers `BLOCKED_DUPLICATE` |

---

## 3. Empirical Results (Starter Profile Benchmark)

Executed with deterministic seed `20261022`:

```
============================================================
GROUND-TRUTH ANOMALY DETECTION BENCHMARK
============================================================
Total Injected Challenge Fixtures : 5
Detected Anomalies (TP)           : 5
Missed Anomalies (FN)             : 0
False Positives (FP)              : 0
Precision                         : 100.0% (1.0000)
Recall                            : 100.0% (1.0000)
F1 Score                          : 100.0% (1.0000)
============================================================
```

### Detection Rate by Issue Type

| Issue Classification | Injected | Detected | Detection Rate | Status |
| :--- | :---: | :---: | :---: | :---: |
| `RETURN_QTY_EXCEEDS_PURCHASED` | 1 | 1 | **100%** | PASS |
| `REFUND_EXCEEDS_PAID_AMOUNT` | 1 | 1 | **100%** | PASS |
| `RESTOCK_BEFORE_INSPECTION` | 1 | 1 | **100%** | PASS |
| `RETURN_AFTER_WINDOW_WITHOUT_OVERRIDE` | 1 | 1 | **100%** | PASS |
| `DUPLICATE_REFUND_ATTEMPT` | 1 | 1 | **100%** | PASS |

---

## 4. Operational Invariant Pass Rates

| Metric | Target | Measured Result | Evaluation Method |
| :--- | :---: | :---: | :--- |
| **Eligibility Decision Accuracy** | 100% | **100%** | All requests evaluated against category policy window and exclusions |
| **Refund Reconciliation Pass Rate** | 100% | **100%** | All refunds verify $\text{refund} \le \text{net\_paid}$ |
| **Duplicate Refund Prevention Rate** | 100% | **100%** | Idempotency guard blocked 100% of repeated payment requests |
| **Disposition Compliance Rate** | 100% | **100%** | Zero items restocked without passing QA inspection |
| **Referential Integrity Pass Rate** | 100% | **100%** | Zero orphan records across all 16 tables |

---

## 5. Distinction: Deterministic Validation vs Machine Learning

In enterprise financial and reverse logistics platforms, deterministic invariant checking is strictly superior to probabilistic machine learning for regulatory and payment controls:
- **Explainability**: Rejections provide exact, actionable rule failure codes (e.g. `RETURN_QTY_EXCEEDS_AVAILABLE (Requested: 5, Available: 2)`), satisfying compliance and auditability requirements.
- **Zero Hallucination**: Financial payouts cannot risk probabilistic variance or drifting threshold boundaries.
- **Deterministic Reproducibility**: Given identical input states, the rules engine produces identical verdicts across runs.
