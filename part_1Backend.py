from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import re


app = FastAPI(title="Medical Report Processor API", version="1.0")


def initialize_database():
    """Create the reports table if it doesn't exist yet."""
    connection = sqlite3.connect("reports.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_text TEXT NOT NULL,
            detected_drug TEXT,
            adverse_events TEXT,
            severity_level TEXT,
            outcome TEXT
        )
    """)
    connection.commit()
    connection.close()

initialize_database()


class ReportSubmission(BaseModel):
    report: str


DRUG_LIST = [
    "arvs", "tenofovir", "lamivudine", "efavirenz", "dolutegravir", "abacavir",
    "paracetamol", "aspirin", "amoxicillin"
]

HIV_EVENTS = ["weight loss", "fever", "night sweats", "fatigue", "diarrhea"]
COMMON_EVENTS = ["nausea", "headache", "vomiting", "rash", "dizziness"]

SEVERITY_LEVELS = ["mild", "moderate", "severe"]
OUTCOME_KEYWORDS = ["recovered", "ongoing", "fatal"]


OUTCOME_TRANSLATIONS = {
    "recovered": "rétabli",
    "ongoing": "en cours",
    "fatal": "fatal"
}


def find_drug(report_text: str) -> str:
    """Return the first known drug found in the report, or 'Not specified'."""
    text_lower = report_text.lower()
    for drug in DRUG_LIST:
        if re.search(rf"\b{drug}\b", text_lower):
            return drug
    return "Not specified"

def find_adverse_events(report_text: str) -> list:
    """Return a list of detected adverse events mentioned in the report."""
    events_found = []
    text_lower = report_text.lower()
    for event in HIV_EVENTS + COMMON_EVENTS:
        if event in text_lower:
            events_found.append(event)
    return events_found

def find_severity(report_text: str) -> str:
    """Detect severity level from the report text."""
    text_lower = report_text.lower()
    for level in SEVERITY_LEVELS:
        if level in text_lower:
            return level
    return "not mentioned"

def find_outcome(report_text: str) -> dict:
    """Detect outcome and return both English and French translations."""
    text_lower = report_text.lower()
    outcome_detected = "not mentioned"
    for keyword in OUTCOME_KEYWORDS:
        if keyword in text_lower:
            outcome_detected = keyword
            break
    return {
        "english": outcome_detected,
        "french": OUTCOME_TRANSLATIONS.get(outcome_detected, "non traduit")
    }

def save_report(report_text: str, drug: str, adverse_events: list, severity: str, outcome: dict) -> int:
    """Save the processed report to the database and return its ID."""
    connection = sqlite3.connect("reports.db")
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO reports (report_text, detected_drug, adverse_events, severity_level, outcome)
        VALUES (?, ?, ?, ?, ?)
    """, (report_text, drug, ", ".join(adverse_events), severity, outcome['english']))
    report_id = cursor.lastrowid
    connection.commit()
    connection.close()
    return report_id


@app.post("/process-report")
def process_report(submission: ReportSubmission):
    """
    Process a medical report:
    - Detect drugs, adverse events, severity, and outcome
    - Return structured information with outcome in English and French
    """
    report_text = submission.report.strip()

    detected_drug = find_drug(report_text)
    adverse_events_found = find_adverse_events(report_text)
    severity_level = find_severity(report_text)
    outcome_info = find_outcome(report_text)

    report_id = save_report(report_text, detected_drug, adverse_events_found, severity_level, outcome_info)

    return {
        "id": report_id,
        "report_text": report_text,
        "drug": detected_drug,
        "adverse_events": adverse_events_found,
        "severity": severity_level,
        "outcome": outcome_info
    }

@app.get("/reports")
def get_all_reports():
    """
    Retrieve all processed reports with outcome translated in French.
    Reports are returned in reverse chronological order (latest first).
    """
    connection = sqlite3.connect("reports.db")
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id, report_text, detected_drug, adverse_events, severity_level, outcome
        FROM reports ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    connection.close()

    reports = []
    for row in rows:
        reports.append({
            "id": row[0],
            "report_text": row[1],
            "drug": row[2],
            "adverse_events": row[3].split(", ") if row[3] else [],
            "severity": row[4],
            "outcome": {
                "english": row[5],
                "french": OUTCOME_TRANSLATIONS.get(row[5].lower(), "non traduit")
            }
        })
    return reports
