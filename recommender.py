import pandas as pd

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
    basic_filters = (
        (df['gender'].str.lower().str.strip() == gender.lower().strip()) &
        (df['category'].str.lower().str.strip() == category.lower().strip()) &
        (df['close rank'] >= float(rank)) &
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