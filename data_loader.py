import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st

def load_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)

    client = gspread.authorize(creds)

    sheet_url = "https://docs.google.com/spreadsheets/d/1LW-TpBjX1mK1JT-kraWZ5g5D6ERD_PszqG6qucVYE3s/edit"
    spreadsheet = client.open_by_url(sheet_url)
    sheet_names = ["NITs Round 5", "IIITs Round 5", "IITs Round 5"]

    data = {}
    for name in sheet_names:
        worksheet = spreadsheet.worksheet(name)
        df = pd.DataFrame(worksheet.get_all_records())

        # Clean column names
        df.columns = (
            df.columns
            .str.encode('ascii', 'ignore').str.decode('ascii')
            .str.strip()
            .str.lower()
            .str.replace(r'\s+', ' ', regex=True)
        )

        # Clean "close rank"
        df['close rank'] = pd.to_numeric(df['close rank'], errors='coerce')

        print(f"[DEBUG] Cleaned Columns in '{name}':", df.columns.tolist())
        data[name.lower()] = df.dropna(subset=['close rank'])

    return data
