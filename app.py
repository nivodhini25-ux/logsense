
import os
import tempfile

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from src.log_parser import parse_log_line
from src.log_analyzer import (
    get_log_statistics,
    get_frequent_errors,
    get_error_timeline,
    detect_error_anomalies,
    get_investigation_suggestions,
    generate_incident_report
)

# Page configuration
st.set_page_config(
    page_title="LogSense - The IT Error Detective",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 LogSense - The IT Error Detective")
st.write("Upload your application log file and investigate errors.")

# File upload
uploaded_file = st.file_uploader(
    "Upload your log file",
    type=["log", "txt"]
)

if uploaded_file is not None:

    file_bytes = uploaded_file.getvalue()

    # File size validation
    MAX_FILE_SIZE = 5 * 1024 * 1024

    if len(file_bytes) > MAX_FILE_SIZE:
        st.error("File is too large. Maximum allowed size is 5 MB.")
        st.stop()

    # Empty file validation
    if not file_bytes:
        st.warning("The uploaded log file is empty.")
        st.stop()

    # UTF-8 validation
    try:
        file_content = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        st.error(
            "Unable to read this file. "
            "Please upload a valid UTF-8 encoded log file."
        )
        st.stop()

    st.success("Log file uploaded successfully!")

    with st.expander("View Uploaded Log File"):
        st.text(file_content)

    # Analyse button
    if st.button("🔍 Analyse Logs", type="primary"):

        log_lines = file_content.splitlines()

        parsed_logs = [
            parse_log_line(line)
            for line in log_lines
        ]

        valid_logs = [
            log for log in parsed_logs
            if log is not None
        ]

        invalid_logs = [
            {"line_number": i + 1, "content": line}
            for i, line in enumerate(log_lines)
            if parse_log_line(line) is None
        ]

        if not valid_logs:
            st.warning("No valid log entries were found.")
            st.write("Please check the supported log format.")
            st.stop()

        # Create temporary file for existing analyzer functions
        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                suffix=".log",
                delete=False
            ) as temp_file:

                temp_file.write(file_content)
                temp_path = temp_file.name

            # Run existing analyzer functions
            statistics = get_log_statistics(temp_path)
            frequent_errors = get_frequent_errors(temp_path)
            timeline = get_error_timeline(temp_path)
            anomalies = detect_error_anomalies(temp_path)
            suggestions = get_investigation_suggestions(temp_path)
            incident_report = generate_incident_report(temp_path)

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

        # Prepare data
        df = pd.DataFrame(valid_logs)

        error_count = statistics["errors"]
        warning_count = statistics["warnings"]
        info_count = statistics["info"]
        invalid_count = len(invalid_logs)

        # Dashboard metrics
        st.header("📊 Log Analysis Dashboard")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Logs", len(log_lines))
        col2.metric("Errors", error_count)
        col3.metric("Warnings", warning_count)
        col4.metric("Invalid Logs", invalid_count)

        st.divider()

        # Parsed entries
        st.subheader("📋 Parsed Log Entries")
        st.dataframe(df, use_container_width=True)

        # Invalid entries
        if invalid_logs:
            with st.expander("View Invalid Log Entries"):
                st.dataframe(
                    pd.DataFrame(invalid_logs),
                    use_container_width=True
                )

        st.divider()

        # Severity distribution
        st.subheader("📌 Error and Log Severity Distribution")

        severity_counts = df["level"].value_counts()

        fig1, ax1 = plt.subplots()

        severity_counts.plot(
            kind="bar",
            ax=ax1
        )

        ax1.set_xlabel("Log Level")
        ax1.set_ylabel("Number of Entries")
        ax1.set_title("Log Severity Distribution")
        ax1.tick_params(axis="x", rotation=0)

        st.pyplot(fig1)
        plt.close(fig1)

        st.divider()

        # Frequent errors
        st.subheader("🔥 Most Frequent Errors")

        if not frequent_errors.empty:

            frequent_df = frequent_errors.head(10).reset_index()
            frequent_df.columns = ["Error Message", "Count"]

            st.dataframe(
                frequent_df,
                use_container_width=True
            )

            fig2, ax2 = plt.subplots()

            frequent_errors.head(10).sort_values().plot(
                kind="barh",
                ax=ax2
            )

            ax2.set_xlabel("Number of Occurrences")
            ax2.set_ylabel("Error Message")
            ax2.set_title("Most Frequent Errors")

            st.pyplot(fig2)
            plt.close(fig2)

        else:
            st.info("No ERROR entries were found.")

        st.divider()

        # Error timeline
        st.subheader("⏱️ Error Timeline")

        if not timeline.empty:

            fig3, ax3 = plt.subplots()

            timeline.plot(
                kind="line",
                marker="o",
                ax=ax3
            )

            ax3.set_xlabel("Time")
            ax3.set_ylabel("Number of Errors")
            ax3.set_title("Errors Over Time")

            plt.xticks(rotation=45)
            fig3.tight_layout()

            st.pyplot(fig3)
            plt.close(fig3)

        else:
            st.info("No error timeline is available.")

        st.divider()

        # Anomaly detection
        st.subheader("🚨 Anomaly Detection")

        if not anomalies.empty:

            st.warning("Possible unusual error activity detected.")

            anomaly_df = anomalies.reset_index()
            anomaly_df.columns = ["Time", "Error Count"]

            st.dataframe(
                anomaly_df,
                use_container_width=True
            )

        else:
            st.success("No unusual error spikes detected.")

        st.divider()

        # Investigation suggestions
        st.subheader("🛠️ Investigation Suggestions")

        if suggestions:

            for number, suggestion in enumerate(suggestions, start=1):
                st.write(f"{number}. {suggestion}")

        else:
            st.info("No specific investigation suggestions are available.")

        st.divider()

        # Incident report
        st.subheader("📄 Download Incident Report")

        report_text = f"""
LOGSENSE - THE IT ERROR DETECTIVE
INCIDENT ANALYSIS REPORT

Total Logs: {len(log_lines)}
Valid Logs: {len(valid_logs)}
Invalid Logs: {invalid_count}

Errors: {error_count}
Warnings: {warning_count}
INFO: {info_count}

FREQUENT ERRORS:
{frequent_errors.to_string() if not frequent_errors.empty else "No errors found"}

ANOMALIES:
{anomalies.to_string() if not anomalies.empty else "No anomalies detected"}

INVESTIGATION SUGGESTIONS:
{chr(10).join(suggestions) if suggestions else "No suggestions available."}

Note: Anomaly alerts and investigation suggestions are
decision-support indicators, not confirmed root causes.
"""

        col5, col6 = st.columns(2)

        col5.download_button(
            label="Download Incident Report",
            data=report_text,
            file_name="logsense_incident_report.txt",
            mime="text/plain"
        )

        col6.download_button(
            label="Download Parsed CSV",
            data=df.to_csv(index=False),
            file_name="logsense_parsed_logs.csv",
            mime="text/csv"
        )

        st.success("LogSense analysis completed successfully!")
