import pandas as pd
import pytimetk as tk

# date range as df
start_date = '2015-01-01'
end_date = '2035-12-31'
date_range = pd.date_range(start=start_date, end=end_date, freq='D')
df = pd.DataFrame({'ds': date_range})




def augment_holidays(data, date_col, country_codes):
    """
    Augments the DataFrame with holiday information for the specified country codes.
    Applies additional transformations for Sweden ('SE').

    Parameters:
    - data: pandas DataFrame containing the date column.
    - date_col: Name of the date column in the DataFrame.
    - country_codes: List of country codes to process.

    Returns:
    - DataFrame with holiday information added for each country.
    """
    holidates = data.copy()
    
    for country_code in country_codes:

        holidates = tk.augment_holiday_signature(holidates, date_col, country_code, reduce_memory=True)
        
        # If country is 'SE', apply additional transformations due to weird behavior ind holidays package
        if country_code == 'SE':
            sunday_index = holidates[holidates['holiday_name'] == "Söndag"].index
            holidates.loc[sunday_index, 'is_holiday'] = 0
            holidates.loc[sunday_index + 1, 'after_holiday'] = 0
            holidates.loc[sunday_index - 1, 'before_holiday'] = 0
        
 
        holidates.rename(columns={
            'is_holiday': f'{country_code.lower()}_holiday',
            'before_holiday': f'{country_code.lower()}_before_holiday',
            'after_holiday': f'{country_code.lower()}_after_holiday'
        }, inplace=True)
        
        holidates.drop('holiday_name', axis=1, inplace=True)

    exogenous_cols = list(holidates)[1:]
    
    return holidates, static_cols

# Usage
country_codes = ['DE', 'IT', 'JP', 'DK', 'SE', 'LU', 'GR', 'CN']
holidates, exogenous_columns = augment_holidays(df, 'ds', country_codes)
holidates
