import pandas as pd

from src.log_parser import parse_log_file


def get_log_statistics(file_path):
    logs = parse_log_file(file_path)
    df = pd.DataFrame(logs)

    total_entries = len(df)

    if total_entries == 0:
        return {
            "total_entries": 0,
            "errors": 0,
            "warnings": 0,
            "info": 0,
            "invalid_entries": 0,
            "error_percentage": 0
        }

    errors = (df["level"] == "ERROR").sum()
    warnings = (df["level"] == "WARNING").sum()
    info = (df["level"] == "INFO").sum()

    return {
        "total_entries": total_entries,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "invalid_entries": 0,
        "error_percentage": (errors / total_entries) * 100
    }
def get_frequent_errors(file_path):
    logs = parse_log_file(file_path)

    error_messages = [
        log["message"]
        for log in logs
        if log["level"] == "ERROR"
    ]

    error_counts = pd.Series(error_messages).value_counts()

    return error_counts
def get_error_timeline(file_path):
    logs = parse_log_file(file_path)

    error_logs = [
        log for log in logs
        if log["level"] == "ERROR"
    ]

    df = pd.DataFrame(error_logs)

    if df.empty:
        return pd.Series(dtype="int64", name="count")

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    timeline = (
        df.set_index("timestamp")
        .resample("1min")
        .size()
    )

    return timeline
def detect_error_anomalies(file_path):
    timeline = get_error_timeline(file_path)

    if timeline.empty:
        return timeline

    average_errors = timeline.mean()
    threshold = average_errors * 2

    anomalies = timeline[timeline > threshold]

    return anomalies
def get_investigation_suggestions(file_path):
    frequent_errors = get_frequent_errors(file_path)

    suggestions = []

    for message, count in frequent_errors.items():
        if "Database" in message:
            suggestions.append(
                "Check database connectivity and connection settings."
            )
        elif "Payment" in message:
            suggestions.append(
                "Check the payment service and its API status."
            )
        elif "Authentication" in message:
            suggestions.append(
                "Check authentication credentials and access permissions."
            )
        elif "timed out" in message:
            suggestions.append(
                "Check network latency and service response times."
            )

    return list(dict.fromkeys(suggestions))
def generate_incident_report(file_path):
    statistics = get_log_statistics(file_path)
    frequent_errors = get_frequent_errors(file_path)
    anomalies = detect_error_anomalies(file_path)
    suggestions = get_investigation_suggestions(file_path)

    return {
        "statistics": statistics,
        "frequent_errors": frequent_errors.to_dict(),
        "anomalies": anomalies.to_dict(),
        "investigation_suggestions": suggestions
    }