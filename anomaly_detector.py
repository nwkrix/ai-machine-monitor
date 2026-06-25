#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI-assisted industrial machine anomaly detection
Author: Christian Nwachioma
"""

import pandas as pd
import sqlite3

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


DATABASE = "machine_database.db"


# ---------------------------------
# Load telemetry
# ---------------------------------

def load_data():

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql(
        "SELECT * FROM machine_telemetry",
        conn
    )

    conn.close()

    return df


# ---------------------------------
# Feature selection
# ---------------------------------

def prepare_features(df):

    return df[
        [
            "temperature_C",
            "vibration_mm_s",
            "pressure_PSI",
            "motor_current_A",
            "cycle_time_s"
        ]
    ]


# ---------------------------------
# Root cause logic (SINGLE SOURCE OF TRUTH)
# ---------------------------------

def diagnose(row):

    if row["temperature_C"] > 85:
        return "OVERHEAT_RISK"

    if row["vibration_mm_s"] > 0.2:
        return "MECHANICAL_FRICTION"

    if row["motor_current_A"] > 15:
        return "MOTOR_OVERLOAD"

    if row["cycle_time_s"] > 7:
        return "PROCESS_INEFFICIENCY"

    return "NORMAL_VARIATION"


# ---------------------------------
# Recommendation engine
# ---------------------------------

def recommend(reason):

    mapping = {
        "OVERHEAT_RISK": "Check cooling system immediately",
        "MECHANICAL_FRICTION": "Inspect bearings and alignment",
        "MOTOR_OVERLOAD": "Reduce load or inspect motor",
        "PROCESS_INEFFICIENCY": "Optimize production cycle timing",
        "NORMAL_VARIATION": "Continue monitoring"
    }

    return mapping.get(reason, "Inspect system")


# ---------------------------------
# ML anomaly detection
# ---------------------------------

def detect_anomalies(df):

    print("Training anomaly detection model...\n")

    X = prepare_features(df)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        contamination=0.02,
        random_state=42
    )

    model.fit(X_scaled)

    df["anomaly"] = model.predict(X_scaled)

    df["condition"] = df["anomaly"].map(
        lambda x: "ANOMALY" if x == -1 else "NORMAL"
    )

    df["anomaly_score"] = model.decision_function(X_scaled)

    # ---------------------------------
    # Severity (ML + rules hybrid)
    # ---------------------------------

    df["severity"] = "LOW"

    df.loc[df.condition == "ANOMALY", "severity"] = "MEDIUM"

    df.loc[
        (df.temperature_C > 95) |
        (df.vibration_mm_s > 0.3) |
        (df.motor_current_A > 18),
        "severity"
    ] = "HIGH"


    # ---------------------------------
    # Engineering diagnostics (THIS IS WHERE YOUR QUESTION WAS)
    # ---------------------------------

    df["diagnostic_reason"] = df.apply(diagnose, axis=1)

    df["recommended_action"] = df["diagnostic_reason"].apply(recommend)

    return df


# ---------------------------------
# Save results
# ---------------------------------

def save_results(df):

    conn = sqlite3.connect(DATABASE)

    df.to_sql(
        "machine_anomaly_results",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()


# ---------------------------------
# Report
# ---------------------------------

def report(df):

    print("\n===== AI DIAGNOSTIC REPORT =====")

    print("Total Samples:", len(df))

    print("\nDetected Anomalies:",
          len(df[df.condition == "ANOMALY"]))

    print("\nSeverity Distribution:")
    print(df.severity.value_counts())

    print("\nMost suspicious events:\n")

    print(
        df.sort_values("anomaly_score")[[
            "timestamp",
            "temperature_C",
            "vibration_mm_s",
            "motor_current_A",
            "fault_code",
            "condition",
            "severity",
            "diagnostic_reason",
            "recommended_action"
        ]].head(10)
    )


# ---------------------------------
# Main
# ---------------------------------

if __name__ == "__main__":

    df = load_data()

    df = detect_anomalies(df)

    save_results(df)

    report(df)

    print("\nAnomaly detection complete.")