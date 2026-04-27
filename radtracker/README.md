# Rad Tracker

`radtracker/` contains local workflow tools for parsing hospital radiology CSV
exports, generating weekly workload reports, tracking selected follow-up cases,
and calculating mammography BI-RADS 0 quality metrics.

Most scripts are designed for local use on the hospital/work computer. Some
outputs contain patient identifiers and report text; do not commit generated
clinical data to GitHub.

## Encoding Rules

- Hospital CSV exports are CP950 encoded tab-separated files.
- AHK-related files are usually UTF-8 with BOM.
- Python, JSON, Markdown, and YAML files should normally remain UTF-8.
- Preserve the existing encoding when editing legacy files.

## Directory Layout

| Path | Purpose |
|---|---|
| `csv_input/` | Input CSV exports from the hospital reporting system. |
| `output/` | Generated reports, schedules, JSON summaries, and mammo tracker data. |
| `week_input.yaml` | Current weekly report input, including start/end remaining counts. |
| `week_input_template.yaml` | Template for a new weekly input file. |
| `history.json` | Accumulated weekly history used for trend review. |
| `schedule_prompt.md` | Prompt/reference text for schedule generation. |
| `weekly_review_prompt.md` | Prompt/reference text for weekly review. |
| `CLAUDE.md` | Historical workflow notes and implementation guidance. |

## Main Scripts

| Script | Purpose |
|---|---|
| `parse_csv.py` | Parse hospital CSV exports by ISO week, modality, weekday, points, and estimated work time. |
| `generate_report.py` | Generate weekly report data from CSV/XLSX plus `week_input.yaml`. |
| `update_history.py` | Append a generated weekly or midweek report into `history.json`. |
| `archive_week.py` | Move weekly output files into `output/Wxx/`. |
| `biopsy_tracker.py` | Track biopsy/FNA/interventional cases from CSV data. |
| `mammo_tracker.py` | Scan monthly mammography screening cases and calculate recall/PPV1 metrics. |
| `mammo_report_fetcher.py` | Fetch mammo reports from the hospital intranet and maintain BI-RADS 0 follow-up tracking. |

## Weekly Workflow

Typical weekly flow:

```powershell
python radtracker\generate_report.py --csv radtracker\csv_input\1150426_CL.csv --input radtracker\week_input.yaml -o radtracker\output\weekly_report.json
python radtracker\update_history.py radtracker\output\weekly_report.json
python radtracker\archive_week.py --week W17
```

Use `parse_csv.py` directly when you need an intermediate CSV summary or a
midweek check:

```powershell
python radtracker\parse_csv.py radtracker\csv_input\1150426_CL.csv --week 2026-W17 --output radtracker\output\w17_midweek.json
```

## Weekly Input

Start from `week_input_template.yaml` when creating a new week.

`week_input.yaml` stores:

- week ID and date range
- start remaining and end remaining counts
- expected thresholds
- manual notes or corrections

Keep this file UTF-8.

## Biopsy/FNA Tracking

`biopsy_tracker.py` scans all CSV files in `csv_input/`, groups rows by
`case_id`, and identifies biopsy/FNA/interventional procedures. It is also used
by `generate_report.py` to add follow-up reminders to the weekly report.

It reuses the same reporter ID convention as the rest of the tracker:

```text
A80748
```

## Mammo BI-RADS 0 Tracking

Mammo tracking has two steps:

1. Scan monthly screening mammography cases from CSV.
2. Fetch report text from the hospital intranet and parse BI-RADS categories.

```powershell
python radtracker\mammo_tracker.py --month 2026-04
python radtracker\mammo_report_fetcher.py --month 2026-04
python radtracker\mammo_tracker.py --month 2026-04 --stats
python radtracker\mammo_report_fetcher.py --list-birads0
```

Report fetching requires the hospital intranet, including hospital Wi-Fi. The
fetcher runs only during 21:00-03:00 to avoid adding load during daytime
clinical work.

### Mammo Output Files

| File | Purpose |
|---|---|
| `output/mammo_YYYYMM_cases.json` | Monthly order_code=91 screening mammography case list. |
| `output/mammo_YYYYMM_reports.json` | Fetched report text and parsed BI-RADS categories. |
| `output/mammo_YYYYMM_metrics.json` | Optional monthly metrics output. |
| `output/mammo_birads0.json` | Cumulative BI-RADS 0 follow-up tracker. |

### Manual Follow-Up Fields

Edit `output/mammo_birads0.json` manually after clinical follow-up.

Generated fields should usually remain unchanged:

- `case_id`
- `chart_no`
- `report_date`
- `recall_month`
- `followup_due`

Manual fields:

| Field | Values | Meaning |
|---|---|---|
| `status` | `pending`, `resolved` | Whether final outcome is available. |
| `outcome` | `null`, `benign`, `malignant`, `inadequate`, `lost_to_followup` | Final recall outcome used for PPV1 statistics. |
| `notes` | free text | Clinical context or follow-up plan. |

Use this pattern when follow-up is still ongoing:

```json
{
  "status": "pending",
  "outcome": null,
  "notes": "US BI-RADS 3, 6-month follow-up"
}
```

Use `resolved + outcome` only when the case should leave the pending list:

```json
{
  "status": "resolved",
  "outcome": "benign",
  "notes": "Follow-up US benign"
}
```

`inadequate` and `lost_to_followup` count as resolved but non-malignant for
PPV1. If a case still needs later follow-up, keep it `pending` with
`outcome: null` and explain the plan in `notes`.

## Metrics

Mammo metrics currently include:

- total monthly screening mammography cases
- BI-RADS 0 count
- recall rate
- resolved count
- malignant count
- PPV1
- pending count

Run:

```powershell
python radtracker\mammo_tracker.py --month 2026-04 --stats --output radtracker\output\mammo_202604_metrics.json
```

## Files Not To Commit

Do not commit generated clinical data or patient-level report text:

- `csv_input/*.csv`
- `output/mammo_*_reports.json`
- `output/mammo_birads0.json`
- manually exported report text such as `*.txt`
- any file containing patient identifiers, report text, or chart numbers

Source code, prompts, templates, and README files are generally safe to commit
after review.

## Common Checks

Compile-check Python scripts:

```powershell
python -m py_compile radtracker\parse_csv.py radtracker\generate_report.py radtracker\mammo_tracker.py radtracker\mammo_report_fetcher.py
```

If PowerShell shows Chinese mojibake, set UTF-8 output for the session:

```powershell
chcp 65001
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [System.Text.UTF8Encoding]::new()
```
