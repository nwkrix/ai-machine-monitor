#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 22:50:11 2026

@author: Christian Nwachioma

Estimates:
    - Remaining Useful Life (RUL)
    - Failure probability trend
"""

import pandas as pd
import sqlite3
import numpy as np

DB = "machine_database.db"


def load_data():

    conn = sqlite3.connect(DB)

    df = pd.read_sql(
        "SELECT * FROM machine_telemetry",
        conn
    )

    conn.close()

    return df


def compute_rul(df):

    # Simple physics-inspired degradation model

    df["stress_index"] = (
        df["temperature_C"] * 0.4 +
        df["vibration_mm_s"] * 100 +
        df["motor_current_A"] * 2
    )

    df["health_score"] = 100 - df["stress_index"]

    df["health_score"] = df["health_score"].clip(0, 100)

    # RUL approximation (simple but interview-worthy)
    df["rul_hours"] = df["health_score"] * 2.5

    return df


def save(df):

    conn = sqlite3.connect(DB)

    df.to_sql(
        "machine_rul_results",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()


if __name__ == "__main__":

    df = load_data()
    df = compute_rul(df)
    save(df)

    print("\nRUL computation complete.")
