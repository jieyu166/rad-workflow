"""Unit tests for radtracker/build_trends.py biopsy QC aggregation (synthetic data, no PHI)."""
import datetime as dt
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "radtracker"))
import build_trends as bt  # noqa: E402

try:
    import openpyxl
except ImportError:  # pragma: no cover
    openpyxl = None


@unittest.skipIf(openpyxl is None, "openpyxl not installed")
class LoadBiopsyQcTest(unittest.TestCase):
    def _make_xlsx(self, rows):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "tracker.xlsx"
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["exec_date", "proc", "chart", "pre", "result", "note"])
        for r in rows:
            ws.append(r)
        wb.save(path)
        return path

    def _run(self, rows):
        path = self._make_xlsx(rows)
        orig = bt.BIOPSY_XLSX
        bt.BIOPSY_XLSX = path
        self.addCleanup(setattr, bt, "BIOPSY_XLSX", orig)
        return bt.load_biopsy_qc()

    def test_total_malignant_includes_thyroid_fna(self):
        d = dt.datetime(2026, 10, 20)
        q = self._run([
            (d, "Thyroid FNA", "00000001", None, "malignant", "papillary carcinoma"),
            (d, "Thyroid FNA", "00000002", None, "benign", "nodular goiter"),
            (d, "Breast CNB", "00000003", None, "malignant", "invasive carcinoma"),
            (d, "CT-Biopsy", "00000004", None, "malignant", "adenocarcinoma"),
        ])
        self.assertEqual(q["total_malignant"], 3)

    def test_ppv_rows_unchanged(self):
        d = dt.datetime(2026, 10, 20)
        q = self._run([
            (d, "Breast CNB", "00000003", None, "malignant", ""),
            (d, "Breast CNB", "00000005", None, "benign", ""),
        ])
        brc = next(r for r in q["summary"] if r["proc"] == "Breast CNB")
        self.assertEqual((brc["malignant"], brc["ppv"]), (1, 50))

    def test_pending_rows_ignored(self):
        d = dt.datetime(2026, 10, 20)
        q = self._run([
            (d, "Thyroid FNA", "00000006", None, "pending", ""),
            (d, "Thyroid FNA", "00000007", None, "malignant", ""),
        ])
        self.assertEqual(q["total_malignant"], 1)


if __name__ == "__main__":
    unittest.main()
