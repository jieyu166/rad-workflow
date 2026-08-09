# -*- coding: utf-8 -*-
"""Parse a copied DICOM header dump into the six columns the KMU bowel-obstruction
mapping sheet needs.

Reads header text from the clipboard (default), a file, or stdin, extracts the
fields, and appends one row to work/result.csv keyed by accession number.

Console output is cp950-safe on purpose: no arrows, no check marks.

Usage:
    python parse_dicom_header.py                 # read clipboard, append to result.csv
    python parse_dicom_header.py --file dump.txt # read a file instead
    python parse_dicom_header.py --inspect       # print detected KEYS only, no values
                                                 # (safe to share when debugging format)
    python parse_dicom_header.py --dry-run       # parse and print, do not append
"""
import argparse
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK_DIR = os.path.join(HERE, "work")
RESULT_CSV = os.path.join(WORK_DIR, "result.csv")
RAW_DIR = os.path.join(WORK_DIR, "raw")

# DICOM tag number -> canonical field name
TAG_MAP = {
    "0008,0020": "StudyDate",
    "0008,0050": "AccessionNumber",
    "0008,0070": "Manufacturer",
    "0008,1090": "ManufacturerModelName",
    "0010,0030": "PatientBirthDate",
    "0010,0040": "PatientSex",
    "0010,1010": "PatientAge",
    "0028,0010": "Rows",
    "0028,0011": "Columns",
}

# Lowercased, punctuation-stripped keyword -> canonical field name.
# Covers both the "StudyDate" and "Study Date" spellings vendors use.
NAME_MAP = {
    "studydate": "StudyDate",
    "accessionnumber": "AccessionNumber",
    "manufacturer": "Manufacturer",
    "manufacturermodelname": "ManufacturerModelName",
    "modelname": "ManufacturerModelName",
    "patientbirthdate": "PatientBirthDate",
    "patientsbirthdate": "PatientBirthDate",
    "birthdate": "PatientBirthDate",
    "patientsex": "PatientSex",
    "patientssex": "PatientSex",
    "sex": "PatientSex",
    "patientage": "PatientAge",
    "patientsage": "PatientAge",
    "age": "PatientAge",
    "rows": "Rows",
    "columns": "Columns",
    "imagerows": "Rows",
    "imagecolumns": "Columns",
}

OUTPUT_COLUMNS = [
    "AccessionNumber",
    "拍攝年",
    "年齡",
    "性別",
    "解析度",
    "CT廠牌",
    "CT型號",
]

TAG_RE = re.compile(r"\(?\s*([0-9A-Fa-f]{4})\s*,\s*([0-9A-Fa-f]{4})\s*\)?")
SEPARATORS = ("|", ":", "\t", "=")

# DICOM value representations. INFINITT prints these in a column of their own, so a
# lone VR on the label line is a column header, not the value. Note this cannot be a
# blanket rule: "GE" is a real Manufacturer, so a VR is only discarded when the next
# line actually carries a |value| to use instead.
VR_SET = {
    "AE", "AS", "AT", "CS", "DA", "DS", "DT", "FL", "FD", "IS", "LO", "LT",
    "OB", "OD", "OF", "OW", "PN", "SH", "SL", "SQ", "SS", "ST", "TM", "UI",
    "UL", "UN", "US", "UT",
}


def _norm_key(text):
    """Lowercase and drop everything that is not a letter, so 'Patient's Age',
    'Patient Age' and 'PatientAge' all collapse to the same key."""
    return re.sub(r"[^a-z]", "", text.lower())


def _split_line(line):
    """Return (label, value) for a header line, or (label, None) when the line
    carries a label but no value on the same line (INFINITT puts the value on the
    following line)."""
    for sep in SEPARATORS:
        if sep in line:
            label, value = line.split(sep, 1)
            return label.strip(), value.strip()
    # Two-or-more spaces also act as a separator in fixed-width dumps.
    m = re.match(r"^(.*?)\s{2,}(.*)$", line)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return line.strip(), None


def _field_for_label(label):
    """Map a header label to a canonical field name, by tag number first (most
    reliable) then by keyword."""
    m = TAG_RE.search(label)
    if m:
        tag = "%s,%s" % (m.group(1).lower(), m.group(2).lower())
        if tag in TAG_MAP:
            return TAG_MAP[tag]
    # Strip a leading tag so "(0010,0040) PatientSex" still matches by name.
    label = TAG_RE.sub(" ", label)
    # Drop a trailing VR code such as "CS" or "LO" that some dumps append.
    label = re.sub(r"\b[A-Z]{2}\b\s*$", "", label).strip()
    return NAME_MAP.get(_norm_key(label))


def parse_header(text):
    """Extract canonical DICOM fields from a pasted header dump.

    Returns (fields, detected_labels). Later occurrences never overwrite an
    earlier non-empty value, so the first (top-level) instance of a tag wins."""
    fields = {}
    detected = []
    lines = [ln.rstrip() for ln in text.replace("\r\n", "\n").split("\n")]

    for i, line in enumerate(lines):
        if not line.strip():
            continue
        label, value = _split_line(line)
        field = _field_for_label(label)
        if not field:
            continue
        detected.append((field, label.strip()))
        nxt_line = lines[i + 1] if i + 1 < len(lines) else ""
        if value and value.upper() in VR_SET and "|" in nxt_line:
            value = None  # that was the VR column; the real value is on the next line
        if value is None or value == "":
            # Value lives on the next line (INFINITT "label" / "|value" layout).
            if i + 1 < len(lines):
                nxt = lines[i + 1]
                _, nxt_value = _split_line(nxt)
                value = nxt_value if nxt_value else nxt.strip().lstrip("|").strip()
        if value:
            value = value.strip().strip("|").strip()
        if value and not fields.get(field):
            fields[field] = value

    return fields, detected


def _digits(value):
    return re.sub(r"\D", "", value or "")


# The exported JPGs delivered to KMU are all this size - measured over 500 images
# sampled across all 250 local case folders. Deliberately NOT taken from DICOM
# Rows/Columns: both happen to be 512 here, but if a study had a 768 matrix the
# DICOM would say 768 while the exported JPG is still 512, which would be wrong.
# The example workbook writes this with '*', not 'x' (it has 150*150).
EXPORT_RESOLUTION = "512*512"


def to_row(fields):
    """Convert canonical DICOM fields to the sheet's columns.

    性別 is M/F, following the 11 rows actually filled in the KMU example
    workbook - not the 1/2 codes shown in its '工作表1' legend.
    Returns (row_dict, problems)."""
    problems = []

    study_date = _digits(fields.get("StudyDate"))
    year = study_date[:4] if len(study_date) >= 4 else ""
    if not year:
        problems.append("StudyDate 缺漏或格式異常")

    age = ""
    raw_age = fields.get("PatientAge") or ""
    m = re.match(r"^\s*0*(\d{1,3})\s*([YyMmWwDd])?", raw_age)
    if m:
        number, unit = int(m.group(1)), (m.group(2) or "Y").upper()
        if unit == "Y":
            age = str(number)
        else:
            # Months/weeks/days all mean an infant; the sheet wants whole years.
            age = "0"
    else:
        birth = _digits(fields.get("PatientBirthDate"))
        if len(birth) == 8 and len(study_date) == 8:
            years = int(study_date[:4]) - int(birth[:4])
            if study_date[4:8] < birth[4:8]:
                years -= 1
            age = str(years)
        else:
            problems.append("年齡無法判定（PatientAge 與 PatientBirthDate 皆缺）")

    sex_raw = (fields.get("PatientSex") or "").strip().upper()
    sex = sex_raw[:1] if sex_raw[:1] in ("M", "F") else ""
    if not sex:
        problems.append("性別無法判定（原值 %r）" % sex_raw)

    # Constant, not derived from the header - see EXPORT_RESOLUTION.
    resolution = EXPORT_RESOLUTION

    # The DICOM matrix is only a cross-check: it should agree with the export.
    rows_v, cols_v = _digits(fields.get("Rows")), _digits(fields.get("Columns"))
    if rows_v and cols_v and "%s*%s" % (rows_v, cols_v) != EXPORT_RESOLUTION:
        problems.append("DICOM 矩陣 %sx%s 與匯出尺寸 %s 不符，請確認這案的圖"
                        % (rows_v, cols_v, EXPORT_RESOLUTION))

    maker = (fields.get("Manufacturer") or "").strip()
    model = (fields.get("ManufacturerModelName") or "").strip()
    if not maker:
        problems.append("CT廠牌缺漏")
    if not model:
        problems.append("CT型號缺漏")

    accession = _digits(fields.get("AccessionNumber"))
    if not accession:
        problems.append("申請單號缺漏，無法對回 mapping 表")

    row = {
        "AccessionNumber": accession,
        "拍攝年": year,
        "年齡": age,
        "性別": sex,
        "解析度": resolution,
        "CT廠牌": maker,
        "CT型號": model,
    }
    return row, problems


def read_clipboard():
    try:
        import tkinter
    except ImportError:
        sys.exit("ERROR: 讀不到剪貼簿（無 tkinter），請改用 --file")
    root = tkinter.Tk()
    root.withdraw()
    try:
        return root.clipboard_get()
    except tkinter.TclError:
        return ""
    finally:
        root.destroy()


def append_result(row):
    os.makedirs(WORK_DIR, exist_ok=True)
    is_new = not os.path.exists(RESULT_CSV)
    with open(RESULT_CSV, "a", newline="", encoding="utf-8-sig") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_COLUMNS)
        if is_new:
            writer.writeheader()
        writer.writerow(row)


def save_raw(text, accession):
    """Keep the raw dump so a parser fix can be replayed without re-visiting PACS."""
    os.makedirs(RAW_DIR, exist_ok=True)
    name = "%s.txt" % (accession or "unknown")
    with open(os.path.join(RAW_DIR, name), "w", encoding="utf-8") as fh:
        fh.write(text)


def main():
    ap = argparse.ArgumentParser(description="Parse a DICOM header dump into sheet columns")
    ap.add_argument("--file", help="read header text from this file instead of the clipboard")
    ap.add_argument("--stdin", action="store_true", help="read header text from stdin")
    ap.add_argument("--inspect", action="store_true",
                    help="print only the field labels detected (no values) - safe to share")
    ap.add_argument("--dry-run", action="store_true", help="parse and print, do not append")
    args = ap.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8", errors="replace") as fh:
            text = fh.read()
    elif args.stdin:
        text = sys.stdin.read()
    else:
        text = read_clipboard()

    if not text.strip():
        print("ERROR: 沒有取得任何檔頭文字（剪貼簿是空的？）")
        return 2

    fields, detected = parse_header(text)

    if args.inspect:
        print("偵測到 %d 行可辨識欄位，共 %d 個不重複標籤：" % (len(detected), len(set(d[0] for d in detected))))
        seen = set()
        for field, label in detected:
            if field in seen:
                continue
            seen.add(field)
            print("  %-24s <- 原標籤 %r" % (field, label))
        missing = [k for k in ("StudyDate", "AccessionNumber", "Manufacturer",
                               "ManufacturerModelName", "PatientSex", "Rows", "Columns")
                   if k not in fields]
        if missing:
            print("未偵測到：%s" % ", ".join(missing))
        print("（--inspect 只印標籤，不印任何病人資料值）")
        return 0

    row, problems = to_row(fields)

    print("解析結果：")
    for col in OUTPUT_COLUMNS:
        print("  %-16s %s" % (col, row[col] or "(空)"))
    if problems:
        print("需注意：")
        for p in problems:
            print("  - %s" % p)

    if args.dry_run:
        print("(dry-run，未寫入 result.csv)")
        return 1 if problems else 0

    save_raw(text, row["AccessionNumber"])
    append_result(row)
    print("已追加至 %s" % RESULT_CSV)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
