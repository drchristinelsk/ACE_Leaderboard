import streamlit as st
import pandas as pd
import os
import datetime
import streamlit.components.v1 as components


# Folder to store uploaded CSVs
UPLOAD_FOLDER = "submissions"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.set_page_config(page_title="Portfolio Leaderboard", layout="wide")

st.title("🏆 ACER Leaderboard")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload your IBKR CSV", type=["csv"])
if uploaded_file:
    file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"Uploaded and saved: {uploaded_file.name}")

# --- Helper Function to Extract NAV and Starting NAV ---
def extract_navs(file_path):
    ending_value = None
    starting_value = None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("Change in NAV,Data,Starting Value"):
                    starting_value = float(line.strip().split(",")[-1])
                if line.startswith("Change in NAV,Data,Ending Value"):
                    ending_value = float(line.strip().split(",")[-1])
    except Exception:
        pass
    return starting_value, ending_value

# --- Process All Submissions ---
data = []
for filename in os.listdir(UPLOAD_FOLDER):
    if filename.endswith(".csv"):
        student = os.path.splitext(filename)[0].title()
        path = os.path.join(UPLOAD_FOLDER, filename)
        start_nav, end_nav = extract_navs(path)
        if start_nav and end_nav:
            change_pct = ((end_nav - start_nav) / start_nav) * 100
            data.append({"Acer": student, "Gain (%)": round(change_pct, 2)})

# --- Display Leaderboard ---
if data:
    df = pd.DataFrame(data).sort_values(by="Gain (%)", ascending=False).reset_index(drop=True)

    def styled_table(df):
        styled_rows = []
        for idx, row in df.iterrows():
            rank_display = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else f"#{idx + 1}"
            styled_rows.append(f"""
                <tr>
                    <td style='color:white;padding:12px;text-align:center;font-size:24px;font-family:"Roboto", sans-serif'>{rank_display}</td>
                    <td style='color:#2B7FFF;padding:12px;font-size:24px;font-family:"Roboto", sans-serif'>{row['Acer']}</td>
                    <td style='color:#3cb371;padding:12px;text-align:right;font-size:24px;font-family:"Roboto", sans-serif'>{row['Gain (%)']}%</td>
                </tr>
            """)

        return f"""
        <link href="https://fonts.googleapis.com/css2?family=Roboto&display=swap" rel="stylesheet">
        <div style='background-color:#0d1b2a;padding: 20px; font-family:"Roboto", sans-serif;'>
            <table style='width:100%;border-collapse:collapse;background-color:#2c2c2c;border-radius:10px'>
                <thead>
                    <tr>
                        <th style='color:white;padding:12px;text-align:center;font-size:24px;font-family:"Roboto", sans-serif'>Rank</th>
                        <th style='color:white;padding:12px;font-size:24px;font-family:"Roboto", sans-serif'>Acer</th>
                        <th style='color:white;padding:12px;text-align:right;font-size:24px;font-family:"Roboto", sans-serif'>Gain (%)</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(styled_rows)}
                </tbody>
            </table>
        </div>
        """

    components.html(styled_table(df), height=600, scrolling=True)

    # Export to CSV
    df.index = df.index + 1
    df.index.name = "Rank"
    csv_export = df.to_csv().encode('utf-8')
    st.download_button(
        label="📥 Download Leaderboard as CSV",
        data=csv_export,
        file_name="portfolio_leaderboard.csv",
        mime='text/csv'
    )
else:
    st.warning("No valid submissions yet. Upload a CSV to get started.")
