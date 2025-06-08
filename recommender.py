import pandas as pd

def filter_colleges(df, gender, category, rank, degrees, branches, state=None, is_nit=False):
    # Make a copy to avoid modifying original dataframe
    df = df.copy()
    
    # Clean and convert close rank to numeric
    df['close rank'] = pd.to_numeric(df['close rank'], errors='coerce')
    df = df.dropna(subset=['close rank'])
    
    # Apply basic filters
    # Close rank should be >= user's JEE rank (user's rank must be better than or equal to close rank)
    filters = (
        (df['gender'].str.lower().str.strip() == gender.lower().strip()) &
        (df['category'].str.lower().str.strip() == category.lower().strip()) &
        (df['close rank'] <= float(rank)) &
        (df['degree'].isin(degrees)) &
        (df['branch'].isin(branches))
    )
    
    df_filtered = df[filters].copy()
    
    if df_filtered.empty:
        return df_filtered[['college name', 'close rank']]
    
    if is_nit and state:
        # Apply College State and Quota logic for NITs
        def should_include_college(row):
            college_state = str(row.get('college state', '')).lower().strip()
            # user_state = state.lower().strip()
            user_state =  state
            quota = str(row.get('quota', '')).upper().strip()
            
            if college_state == user_state:
                # Same state as user: only include HS quota, exclude OS quota
                return quota == 'HS'
            else:
                # Different state from user: only include OS quota, exclude HS quota
                return quota == 'OS'
        
        # Filter based on College State and Quota logic
        df_filtered = df_filtered[df_filtered.apply(should_include_college, axis=1)].copy()
        
        if df_filtered.empty:
            return df_filtered[['college name', 'close rank']]
        
        # Sort by close rank in ascending order
        df_filtered = df_filtered.sort_values(by='close rank', ascending=True)
    else:
        # For IIITs, just sort by close rank in ascending order
        df_filtered = df_filtered.sort_values(by='close rank', ascending=True)
    
    # Return only college name and close rank columns (no index)
    return df_filtered[['college name', 'close rank']].reset_index(drop=True)
