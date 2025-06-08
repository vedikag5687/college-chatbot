import pandas as pd

def filter_colleges(df, gender, category, rank, degrees, branches, state=None, is_nit=False):
    df = df.copy()
    
    df['close rank'] = pd.to_numeric(df['close rank'], errors='coerce')
    df = df.dropna(subset=['close rank'])
    
    # MODIFIED: Show only colleges where Close Rank >= User's Rank (user can get admission)
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
        def should_include_college(row):
            college_state = str(row.get('college state', '')).lower().strip()
            # Fix: Handle state parameter correctly - it comes as a list from stream.py
            user_state = state[0].lower().strip() if isinstance(state, list) else str(state).lower().strip()
            quota = str(row.get('quota', '')).upper().strip()
            
            print(f"[DEBUG] College: {row.get('college name', '')}")
            print(f"[DEBUG] College State: '{college_state}' | User State: '{user_state}' | Quota: '{quota}'")
            
            if college_state == user_state:
                # Same state: Only HS quota
                result = quota == 'HS'
                print(f"[DEBUG] Same state - Include: {result} (quota should be HS)")
                return result
            else:
                # Different state: Only OS quota
                result = quota == 'OS'
                print(f"[DEBUG] Different state - Include: {result} (quota should be OS)")
                return result
        
        df_filtered = df_filtered[df_filtered.apply(should_include_college, axis=1)].copy()
        
        if df_filtered.empty:
            return df_filtered[['college name', 'close rank']]
        
        # Sort by close rank (ascending) - lowest closing rank first (easiest to get)
        df_filtered = df_filtered.sort_values(by='close rank', ascending=True)
    else:
        # Sort by close rank (ascending) - lowest closing rank first (easiest to get)
        df_filtered = df_filtered.sort_values(by='close rank', ascending=True)
    
    return df_filtered[['college name', 'close rank']].reset_index(drop=True)