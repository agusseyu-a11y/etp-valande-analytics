"""
generate_aramco_scale_maintenance.py
-------------------------------------------------------------
Synthesizes a 4-year (2023-01-01 to 2026-12-31) daily dataset for a
1,000,000 BWPD water injection facility modeled on Aramco-scale design
conventions: intake lift pumps, treatment/booster pumps, vacuum deaeration,
and high-pressure (3,000 psi) injection pumps, plus a full predictive-
maintenance layer (daily equipment health index) and a discrete
maintenance-event log.

Output: Aramco_Scale_Electrical_Maintenance_2023-2026.xlsx
  - Electrical_Consumption_Data  (daily, per equipment unit)
  - Equipment_Health_Index       (daily, per major rotating equipment unit)
  - Maintenance_Data             (event-based)
  - Daily_Summary_KPI            (daily, plant-level rollup)

Currency: USD throughout.
-------------------------------------------------------------
"""
import numpy as np
import pandas as pd

np.random.seed(42)
rng = np.random.default_rng(7)

START = pd.Timestamp("2023-01-01")
END = pd.Timestamp("2026-12-31")
dates = pd.date_range(START, END, freq="D")
n_days = len(dates)
print(f"Total hari: {n_days} ({START.date()} - {END.date()})")

CAPACITY_BWPD = 1_000_000
COST_PER_KWH_USD = 0.07  # asumsi tarif listrik industri skala besar

# ============================================================
# EQUIPMENT INVENTORY
# ============================================================
GREEK = ["ALPHA", "BETA", "GAMMA", "DELTA", "EPSILON", "ZETA", "ETA", "THETA"]

def make_units(prefix, n_units, n_duty, rated_kw, head_note):
    units = []
    for i in range(n_units):
        units.append({
            "Equipment_ID": f"{prefix}-{GREEK[i]}",
            "Equipment_Group": {
                "ITK": "Intake Pump", "TRT": "Treatment Pump",
                "DEA": "Deaerator", "INJ": "Injection Pump",
            }[prefix],
            "Is_Duty_Default": i < n_duty,
            "Rated_Power_kW": rated_kw,
            "Note": head_note,
        })
    return units

equipment = (
    make_units("ITK", 6, 5, 77, "Intake lift, head 15m")
    + make_units("TRT", 8, 6, 146, "Treatment/booster, head 35m")
    + make_units("DEA", 2, 1, 420, "Vacuum deaerator tower")
    + make_units("INJ", 4, 3, 16704, "High-pressure injection, 3000 psi")
)
equip_df = pd.DataFrame(equipment)
print(f"\nTotal major rotating equipment units: {len(equip_df)}")
print(equip_df.groupby("Equipment_Group")["Rated_Power_kW"].agg(["count", "sum"]))

CHEMICALS = ["Biocide", "Oxygen Scavenger", "Scale Inhibitor", "Corrosion Inhibitor", "Antifoam"]
CHEM_RATED_KW = 2.0  # per dosing skid, lumped

# ============================================================
# YEARLY EVENT SCHEDULE (narrative anomalies)
# ============================================================
# 2023: baseline, no major incident
# 2024: unplanned shutdown -- INJ-BETA trips, cascades to INJ-GAMMA overload -> multi-day outage
# 2025: energy leak -- TRT-DELTA degrades gradually (efficiency loss), caught late
# 2026: predictive maintenance save -- INJ-DELTA shows early warning, serviced in time;
#       plus one minor lost-time incident mid-year
EVENTS = {
    "unplanned_shutdown_2024": {
        "unit": "INJ-BETA", "start": pd.Timestamp("2024-07-14"),
    },
}

print("\nBuilding daily equipment health index...")

# ============================================================
# EQUIPMENT_HEALTH_INDEX (daily, per major unit)
# ============================================================
health_rows = []

for _, eq in equip_df.iterrows():
    eid = eq["Equipment_ID"]
    health = np.full(n_days, 100.0)
    vib = np.full(n_days, 1.5)  # mm/s baseline, ISO 10816 "good" zone

    # baseline slow random-walk degradation + periodic preventive reset (~every 180 days)
    idx = np.arange(n_days)
    cycle = 180
    for start in range(0, n_days, cycle):
        end = min(start + cycle, n_days)
        length = end - start
        decay = np.linspace(0, rng.uniform(3, 8), length)  # gentle normal wear
        health[start:end] = 100 - decay
        vib[start:end] = 1.5 + (decay / 8) * 1.2

    # ---- 2024 unplanned shutdown: INJ-BETA sudden failure (no gradual warning) ----
    if eid == "INJ-BETA":
        d = (pd.Timestamp("2024-07-14") - START).days
        health[d:d+5] = [45, 20, 5, 60, 95]  # sudden drop, repaired, restored
        vib[d:d+3] = [8.5, 12.0, 14.2]  # severe vibration spike (ISO Zone D)

    # ---- 2025 energy leak: TRT-DELTA gradual undetected degradation over ~5 months ----
    if eid == "TRT-DELTA":
        leak_start = (pd.Timestamp("2025-02-01") - START).days
        leak_end = (pd.Timestamp("2025-07-10") - START).days
        length = leak_end - leak_start
        health[leak_start:leak_end] = np.linspace(96, 58, length)
        vib[leak_start:leak_end] = np.linspace(1.8, 5.5, length)
        health[leak_end:leak_end+3] = [40, 92, 98]  # caught + corrective maintenance
        vib[leak_end:leak_end+3] = [6.8, 1.6, 1.4]

    # ---- 2026 predictive save: INJ-DELTA shows early warning, serviced before failure ----
    if eid == "INJ-DELTA":
        warn_start = (pd.Timestamp("2026-03-01") - START).days
        warn_end = (pd.Timestamp("2026-04-05") - START).days
        length = warn_end - warn_start
        health[warn_start:warn_end] = np.linspace(94, 72, length)
        vib[warn_start:warn_end] = np.linspace(1.9, 4.4, length)
        health[warn_end:warn_end+2] = [88, 99]  # predictive maintenance intervention, minimal downtime
        vib[warn_end:warn_end+2] = [3.0, 1.4]

    health = np.clip(health, 0, 100)
    vib = np.clip(vib, 0.5, 20)

    risk = np.select(
        [health >= 90, health >= 75, health >= 55],
        ["Low", "Medium", "High"],
        default="Critical",
    )

    health_rows.append(pd.DataFrame({
        "DATE": dates, "Equipment_ID": eid, "Equipment_Group": eq["Equipment_Group"],
        "Health_Index_Pct": health.round(1), "Vibration_mm_s": vib.round(2),
        "Predicted_Failure_Risk": risk,
    }))

health_df = pd.concat(health_rows, ignore_index=True)
print(f"Equipment_Health_Index: {len(health_df)} rows")

# ============================================================
# ELECTRICAL_CONSUMPTION_DATA (daily, per unit incl. chemical dosing)
# ============================================================
elec_rows = []
health_lookup = health_df.set_index(["DATE", "Equipment_ID"])["Health_Index_Pct"]

for _, eq in equip_df.iterrows():
    eid = eq["Equipment_ID"]
    grp = eq["Equipment_Group"]
    is_duty_default = eq["Is_Duty_Default"]
    rated_kw = eq["Rated_Power_kW"]

    running_hours = np.where(is_duty_default, 24.0, 0.0) * np.ones(n_days)
    power_draw = np.where(is_duty_default, rated_kw, 0.0) * np.ones(n_days)

    # 2024 unplanned shutdown: INJ-BETA down, INJ-GAMMA (next standby-turned-duty logic) overloaded
    if eid == "INJ-BETA":
        d = (pd.Timestamp("2024-07-14") - START).days
        running_hours[d:d+4] = [6, 0, 0, 18]
        power_draw[d:d+4] = [rated_kw, 0, 0, rated_kw]
    if eid == "INJ-DELTA":  # standby unit picks up load during INJ-BETA outage
        d = (pd.Timestamp("2024-07-14") - START).days
        running_hours[d:d+4] = [18, 24, 24, 6]
        power_draw[d:d+4] = [rated_kw, rated_kw * 1.05, rated_kw * 1.05, rated_kw]

    # 2025 energy leak: TRT-DELTA draws progressively more power for same duty (efficiency loss)
    if eid == "TRT-DELTA":
        leak_start = (pd.Timestamp("2025-02-01") - START).days
        leak_end = (pd.Timestamp("2025-07-10") - START).days
        length = leak_end - leak_start
        power_draw[leak_start:leak_end] = rated_kw * np.linspace(1.0, 1.42, length)
        power_draw[leak_end:leak_end+2] = [rated_kw * 0.3, rated_kw]  # brief outage for repair, then normal

    # 2026 predictive intervention: INJ-DELTA brief planned outage (short, controlled)
    if eid == "INJ-DELTA":
        warn_end = (pd.Timestamp("2026-04-05") - START).days
        running_hours[warn_end:warn_end+1] = [8]  # short planned maintenance window

    # small random daily noise on duty units for realism
    noise = np.random.normal(1.0, 0.015, n_days)
    power_draw = np.where(running_hours > 0, power_draw * noise, 0.0)

    energy_kwh = power_draw * running_hours
    voltage = 11000 if "INJ" in eid else (6600 if grp in ("Treatment Pump", "Deaerator") else 400)
    current = np.where(power_draw > 0, (power_draw * 1000) / (np.sqrt(3) * voltage * 0.87), 0.0)

    elec_rows.append(pd.DataFrame({
        "DATE": dates, "Equipment_ID": eid, "Equipment_Group": grp,
        "Running_Hours": running_hours.round(2), "Power_Draw_kW": power_draw.round(2),
        "Energy_kWh": energy_kwh.round(1), "Voltage_V": voltage, "Current_A": current.round(1),
        "Power_Factor": 0.87, "Cost_per_kWh_USD": COST_PER_KWH_USD,
        "Total_Cost_USD": (energy_kwh * COST_PER_KWH_USD).round(2),
    }))

# chemical dosing (lumped per chemical, continuous low load)
for chem in CHEMICALS:
    running_hours = np.full(n_days, 24.0)
    power_draw = np.random.normal(CHEM_RATED_KW, 0.15, n_days).clip(0.5, 4)
    energy_kwh = power_draw * running_hours
    elec_rows.append(pd.DataFrame({
        "DATE": dates, "Equipment_ID": f"CHEM-{chem.replace(' ', '_').upper()}",
        "Equipment_Group": "Chemical Dosing", "Running_Hours": running_hours,
        "Power_Draw_kW": power_draw.round(2), "Energy_kWh": energy_kwh.round(1),
        "Voltage_V": 400, "Current_A": ((power_draw*1000)/(np.sqrt(3)*400*0.87)).round(1),
        "Power_Factor": 0.87, "Cost_per_kWh_USD": COST_PER_KWH_USD,
        "Total_Cost_USD": (energy_kwh * COST_PER_KWH_USD).round(2),
    }))

elec_df = pd.concat(elec_rows, ignore_index=True).sort_values(["DATE", "Equipment_ID"]).reset_index(drop=True)
print(f"Electrical_Consumption_Data: {len(elec_df)} rows")

# ============================================================
# MAINTENANCE_DATA (event-based)
# ============================================================
maint_events = []

# Routine preventive maintenance every ~180 days per major unit
for _, eq in equip_df.iterrows():
    eid = eq["Equipment_ID"]
    for start in range(90, n_days, 180):
        d = dates[start]
        labor = rng.uniform(1500, 4000)
        parts = rng.uniform(2000, 8000)
        maint_events.append({
            "DATE": d, "Equipment_ID": eid, "Equipment_Type": eq["Equipment_Group"],
            "Maintenance_Type": "Preventive", "Trigger": "Scheduled",
            "Downtime_Hours": round(rng.uniform(2, 6), 1),
            "Labor_Cost_USD": round(labor, 2), "Parts_Cost_USD": round(parts, 2),
            "Lost_Production_Cost_USD": 0.0, "Failure_Mode": None,
        })

# 2024 unplanned shutdown -- corrective/emergency
maint_events.append({
    "DATE": pd.Timestamp("2024-07-14"), "Equipment_ID": "INJ-BETA", "Equipment_Type": "Injection Pump",
    "Maintenance_Type": "Emergency", "Trigger": "Failure",
    "Downtime_Hours": 42.0, "Labor_Cost_USD": 38000, "Parts_Cost_USD": 165000,
    "Lost_Production_Cost_USD": 612000, "Failure_Mode": "Motor Winding Fault / Trip",
})

# 2025 energy leak -- corrective, caught late
maint_events.append({
    "DATE": pd.Timestamp("2025-07-10"), "Equipment_ID": "TRT-DELTA", "Equipment_Type": "Treatment Pump",
    "Maintenance_Type": "Corrective", "Trigger": "Efficiency Degradation (belated)",
    "Downtime_Hours": 16.0, "Labor_Cost_USD": 6200, "Parts_Cost_USD": 21500,
    "Lost_Production_Cost_USD": 41000, "Failure_Mode": "Impeller Wear / Bearing Degradation",
})

# 2026 predictive save -- planned, minimal cost/downtime
maint_events.append({
    "DATE": pd.Timestamp("2026-04-05"), "Equipment_ID": "INJ-DELTA", "Equipment_Type": "Injection Pump",
    "Maintenance_Type": "Predictive", "Trigger": "Vibration Alert (early)",
    "Downtime_Hours": 8.0, "Labor_Cost_USD": 5400, "Parts_Cost_USD": 12800,
    "Lost_Production_Cost_USD": 9600, "Failure_Mode": "Bearing Wear (pre-emptive replacement)",
})

# 2026 minor lost-time incident
maint_events.append({
    "DATE": pd.Timestamp("2026-08-22"), "Equipment_ID": "ITK-GAMMA", "Equipment_Type": "Intake Pump",
    "Maintenance_Type": "Corrective", "Trigger": "Safety Lost-Time Incident",
    "Downtime_Hours": 12.0, "Labor_Cost_USD": 4100, "Parts_Cost_USD": 3200,
    "Lost_Production_Cost_USD": 8700, "Failure_Mode": "Seal Leak (minor, LTI during repair)",
})

maint_df = pd.DataFrame(maint_events)
maint_df["Total_Cost_USD"] = (maint_df["Labor_Cost_USD"] + maint_df["Parts_Cost_USD"] + maint_df["Lost_Production_Cost_USD"]).round(2)
maint_df = maint_df.sort_values("DATE").reset_index(drop=True)
print(f"Maintenance_Data: {len(maint_df)} events")

# ============================================================
# DAILY_SUMMARY_KPI
# ============================================================
daily_elec = elec_df.groupby("DATE")["Total_Cost_USD"].sum().rename("Total_Electrical_Cost_USD")
daily_energy = elec_df.groupby("DATE")["Energy_kWh"].sum().rename("Total_Energy_kWh")
daily_maint = maint_df.groupby("DATE")["Total_Cost_USD"].sum().rename("Total_Maintenance_Cost_USD")
daily_downtime = maint_df.groupby("DATE")["Downtime_Hours"].sum().rename("Total_Lost_Time_Hours")

summary = pd.DataFrame({"DATE": dates}).set_index("DATE")
summary = summary.join(daily_elec).join(daily_energy).join(daily_maint).join(daily_downtime).fillna(0)
summary["Combined_OPEX_USD"] = (summary["Total_Electrical_Cost_USD"] + summary["Total_Maintenance_Cost_USD"]).round(2)
summary["Uptime_Pct"] = (100 - (summary["Total_Lost_Time_Hours"] / 24 * 100)).clip(0, 100).round(2)
summary = summary.reset_index()

print(f"Daily_Summary_KPI: {len(summary)} rows")
print(f"\nTotal 4-year electrical cost: ${elec_df['Total_Cost_USD'].sum():,.0f}")
print(f"Total 4-year maintenance cost: ${maint_df['Total_Cost_USD'].sum():,.0f}")
print(f"Total lost-time hours across all incidents: {maint_df['Downtime_Hours'].sum():,.1f}")

# ============================================================
# EXPORT
# ============================================================
out_path = "/mnt/user-data/outputs/Aramco_Scale_Electrical_Maintenance_2023-2026.xlsx"
with pd.ExcelWriter(out_path, engine="openpyxl", datetime_format="YYYY-MM-DD") as writer:
    elec_df.to_excel(writer, sheet_name="Electrical_Consumption_Data", index=False)
    health_df.to_excel(writer, sheet_name="Equipment_Health_Index", index=False)
    maint_df.to_excel(writer, sheet_name="Maintenance_Data", index=False)
    summary.to_excel(writer, sheet_name="Daily_Summary_KPI", index=False)
    equip_df.to_excel(writer, sheet_name="Equipment_Master", index=False)

print(f"\nSaved: {out_path}")
