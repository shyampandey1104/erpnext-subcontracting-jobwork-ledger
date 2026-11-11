# ERPNext Subcontracting Jobwork & ITC-04 Ledger 🏭📜

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![ERPNext](https://img.shields.io/badge/ERPNext-v14%20%7C%20v15-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Build](https://img.shields.io/badge/Build-Passing-brightgreen.svg)

An enterprise outsourced subcontracting manufacturing ledger, Principal-Jobworker raw material custody tracker, GST Section 143 (ITC-04 return compliance), and scrap tolerance reconciliation system for **ERPNext Manufacturing**.

---

## 🚀 Key Features

- **GST Section 143 Compliance Tracking**: Automatically audits the 1-year statutory return timeline for raw materials sent under Job Work delivery challans.
- **BOM Material Balance & Scrap Audit**: Reconciles issued inputs against finished goods and returned turnings/scrap with tolerance thresholds.
- **Excess Loss Debit Notes**: Automatically deducts raw material costs from jobworker service billing when scrap exceeds agreed limits.
- **Subcontracting Purchase Receipt Integration**: Direct generation of ERPNext `Subcontracting Order`, `Purchase Receipt`, and `Stock Entry`.

---

## 📦 Installation & Setup

```bash
git clone https://github.com/shyampandey1104/erpnext-subcontracting-jobwork-ledger.git
cd erpnext-subcontracting-jobwork-ledger
pip install -r requirements.txt
```

---

## 🛠️ Usage Example

```python
from subcontracting.engine import SubcontractingJobworkEngine

engine = SubcontractingJobworkEngine()

# Issue raw material under GST Jobwork Challan
challan = engine.issue_jobwork_challan(
    challan_no="CH-501",
    jobworker="Apex Heat Treaters",
    gstin="27AAACH1234F1Z9",
    raw_sku="STEEL-PIN-RAW",
    issued_kg=500.0,
    raw_rate=180.0,
    finished_sku="HARDENED-PIN-HEAT-TREATED",
    dispatch_date_str="2026-04-01"
)

# Reconcile inward receipt
audit = engine.reconcile_finished_receipt(
    challan=challan,
    receipt_no="RCP-901",
    received_finished_units=490.0,
    scrap_returned_kg=5.0,
    receipt_date_str="2026-05-10"
)
print(f"Status: {audit.status} | Net Payable: ₹{audit.jobwork_conversion_charges_payable}")
```

---

## 🧪 Testing

```bash
pytest tests/
```

---

## 📄 License
MIT License. Created with ❤️ by [Shyam Pandey](https://github.com/shyampandey1104).
