import unittest
from subcontracting.engine import SubcontractingJobworkEngine


class TestSubcontractingJobwork(unittest.TestCase):
    def setUp(self):
        self.engine = SubcontractingJobworkEngine()

    def test_challan_issue_and_reconciliation(self):
        # Issue 1000 kg Aluminium ingots to jobworker for die casting
        challan = self.engine.issue_jobwork_challan(
            challan_no="JW-CHALLAN-2026-01",
            jobworker="Om Precision Die Casters",
            gstin="27AABCU9603R1ZM",
            raw_sku="ALU-INGOT-ADC12",
            issued_kg=1000.0,
            raw_rate=220.0,
            finished_sku="CASTING-HOUSING-PART",
            dispatch_date_str="2026-02-01",
            scrap_pct=2.0  # 20 kg permitted loss
        )
        self.assertEqual(challan.due_return_date, "2027-02-01")  # +365 days

        # Receive 960 units finished, 25 kg returned scrap, 15 kg loss (<= 20kg permitted)
        audit = self.engine.reconcile_finished_receipt(
            challan=challan,
            receipt_no="JWR-881",
            received_finished_units=960.0,
            scrap_returned_kg=25.0,
            receipt_date_str="2026-03-15",
            conversion_rate_per_unit=50.0  # 960 * 50 = 48,000
        )
        self.assertTrue(audit.is_scrap_within_permitted_limit)
        self.assertEqual(audit.actual_loss_kg, 15.0)
        self.assertEqual(audit.penalty_excess_scrap_charge, 0.0)
        self.assertEqual(audit.jobwork_conversion_charges_payable, 48000.0)
        self.assertTrue(audit.is_within_gst_1yr_statutory_window)
        self.assertEqual(audit.status, "RECONCILED_APPROVED")


if __name__ == "__main__":
    unittest.main()
