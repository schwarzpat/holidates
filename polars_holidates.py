import polars as pl
import pytimetk as tk

def augment_holidays(data, date_col, country_codes):
    """
    Augments the DataFrame with holiday information for the specified country codes.
    Applies additional transformations for Sweden ('SE').

    Parameters:
    - data: Polars DataFrame containing the date column.
    - date_col: Name of the date column in the DataFrame.
    - country_codes: List of country codes to process.

    Returns:
    - DataFrame with holiday information added for each country.
    """
    holidates = data.clone()
    
    for country_code in country_codes:

        holidates = tk.augment_holiday_signature(
            holidates, 
            date_column=date_col, 
            country_code=country_code, 
            reduce_memory=True,
            engine='polars'
        )
        
        # If country is 'SE', apply additional transformations
        if country_code == 'SE':

            holidates = holidates.with_columns(
                pl.col('holiday_name').eq("Söndag").alias('is_sunday')
            )
            
            holidates = holidates.with_columns(
                pl.when(pl.col('is_sunday'))
                .then(0)
                .otherwise(pl.col('is_holiday'))
                .alias('is_holiday')
            )
            
            holidates = holidates.with_columns([
                pl.col('is_sunday').shift(-1).fill_null(False).alias('next_is_sunday'),
                pl.col('is_sunday').shift(1).fill_null(False).alias('prev_is_sunday')
            ])

            holidates = holidates.with_columns(
                pl.when(pl.col('prev_is_sunday'))
                .then(0)
                .otherwise(pl.col('after_holiday'))
                .alias('after_holiday')
            )

            holidates = holidates.with_columns(
                pl.when(pl.col('next_is_sunday'))
                .then(0)
                .otherwise(pl.col('before_holiday'))
                .alias('before_holiday')
            )
            
            # Drop helper columns
            holidates = holidates.drop(['is_sunday', 'next_is_sunday', 'prev_is_sunday'])
        
        holidates = holidates.rename({
            'is_holiday': f'{country_code.lower()}_holiday',
            'before_holiday': f'{country_code.lower()}_before_holiday',
            'after_holiday': f'{country_code.lower()}_after_holiday'
        })
        
        holidates = holidates.drop('holiday_name')
    
    return holidates

# Usage example
data = pl.read_csv('dates4timetk.csv')
data = data.with_columns(
    pl.col('ds').str.strptime(pl.Datetime, "%Y-%m-%d")
)

country_codes = ['SE', 'NO', 'FI', 'DK']
holidates = augment_holidays(data, 'ds', country_codes)
holidates
