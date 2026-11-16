from src.log_analyzer import (
    get_log_statistics,
    get_frequent_errors,
    get_error_timeline,
    detect_error_anomalies,
    get_investigation_suggestions,
    generate_incident_report
)


def test_log_statistics():
    result = get_log_statistics("data/sample.log")

    assert result["total_entries"] == 51
    assert result["errors"] == 16
    assert result["warnings"] == 7
    assert result["info"] == 22


def test_frequent_errors():
    result = get_frequent_errors("data/sample.log")

    assert result["Database connection failed"] == 8


def test_error_timeline():
    result = get_error_timeline("data/sample.log")

    assert result.max() == 6


def test_anomaly_detection():
    result = detect_error_anomalies("data/sample.log")

    assert result.max() == 6


def test_investigation_suggestions():
    result = get_investigation_suggestions("data/sample.log")

    assert len(result) == 4


def test_incident_report():
    result = generate_incident_report("data/sample.log")

    assert result["statistics"]["total_entries"] == 51
    assert len(result["investigation_suggestions"]) == 4