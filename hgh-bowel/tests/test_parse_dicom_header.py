# -*- coding: utf-8 -*-
"""Tests for parse_dicom_header. All fixtures are synthetic - no patient data."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parse_dicom_header import parse_header, to_row  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    with open(os.path.join(HERE, name), "r", encoding="utf-8") as fh:
        return fh.read()


class TestInfinittLayout(unittest.TestCase):
    """INFINITT prints the label and VR on one line, the value on the next as |value|."""

    def setUp(self):
        self.fields, _ = parse_header(load("sample_header_infinitt.txt"))
        self.row, self.problems = to_row(self.fields)

    def test_no_problems(self):
        self.assertEqual(self.problems, [])

    def test_vr_not_mistaken_for_value(self):
        # "DA" sits in the VR column of the Study Date line; the value is on the next.
        self.assertEqual(self.fields["StudyDate"], "20240115")

    def test_all_six_columns(self):
        self.assertEqual(self.row["拍攝年"], "2024")
        self.assertEqual(self.row["年齡"], "65")       # 065Y -> 65
        self.assertEqual(self.row["性別"], "M")        # M/F per the KMU example sheet
        self.assertEqual(self.row["解析度"], "512*512")  # export size, constant
        self.assertEqual(self.row["CT廠牌"], "SIEMENS")
        self.assertEqual(self.row["CT型號"], "SOMATOM Definition AS+")

    def test_accession_kept_as_digits(self):
        self.assertEqual(self.row["AccessionNumber"], "999999999999999")


class TestOtherLayouts(unittest.TestCase):
    def test_colon_separated(self):
        text = (
            "StudyDate: 20231204\n"
            "AccessionNumber: 999999999999998\n"
            "Manufacturer: GE MEDICAL SYSTEMS\n"
            "ManufacturerModelName: Revolution CT\n"
            "PatientSex: F\n"
            "PatientAge: 042Y\n"
            "Rows: 512\n"
            "Columns: 512\n"
        )
        row, problems = to_row(parse_header(text)[0])
        self.assertEqual(problems, [])
        self.assertEqual(row["性別"], "F")
        self.assertEqual(row["年齡"], "42")
        self.assertEqual(row["CT廠牌"], "GE MEDICAL SYSTEMS")

    def test_two_letter_manufacturer_survives(self):
        # "GE" is a valid VR string, but with no |value| line following it must be kept.
        text = "(0008,0070) Manufacturer  GE\n(0028,0010) Rows  512\n"
        fields, _ = parse_header(text)
        self.assertEqual(fields["Manufacturer"], "GE")

    def test_age_from_birthdate_when_patientage_missing(self):
        text = (
            "StudyDate: 20240115\n"
            "PatientBirthDate: 19580712\n"   # birthday not yet reached in January
            "PatientSex: M\n"
            "AccessionNumber: 1\n"
            "Manufacturer: X\nManufacturerModelName: Y\nRows: 512\nColumns: 512\n"
        )
        row, _ = to_row(parse_header(text)[0])
        self.assertEqual(row["年齡"], "65")

    def test_first_occurrence_wins(self):
        text = "PatientSex: M\nPatientSex: F\n"
        self.assertEqual(parse_header(text)[0]["PatientSex"], "M")


class TestProblemReporting(unittest.TestCase):
    def test_missing_fields_are_reported_not_silently_blank(self):
        row, problems = to_row(parse_header("StudyDate: 20240115\n")[0])
        self.assertEqual(row["拍攝年"], "2024")
        self.assertTrue(any("性別" in p for p in problems))
        self.assertTrue(any("申請單號" in p for p in problems))

    def test_resolution_is_the_export_size_not_the_dicom_matrix(self):
        # The field means the size of the JPG delivered to KMU, which is constant.
        row, problems = to_row(parse_header("Rows: 512\nColumns: 512\n")[0])
        self.assertEqual(row["解析度"], "512*512")
        self.assertFalse(any("矩陣" in p for p in problems))

    def test_matrix_disagreeing_with_export_is_flagged(self):
        # A 768 matrix still exports as a 512 JPG - worth a look, not a silent fill.
        row, problems = to_row(parse_header("Rows: 768\nColumns: 768\n")[0])
        self.assertEqual(row["解析度"], "512*512")
        self.assertTrue(any("矩陣" in p for p in problems))

    def test_empty_input(self):
        row, problems = to_row(parse_header("")[0])
        self.assertEqual(row["拍攝年"], "")
        self.assertGreaterEqual(len(problems), 5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
