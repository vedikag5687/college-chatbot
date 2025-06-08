import pandas as pd
import json
import os
from datetime import datetime

def filter_colleges(df, gender, category, rank, degrees, branches, state=None, is_nit=False):
    """Filter colleges with improved debugging and data validation"""
    
    # Make a copy to avoid modifying original dataframe
    df = df.copy()
    
    print(f"[DEBUG] Input dataframe shape: {df.shape}")
    print(f"[DEBUG] Available columns: {df.columns.tolist()}")
    
    # Clean and convert close rank to numeric
    df['close rank'] = pd.to_numeric(df['close rank'], errors='coerce')
    df = df.dropna(subset=['close rank'])
    
    print(f"[DEBUG] After removing invalid close ranks: {df.shape}")
    print(f"[DEBUG] Close rank range: {df['close rank'].min()} - {df['close rank'].max()}")
    
    # Debug: Check unique values in key columns
    print(f"[DEBUG] Unique genders: {df['gender'].unique()}")
    print(f"[DEBUG] Unique categories: {df['category'].unique()}")
    print(f"[DEBUG] User filters - Gender: {gender}, Category: {category}, Rank: {rank}")
    
    # Apply basic filters with case-insensitive matching
    # FIXED: Changed condition from >= to <= for close rank (students can get admitted if their rank is better than closing rank)
    basic_filters = (
        (df['gender'].str.lower().str.strip() == gender.lower().strip()) &
        (df['category'].str.lower().str.strip() == category.lower().strip()) &
        (df['close rank'] >= float(rank)) &  # Keep colleges where closing rank is higher than user rank
        (df['degree'].isin(degrees)) &
        (df['branch'].isin(branches))
    )
    
    df_filtered = df[basic_filters].copy()
    
    print(f"[DEBUG] After basic filters: {df_filtered.shape}")
    
    if df_filtered.empty:
        print("[DEBUG] No colleges found after basic filtering")
        return df_filtered[['college name', 'close rank']]
    
    # Debug: Show some sample filtered data
    print(f"[DEBUG] Sample filtered data:")
    print(df_filtered[['college name', 'close rank']].head())
    
    if is_nit and state:
        print(f"[DEBUG] Applying NIT quota filtering for state: {state}")
        
        # Apply quota filtering based on state matching
        def should_keep_row(row):
            college_state = str(row.get('college state', '')).lower().strip()
            user_state = state.lower().strip()
            quota = str(row.get('quota', '')).upper().strip()
            
            print(f"[DEBUG] College: {row.get('college name', 'N/A')[:30]}, State: {college_state}, Quota: {quota}, User State: {user_state}")
            
            if college_state == user_state:
                # For same state colleges, keep only HS (Home State) quota
                return quota == 'HS'
            else:
                # For different state colleges, keep only OS (Other State) quota
                return quota == 'OS'
        
        # Apply the quota filter
        quota_mask = df_filtered.apply(should_keep_row, axis=1)
        df_filtered = df_filtered[quota_mask].copy()
        
        print(f"[DEBUG] After quota filtering: {df_filtered.shape}")
        
        if df_filtered.empty:
            print("[DEBUG] No colleges found after quota filtering")
            return df_filtered[['college name', 'close rank']]
        
        # Create priority for sorting (same state colleges first, then different state)
        def assign_priority(row):
            college_state = str(row.get('college state', '')).lower().strip()
            user_state = state.lower().strip()
            
            if college_state == user_state:
                return 0  # Higher priority for same state colleges
            else:
                return 1  # Lower priority for different state colleges
        
        df_filtered['priority'] = df_filtered.apply(assign_priority, axis=1)
        
        # Sort by priority first, then by close rank (ascending)
        df_filtered = df_filtered.sort_values(by=['priority', 'close rank'])
        
        # Remove the priority column before returning
        df_filtered = df_filtered.drop('priority', axis=1)
        
    else:
        # For IIITs, just sort by close rank (ascending)
        df_filtered = df_filtered.sort_values(by='close rank')
    
    # Ensure close rank is integer for display
    df_filtered = df_filtered.copy()
    df_filtered['close rank'] = df_filtered['close rank'].astype(int)
    
    print(f"[DEBUG] Final filtered results: {df_filtered.shape}")
    if not df_filtered.empty:
        print(f"[DEBUG] Final close rank range: {df_filtered['close rank'].min()} - {df_filtered['close rank'].max()}")
        print(f"[DEBUG] Sample final results:")
        print(df_filtered[['college name', 'close rank']].head())
    
    # Return only college name and close rank columns (no index)
    return df_filtered[['college name', 'close rank']].reset_index(drop=True)

def save_user_data_locally(user_data, nits_df, iiits_df, format='json'):
    """Save user data and recommendations locally in JSON or CSV format"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Prepare complete user session data
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'user_info': {
                'name': user_data['name'],
                'phone': user_data['phone'],
                'gender': user_data['gender'],
                'category': user_data['category'],
                'state': user_data['state'],
                'degrees': user_data['degrees'].split(', ') if isinstance(user_data['degrees'], str) else user_data['degrees'],
                'branches': user_data['branches'].split(', ') if isinstance(user_data['branches'], str) else user_data['branches'],
                'rank': user_data['rank']
            },
            'recommendations': {
                'nits': {
                    'count': len(nits_df),
                    'colleges': nits_df.to_dict('records') if not nits_df.empty else []
                },
                'iiits': {
                    'count': len(iiits_df),
                    'colleges': iiits_df.to_dict('records') if not iiits_df.empty else []
                }
            },
            'summary': {
                'total_colleges_found': len(nits_df) + len(iiits_df),
                'nit_count': len(nits_df),
                'iiit_count': len(iiits_df)
            }
        }
        
        if format.lower() == 'json':
            # Save as JSON
            filename = f"user_session_{user_data['name'].replace(' ', '_')}_{timestamp}.json"
            filepath = os.path.join('.', filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            print(f"[INFO] User session saved as JSON: {filepath}")
            
        else:
            # Save as CSV (separate files)
            user_info_filename = f"user_info_{user_data['name'].replace(' ', '_')}_{timestamp}.csv"
            recommendations_filename = f"recommendations_{user_data['name'].replace(' ', '_')}_{timestamp}.csv"
            
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
                'Timestamp': datetime.now().isoformat()
            }])
            
            user_info_df.to_csv(user_info_filename, index=False)
            
            # Save recommendations
            recommendations_list = []
            
            # Add NITs
            for idx, (_, row) in enumerate(nits_df.iterrows(), 1):
                recommendations_list.append({
                    'S.No.': idx,
                    'Type': 'NIT',
                    'College Name': row['college name'],
                    'Close Rank': int(row['close rank'])
                })
            
            # Add IIITs
            start_idx = len(recommendations_list) + 1
            for idx, (_, row) in enumerate(iiits_df.iterrows(), start_idx):
                recommendations_list.append({
                    'S.No.': idx,
                    'Type': 'IIIT',
                    'College Name': row['college name'],
                    'Close Rank': int(row['close rank'])
                })
            
            if recommendations_list:
                recommendations_df = pd.DataFrame(recommendations_list)
                recommendations_df.to_csv(recommendations_filename, index=False)
            
            print(f"[INFO] User data saved as CSV: {user_info_filename}")
            print(f"[INFO] Recommendations saved as CSV: {recommendations_filename}")
        
        # Also maintain a master log
        master_log_file = "master_user_log.json"
        
        # Load existing master log or create new
        if os.path.exists(master_log_file):
            try:
                with open(master_log_file, 'r', encoding='utf-8') as f:
                    master_data = json.load(f)
            except:
                master_data = {"sessions": []}
        else:
            master_data = {"sessions": []}
        
        # Add current session to master log
        master_data["sessions"].append({
            "session_id": len(master_data["sessions"]) + 1,
            "timestamp": session_data["timestamp"],
            "user_name": user_data['name'],
            "user_phone": user_data['phone'],
            "rank": user_data['rank'],
            "total_recommendations": session_data["summary"]["total_colleges_found"],
            "filename": filename if format == 'json' else f"{user_info_filename}, {recommendations_filename}"
        })
        
        # Save updated master log
        with open(master_log_file, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, indent=2, ensure_ascii=False)
        
        print(f"[INFO] Master log updated: {master_log_file}")
        print(f"[INFO] Total sessions logged: {len(master_data['sessions'])}")
        
        return True, filepath if format == 'json' else [user_info_filename, recommendations_filename]
        
    except Exception as e:
        print(f"[ERROR] Failed to save user data locally: {str(e)}")
        return False, None