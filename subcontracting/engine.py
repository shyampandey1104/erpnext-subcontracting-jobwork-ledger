"""Subcontracting Jobwork, Principal-Jobworker Ledger & GST Section 143 ITC-04 Engine."""

from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class JobworkChallan:
    challan_number: str
    jobworker_name: str
    jobworker_gstin: str
    raw_material_sku: str
    issued_raw_material_qty_kg: float
    raw_material_unit_rate: float
    expected_finished_sku: str
    dispatch_date: str
    due_return_date: str
    bom_conversion_ratio: float = 1.0
    permitted_scrap_loss_pct: float = 2.0


@dataclass
class JobworkReceiptAudit:
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
        scrap_pct: float = 2.0
    ) -> JobworkChallan:
        d_out = datetime.strptime(dispatch_date_str, "%Y-%m-%d").date()
        due_date = (d_out + timedelta(days=365)).strftime("%Y-%m-%d")

        return JobworkChallan(
            challan_number=challan_no,
            jobworker_name=jobworker,
            jobworker_gstin=gstin,
            raw_material_sku=raw_sku,
            issued_raw_material_qty_kg=issued_kg,
            raw_material_unit_rate=raw_rate,
            expected_finished_sku=finished_sku,
            dispatch_date=dispatch_date_str,
            due_return_date=due_date,
            permitted_scrap_loss_pct=scrap_pct
        )

    def reconcile_finished_receipt(
        self,
        challan: JobworkChallan,
        receipt_no: str,
        received_finished_units: float,
        scrap_returned_kg: float,
        receipt_date_str: str,
        conversion_rate_per_unit: float
    ) -> JobworkReceiptAudit:
        d_out = datetime.strptime(challan.dispatch_date, "%Y-%m-%d").date()
        d_recv = datetime.strptime(receipt_date_str, "%Y-%m-%d").date()

        days_elapsed = (d_recv - d_out).days
        is_within_statutory = days_elapsed <= 365

        consumed_raw_material = received_finished_units * challan.bom_conversion_ratio
        accounted_material = consumed_raw_material + scrap_returned_kg
        actual_loss_kg = max(0.0, round(challan.issued_raw_material_qty_kg - accounted_material, 2))

        permitted_scrap_kg = (challan.issued_raw_material_qty_kg * challan.permitted_scrap_loss_pct) / 100.0

        if actual_loss_kg <= permitted_scrap_kg:
            is_scrap_ok = True
            penalty = 0.0
        else:
            is_scrap_ok = False
            excess_kg = actual_loss_kg - permitted_scrap_kg
            penalty = round(excess_kg * challan.raw_material_unit_rate, 2)

        payable_conversion = round(received_finished_units * conversion_rate_per_unit, 2)
        net_payable = max(0.0, round(payable_conversion - penalty, 2))

        status = "RECONCILED_APPROVED" if is_scrap_ok and is_within_statutory else "AUDIT_WARNING_PENALTY_LEVIED"

        return JobworkReceiptAudit(
            receipt_number=receipt_no,
            challan_number=challan.challan_number,
            received_finished_qty=received_finished_units,
            scrap_returned_kg=scrap_returned_kg,
            actual_loss_kg=actual_loss_kg,
            is_scrap_within_permitted_limit=is_scrap_ok,
            penalty_excess_scrap_charge=penalty,
            jobwork_conversion_charges_payable=net_payable,
            is_within_gst_1yr_statutory_window=is_within_statutory,
            status=status
        )
