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
