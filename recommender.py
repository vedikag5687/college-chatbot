import pandas as pd

def filter_colleges(df, gender, category, rank, degrees, branches, state=None, is_nit=False):
    # Make a copy to avoid modifying original dataframe
    df = df.copy()
    
    # Clean and convert close rank to numeric
    df['close rank'] = pd.to_numeric(df['close rank'], errors='coerce')
    df = df.dropna(subset=['close rank'])
    
    # Basic filters (without quota filtering for now)
    basic_filters = (
        (df['gender'].str.lower().str.strip() == gender.lower().strip()) &
        (df['category'].str.lower().str.strip() == category.lower().strip()) &
        (df['close rank'] >= float(rank)) &
        (df['degree'].isin(degrees)) &
        (df['branch'].isin(branches))
    )
    
    df_filtered = df[basic_filters].copy()
    
    if df_filtered.empty:
        return df_filtered[['college name', 'close rank']]
    
    if is_nit and state:
        # Apply quota filtering based on state matching
        def should_keep_row(row):
            college_state = str(row.get('college state', '')).lower().strip()
            user_state = state.lower().strip()
            quota = str(row.get('quota', '')).upper().strip()
            
            if college_state == user_state:
                # For same state colleges, keep only HS (Home State) quota
                return quota == 'HS'
            else:
                # For different state colleges, keep only OS (Other State) quota
                return quota == 'OS'
        
        # Apply the quota filter
        quota_mask = df_filtered.apply(should_keep_row, axis=1)
        df_filtered = df_filtered[quota_mask].copy()
        
        if df_filtered.empty:
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
    
    # Return only college name and close rank columns (no index)
    return df_filtered[['college name', 'close rank']].reset_index(drop=True)