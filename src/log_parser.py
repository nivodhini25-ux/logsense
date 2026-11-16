from datetime import datetime
from datetime import datetime
def read_log_file(file_path):
    """
    Read a log file and return its lines.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        return [line.strip() for line in lines]

    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
        return []

    except OSError as error:
        print(f"Error reading file: {error}")
        return []

def parse_log_line(line):
    """
    Convert a log line into structured data.
    """
    parts = line.split(" ", 3)

    if len(parts) < 4:
        return None

    timestamp = parts[0] + " " + parts[1]
    try:
        datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    level = parts[2]
    if level not in ["INFO", "WARNING", "ERROR", "DEBUG"]:
     return None
    message = parts[3]
    if not message.strip():
     return None

    return {
        "timestamp": timestamp,
        "level": level,
        "message": message
    }
def parse_log_file(file_path):
    lines = read_log_file(file_path)

    parsed_logs = []

    for line in lines:
        parsed_entry = parse_log_line(line)

        if parsed_entry is not None:
            parsed_logs.append(parsed_entry)

    return parsed_logs