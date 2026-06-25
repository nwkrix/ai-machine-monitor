#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 20:19:37 2026

@author: Christian Nwachioma
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
st.set_page_config(page_title="Industrial AI Monitor", layout="wide")

import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

import plotly.graph_objects as go
import plotly.graph_objects as go



DATABASE = "machine_database.db"


# ------------------------------------------------
# DATA LOADER (define FIRST)
# ------------------------------------------------
def load_data():

    conn = sqlite3.connect(DATABASE)

    df = pd.read_sql("SELECT * FROM machine_anomaly_results", conn)

    # SAFE RUL LOAD
    try:
        rul = pd.read_sql("SELECT * FROM machine_rul_results", conn)

        df = df.merge(
            rul[["timestamp", "rul_hours"]],
            on="timestamp",
            how="left"
        )

    except:
        df["rul_hours"] = None

    conn.close()

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


# ------------------------------------------------
# LOAD DATA (AFTER FUNCTION EXISTS)
# ------------------------------------------------
df = load_data()

# --------------------------------
# Header
# --------------------------------

st.title(
    "AI-Assisted Industrial Machine Monitoring Dashboard"
)


st.caption(
    "Simulated Industry 4.0 telemetry pipeline with ML anomaly detection"
)






def health_gauge(value):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': "Machine Health Score"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkgreen"},
            'steps': [
                {'range': [0, 50], 'color': "red"},
                {'range': [50, 75], 'color': "orange"},
                {'range': [75, 90], 'color': "yellow"},
                {'range': [90, 100], 'color': "green"},
            ],
        }
    ))
    return fig

# --------------------------------
# Load machine + AI results
# --------------------------------




def rul_gauge(value):

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': "Remaining Useful Life (hrs)"},
        gauge={
            'axis': {'range': [0, 200]},
            'bar': {'color': "blue"},
            'steps': [
                {'range': [0, 50], 'color': "red"},
                {'range': [50, 120], 'color': "orange"},
                {'range': [120, 200], 'color': "green"},
            ],
        }
    ))

    return fig

# df = load_data()










# --------------------------------
# KPI Section
# --------------------------------


total_anomalies = len(
    df[
        df.condition=="ANOMALY"
    ]
)


fault_count = len(
    df[
        df.fault_code!="NONE"
    ]
)


machine_status = (

    "WARNING"

    if total_anomalies > 0

    else

    "NORMAL"

)



c1,c2,c3,c4,c5 = st.columns(5)



c1.metric(
    "Health Score",
    f"{df.health_score.mean():.1f}%"
)


c2.metric(
    "Avg Temperature",
    f"{df.temperature_C.mean():.1f} °C"
)


c3.metric(
    "Fault Events",
    fault_count
)


c4.metric(
    "AI Anomalies",
    total_anomalies
)


c5.metric(
    "Machine Status",
    machine_status
)




# --------------------------------
# Sensor trends
# --------------------------------


st.subheader(
    "Machine Sensor Trends"
)


fig, ax = plt.subplots(
    figsize=(10,4)
)


ax.plot(
    df.timestamp,
    df.temperature_C,
    label="Temperature"
)


ax.plot(
    df.timestamp,
    df.motor_current_A,
    label="Motor Current"
)


ax.set_xlabel(
    "Time"
)


ax.legend()


st.pyplot(fig)



# --------------------------------
# AI diagnostics
# --------------------------------


st.subheader(
    "AI Detected Anomalies"
)



anomaly_df = (

    df[
        df.condition=="ANOMALY"
    ]

    .sort_values(
        "anomaly_score"
    )

)



st.dataframe(

    anomaly_df[
        [
        "timestamp",
        "fault_code",
        "severity",
        "diagnostic_reason",
        "recommended_action"
        ]

    ],

    use_container_width=True

)



# --------------------------------
# Fault distribution
# --------------------------------


st.subheader(
    "Fault Distribution"
)



faults = (

    df.fault_code
    .value_counts()

)


st.bar_chart(
    faults
)



# --------------------------------
# Health monitoring
# --------------------------------


st.subheader(
    "Machine Health Trend"
)



st.line_chart(

    df.set_index(
        "timestamp"
    )
    [
     "health_score"
    ]

)



# --------------------------------
# Latest telemetry
# --------------------------------


st.subheader(
    "Latest Machine Telemetry"
)



st.dataframe(

    df.tail(20),

    use_container_width=True

)

st.subheader("Machine Health Overview")

col1, col2 = st.columns([2, 3])

with col1:
    st.metric(
        "Avg Health Score",
        f"{df.health_score.mean():.1f}%"
    )

with col2:
    st.plotly_chart(
        health_gauge(df.health_score.mean()),
        use_container_width=True
    )

#New section
st.subheader("Anomaly Timeline")
anomaly_df = df[df["condition"] == "ANOMALY"].copy()
anomaly_df = anomaly_df.sort_values("timestamp")

fig, ax = plt.subplots(figsize=(10, 3))

ax.scatter(
    anomaly_df["timestamp"],
    anomaly_df["temperature_C"],
    color="red",
    label="Anomaly Events"
)

ax.plot(
    df["timestamp"],
    df["temperature_C"],
    alpha=0.3,
    label="Temperature Baseline"
)

ax.set_ylabel("Temperature (C)")
ax.legend()

st.pyplot(fig)


# section ~
df["anomaly_flag"] = df["condition"].map({"NORMAL": 0, "ANOMALY": 1})
st.subheader("System Anomaly Heatmap (Simplified)")

st.line_chart(
    df.set_index("timestamp")["anomaly_flag"]
)

# new KPI row
c1,c2,c3,c4,c5,c6 = st.columns(6)

c1.metric("Health", f"{df.health_score.mean():.1f}%")
c2.metric("Anomalies", len(df[df.condition=="ANOMALY"]))
c3.metric("Faults", len(df[df.fault_code!="NONE"]))
c4.metric("Status", "WARNING")
c5.metric("Avg Temp", f"{df.temperature_C.mean():.1f}")
c6.metric("RUL", f"{df.rul_hours.mean():.1f} hrs")


# RUL Gauge Visual
st.subheader("Remaining Useful Life")


rul_value = df["rul_hours"].dropna().mean()

if pd.isna(rul_value):
    rul_value = 0.0

st.plotly_chart(rul_gauge(float(rul_value)))




# Upgradwe anomaly timeline
st.subheader("Anomaly Timeline")

anom = df[df.condition == "ANOMALY"]

fig, ax = plt.subplots(figsize=(10,3))

ax.plot(df.timestamp, df.temperature_C, alpha=0.3)
ax.scatter(
    anom.timestamp,
    anom.temperature_C,
    color="red",
    label="Anomaly"
)

ax.legend()

st.pyplot(fig)















