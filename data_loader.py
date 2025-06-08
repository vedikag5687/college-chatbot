import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
from datetime import datetime
import os
import json

def load_sheets():
    """Load data from Google Sheets with improved column cleaning"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)

    client = gspread.authorize(creds)

    sheet_url = "https://docs.google.com/spreadsheets/d/1LW-TpBjX1mK1JT-kraWZ5g5D6ERD_PszqG6qucVYE3s/edit"
    spreadsheet = client.open_by_url(sheet_url)
    sheet_names = ["NITs Round 5", "IIITs Round 5", "IITs Round 5"]

    data = {}
    for name in sheet_names:
        try:
            worksheet = spreadsheet.worksheet(name)
            df = pd.DataFrame(worksheet.get_all_records())

            print(f"[DEBUG] Original columns in '{name}':", df.columns.tolist())
            print(f"[DEBUG] Original shape: {df.shape}")
            
            # Clean column names to match your Google Sheet structure
            df.columns = df.columns.str.strip().str.lower()
            
            # Map column names based on your sheet structure
            column_mapping = {
                'open rank': 'open rank',
                'close rank': 'close rank', 
                'college name': 'college name',
                'college state': 'college state',
                'branch': 'branch',
                'degree': 'degree',
                'quota': 'quota',
                'gender': 'gender'
            }
            
            # Rename columns if they exist
            existing_mapping = {k: v for k, v in column_mapping.items() if k in df.columns}
            df = df.rename(columns=existing_mapping)

            print(f"[DEBUG] Cleaned columns in '{name}':", df.columns.tolist())
            
            # Ensure we have the essential columns
            if 'close rank' not in df.columns:
                print(f"[ERROR] 'close rank' column not found in {name}")
                print(f"Available columns: {df.columns.tolist()}")
                continue
                
            if 'college name' not in df.columns:
                print(f"[ERROR] 'college name' column not found in {name}")
                print(f"Available columns: {df.columns.tolist()}")
                continue
            
            # Clean and convert close rank to numeric
            df['close rank'] = pd.to_numeric(df['close rank'], errors='coerce')
            
            # Remove rows with invalid close rank
            original_len = len(df)
            df = df.dropna(subset=['close rank'])
            df = df[df['close rank'] > 0]
            print(f"[DEBUG] Removed {original_len - len(df)} rows with invalid close rank")
            
            # Remove duplicate entries
            df = df.drop_duplicates()

            print(f"[DEBUG] Final shape for '{name}': {df.shape}")
            if not df.empty:
                print(f"[DEBUG] Close rank range: {df['close rank'].min()} - {df['close rank'].max()}")
                print(f"[DEBUG] Sample college names: {df['college name'].head(3).tolist()}")
            
            data[name.lower()] = df

        except Exception as e:
            print(f"[ERROR] Failed to load sheet '{name}': {str(e)}")
            continue

    return data

def save_user_data_locally(user_data, nits_df, iiits_df, format='json'):
    """Save user data and recommendations locally in the project folder"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Prepare complete user session data
        session_data = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'user_info': {
                'name': user_data['name'],
                'phone': user_data['phone'],
                'gender': user_data['gender'],
                'category': user_data['category'],
                'state': user_data['state'],
                'degrees': user_data['degrees'],
                'branches': user_data['branches'],
                'rank': user_data['rank']
            },
            'recommendations': {
                'nits': [],
                'iiits': []
            },
            'summary': {
                'total_nits': len(nits_df),
                'total_iiits': len(iiits_df),
                'total_colleges': len(nits_df) + len(iiits_df)
            }
        }
        
        # Add NIT recommendations
        if not nits_df.empty:
            for _, row in nits_df.iterrows():
                session_data['recommendations']['nits'].append({
                    'college_name': row['college name'],
                    'close_rank': int(row['close rank'])
                })
        
        # Add IIIT recommendations
        if not iiits_df.empty:
            for _, row in iiits_df.iterrows():
                session_data['recommendations']['iiits'].append({
                    'college_name': row['college name'],
                    'close_rank': int(row['close rank'])
                })
        
        # Save based on format preference
        if format.lower() == 'json':
            filename = f"user_session_{user_data['name'].replace(' ', '_')}_{timestamp}.json"
            filepath = os.path.join(os.getcwd(), filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            print(f"[INFO] Session data saved to: {filepath}")
            
        else:  # CSV format
            # Save user info
            user_info_df = pd.DataFrame([{
                'Name': user_data['name'],
                'Phone': user_data['phone'],
                'Gender': user_data['gender'],
                'Category': user_data['category'],
                'State': user_data['state'],
                'Degrees': user_data['degrees'],
                'Branches': user_data['branches'],
                'JEE_Rank': user_data['rank'],
                'NITs_Found': len(nits_df),
                'IIITs_Found': len(iiits_df),
                'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            
            filename = f"user_session_{user_data['name'].replace(' ', '_')}_{timestamp}.csv"
            filepath = os.path.join(os.getcwd(), filename)
            user_info_df.to_csv(filepath, index=False)
            print(f"[INFO] Session data saved to: {filepath}")
        
        # Also maintain a master log file
        master_filename = "master_user_log.json"
        master_filepath = os.path.join(os.getcwd(), master_filename)
        
        # Load existing master data or create new
        if os.path.exists(master_filepath):
            with open(master_filepath, 'r', encoding='utf-8') as f:
                master_data = json.load(f)
        else:
            master_data = {'sessions': []}
        
        # Add current session to master
        master_data['sessions'].append(session_data)
        
        # Save updated master data
        with open(master_filepath, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, indent=2, ensure_ascii=False)
        
        print(f"[INFO] Master log updated: {master_filepath}")
        print(f"[INFO] Total sessions logged: {len(master_data['sessions'])}")
        
        return filepath, master_filepath
        
    except Exception as e:
        print(f"[ERROR] Failed to save user data: {str(e)}")
        return None, None

# Keep this function for backward compatibility but make it save locally
def save_user_data_to_master_csv(user_data):
    """Save user data to local master CSV for backward compatibility"""
    try:
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
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
        
        master_csv_path = os.path.join(os.getcwd(), "master_user_data.csv")
        
        try:
            if os.path.exists(master_csv_path):
                existing_df = pd.read_csv(master_csv_path)
                new_row_df = pd.DataFrame([new_user_data])
                updated_df = pd.concat([existing_df, new_row_df], ignore_index=True)
            else:
                updated_df = pd.DataFrame([new_user_data])
            
            updated_df.to_csv(master_csv_path, index=False)
            print(f"[INFO] Master CSV updated: {master_csv_path}")
            
            return updated_df, master_csv_path
            
        except Exception as e:
            print(f"[ERROR] Failed to write master CSV: {str(e)}")
            return None, None
        
    except Exception as e:
        print(f"[ERROR] Failed to prepare CSV data: {str(e)}")
        return None, None

# Remove the Google Sheets creation functions since we're saving locally now
def create_user_csv_report(user_data, nits_df, iiits_df):
    """Create local CSV report"""
    return save_user_data_locally(user_data, nits_df, iiits_df, format='csv')

def create_user_sheet_and_save_data(user_data, nits_df, iiits_df):
    """Legacy function - now saves locally"""
    filepath, master_path = save_user_data_locally(user_data, nits_df, iiits_df)
    return "LOCAL_FILE_SAVED", filepath if filepath else "failed_report"