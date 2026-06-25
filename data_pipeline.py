#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 20:05:13 2026

@author: Christian Nwachioma
"""
import pandas as pd
import sqlite3
from datetime import datetime


# -----------------------------------------
# Configuration
# -----------------------------------------

INPUT_FILE = "machine_data.csv"
DATABASE_FILE = "machine_database.db"


# -----------------------------------------
# Load raw machine telemetry
# -----------------------------------------

def load_data():

    print("Loading machine telemetry...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Records loaded: {len(df)}")

    return df



# -----------------------------------------
# Data cleaning
# -----------------------------------------

def clean_data(df):

    print("Cleaning data...")

    # Convert timestamp
    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )


    # Remove duplicate records
    df = df.drop_duplicates()


    # Handle missing values

    df = df.fillna({
        "temperature_C": df["temperature_C"].mean(),
        "vibration_mm_s": df["vibration_mm_s"].mean(),
        "pressure_PSI": df["pressure_PSI"].mean(),
        "motor_current_A": df["motor_current_A"].mean(),
        "cycle_time_s": df["cycle_time_s"].mean()
    })


    return df



# -----------------------------------------
# Feature engineering
# -----------------------------------------

def create_features(df):

    print("Creating engineering features...")


    # Temperature risk indicator

    df["temperature_warning"] = (
        df["temperature_C"] > 80
    )


    # Vibration risk

    df["vibration_warning"] = (
        df["vibration_mm_s"] > 0.1
    )


    # Motor stress indicator

    df["motor_stress_index"] = (
        df["motor_current_A"] /
        df["motor_current_A"].mean()
    )


    # Overall health score

    df["health_score"] = (

        100
        - (df["temperature_warning"] * 10)
        - (df["vibration_warning"] * 20)

    )


    df["health_score"] = (
        df["health_score"]
        .clip(0,100)
    )


    return df



# -----------------------------------------
# Store into SQLite database
# -----------------------------------------

def store_database(df):

    print("Writing database...")

    conn = sqlite3.connect(
        DATABASE_FILE
    )


    df.to_sql(
        "machine_telemetry",
        conn,
        if_exists="replace",
        index=False
    )


    conn.close()



# -----------------------------------------
# Generate summary report
# -----------------------------------------

def generate_report(df):

    print("\n===== MACHINE SUMMARY =====")


    print(
        "Average Temperature:",
        round(
            df["temperature_C"].mean(),
            2
        ),
        "C"
    )


    print(
        "Average Vibration:",
        round(
            df["vibration_mm_s"].mean(),
            4
        ),
        "mm/s"
    )


    print(
        "Average Cycle Time:",
        round(
            df["cycle_time_s"].mean(),
            2
        ),
        "seconds"
    )


    print(
        "\nFault Distribution:"
    )


    print(
        df["fault_code"]
        .value_counts()
    )


    print(
        "\nAverage Health Score:",
        round(
            df["health_score"].mean(),
            2
        )
    )



# -----------------------------------------
# Main pipeline
# -----------------------------------------

if __name__ == "__main__":


    df = load_data()


    df = clean_data(df)


    df = create_features(df)


    store_database(df)


    generate_report(df)


    print(
        "\nPipeline complete."
    )


