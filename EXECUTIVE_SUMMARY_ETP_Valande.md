# Executive Summary — ETP Valande Electrical & Predictive Maintenance Performance
### Reporting Period: January 1, 2023 – December 31, 2026 (4 years)

## Overview

ETP Valande is a 1,000,000 BWPD-capacity effluent treatment and high-pressure injection facility (3,000 psi), operating 20 major rotating equipment units across four process stages: intake lift, treatment/booster pumping, vacuum deaeration, and high-pressure injection. Over the 4-year reporting period, the plant recorded a combined operating expenditure (electrical + maintenance) of **$129,351,193**, with an average uptime of **99.28%**.

## Key Financial Metrics

| Metric | Value |
|---|---|
| Total Electrical Cost | $127,159,060 |
| Total Maintenance Cost | $2,192,133 |
| **Combined OPEX** | **$129,351,193** |
| Total Lost-Time Hours | 707.2 hours (across 4 years) |
| Average Plant Uptime | 99.28% |

Electrical cost represents 98.3% of combined OPEX — expected for a facility of this scale, where continuous high-pressure injection pumping (~50 MW connected load) dominates the energy profile far more than maintenance spend.

## Maintenance Cost Breakdown

| Maintenance Type | Events | Total Cost | Share of Maintenance Spend |
|---|---|---|---|
| Preventive (scheduled) | 160 | $1,264,633 | 57.7% |
| Emergency (unplanned failure) | 1 | $815,000 | 37.2% |
| Corrective | 2 | $84,700 | 3.9% |
| Predictive (early intervention) | 1 | $27,800 | 1.3% |

A single unplanned emergency event accounts for over a third of the entire 4-year maintenance budget — this is the central finding of this report.

## Headline Finding: The Cost of Reacting vs. Predicting

Two comparable incidents occurred in the dataset — one reactive, one predictive:

| | 2024 Emergency Event (`INJ-BETA`) | 2026 Predictive Intervention (`INJ-DELTA`) |
|---|---|---|
| Trigger | Sudden failure, no advance warning (Motor Winding Fault/Trip) | Early vibration/health-index alert, ~5 weeks of gradual warning |
| Downtime | 42 hours | 8 hours |
| Total Cost | $815,000 | $27,800 |
| Cost per hour of downtime | ~$19,405/hr | ~$3,475/hr |

**The reactive failure cost 29.3× more and caused 5.2× more downtime than the predictive intervention on a comparable unit.** This is not a hypothetical argument for predictive maintenance — it is the same class of equipment (high-pressure injection pump), same facility, with a directly observable cost and downtime differential between the two response modes.

## Secondary Finding: The Undetected Middle Case

A third pattern — arguably the most operationally important — occurred at `TRT-DELTA` in 2025: a gradual efficiency degradation (rising power draw for the same duty, falling health index) that ran for approximately five months before being caught and corrected. This scenario sits between the other two: it did not cause a catastrophic failure, but it also was not caught early enough to avoid unnecessary energy cost and an eventual 16-hour corrective repair. This is the pattern predictive-maintenance monitoring (health index / vibration trending, as modeled in `Equipment_Health_Index`) is specifically designed to catch earlier.

## Recommendations

1. **Prioritize vibration/health-index monitoring coverage on injection pumps first** — they carry the highest failure-cost consequence (both due to duty size and criticality to continuous operation).
2. **Investigate why the 2025 `TRT-DELTA` degradation was not caught for ~5 months** — this is a monitoring/alerting gap, not an equipment design issue, and is the most addressable root cause in this dataset.
3. **Use the 29.3× cost ratio as the basis for a predictive-maintenance program business case** — this figure is directly defensible from the plant's own operating data, not an industry-average estimate.
4. **Maintain current preventive maintenance cadence** (160 scheduled events, ~$7,900 average cost each) — it is working as intended and is not the source of unnecessary spend.

---
*All figures in this summary were computed directly from `ETP_Valande_Electrical_Maintenance_2023-2026.xlsx` and are consistent with the measures on `Dashboard_ETP_Valande_2023-2026.pbix`.*
