from src.log_parser import parse_log_line


def test_parse_valid_log_line():
    result = parse_log_line(
        "2026-10-29 09:03:00 ERROR Database connection failed"
    )

    assert result["level"] == "ERROR"
    assert result["message"] == "Database connection failed"


def test_invalid_timestamp():
    result = parse_log_line("invalid-date 09:03:00 ERROR Test error")

    assert result is None


def test_invalid_log_level():
    result = parse_log_line("2026-10-29 09:03:00 UNKNOWN Test error")

    assert result is None


def test_malformed_log_line():
    result = parse_log_line("Invalid log")

    assert result is None