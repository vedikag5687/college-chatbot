import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
from datetime import datetime

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

def create_user_sheet_and_save_data(user_data, nits_df, iiits_df):
    """Create a new Google Sheet for the user and save their data and recommendations"""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        client = gspread.authorize(creds)

        # Create a new spreadsheet with user's name and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sheet_title = f"JEE_Recommendations_{user_data['name']}_{timestamp}"
        
        # Create new spreadsheet
        spreadsheet = client.create(sheet_title)
        
        # Share with specified email addresses with editor access
        email_addresses = [
            "vidhig5687@gmail.com",
            "white.walter.here@gmail.com", 
            "aspirantssquare.official@gmail.com"
        ]
        
        for email in email_addresses:
            try:
                spreadsheet.share(email, perm_type='user', role='writer')
            except Exception as e:
                print(f"Warning: Could not share with {email}: {str(e)}")
        
        # Get the default worksheet and rename it to "User Information"
        user_info_sheet = spreadsheet.sheet1
        user_info_sheet.update_title("User Information")
        
        # Add user information headers and data
        user_headers = [
            "Field", "Value"
        ]
        user_info_sheet.append_row(user_headers)
        
        # Add user data rows
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_rows = [
            ["Timestamp", timestamp_str],
            ["Name", user_data['name']],
            ["Phone", user_data['phone']],
            ["Gender", user_data['gender']],
            ["Category", user_data['category']],
            ["Home State", user_data['state']],
            ["Selected Degrees", user_data['degrees']],
            ["Selected Branches", user_data['branches']],
            ["JEE Mains Rank", str(user_data['rank'])],
            ["NITs Found", str(user_data['nit_count'])],
            ["IIITs Found", str(user_data['iiit_count'])]
        ]
        
        for row in user_rows:
            user_info_sheet.append_row(row)
        
        # Create NIT Recommendations sheet
        if not nits_df.empty:
            nit_sheet = spreadsheet.add_worksheet(title="NIT Recommendations", rows=len(nits_df)+10, cols=10)
            
            # Add headers
            nit_headers = ["S.No.", "College Name", "Close Rank"]
            nit_sheet.append_row(nit_headers)
            
            # Add NIT data with serial numbers
            for idx, (_, row) in enumerate(nits_df.iterrows(), 1):
                nit_row = [str(idx), row['college name'], str(int(row['close rank']))]
                nit_sheet.append_row(nit_row)
        
        # Create IIIT Recommendations sheet
        if not iiits_df.empty:
            iiit_sheet = spreadsheet.add_worksheet(title="IIIT Recommendations", rows=len(iiits_df)+10, cols=10)
            
            # Add headers
            iiit_headers = ["S.No.", "College Name", "Close Rank"]
            iiit_sheet.append_row(iiit_headers)
            
            # Add IIIT data with serial numbers
            for idx, (_, row) in enumerate(iiits_df.iterrows(), 1):
                iiit_row = [str(idx), row['college name'], str(int(row['close rank']))]
                iiit_sheet.append_row(iiit_row)
        
        # Create a Chat/Notes sheet for future interactions
        chat_sheet = spreadsheet.add_worksheet(title="Chat_Notes", rows=100, cols=5)
        chat_headers = ["Timestamp", "User Message", "Bot Response", "Additional Notes", "Status"]
        chat_sheet.append_row(chat_headers)
        
        # Add initial entry
        initial_chat = [
            timestamp_str,
            f"User requested JEE recommendations with rank {user_data['rank']}",
            f"Provided {user_data['nit_count']} NIT and {user_data['iiit_count']} IIIT recommendations",
            "Initial recommendation request",
            "Completed"
        ]
        chat_sheet.append_row(initial_chat)
        
        return spreadsheet.url, sheet_title
        
    except Exception as e:
        raise Exception(f"Failed to create user sheet and save data: {str(e)}")

def save_user_data(user_data):
    """Legacy function - kept for backward compatibility"""
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