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
        # Create priority column for NITs based on state and quota
        def assign_priority(row):
            college_state = str(row.get('college state', '')).lower().strip()
            quota = str(row.get('quota', '')).upper().strip()
            user_state = state.lower().strip()
            
            if college_state == user_state and quota == 'HS':
                return 0  # Highest priority: Home state + HS quota
            elif quota == 'OS':
                return 1  # Medium priority: Other state quota
            else:
                return 2  # Lowest priority: Others
        
        df_filtered['priority'] = df_filtered.apply(assign_priority, axis=1)
        df_filtered = df_filtered.sort_values(by=['priority', 'close rank'])
    else:
        # For IIITs, just sort by close rank
        df_filtered = df_filtered.sort_values(by='close rank')
    
    # Return only required columns
    return df_filtered[['college name', 'close rank']]