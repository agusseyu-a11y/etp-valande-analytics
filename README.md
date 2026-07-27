# ETP Valande — Electrical Consumption & Predictive Maintenance Analytics

Aramco-scale (1,000,000 BWPD) Effluent Treatment Plant analytics project: a synthetic 4-year (2023–2026) daily dataset covering electrical consumption, equipment health/predictive-maintenance indicators, and maintenance cost events across 20 major rotating equipment units — visualized in Power BI with a full DAX measure layer.

> **Note on data:** all data in this repository is synthetically generated for demonstration purposes, modeled on realistic hydraulic/electrical engineering calculations (pump power derived from flow, head, and efficiency) and industry-typical equipment redundancy conventions (N+1/N+2). It does not represent any real facility's actual performance.

---

## Repository Contents

| File | Location | Description |
|---|---|---|
| `README.md` | root | This file |
| `EXECUTIVE_SUMMARY.md` | root | Management-style summary of key findings |
| `ETP_Valande_Electrical_Maintenance_2023-2026.xlsx` | `data/` | Source data — 5 sheets: `Electrical_Consumption_Data`, `Equipment_Health_Index`, `Maintenance_Data`, `Daily_Summary_KPI`, `Equipment_Master` |
| `generate_aramco_scale_maintenance.py` | `scripts/` | Python script that generates the full dataset from scratch (reproducible, fixed random seeds) |
| `Dashboard_ETP_Valande_2023-2026.pbix` | `dashboard/` | Power BI dashboard file |
| `Visualization_ETP_Valande.pdf` | `dashboard/` | Static export of the dashboard |
| `Panduan_Dashboard_PowerBI_ETP_Valande.md` | `docs/` | Step-by-step Power BI build guide (Bahasa Indonesia), including a troubleshooting log of real issues encountered while building this dashboard |

---

## Plant Overview

| Parameter | Value |
|---|---|
| Design capacity | 1,000,000 BWPD (~158,987 m³/day) |
| Injection pressure | 3,000 psi |
| Reporting period | Jan 1, 2023 – Dec 31, 2026 (1,461 days) |
| Major equipment units | 20 (6 Intake, 8 Treatment, 2 Deaerator, 4 Injection) + 5 chemical dosing lines |
| Redundancy philosophy | N+1 (Intake, Injection), N+2 (Treatment) |

**Equipment naming convention:** each unit is coded `<GROUP>-<GREEK LETTER>` (e.g. `INJ-ALPHA`, `TRT-DELTA`) — group prefixes: `ITK` (Intake), `TRT` (Treatment), `DEA` (Deaerator), `INJ` (Injection).

---

## Key Findings (see `EXECUTIVE_SUMMARY.md` for full detail)

| KPI | Value |
|---|---|
| Total electrical cost (4 yrs) | $127,159,060 |
| Total maintenance cost (4 yrs) | $2,192,133 |
| Combined OPEX (4 yrs) | $129,351,193 |
| Total lost-time hours | 707.2 |
| Average plant uptime | 99.28% |
| **Emergency vs. Predictive maintenance cost ratio** | **29.3×** |

---

## Methodology

**Engineering basis for equipment sizing:** pump power ratings are derived from the standard hydraulic power formula `P (kW) = (ρ × g × Q × H) / (η × 1000)`, using the plant's actual flow rate, assumed head per duty (15–35 m for intake/treatment stages, ~2,110 m equivalent head for 3,000 psi injection), and realistic pump efficiencies (0.70–0.76). This produces power ratings consistent with real large-scale water injection facility design (injection pumps in the multi-MW range, dominating total plant load — treatment-train pumping is comparatively minor).

**Predictive maintenance modeling:** each equipment unit has a daily `Health_Index_Pct` (0–100) and `Vibration_mm_s` series. Three narrative scenarios are embedded across the 4 years:
- **2024 — Unplanned failure** (`INJ-BETA`): sudden health collapse with no advance warning, 42-hour emergency repair, $815,000 cost.
- **2025 — Undetected energy leak** (`TRT-DELTA`): gradual efficiency degradation over ~5 months (rising power draw for the same duty) before being caught.
- **2026 — Predictive maintenance save** (`INJ-DELTA`): early vibration/health-index warning acted on in time — 8-hour planned intervention, $27,800 cost, avoiding a failure of similar magnitude to 2024's.

Random generation uses fixed seeds (`np.random.seed(42)`, `np.random.default_rng(7)`) — the script is fully reproducible.

---

## How to Reproduce

```bash
pip install pandas numpy openpyxl
python scripts/generate_aramco_scale_maintenance.py
# → outputs ETP_Valande_Electrical_Maintenance_2023-2026.xlsx
```

Then follow `docs/Panduan_Dashboard_PowerBI_ETP_Valande.md` to rebuild the Power BI dashboard: data import → two-dimension star schema (Date + Equipment) → DAX measures → visuals → conditional formatting on predicted failure risk.

---

## Honest Caveats

- Injection pressure (3,000 psi) and resulting pump power (~50 MW total duty) are illustrative assumptions, not derived from any specific real reservoir's characteristics.
- Electricity rate ($0.07/kWh) and maintenance labor/parts costs are illustrative assumptions for demonstration purposes.
- `Equipment_Master` does not include the 5 chemical dosing lines present in `Electrical_Consumption_Data` — this is intentional (dosing skids are not major rotating equipment), but means a direct relationship join between the two will show unmatched rows for those lines. Use the `Equipment_Group` column (present directly on `Electrical_Consumption_Data`) for filtering instead.

## License

MIT (or your preferred license — update this section before publishing).
