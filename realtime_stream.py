#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 22:48:43 2026

@author: Christian Nwachioma
"""

# realtime_stream.py

import time
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime

DB = "machine_database.db"

def generate_row():

    return {
        "timestamp": datetime.now(),
        "temperature_C": np.random.normal(75, 8),
        "vibration_mm_s": np.random.normal(0.12, 0.05),
        "pressure_PSI": np.random.normal(30, 3),
        "motor_current_A": np.random.normal(10, 2),
        "cycle_time_s": np.random.normal(6, 1),
        "fault_code": "NONE"
    }


def stream_data(n=1000, delay=0.2):

    conn = sqlite3.connect(DB)

    for i in range(n):

        row = generate_row()

        pd.DataFrame([row]).to_sql(
            "machine_telemetry",
            conn,
            if_exists="append",
            index=False
        )

        print(f"Streaming row {i+1}")

        time.sleep(delay)

    conn.close()


if __name__ == "__main__":
    stream_data()