import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
from datetime import datetime
import json
import os

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

def save_user_data(user_data):
    """Save user data and preferences to Google Sheets"""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        client = gspread.authorize(creds)

        # Open the same spreadsheet
        sheet_url = "https://docs.google.com/spreadsheets/d/1LW-TpBjX1mK1JT-kraWZ5g5D6ERD_PszqG6qucVYE3s/edit"
        spreadsheet = client.open_by_url(sheet_url)
        
        # Try to open existing "User Data" sheet, or create new one
        try:
            worksheet = spreadsheet.worksheet("User Data")
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title="User Data", rows="1000", cols="20")
            # Add headers
            headers = [
                "Timestamp", "Name", "Phone", "Gender", "Category", "State", 
                "Degrees", "Branches", "JEE Rank", "NITs Found", "IIITs Found"
            ]
            worksheet.append_row(headers)

        # Prepare data row
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row_data = [
            timestamp,
            user_data['name'],
            user_data['phone'],
            user_data['gender'],
            user_data['category'],
            user_data['state'],
            user_data['degrees'],
            user_data['branches'],
            str(user_data['rank']),
            str(user_data['nit_count']),
            str(user_data['iiit_count'])
        ]
        
        # Append the row
        worksheet.append_row(row_data)
        
    except Exception as e:
        raise Exception(f"Failed to save user data: {str(e)}")

def save_user_chat_json(user_data, nits_results, iiits_results):
    """Save complete user chat data to JSON file in project folder"""
    try:
        # Create chat data structure
        chat_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_info": {
                "name": user_data['name'],
                "phone": user_data['phone'],
                "gender": user_data['gender'],
                "category": user_data['category'],
                "state": user_data['state'],
                "degrees": user_data['degrees'].split(', ') if isinstance(user_data['degrees'], str) else user_data['degrees'],
                "branches": user_data['branches'].split(', ') if isinstance(user_data['branches'], str) else user_data['branches'],
                "jee_rank": user_data['rank']
            },
            "recommendations": {
                "nits": {
                    "count": user_data['nit_count'],
                    "colleges": nits_results.to_dict('records') if not nits_results.empty else []
                },
                "iiits": {
                    "count": user_data['iiit_count'],
                    "colleges": iiits_results.to_dict('records') if not iiits_results.empty else []
                }
            },
            "filters_applied": {
                "college_state_filter": True,
                "quota_logic": "Same state: HS only, Different state: OS only",
                "sorting": "Close rank ascending"
            }
        }
        
        # Create filename with timestamp and user name
        safe_name = "".join(c for c in user_data['name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"user_chat_{safe_name}_{timestamp_str}.json"
        
        # Save to project folder
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(chat_data, f, indent=2, ensure_ascii=False)
        
        return filename
        
    except Exception as e:
        raise Exception(f"Failed to save chat JSON: {str(e)}")
