import xml.etree.ElementTree as ET
import pandas as pd
import datetime as dt
import numpy as np
import re

### get heart rate for workout
def get_heartrate_for_workout(heartrate, workout):
    def get_heartrate_for_date(hr, start, end):
        hr = hr[hr["startDate"] >= start]
        hr = hr[hr["endDate"] <= end]
        return hr
    
    return get_heartrate_for_date(heartrate, workout["startDate"].item(), workout["endDate"].item())


### get statistics for workout
def get_statistics_for_workout(workout_statistics, workout):
    def get_stats_for_date(stats, start, end):
        stats = stats[stats["startDate"] >= start]
        stats = stats[stats["endDate"] <= end]
        return stats

    return get_stats_for_date(workout_statistics, workout["startDate"].item(), workout["endDate"].item())


### filter workouts by type
def get_workouts(df, workout_type):
    return df[df["Type"] == workout_type]


### get hr per workout row
def get_hr_for_workout_row(workout, heartrate):
    def get_hr_for_date(hr, start, end):
        hr = hr[hr["startDate"] >= start]
        hr = hr[hr["endDate"] <= end]
        return hr
    return get_hr_for_date(heartrate, workout["startDate"], workout["endDate"])



### get pace for workout
def get_pace_for_workout(workout):
    if workout["totalDistance"] == 0.0:
        return 0.0
    # pace=min/km
    pace = workout["duration"] / workout["totalDistance"]
    return convert_to_minute_proportion(pace)


### get VOX consuption for workout
def get_vox_for_workout(vox_db, exercise_db):
    def get_vox_for_date(vox,data):
        vox = vox[vox["Date_only"] == data]
        if vox.empty:
            return 'no_value_registerd'
        else:
            return vox
       
    return get_vox_for_date(vox_db, exercise_db["Date_only"].item())

### get "dietary" from records
# Function to check if the word "dietary" is followed by other words
def has_Dietary(text):
    return bool(re.search(r'Dietary\w*', text))


# Function to add the corresponding day names to a date
def add_corresponding_day_name(date):
    corresponding_day_name = date.strftime("%A")
    return corresponding_day_name

# Get data in a specific time interval
def get_data_from_to(df, start, end):
    start = pd.to_datetime(start, utc=True)
    end = pd.to_datetime(end, utc=True)
    data = df[df["Date_only"] >= start]
    data = data[data["Date_only"] <= end]
    return data

# Add missing days in weekly database
def add_missing_days(df):
    # Convert the 'Date_only' column to datetime type if it's not already
    df['Date_only'] = pd.to_datetime(df['Date_only'])

    # Find the start of the week (Monday) for the min date in the DataFrame
    start_of_week = df['Date_only'].min() - pd.Timedelta(days=df['Date_only'].min().dayofweek)

    # Find the end of the week (Sunday) for the max date in the DataFrame
    end_of_week = df['Date_only'].max() + pd.Timedelta(days=6 - df['Date_only'].max().dayofweek)

    # Create a DataFrame with all the days of the week (Monday to Sunday)
    all_days = pd.date_range(start=start_of_week, end=end_of_week, freq='D')
    all_days_df = pd.DataFrame({'Date_only': all_days})

    # Merge the original DataFrame with the DataFrame containing all days to find missing days
    merged_df = all_days_df.merge(df, on='Date_only', how='left')

    # Find the missing days (i.e., rows with NaN values)
    missing_days = merged_df[merged_df.isnull().any(axis=1)]

    # Filter out missing days that are already present in the original DataFrame
    missing_days = missing_days[~missing_days['Date_only'].isin(df['Date_only'])]

    # Add rows with missing days and 0 values
    if not missing_days.empty:
        df = pd.concat([df, missing_days[['Date_only']]])

    # Sort the DataFrame by date
    df = df.sort_values(by='Date_only')
    
    # Replace NaN values with 0
    df = df.fillna(0)
    
    df['Corresponding_Day'] = df['Date_only'].apply(add_corresponding_day_name)

    return df