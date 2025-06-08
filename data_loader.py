import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
from datetime import datetime
import os

def load_sheets():
    """Load data from Google Sheets (this part stays the same for data loading)"""
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

def create_user_csv_report(user_data, nits_df, iiits_df):
    """Create CSV files for user data and recommendations"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"JEE_Recommendations_{user_data['name']}_{timestamp}"
        
        # Create user information DataFrame
        user_info_data = {
            'Field': [
                'Name', 'Phone', 'Gender', 'Category', 'Home State',
                'Selected Degrees', 'Selected Branches', 'JEE Mains Rank',
                'NITs Found', 'IIITs Found', 'Generated On'
            ],
            'Value': [
                user_data['name'],
                user_data['phone'],
                user_data['gender'],
                user_data['category'],
                user_data['state'],
                user_data['degrees'],
                user_data['branches'],
                str(user_data['rank']),
                str(user_data['nit_count']),
                str(user_data['iiit_count']),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
        }
        user_info_df = pd.DataFrame(user_info_data)
        
        # Create combined recommendations DataFrame
        combined_recommendations = []
        
        # Add NIT recommendations
        if not nits_df.empty:
            for idx, (_, row) in enumerate(nits_df.iterrows(), 1):
                combined_recommendations.append({
                    'S.No.': idx,
                    'Type': 'NIT',
                    'College Name': row['college name'],
                    'Close Rank': int(row['close rank']),
                    'Rank Difference': int(row['close rank']) - user_data['rank']
                })
        
        # Add IIIT recommendations
        if not iiits_df.empty:
            start_idx = len(combined_recommendations) + 1
            for idx, (_, row) in enumerate(iiits_df.iterrows(), start_idx):
                combined_recommendations.append({
                    'S.No.': idx,
                    'Type': 'IIIT',
                    'College Name': row['college name'],
                    'Close Rank': int(row['close rank']),
                    'Rank Difference': int(row['close rank']) - user_data['rank']
                })
        
        recommendations_df = pd.DataFrame(combined_recommendations)
        
        return user_info_df, recommendations_df, report_name
        
    except Exception as e:
        raise Exception(f"Failed to create CSV report: {str(e)}")

def save_user_data_to_master_csv(user_data):
    """Save user data to a master tracking CSV file and auto-update it"""
    try:
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create new user data entry
        new_user_data = {
            'Timestamp': timestamp_str,
            'Name': user_data['name'],
            'Phone': user_data['phone'],
            'Gender': user_data['gender'],
            'Category': user_data['category'],
            'State': user_data['state'],
            'Degrees': user_data['degrees'],
            'Branches': user_data['branches'],
            'JEE_Rank': user_data['rank'],
            'NITs_Found': user_data['nit_count'],
            'IIITs_Found': user_data['iiit_count']
        }
        
        # Define the master CSV file path
        master_csv_path = "master_user_data.csv"
        
        # Check if master CSV file exists
        if os.path.exists(master_csv_path):
            # Read existing data
            existing_df = pd.read_csv(master_csv_path)
            # Add new row
            new_row_df = pd.DataFrame([new_user_data])
            updated_df = pd.concat([existing_df, new_row_df], ignore_index=True)
        else:
            # Create new DataFrame if file doesn't exist
            updated_df = pd.DataFrame([new_user_data])
        
        # Save updated data back to CSV
        updated_df.to_csv(master_csv_path, index=False)
        
        return updated_df, master_csv_path
        
    except Exception as e:
        print(f"Warning: Could not update master CSV: {str(e)}")
        return None, None

def get_master_csv_download():
    """Get the master CSV file for download"""
    try:
        master_csv_path = "master_user_data.csv"
        if os.path.exists(master_csv_path):
            with open(master_csv_path, 'r') as f:
                return f.read()
        else:
            return None
    except Exception as e:
        print(f"Error reading master CSV: {str(e)}")
        return None

# Legacy function for backward compatibility
def create_user_sheet_and_save_data(user_data, nits_df, iiits_df):
    """Legacy function - now returns CSV data instead of Google Sheet"""
    user_info_df, recommendations_df, report_name = create_user_csv_report(user_data, nits_df, iiits_df)
    
    # Also save to master CSV
    save_user_data_to_master_csv(user_data)
    
    # Return a fake URL and the report name for compatibility
    return "CSV_REPORT_GENERATED", report_name