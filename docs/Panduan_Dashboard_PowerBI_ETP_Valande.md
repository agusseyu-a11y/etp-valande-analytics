# Panduan Visualisasi Power BI — ETP Valande
### Electrical Consumption & Predictive Maintenance Dashboard (2023–2026)

Panduan ini khusus untuk file **Aramco_Scale_Electrical_Maintenance_2023-2026.xlsx** — skala plant ETP Valande (1.000.000 BWPD, 20 unit equipment utama). Berbeda dari panduan WTP Zeta sebelumnya, di sini ada **2 tabel dimensi** (Tanggal & Equipment) dan **3 tabel catatan harian/event**, jadi relasinya sedikit lebih kompleks — ikuti pelan-pelan, urutannya penting.

File berisi 5 sheet: `Electrical_Consumption_Data`, `Equipment_Health_Index`, `Maintenance_Data`, `Daily_Summary_KPI`, `Equipment_Master`.

---

## SECTION 1 — Memasukkan Data ke Power BI

1. Buka **Power BI Desktop** → tab **Home** → **Get Data** → **Excel Workbook**.
2. Pilih **Aramco_Scale_Electrical_Maintenance_2023-2026.xlsx** → **Open**.
3. Di jendela **Navigator**, centang **kelima sheet**: ☑ `Electrical_Consumption_Data`, ☑ `Equipment_Health_Index`, ☑ `Maintenance_Data`, ☑ `Daily_Summary_KPI`, ☑ `Equipment_Master`.
4. Klik **Transform Data**.
5. Cek kolom **DATE** di 4 sheet yang punya kolom itu (semua kecuali `Equipment_Master`) → klik kanan → **Change Type** → pastikan **Date**.
6. Klik **Close & Apply**.

---

## SECTION 2 — Membangun Relasi (2 Tabel Dimensi)

### 2.1 Tabel Hubung / Pusat Tanggal (sama seperti sebelumnya)

1. Buka layar **Model**.
2. Tab **Home** → **New Table**:
   ```
   Tabel_Tanggal = CALENDAR(DATE(2023,1,1), DATE(2026,12,31))
   ```
3. Klik kolom `Date` → **Column tools** → **Data type** → **Date**.
4. Klik kanan `Tabel_Tanggal` → **Mark as Date Table** → pilih `Date` → **OK**.
5. Buat kolom pendukung (satu formula per kotak, jangan digabung):
   ```
   Tahun = YEAR(Tabel_Tanggal[Date])
   ```
   ```
   Bulan = FORMAT(Tabel_Tanggal[Date], "MMM YYYY")
   ```
   ```
   BulanUrut = Tabel_Tanggal[Tahun] * 100 + MONTH(Tabel_Tanggal[Date])
   ```
6. Klik kolom `Bulan` → **Data type** → pastikan **Text** (bukan Whole Number/Date). Klik kolom `Tahun`/`BulanUrut` → pastikan **Whole Number**.
7. Klik kolom `Bulan` → **Column tools** → **Sort by Column** → pilih `BulanUrut`.
8. Seret `Date` dari `Tabel_Tanggal` ke kolom **DATE** di masing-masing: `Electrical_Consumption_Data`, `Equipment_Health_Index`, `Maintenance_Data`, `Daily_Summary_KPI`. Cek tiap relasi: **One to many (1:*)**, **Single** direction.

### 2.2 Tabel Dimensi Equipment (baru — ini yang beda dari panduan sebelumnya)

`Equipment_Master` berisi 20 unit equipment utama (kode Yunani seperti `INJ-ALPHA`, `TRT-DELTA`, dst.) dengan atribut tetapnya (grup, rated power, status duty default). Ini kita jadikan **tabel dimensi kedua**, disambungkan lewat `Equipment_ID`:

1. Masih di layar **Model**, seret kolom `Equipment_ID` dari `Equipment_Master` ke kolom `Equipment_ID` di `Electrical_Consumption_Data`.
2. Ulangi: seret `Equipment_ID` dari `Equipment_Master` ke `Equipment_ID` di `Equipment_Health_Index`.
3. Ulangi sekali lagi ke `Equipment_ID` di `Maintenance_Data`.
4. Cek tiap relasi: **One to many (1:*)**, **Single** direction, arah panah dari `Equipment_Master` menuju ke tabel-tabel data.

> ⚠️ **Penting — jangan panik kalau nanti ada baris "kosong" di beberapa visual.** `Electrical_Consumption_Data` juga berisi baris pemakaian listrik untuk **dosing kimia** (`CHEM-BIOCIDE`, `CHEM-OXYGEN_SCAVENGER`, dst.) yang **tidak ada** di `Equipment_Master` (karena itu bukan unit rotating equipment utama). Baris-baris ini akan tampil "unmatched" kalau kamu narik atribut dari `Equipment_Master` (misal `Rated_Power_kW`) ke visual yang isinya termasuk data kimia — itu wajar, bukan error. Kolom `Equipment_Group` sudah tersedia langsung di `Electrical_Consumption_Data` sendiri, jadi untuk filter/grouping biasa kamu **tidak wajib** lewat relasi `Equipment_Master` ini — relasi ini gunanya kalau suatu saat butuh atribut tambahan seperti `Rated_Power_kW` per unit.

---

## SECTION 3 — Kenalan Isi Tiap Tabel

| Tabel | Isinya apa | Kolom penting |
|---|---|---|
| `Electrical_Consumption_Data` | Pemakaian listrik harian per unit (termasuk dosing kimia) | `Equipment_ID`, `Running_Hours`, `Power_Draw_kW`, `Energy_kWh`, `Total_Cost_USD` |
| `Equipment_Health_Index` | Indikator kesehatan harian per unit — dasar predictive maintenance | `Health_Index_Pct`, `Vibration_mm_s`, `Predicted_Failure_Risk` |
| `Maintenance_Data` | Catatan tiap event maintenance (bukan harian — cuma muncul kalau ada kejadian) | `Maintenance_Type`, `Trigger`, `Downtime_Hours`, `Total_Cost_USD`, `Failure_Mode` |
| `Daily_Summary_KPI` | Rollup harian tingkat plant, siap pakai buat card/trend | `Combined_OPEX_USD`, `Uptime_Pct`, `Total_Lost_Time_Hours` |
| `Equipment_Master` | Daftar referensi 20 unit equipment | `Equipment_ID`, `Equipment_Group`, `Rated_Power_kW` |

---

## SECTION 4 — Membuat Rumus (DAX Measure)

Cara bikin measure: klik ikon **Data** → klik tabel tujuan → tab **Table tools** → **New Measure**.

### 4.1 Measure Biaya & Energi

```
Total Electrical Cost (USD) = SUM(Electrical_Consumption_Data[Total_Cost_USD])
```
```
Total Energy (kWh) = SUM(Electrical_Consumption_Data[Energy_kWh])
```
```
Total Maintenance Cost (USD) = SUM(Maintenance_Data[Total_Cost_USD])
```
```
Combined OPEX (USD) = [Total Electrical Cost (USD)] + [Total Maintenance Cost (USD)]
```
> 🧠 **Fungsinya:** `Combined OPEX` menjumlahkan dua measure lain langsung (bukan dari kolom) — ini contoh **measure yang memanggil measure lain**, praktik umum di DAX supaya tidak menulis ulang rumus panjang berkali-kali.

### 4.2 Measure Uptime & Lost Time

```
Total Lost Time (Hours) = SUM(Maintenance_Data[Downtime_Hours])
```
```
Average Uptime % = AVERAGE(Daily_Summary_KPI[Uptime_Pct])
```

### 4.3 Measure Predictive Maintenance (inti dashboard ini)

```
Average Health Index = AVERAGE(Equipment_Health_Index[Health_Index_Pct])
```
```
Critical Risk Days =
CALCULATE(
    COUNTROWS(Equipment_Health_Index),
    Equipment_Health_Index[Predicted_Failure_Risk] = "Critical"
)
```
> 🧠 **Fungsinya:** menghitung berapa hari (across semua unit yang sedang difilter) status risikonya jatuh ke "Critical" (Health Index < 55). Cocok jadi KPI "berapa kali plant ini nyaris kena masalah besar".

### 4.4 Measure Perbandingan Biaya per Jenis Maintenance

```
Emergency Maintenance Cost (USD) =
CALCULATE([Total Maintenance Cost (USD)], Maintenance_Data[Maintenance_Type] = "Emergency")
```
```
Predictive Maintenance Cost (USD) =
CALCULATE([Total Maintenance Cost (USD)], Maintenance_Data[Maintenance_Type] = "Predictive")
```
> 🧠 **Fungsinya:** dua measure ini yang bakal jadi bukti visual paling kuat di dashboard — bandingkan biaya kejadian **Emergency** (2024, ~$815rb, downtime 42 jam) vs **Predictive** (2026, ~$27,8rb, downtime cuma 8 jam). Ini argumen langsung buat manajemen soal ROI predictive maintenance.

### 4.5 Kolom Bantu Warna untuk Risk Level (dipakai di Section 6)

Ini **kolom**, bukan measure — dibuat di tabel `Equipment_Health_Index` lewat **New Column**:

```
Risk_Color =
SWITCH(
    TRUE(),
    Equipment_Health_Index[Health_Index_Pct] < 55, "#C00000",
    Equipment_Health_Index[Health_Index_Pct] < 75, "#FFA500",
    Equipment_Health_Index[Health_Index_Pct] < 90, "#FFC000",
    "#00B050"
)
```
> 🧠 **Fungsinya:** `SWITCH(TRUE(), kondisi1, hasil1, kondisi2, hasil2, ..., default)` itu pola DAX buat bikin logika bertingkat (mirip IF berantai tapi lebih rapi dibaca). Di sini: merah tua kalau Critical, oranye kalau High, kuning kalau Medium, hijau kalau Low — dipakai nanti buat pewarnaan tabel di Section 6.

---

## SECTION 5 — Membuat Visual

Susun layout: **Baris 1** = KPI cards, **Baris 2** = trend chart Health Index (visual utama dashboard ini) + bar chart perbandingan biaya maintenance, **Baris 3** = tabel event maintenance.

### 5.1 KPI Cards (Baris 1)

Buat 5 card: `Total Electrical Cost (USD)`, `Total Maintenance Cost (USD)`, `Combined OPEX (USD)`, `Total Lost Time (Hours)`, `Average Uptime %`. Untuk card biaya, ubah format ke **Currency ($)** lewat panel Format.

### 5.2 Line Chart — Health Index Trend (visual paling penting di dashboard ini)

1. Klik ikon **Line Chart**.
2. X-axis: seret `Bulan` dari `Tabel_Tanggal` — atau kalau mau lihat harian detail per insiden (misal zoom ke Juli 2024), pakai `Date` langsung.
3. Y-axis: `Average Health Index`.
4. **Legend**: seret `Equipment_ID` dari `Equipment_Health_Index` — ini bikin satu garis per unit, jadi kamu bisa lihat pola `INJ-BETA` (jatuh mendadak), `TRT-DELTA` (turun pelan-pelan), `INJ-DELTA` (turun lalu kepotong cepat) sekaligus dalam satu grafik.
5. Karena ada 20 unit, grafik bakal penuh garis kalau ditampilkan semua — tambahkan **Slicer** `Equipment_ID` (Section 5.5) supaya bisa fokus ke unit tertentu.

### 5.3 Bar Chart — Biaya Maintenance per Jenis

1. Klik ikon **Clustered Bar Chart**.
2. Y-axis: `Maintenance_Type` (dari `Maintenance_Data`).
3. X-axis: `Total Maintenance Cost (USD)`.
4. Ini akan langsung kelihatan kontras: batang **Emergency** jauh lebih panjang dari **Predictive** — visual paling kuat buat argumen ROI predictive maintenance.

### 5.4 Table — Log Event Maintenance

1. Klik ikon **Table**.
2. Kolom: `DATE`, `Equipment_ID`, `Maintenance_Type`, `Trigger`, `Downtime_Hours`, `Failure_Mode`, `Total_Cost_USD`.
3. `Downtime_Hours` dan `Total_Cost_USD` biarkan **Sum** (di tabel ini itu benar, karena tiap baris memang satu event unik, bukan data yang perlu Don't Summarize seperti kasus baku mutu sebelumnya).

### 5.5 Slicer

Slicer 1: `Date` dari `Tabel_Tanggal` (format **Between**). Slicer 2: `Equipment_ID` dari `Equipment_Health_Index`. Slicer 3: `Maintenance_Type` dari `Maintenance_Data`.

---

## SECTION 6 — Pewarnaan Risk Level (Conditional Formatting)

Sama seperti trik `Warna_Status` di panduan WTP Zeta — pakai kolom bantu `Risk_Color` dari Section 4.5, bukan Rules manual (Rules tidak bisa merujuk kolom lain secara dinamis).

1. Bikin visual **Table** baru (atau pakai yang sudah ada), masukkan kolom `Equipment_ID`, `DATE`, `Health_Index_Pct`, `Predicted_Failure_Risk` dari `Equipment_Health_Index`.
2. Klik field `Predicted_Failure_Risk` di visual → **Conditional formatting** → **Background color**.
3. **Format style** → **Field value**.
4. **"What field should we base this on?"** → pilih `Risk_Color`.
5. Klik **OK**.

Sekarang baris dengan status "Critical" otomatis merah tua, "High" oranye, "Medium" kuning, "Low" hijau — tanpa perlu bikin 4 aturan manual.

---

## SECTION 7 — Troubleshooting Tambahan (khusus dataset ini)

**Baris data kimia (`CHEM-...`) tidak muncul saat saya filter pakai atribut dari Equipment_Master**
→ Ini bukan bug — sudah dijelaskan di Section 2.2, wajar karena dosing kimia memang tidak terdaftar di `Equipment_Master`. Kalau butuh grouping, pakai kolom `Equipment_Group` yang sudah ada langsung di `Electrical_Consumption_Data`, jangan lewat `Equipment_Master`.

**Line chart Health Index isinya 20 garis campur aduk, susah dibaca**
→ Wajar untuk 20 unit sekaligus. Tambahkan slicer `Equipment_ID` (Section 5.5), lalu pilih 1-3 unit yang mau dibandingkan saja — misal `INJ-BETA` vs `TRT-DELTA` vs `INJ-DELTA` buat bandingkan 3 skenario insiden.

**Measure `Critical Risk Days` angkanya kelihatan double-count kalau tidak difilter per unit**
→ Ingat, `Equipment_Health_Index` itu granularity-nya **per unit per hari**, jadi kalau 3 unit sama-sama "Critical" di hari yang sama, itu dihitung 3 baris (bukan 1 hari plant-level). Kalau maunya "berapa hari kalender ada MINIMAL 1 unit Critical", butuh rumus berbeda (pakai `DISTINCTCOUNT` di kolom `DATE` dengan filter yang sama) — tanya saja kalau butuh versi itu.

**Relasi ke `Equipment_Master` bikin error "many-to-many not allowed"**
→ Cek arah relasinya — pastikan panahnya dari `Equipment_Master` (sisi "1") ke tabel data (sisi "banyak"), bukan kebalik. `Equipment_ID` di `Equipment_Master` harus unik (20 baris, 20 ID beda) — kalau ada duplikat di situ, itu yang bikin error.

---

## SECTION 8 — Simpan & Bagikan

1. **File** → **Save As** → `Dashboard_ETP_Valande_2023-2026.pbix`.
2. Publish atau share `.pbix` sesuai kebutuhan (lihat panduan sebelumnya, langkahnya sama).

---

### Penutup

Dashboard ini beda tantangan dari WTP Zeta — bukan soal baku mutu air lagi, tapi soal **membaca tren, bukan cuma angka hari ini**. Fokus utamanya di line chart Health Index (Section 5.2) — itu jantung dari cerita predictive maintenance yang mau disampaikan ke manajemen: masalah yang keliatan dari jauh-jauh hari itu jauh lebih murah ditangani daripada yang muncul mendadak.
