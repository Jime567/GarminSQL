import garth
import os
import mysql.connector
import json

email = os.getenv('GARMIN_USER')
password = os.getenv('GARMIN_PASS')
sql_pass = os.getenv('SQL_PASS')
sql_user = os.getenv('SQL_USER')
weekly_hr_endpoint = 'usersummary-service/stats/heartRate/daily/2024-06-11/2024-06-17'
weekly_sleep_endpoint = '/sleep-service/stats/sleep/daily/2024-06-11/2024-06-17'
weekly_resp_endpoint = '/wellness-service/wellness/daily/respiration/2024-06-17'
weekly_steps_endpoint = 'usersummary-service/stats/daily/2024-06-11/2024-06-17?statsType=STEPS&currentDate=2024-06-17'
weekly_stress_endpoint = '/usersummary-service/stats/stress/daily/2024-06-11/2024-06-17'

# garth.login(email, password)
# garth.save("~/.garth")

garth.resume("~/.garth")

try:
    garth.client.username
    print("Logged in as", garth.client.username)
except GarthException:
    # Session is expired. You'll need to log in again
    print("Session is expired. You'll need to log in again")

conn = mysql.connector.connect(
    host='localhost',
    user=sql_user,
    password=sql_pass,
    database='garmin'
)


cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS heart_rate (
        calendar_date DATE,
        min_avg_hr INT,
        resting_hr INT,
        max_avg_hr INT
    );
''')

cursor.execute('''
               CREATE TABLE IF NOT EXISTS sleep (
    calendar_date DATE,
    remTime INT,
    restingHeartRate INT,
    totalSleepTimeInSeconds INT,
    respiration FLOAT,
    localSleepEndTimeInMillis BIGINT,
    deepTime INT,
    awakeTime INT,
    sleepScoreQuality VARCHAR(20),
    spO2 FLOAT,
    localSleepStartTimeInMillis BIGINT,
    sleepNeed INT,
    bodyBatteryChange INT,
    gmtSleepStartTimeInMillis BIGINT,
    gmtSleepEndTimeInMillis BIGINT,
    hrvStatus VARCHAR(20),
    skinTempF FLOAT,
    sleepScore INT,
    skinTempC FLOAT,
    lightTime INT,
    hrv7dAverage FLOAT
);              
              ''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS respiration (
        calendar_date DATE,
        lowest_respiration_value INT,
        highest_respiration_value INT,
        avg_waking_respiration_value INT,
        avg_sleep_respiration_value INT
    );
''')

cursor.execute('''
               CREATE TABLE IF NOT EXISTS steps (
    calendarDate DATE,
    stepGoal INT,
    totalSteps INT,
    totalDistance FLOAT
);
                ''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS stress (
        calendarDate DATE,
        highStressDuration INT,
        lowStressDuration INT,
        overallStressLevel INT,
        restStressDuration INT,
        mediumStressDuration INT
    );
''')



# HEART RATE
insert_query = '''
    INSERT INTO heart_rate (calendar_date, min_avg_hr, resting_hr, max_avg_hr)
    VALUES (%s, %s, %s, %s)
'''
data = garth.connectapi(weekly_hr_endpoint)

for entry in data:
    calendar_date = entry['calendarDate']
    resting_hr = entry['values']['restingHR']
    max_avg_hr = entry['values']['wellnessMaxAvgHR']
    min_avg_hr = entry['values']['wellnessMinAvgHR']
    cursor.execute(insert_query, (calendar_date, min_avg_hr, resting_hr, max_avg_hr))

# SLEEP
data = garth.connectapi(weekly_sleep_endpoint)

insert_query = '''
    INSERT INTO sleep (
        calendar_date, remTime, restingHeartRate, totalSleepTimeInSeconds, respiration,
        localSleepEndTimeInMillis, deepTime, awakeTime, sleepScoreQuality, spO2,
        localSleepStartTimeInMillis, sleepNeed, bodyBatteryChange, gmtSleepStartTimeInMillis,
        gmtSleepEndTimeInMillis, hrvStatus, skinTempF, sleepScore, skinTempC, lightTime, hrv7dAverage
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
'''

for entry in data["individualStats"]:
    calendar_date = entry["calendarDate"]
    values = entry["values"]
    cursor.execute(insert_query, (
        calendar_date,
        values["remTime"],
        values["restingHeartRate"],
        values["totalSleepTimeInSeconds"],
        values["respiration"],
        values["localSleepEndTimeInMillis"],
        values["deepTime"],
        values["awakeTime"],
        values["sleepScoreQuality"],
        values["spO2"],
        values["localSleepStartTimeInMillis"],
        values["sleepNeed"],
        values["bodyBatteryChange"],
        values["gmtSleepStartTimeInMillis"],
        values["gmtSleepEndTimeInMillis"],
        values["hrvStatus"],
        values["skinTempF"],
        values["sleepScore"],
        values["skinTempC"],
        values["lightTime"],
        values["hrv7dAverage"]
    ))

# RESPIRATION 
insert_query = '''
    INSERT INTO respiration (calendar_date, lowest_respiration_value, highest_respiration_value, avg_waking_respiration_value, avg_sleep_respiration_value)
    VALUES (%s, %s, %s, %s, %s)
'''

data = garth.connectapi(weekly_resp_endpoint)

for entry in data['respirationValueDescriptorsDTOList']:
    calendar_date = data['calendarDate']
    lowest_respiration_value = data['lowestRespirationValue']
    highest_respiration_value = data['highestRespirationValue']
    avg_waking_respiration_value = data['avgWakingRespirationValue']
    avg_sleep_respiration_value = data['avgSleepRespirationValue']

    # Execute insert query
    cursor.execute(insert_query, (
        calendar_date,
        lowest_respiration_value,
        highest_respiration_value,
        avg_waking_respiration_value,
        avg_sleep_respiration_value
    ))

# STEPS 
insert_query = '''
    INSERT INTO steps (calendarDate, stepGoal, totalSteps, totalDistance)
    VALUES (%s, %s, %s, %s)
'''

data = garth.connectapi(weekly_steps_endpoint)

for entry in data['values']:
    calendar_date = entry['calendarDate']
    step_goal = entry['values']['stepGoal']
    total_steps = entry['values']['totalSteps']
    total_distance = entry['values']['totalDistance']
    
    cursor.execute(insert_query, (calendar_date, step_goal, total_steps, total_distance))

# STRESS
insert_query = '''
    INSERT INTO stress (
        calendarDate, highStressDuration, lowStressDuration, 
        overallStressLevel, restStressDuration, mediumStressDuration
    ) VALUES (%s, %s, %s, %s, %s, %s)
'''

data = garth.connectapi(weekly_stress_endpoint)

for entry in data:
    calendar_date = entry['calendarDate']
    values = entry['values']
    high_stress_duration = values['highStressDuration']
    low_stress_duration = values['lowStressDuration']
    overall_stress_level = values['overallStressLevel']
    rest_stress_duration = values['restStressDuration']
    medium_stress_duration = values['mediumStressDuration']
    
    cursor.execute(insert_query, (
        calendar_date, high_stress_duration, low_stress_duration,
        overall_stress_level, rest_stress_duration, medium_stress_duration
    ))


conn.commit()

cursor.close()
conn.close()