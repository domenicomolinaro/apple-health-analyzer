import xml.etree.ElementTree as ET
import pandas as pd
import datetime as dt
import numpy as np
import re
from pt2sheets import *
from usefull_function import *
from apple2sheets import *
import calendar    

def apple_health_analyzer(tree, sunday_date,n_of_week):
    
    # for every health record, extract the attributes
    root = tree.getroot()

    # %%
    # ## Create principal database

    record_list = [x.attrib for x in root.iter('Record')]

    record_data = pd.DataFrame(record_list)
    # proper type to dates
    for col in ['creationDate', 'startDate', 'endDate']:
        record_data[col] = pd.to_datetime(record_data[col])

    # value is numeric, NaN if fails
    record_data['value'] = pd.to_numeric(record_data['value'], errors='coerce')

    # some records do not measure anything, just count occurences
    # filling with 1.0 (= one time) makes it easier to aggregate
    record_data['value'] = record_data['value'].fillna(1.0)

    # shorter observation names
    record_data['type'] = record_data['type'].str.replace('HKQuantityTypeIdentifier', '')
    record_data['type'] = record_data['type'].str.replace('HKCategoryTypeIdentifier', '')

    record_data['Date_only'] = record_data['creationDate'].dt.date
    #record_data['type'].unique()

    record_data['Date_only'] = pd.to_datetime(record_data['Date_only'])
    record_data['Corresponding_Day'] = record_data['Date_only'].apply(add_corresponding_day_name)


    # 
    workout_list = [x.attrib for x in root.iter('Workout')]

    # create DataFrame
    workout_data = pd.DataFrame(workout_list)
    workout_data['workoutActivityType'] = workout_data['workoutActivityType'].str.replace('HKWorkoutActivityType', '')
    workout_data = workout_data.rename({"workoutActivityType": "Type"}, axis=1)

    # proper type to dates
    for col in ['creationDate', 'startDate', 'endDate']:
        workout_data[col] = pd.to_datetime(workout_data[col])

    # convert string to numeric   
    workout_data['duration'] = pd.to_numeric(workout_data['duration'])
    workout_data['Date_only'] = workout_data['creationDate'].dt.date
    workout_data['Date_only'] = pd.to_datetime(workout_data['Date_only'])
    workout_data['Corresponding_Day'] = workout_data['Date_only'].apply(add_corresponding_day_name)

    
    workoutStatistics_list = [x.attrib for x in root.iter('WorkoutStatistics')]
    workoutStatistics_data = pd.DataFrame(workoutStatistics_list)

    workoutStatistics_data['type'] = workoutStatistics_data['type'].str.replace('HKQuantityTypeIdentifier', '')

    for col in [ 'startDate', 'endDate']:
        workoutStatistics_data[col] = pd.to_datetime(workoutStatistics_data[col])

    workoutStatistics_data['sum'] = pd.to_numeric(workoutStatistics_data['sum'], errors='coerce')



    # %%  
    # ## Create sub-dataFrame
    # * running data
    # * training data

    running_data = get_workouts(workout_data, 'Running')
    training_data = get_workouts(workout_data, 'TraditionalStrengthTraining')
    heartrate_data = record_data[record_data["type"] == "HeartRate"]
    vo2x_data = record_data[record_data["type"] == "VO2Max"]

    diet_data = record_data[record_data['type'].apply(has_Dietary)]
    diet_data['type'] = diet_data['type'].str.replace('Dietary', '')
    nuovo_valore = diet_data.loc[diet_data['type'] == 'Sodium', 'value'] / 1000
    diet_data.loc[diet_data['type'] == 'Sodium', 'value'] = nuovo_valore
    diet_data.loc[diet_data['type'] == 'Sodium', 'unit'] = 'g'
    diet_data = diet_data.groupby(['type', 'Date_only','unit','creationDate']).agg({'value': 'sum'}).reset_index().to_dict(orient='records')
    diet_data = pd.DataFrame(diet_data)
    diet_data['Date_only'] = pd.to_datetime(diet_data['Date_only'])
    diet_data['Corresponding_Day'] = diet_data['Date_only'].apply(add_corresponding_day_name)


    df = diet_data
    carbo_data = df[df["type"] == "Carbohydrates"]
    carbo_data = carbo_data[['value','Corresponding_Day','creationDate','Date_only']]
    carbo_data.rename(columns={'value': 'carbo'}, inplace=True)
    carbo_data = carbo_data.reset_index(drop=True)

    sugar_data = df[df["type"] == "Sugar"]
    sugar_data = sugar_data[['value']]
    sugar_data = pd.DataFrame(sugar_data)
    sugar_data.rename(columns={'value': 'sugar'}, inplace=True)
    sugar_data = sugar_data.reset_index(drop=True)

    protein_data = df[df["type"] == "Protein"]
    protein_data = protein_data[['value']]
    protein_data = pd.DataFrame(protein_data)
    protein_data.rename(columns={'value': 'protein'}, inplace=True)
    protein_data = protein_data.reset_index(drop=True)

    fiber_data = df[df["type"] == "Fiber"]
    fiber_data = fiber_data[['value']]
    fiber_data = pd.DataFrame(fiber_data)
    fiber_data.rename(columns={'value': 'fiber'}, inplace=True)
    fiber_data = fiber_data.reset_index(drop=True)

    sodium_data = df[df["type"] == "Sodium"]
    sodium_data = sodium_data[['value']]
    sodium_data = pd.DataFrame(sodium_data)
    sodium_data.rename(columns={'value': 'sodium'}, inplace=True)
    sodium_data = sodium_data.reset_index(drop=True)

    energy_data = df[df["type"] == 'EnergyConsumed']
    energy_data = energy_data[['value']]
    energy_data = pd.DataFrame(energy_data)
    energy_data.rename(columns={'value': 'energy'}, inplace=True)
    energy_data = energy_data.reset_index(drop=True)

    df = pd.concat([sugar_data, protein_data, fiber_data, sodium_data,  carbo_data,energy_data], axis = 1)
    diet_data = df

    # %%  
    # ## Extrapolate additional data for running

    distance = [] # in km
    energy_burned_running = [] # in kcal
    hr_running_min = [] #count/min
    hr_running_max = [] #count/min
    hr_running_mean = [] #count/min
    vo2Max_running = [] #mL/min·kg
    for index in range(running_data.shape[0]):
        stats = get_statistics_for_workout(workoutStatistics_data, running_data.iloc[[index]])
        
        energy_burned_running.append(stats.loc[stats['type']=='ActiveEnergyBurned','sum'].values[0])
        distance.append(stats.loc[stats['type']=='DistanceWalkingRunning','sum'].values[0])
        
        hr_db = get_heartrate_for_workout(heartrate_data, running_data.iloc[[index]])
        minh = hr_db["value"].min()
        maxh = hr_db["value"].max()
        meanh = hr_db["value"].mean()
        
        hr_running_min.append(minh)
        hr_running_max.append(maxh)
        hr_running_mean.append(meanh)
        
        vo2x_for_workout = get_vox_for_workout(vo2x_data, running_data.iloc[[index]])
        if isinstance(vo2x_for_workout, str):
            vo2Max_running.append(vo2x_for_workout)
        else:
            vo2Max_running.append(vo2x_for_workout.loc[vo2x_for_workout['type']=='VO2Max','value'].values[0])
            
    # add the data to the database
    running_data['distance_in_km'] = distance
    running_data['energy_burned_in_kcal'] = energy_burned_running
    running_data['pace_in_min/km'] = running_data['duration']/(running_data['distance_in_km'])
    running_data['BPM_min'] = hr_running_min
    running_data['BPM_max'] = hr_running_max
    running_data['BPM_mean'] = hr_running_mean
    running_data['VO2_max'] = vo2Max_running


    # %%  
    # ## Extrapolate additional data for training

    hr_training_min = [] # count/min
    hr_training_max = [] # count/min
    hr_training_mean = [] # count/min
    energy_burned_training = [] # in kcal
    vo2Max_training = [] # in mL/min·kg

    for index in range(training_data.shape[0]):
        stats = get_statistics_for_workout(workoutStatistics_data, training_data.iloc[[index]])
        
        energy_burned_training.append(stats.loc[stats['type']=='ActiveEnergyBurned','sum'].values[0])
        hr_db = get_heartrate_for_workout(heartrate_data, training_data.iloc[[index]])
        minh = hr_db["value"].min()
        maxh = hr_db["value"].max()
        meanh = hr_db["value"].mean()
        
        hr_training_min.append(minh)
        hr_training_max.append(maxh)
        hr_training_mean.append(meanh)
        vo2x_for_workout = get_vox_for_workout(vo2x_data, training_data.iloc[[index]])
        if isinstance(vo2x_for_workout, str):
            vo2Max_training.append(vo2x_for_workout)
        else:
            vo2Max_training.append(vo2x_for_workout.loc[vo2x_for_workout['type']=='VO2Max','value'].values[0])
        

    training_data['energy_burned_in_kcal'] = energy_burned_training
    training_data['BPM_min'] = hr_training_min
    training_data['BPM_max'] = hr_training_max
    training_data['BPM_mean'] = hr_training_mean
    training_data['VO2_max'] = vo2Max_training


    # %%  
    # ## Getting data from a certain time period

    # ### weekly data
    end_time = sunday_date
    start_time = end_time - dt.timedelta(days=7)

    weekly_training_data = get_data_from_to(training_data, start_time, end_time)
    weekly_running_data = get_data_from_to(running_data, start_time, end_time)
    weekly_diet_data = get_data_from_to(diet_data, start_time, end_time)
    weekly_hearthrate_data = get_data_from_to(heartrate_data, start_time, end_time)


    weekly_diet_data = add_missing_days(weekly_diet_data)  # mancano i dati a diet data perciò non tira fuori niente
    weekly_training_data = add_missing_days(weekly_training_data)

    n_month = sunday_date.month
    month_name = calendar.month_name[n_month]
    apple_health_2_google_sheets(weekly_diet_data, 'diet', month_name, n_of_week)
    apple_health_2_google_sheets(weekly_training_data, 'training', month_name, n_of_week)