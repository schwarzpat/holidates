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

def calculate_dk_pension_day(date, holiday_dates):
    if date.day == 1:  # Only consider the first of the month
        adjusted_date = np.busday_offset(date.date(), 0, roll='forward', holidays=holiday_dates)
        if adjusted_date == date.date():
            return 1  # The original date is valid
    return 0

# Apply the function to create dk_pension_day column
df['dk_pension'] = df['ds'].apply(lambda x: calculate_dk_pension_day(x, holiday_dates))



