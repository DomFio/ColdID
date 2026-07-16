# logger.py
# Logging system for ColdIQ
# Saves every application run to a JSON file in logs/
# Lets you track which emails got responses over time

import json
import os
from datetime import datetime
from config import LOG_PATH

def save_application_log(result: dict) -> str:
    """
    Takes the final pipeline result state and saves it as a log entry.
    Returns the path of the saved log file.
    """

    # Build a clean log entry from the pipeline result
    log_entry = {
        "date_applied": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "company": result.get("company_name", ""),
        "job_title": result.get("job_title", ""),
        "qualifier_score": result.get("qualifier_score", 0),
        "qualifier_reasoning": result.get("qualifier_reasoning", ""),
        "hiring_manager_name": result.get("hiring_manager_name", ""),
        "hiring_manager_title": result.get("hiring_manager_title", ""),
        "hiring_manager_linkedin": result.get("hiring_manager_linkedin", ""),
        "hiring_manager_email": result.get("hiring_manager_email", ""),
        "email_sent": result.get("draft_email", ""),
        "review_loops": result.get("review_loops", 0),
        "outcome": "pending"  # updated later when you hear back
    }

    # Create a unique filename based on company and timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    company_clean = result.get("company_name", "unknown").replace(" ", "_").lower()
    filename = f"{timestamp}_{company_clean}.json"
    filepath = os.path.join(LOG_PATH, filename)

    # Make sure logs/ directory exists
    os.makedirs(LOG_PATH, exist_ok=True)

    # Save the log entry
    with open(filepath, "w") as f:
        json.dump(log_entry, f, indent=2)

    return filepath


def load_all_logs() -> list:
    """
    Loads all application logs from the logs/ folder.
    Returns a list of log entries sorted by date, most recent first.
    """
    logs = []

    if not os.path.exists(LOG_PATH):
        return logs

    for filename in os.listdir(LOG_PATH):
        if filename.endswith(".json"):
            filepath = os.path.join(LOG_PATH, filename)
            with open(filepath, "r") as f:
                try:
                    log = json.load(f)
                    logs.append(log)
                except:
                    pass

    # Sort by date, most recent first
    logs.sort(key=lambda x: x.get("date_applied", ""), reverse=True)
    return logs


def update_outcome(company: str, job_title: str, outcome: str) -> bool:
    """
    Updates the outcome field of a log entry.
    outcome can be: 'pending', 'responded', 'no response', 'interview', 'rejected'
    Returns True if updated successfully.
    """
    if not os.path.exists(LOG_PATH):
        return False

    for filename in os.listdir(LOG_PATH):
        if filename.endswith(".json"):
            filepath = os.path.join(LOG_PATH, filename)
            with open(filepath, "r") as f:
                try:
                    log = json.load(f)
                except:
                    continue

            if log.get("company") == company and log.get("job_title") == job_title:
                log["outcome"] = outcome
                with open(filepath, "w") as f:
                    json.dump(log, f, indent=2)
                return True

    return False

def delete_log(company: str, job_title: str, date_applied: str) -> bool:
    """
    Deletes a specific log entry by matching company, job title, and date.
    Returns True if deleted successfully.
    """
    if not os.path.exists(LOG_PATH):
        return False

    for filename in os.listdir(LOG_PATH):
        if filename.endswith(".json"):
            filepath = os.path.join(LOG_PATH, filename)
            with open(filepath, "r") as f:
                try:
                    log = json.load(f)
                except:
                    continue

            if (log.get("company") == company and
                log.get("job_title") == job_title and
                log.get("date_applied") == date_applied):
                os.remove(filepath)
                return True

    return False