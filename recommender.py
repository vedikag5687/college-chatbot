import pandas as pd

def filter_colleges(df, gender, category, rank, degrees, branches, state=None, is_nit=False):
    # Make a copy to avoid modifying original dataframe
    df = df.copy()
    
    # Clean and convert close rank to numeric
    df['close rank'] = pd.to_numeric(df['close rank'], errors='coerce')
    df = df.dropna(subset=['close rank'])
    
    # Apply filters
    filters = (
        (df['gender'].str.lower().str.strip() == gender.lower().strip()) &
        (df['category'].str.lower().str.strip() == category.lower().strip()) &
        (df['close rank'] >= float(rank)) &
        (df['degree'].isin(degrees)) &
        (df['branch'].isin(branches))
    )
    
    df_filtered = df[filters].copy()
    
    if df_filtered.empty:
        return df_filtered[['college name', 'close rank']]
    
    if is_nit and state:
        # Update quota based on college state vs user state
        def update_quota(row):
            college_state = str(row.get('college state', '')).lower().strip()
            user_state = state.lower().strip()
            
            if college_state == user_state:
                return 'HS'  # Home State
            else:
                return 'OS'  # Other State
        
        # Update the quota column based on state matching
        df_filtered['quota'] = df_filtered.apply(update_quota, axis=1)
        
        # Create priority for sorting (HS first, then OS)
        def assign_priority(row):
            quota = str(row.get('quota', '')).upper().strip()
            if quota == 'HS':
                return 0  # Higher priority for Home State
            else:
                return 1  # Lower priority for Other State
        
        df_filtered['priority'] = df_filtered.apply(assign_priority, axis=1)
        
        # Sort by priority first, then by close rank (ascending)
        df_filtered = df_filtered.sort_values(by=['priority', 'close rank'])
    else:
        # For IIITs, just sort by close rank (ascending)
        df_filtered = df_filtered.sort_values(by='close rank')
    
    # Return only college name and close rank columns (no index)
    return df_filtered[['college name', 'close rank']].reset_index(drop=True)