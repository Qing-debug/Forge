
# Code 1:
for participant_id, group in calibration_data_raw.groupby('Participant_ID'):
    rr_intervals = group['Polar_HeartRate_RR_Interval']
    rmssd_participant = np.sqrt(np.mean(np.diff(rr_intervals) ** 2))
    aggregated_data.loc[
        aggregated_data['Participant_ID'] == participant_id, 'Calibration_RR_Interval_RAW_RMSSD'] = rmssd_participant

#Code 2:
HR_std_map = calibration_data_raw.groupby('Participant_ID')['Polar_HearRateBPM'].std().to_dict()
aggregated_data['Calibration_SD_Resting_HeartRate'] = aggregated_data['Participant_ID'].map(HR_std_map)

#Code 1 and 2 are different ways of achieving the same outcome. That is creating a column x in aggregated_data where we have
#values placed in cells based off the participant ID.  But code 1 needed to be done manually due to how we compute the data.




#pattern to compute a value based off crossection of rows and columns, then compute some value from it
targetted_cells = df.loc[df['some_column'] == some_value, 'target_column']]
targetted_cells.median(), or targetted_cells.mean(), targetted_cells.std(), or some custom function like np.sqrt(np.mean(np.diff(rr_intervals) ** 2)).


# pattern to select cells based off the crossection of rows and columns, and add in a number to those cells:
# this will create the target column if it doesn't exist already, or update it if it does
df.loc[df['some_column'] == some_value, 'target_column'] = computed_value



