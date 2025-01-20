import pandas as pd
import numpy as np

# Create example data
date_range = pd.date_range(start="2023-01-01", end="2023-12-31", freq="D")
is_holiday = np.random.choice([0, 1], size=len(date_range), p=[0.9, 0.1])  # 10% chance of being a holiday

example_df = pd.DataFrame({
    "ds": date_range,
    "is_se_holiday": is_holiday
})

# Extract the list of holidays
holiday_list = example_df.loc[example_df["is_se_holiday"] == 1, "ds"].dt.date.unique()
holiday_dates = np.array(holiday_list, dtype="datetime64[D]")  # Convert to numpy datetime64 array

# Define business days (Mon-Fri) as the weekmask
weekmask = "Mon Tue Wed Thu Fri"

# Compute adjusted paydays using numpy.busday_offset
paydays = []
for period in example_df["ds"].dt.to_period("M").unique():
    year = period.year
    month = period.month

    # Define potential paydays
    potential_paydays = [
        np.datetime64(f"{year}-{month:02d}-25", "D"),
        np.datetime64(f"{year}-{month:02d}-27", "D"),
    ]
    
    # Adjust paydays backward to the nearest valid business day
    for payday in potential_paydays:
        adjusted_payday = np.busday_offset(
            payday,
            offsets=0,  # Start from the given date
            roll="backward",  # Move to the nearest valid business day
            weekmask=weekmask,
            holidays=holiday_dates,
        )
        paydays.append(adjusted_payday)

# Add a new column to indicate if a date is a payday
example_df["payday_se"] = example_df["ds"].isin(pd.to_datetime(paydays)).astype(int)

# Testing the output
# Check if paydays fall on weekdays and are not holidays
payday_dates = example_df.loc[example_df["payday_se"] == 1, "ds"]
weekday_check = payday_dates.dt.weekday.isin([0, 1, 2, 3, 4]).all()  # True if all paydays are weekdays
holiday_check = ~payday_dates.isin(pd.to_datetime(holiday_dates)).all()  # True if no paydays are holidays


fi_paydays = []
for period in example_df["ds"].dt.to_period("M").unique():
    year = period.year
    month = period.month

    # Define potential paydays (15th and last day of the month)
    potential_paydays = [
        np.datetime64(f"{year}-{month:02d}-15", "D"),
        np.datetime64(f"{year}-{month:02d}-{pd.Timestamp(year, month, 1).days_in_month}", "D"),  # Last day of the month
    ]
    
    # Adjust paydays backward to the nearest valid business day
    for payday in potential_paydays:
        adjusted_payday = np.busday_offset(
            payday,
            offsets=0,  # Start from the given date
            roll="backward",  # Move to the nearest valid business day
            weekmask=weekmask,
            holidays=fi_holiday_dates,
        )
        fi_paydays.append(adjusted_payday)

# Add a new column to indicate if a date is a Finnish payday
example_df["payday_fi"] = example_df["ds"].isin(pd.to_datetime(fi_paydays)).astype(int)

------------------


# Compute adjusted Danish paydays using the rule (last banking day of the month)
dk_paydays = []
for period in example_df["ds"].dt.to_period("M").unique():
    year = period.year
    month = period.month

    # Define the last day of the month
    last_day_of_month = np.datetime64(f"{year}-{month:02d}-{pd.Timestamp(year, month, 1).days_in_month}", "D")
    
    # Adjust the last day of the month backward to the nearest valid business day
    adjusted_payday = np.busday_offset(
        last_day_of_month,
        offsets=0,  # Start from the given date
        roll="backward",  # Move to the nearest valid business day
        weekmask=weekmask,
        holidays=holiday_dates,  # Reuse SE holidays for now; can customize if needed
    )
    dk_paydays.append(adjusted_payday)

# Add a new column to indicate if a date is a Danish payday
example_df["payday_dk"] = example_df["ds"].isin(pd.to_datetime(dk_paydays)).astype(int)
-----------------
no_paydays = []
for period in example_df["ds"].dt.to_period("M").unique():
    year = period.year
    month = period.month

    # Define the 20th of the month
    payday = np.datetime64(f"{year}-{month:02d}-20", "D")
    
    # Adjust the 20th of the month backward to the nearest valid business day
    adjusted_payday = np.busday_offset(
        payday,
        offsets=0,  # Start from the given date
        roll="backward",  # Move to the nearest valid business day
        weekmask=weekmask,
        holidays=holiday_dates,  # Reuse SE holidays for now; can customize if needed
    )
    no_paydays.append(adjusted_payday)

# Add a new column to indicate if a date is a Norwegian payday
example_df["payday_no"] = example_df["ds"].isin(pd.to_datetime(no_paydays)).astype(int)

----------------------

pension_days = []
for period in example_df["ds"].dt.to_period("M").unique():
    year = period.year
    month = period.month

    # Define the potential pension day (1st of the month)
    potential_pension_day = np.datetime64(f"{year}-{month:02d}-01", "D")
    
    # Adjust pension day forward to the nearest valid business day
    adjusted_pension_day = np.busday_offset(
        potential_pension_day,
        offsets=0,  # Start from the given date
        roll="forward",  # Move to the nearest valid business day
        weekmask=weekmask,
        holidays=holiday_dates,
    )
    pension_days.append(adjusted_pension_day)

# Add a new column to indicate if a date is a pension day
example_df["pension_dk"] = example_df["ds"].isin(pd.to_datetime(pension_days)).astype(int)


----------

# Melt the data to a long format including all columns except the extracted 'item_id'
long_df = initial_df.melt(id_vars=["ds", "weekend"], var_name="variable", value_name="value")

# Extract the country abbreviation (e.g., SE, DK, FI, NO) and the corresponding indicator
long_df["item_id"] = long_df["variable"].str.extract(r"(se|no|dk|fi)", expand=False).str.upper()
long_df["indicator"] = long_df["variable"].str.replace(r"(se_|no_|dk_|fi_)", "", regex=True)

# Drop rows where `item_id` is NaN (indicators without country association)
long_df = long_df.dropna(subset=["item_id"])

# Pivot the data back to wide format
target_form = long_df.pivot_table(index=["ds", "weekend", "item_id"], 
                                  columns="indicator", 
                                  values="value", 
                                  fill_value=0).reset_index()

# Flatten the column hierarchy resulting from the pivot
target_form.columns.name = None
------
# Add 'year-month' column for grouping
df['year_month'] = df['ds'].dt.to_period('M')

# Define a function to calculate workdays per country
def calculate_workdays(group):
    total_days = len(group)
    weekdays = group[~group['ds'].dt.weekday.isin([5, 6])]  # Exclude weekends
    result = {
        'se_workdays': len(weekdays) - weekdays['se_holiday'].sum(),
        'dk_workdays': len(weekdays) - weekdays['dk_holiday'].sum(),
        'no_workdays': len(weekdays) - weekdays['no_holiday'].sum(),
        'fi_workdays': len(weekdays) - weekdays['fi_holiday'].sum()
    }
    return pd.Series(result)

# Group by 'year_month' and apply the function
workdays_per_month = df.groupby('year_month').apply(calculate_workdays)

# Reset index to make it more readable
workdays_per_month.reset_index(inplace=True)

--------

# Function to adjust the `bys` column
def adjust_bys(row, df):
    if row['bys'] == 1:  # Only adjust where `bys` is 1
        current_date = row['date']
        while True:
            # Check if the date is a weekend or a holiday in any country
            is_weekend = current_date.weekday() in [5, 6]  # Saturday = 5, Sunday = 6
            is_holiday = df.loc[df['date'] == current_date, ['se_holiday', 'dk_holiday', 'fi_holiday', 'no_holiday']].values[0].sum() > 0
            
            if is_weekend or is_holiday:
                current_date += pd.Timedelta(days=1)  # Move to the next day
            else:
                break
        # Update the date directly in the row
        return current_date
    return row['date']

# Apply the adjustment logic directly to the `date` column where `bys` is 1
df.loc[df['bys'] == 1, 'date'] = df.apply(lambda row: adjust_bys(row, df), axis=1)

-------------

df = pd.DataFrame(data)

# Define a combined holiday calendar
holidays = df['date'][
    (df['se_holiday'] == 1) | 
    (df['dk_holiday'] == 1) | 
    (df['fi_holiday'] == 1) | 
    (df['no_holiday'] == 1)
].dt.strftime('%Y-%m-%d').tolist()

# Adjust the `bys` column using numpy's busday_offset to ensure only one day has `1`
adjusted_bys_date = np.busday_offset('2023-01-01', 0, roll='forward', holidays=holidays)
df['bys'] = df['date'].apply(lambda x: 1 if np.datetime64(x) == np.datetime64(adjusted_bys_date) else 0)




