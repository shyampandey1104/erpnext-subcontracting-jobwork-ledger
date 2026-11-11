"""Subcontracting Jobwork, Principal-Jobworker Ledger & GST Section 143 ITC-04 Engine."""

from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class JobworkChallan(BaseModel):
    challan_number: str
    jobworker_name: str
    jobworker_gstin: str
    raw_material_sku: str
    issued_raw_material_qty_kg: float
    raw_material_unit_rate: float
    expected_finished_sku: str
    bom_conversion_ratio: float = 1.0  # 1 kg raw material yields 1 unit finished
    permitted_scrap_loss_pct: float = 2.0
    dispatch_date: str  # YYYY-MM-DD
    due_return_date: str # 1 year deadline as per Section 143


class JobworkReceiptAudit(BaseModel):
    receipt_number: str
    challan_number: str
    received_finished_qty: float
    scrap_returned_kg: float
    actual_loss_kg: float
    is_scrap_within_permitted_limit: bool
    penalty_excess_scrap_charge: float
    jobwork_conversion_charges_payable: float
    is_within_gst_1yr_statutory_window: bool
    status: str


class SubcontractingJobworkEngine:
    """Manages outsourced manufacturing jobwork, Section 143 ITC-04 return timelines, and scrap limits."""

    def issue_jobwork_challan(
        self,
        challan_no: str,
        jobworker: str,
        gstin: str,
        raw_sku: str,
        issued_kg: float,
        raw_rate: float,
        finished_sku: str,
        dispatch_date_str: str,
        scrap_pct: float = 2.5
    ) -> JobworkChallan:
        d_out = datetime.strptime(dispatch_date_str, "%Y-%m-%d").date()
        # Statutory 1-year window for inputs return (Section 143 of CGST Act)
        due_date = (d_out + timedelta(days=365)).strftime("%Y-%m-%d")

        return JobworkChallan(
            challan_number=challan_no,
            jobworker_name=jobworker,
            jobworker_gstin=gstin,
            raw_material_sku=raw_sku,
            issued_raw_material_qty_kg=issued_kg,
            raw_material_unit_rate=raw_rate,
            expected_finished_sku=finished_sku,
            bom_conversion_ratio=1.0,
            permitted_scrap_loss_pct=scrap_pct,
            dispatch_date=dispatch_date_str,
            due_return_date=due_date
        )

    def reconcile_finished_receipt(
        self,
        challan: JobworkChallan,
        receipt_no: str,
        received_finished_units: float,
        scrap_returned_kg: float,
        receipt_date_str: str,
        conversion_rate_per_unit: float = 45.0
    ) -> JobworkReceiptAudit:
        d_rcv = datetime.strptime(receipt_date_str, "%Y-%m-%d").date()
        d_due = datetime.strptime(challan.due_return_date, "%Y-%m-%d").date()
        is_timely = d_rcv <= d_due

        # Material Balance: Issued = Finished Content + Returned Scrap + Unaccounted Loss
        accounted_material = received_finished_units + scrap_returned_kg
        actual_loss_kg = max(0.0, challan.issued_raw_material_qty_kg - accounted_material)

        permitted_loss_kg = challan.issued_raw_material_qty_kg * (challan.permitted_scrap_loss_pct / 100.0)
        is_scrap_ok = actual_loss_kg <= permitted_loss_kg

        # Penalty on excess unaccounted loss
        excess_loss_kg = max(0.0, actual_loss_kg - permitted_loss_kg)
        penalty_charge = excess_loss_kg * challan.raw_material_unit_rate

        # Gross conversion payment
        gross_jobwork_charge = received_finished_units * conversion_rate_per_unit
        net_payable = max(0.0, gross_jobwork_charge - penalty_charge)

        return JobworkReceiptAudit(
            receipt_number=receipt_no,
            challan_number=challan.challan_number,
            received_finished_qty=received_finished_units,
            scrap_returned_kg=scrap_returned_kg,
            actual_loss_kg=round(actual_loss_kg, 2),
            is_scrap_within_permitted_limit=is_scrap_ok,
            penalty_excess_scrap_charge=round(penalty_charge, 2),
            jobwork_conversion_charges_payable=round(net_payable, 2),
            is_within_gst_1yr_statutory_window=is_timely,
            status="RECONCILED_APPROVED" if is_scrap_ok else "RECONCILED_WITH_SCRAP_DEBIT"
        )
