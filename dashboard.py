import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv(r"D:\Games\UAC_Project\HHS_Unaccompanied_Alien_Children_Program.csv")

# Cleaning
df['Date'] = pd.to_datetime(df['Date'])
numeric_cols = [
    'Children apprehended and placed in CBP custody*',
    'Children in CBP custody',
    'Children transferred out of CBP custody',
    'Children in HHS Care',
    'Children discharged from HHS Care'
]

for col in numeric_cols:
    df[col] = df[col].astype(str).str.replace(',', '').astype(float)

df = df.sort_values('Date')

# Feature Engineering
df['Total_System_Load'] = df['Children in CBP custody'] + df['Children in HHS Care']
df['Net_Intake'] = df['Children transferred out of CBP custody'] - df['Children discharged from HHS Care']
df['Backlog_Indicator'] = df['Net_Intake'].rolling(7).sum()
 
# Title
st.title("UAC System Capacity & Care Load Analytics Dashboard")
 
# Date filter
start_date, end_date = st.date_input(
    "Select Date Range",
    [df['Date'].min(), df['Date'].max()]
)

filtered = df[(df['Date'] >= pd.to_datetime(start_date)) & 
               (df['Date'] <= pd.to_datetime(end_date))]
 
 # KPI Cards
col1, col2, col3, col4, col5 = st.columns(5)
 
col1.metric("Total Children Under Care", int(filtered['Total_System_Load'].iloc[-1]))
col2.metric("Avg Net Intake", round(filtered['Net_Intake'].mean(),2))
col3.metric("Care Load Volatility", round(filtered['Total_System_Load'].std(),2))
col4.metric("Backlog Rate", round(filtered['Backlog_Indicator'].mean(),2))
 
discharge_ratio = (
     filtered['Children discharged from HHS Care'].sum() /
     filtered['Children transferred out of CBP custody'].sum()
 )
col5.metric("Discharge Offset Ratio", round(discharge_ratio,2))

# ============================
# Visual Analytics
# ============================

st.subheader("📊 System Capacity & Backlog Trends")

fig, ax = plt.subplots(figsize=(12,5))

ax.plot(filtered['Date'], filtered['Total_System_Load'], label="Total System Load", linewidth=2)
ax.plot(filtered['Date'], filtered['Backlog_Indicator'], label="Backlog Indicator", linewidth=2)

ax.set_xlabel("Date")
ax.set_ylabel("Children Count")
ax.set_title("UAC System Load vs Backlog Trend")
ax.legend()
ax.grid(True)

st.pyplot(fig)

# ----------------------------

st.subheader("📈 Net Intake Trend")

st.line_chart(
    filtered.set_index('Date')[['Net_Intake']]
)
# ============================
# Smart Insights Engine
# ============================

st.subheader("🧠 Smart System Insights")

latest = filtered.iloc[-1]

alerts = []

# 1. System Load Risk
if latest['Total_System_Load'] > filtered['Total_System_Load'].mean():
    alerts.append("🔴 System Load is above average → Risk of capacity stress")

# 2. Backlog Risk
if latest['Backlog_Indicator'] > filtered['Backlog_Indicator'].mean():
    alerts.append("🟠 Backlog trend rising → Possible shelter overcrowding risk")

# 3. Intake Pressure
if latest['Net_Intake'] > 0:
    alerts.append("🔺 Positive Net Intake → More children entering than exiting system")

# 4. Discharge Efficiency
if discharge_ratio < 1:
    alerts.append("🟡 Discharge efficiency low → Slow system clearance rate")

# 5. Volatility Risk
if filtered['Total_System_Load'].std() > filtered['Total_System_Load'].mean() * 0.15:
    alerts.append("⚠ High volatility in system load → Unstable operational planning")

# Display Insights
if alerts:
    for a in alerts:
        st.warning(a)
else:
    st.success("✅ System operating within stable parameters")

# Summary Box
st.info(f"""
📊 **System Summary**
- Current Load: {int(latest['Total_System_Load'])}
- Avg Load: {int(filtered['Total_System_Load'].mean())}
- Current Net Intake: {round(latest['Net_Intake'],2)}
- Backlog Indicator: {round(latest['Backlog_Indicator'],2)}
- Discharge Efficiency: {round(discharge_ratio,2)}
""")
# ============================
# Auto PDF Report Generator
# ============================

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

st.subheader("📄 Auto Report Generator")

if st.button("📥 Generate PDF Report"):

    file_name = f"UAC_Analytics_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    c = canvas.Canvas(file_name, pagesize=A4)
    width, height = A4

    y = height - 50

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "UAC System Capacity & Care Load Analytics Report")
    y -= 30

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    y -= 40

    # KPIs
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Key Performance Indicators")
    y -= 20

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Total Children Under Care: {int(latest['Total_System_Load'])}")
    y -= 15
    c.drawString(50, y, f"Average Net Intake: {round(filtered['Net_Intake'].mean(),2)}")
    y -= 15
    c.drawString(50, y, f"Care Load Volatility Index: {round(filtered['Total_System_Load'].std(),2)}")
    y -= 15
    c.drawString(50, y, f"Backlog Accumulation Rate: {round(filtered['Backlog_Indicator'].mean(),2)}")
    y -= 15
    c.drawString(50, y, f"Discharge Offset Ratio: {round(discharge_ratio,2)}")
    y -= 30

    # Insights
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "System Insights")
    y -= 20

    c.setFont("Helvetica", 10)

    if alerts:
        for a in alerts:
            c.drawString(50, y, f"- {a}")
            y -= 15
    else:
        c.drawString(50, y, "- System operating within stable parameters")

    y -= 30

    # Summary
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "System Summary")
    y -= 20

    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Current Load: {int(latest['Total_System_Load'])}")
    y -= 15
    c.drawString(50, y, f"Average Load: {int(filtered['Total_System_Load'].mean())}")
    y -= 15
    c.drawString(50, y, f"Current Net Intake: {round(latest['Net_Intake'],2)}")
    y -= 15
    c.drawString(50, y, f"Backlog Indicator: {round(latest['Backlog_Indicator'],2)}")
    y -= 15
    c.drawString(50, y, f"Discharge Efficiency: {round(discharge_ratio,2)}")

    # Footer
    y -= 40
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(50, y, "Generated by UAC Analytics Dashboard | Internship Project | Anshul Ruhela")

    c.save()

    st.success(f"✅ PDF Report Generated: {file_name}")


 
 # Charts
st.subheader("System Load Trend")
st.line_chart(filtered.set_index('Date')['Total_System_Load'])
 
st.subheader("Net Intake Pressure")
st.line_chart(filtered.set_index('Date')['Net_Intake'])
 
st.subheader("Backlog Accumulation")
st.line_chart(filtered.set_index('Date')['Backlog_Indicator'])
