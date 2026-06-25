#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 23:23:01 2026

@author: nwx
"""

import pandas as pd
import sqlite3
import numpy as np

DATABASE = "machine_database.db"

def load():
    conn = sqlite3.connect(DATABASE)
    df = pd.read_sql("SELECT * FROM machine_anomaly_results", conn)
    conn.close()
    return df

def compute_rul(df):

    # Simple physics-inspired degradation model
    health = df["health_score"] / 100

    stress = (
        df["temperature_C"] * 0.3 +
        df["vibration_mm_s"] * 200 +
        df["motor_current_A"] * 2
    )

    stress_norm = (stress - stress.min()) / (stress.max() - stress.min() + 1e-9)

    df["rul_hours"] = (1 - stress_norm) * 200 * health

    return df

def save(df):
    conn = sqlite3.connect(DATABASE)
    df[["timestamp", "rul_hours"]].to_sql(
        "machine_rul_results",
        conn,
        if_exists="replace",
        index=False
    )
    conn.close()

if __name__ == "__main__":
    df = load()
    df = compute_rul(df)
    save(df)

    print("RUL pipeline complete")