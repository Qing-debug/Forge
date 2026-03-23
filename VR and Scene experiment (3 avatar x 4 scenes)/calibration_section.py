#Need to figure out what the intent of this part of the script is. The code is just a way of carrying out their intention, if you can figure out their intent, you'll be able to figure out
# what it is you actually need to code up.

#----------------------------------------------------------------------------------------beginning of calibration part of things ----------------------------------------------------------------------------------------

aggregated_data = merged_data

#------------------------------------------------------------------------------------------------------------
# Dilation Data
#done

# List of possible values for Shown_Gray_Scale_Value
possible_grayscale_values = [0, 16, 32, 48, 64, 80, 96, 112, 128, 144, 160, 176, 192, 208, 224, 240, 255]
# Iterate through each possible value
for value in possible_grayscale_values:
    # Filter rows where Shown_Gray_Scale_Value equals the current value
    filtered_data = calibration_data[calibration_data['Shown_Gray_Scale_Value'] == value]

    # Create a dictionary with Participant_ID as the index and median values as values
    median_dict = filtered_data.set_index('Participant_ID')[
        ['Median_Pupil_Dilation_Left', 'Median_Pupil_Dilation_Right']].to_dict()

    # Column names for the existing median value columns
    col_left = f'Calibration_PupilDilation_Left_{value}'
    col_right = f'Calibration_PupilDilation_Right_{value}'

    # Update the existing columns in 'aggregate_data' with the calculated median values
    aggregated_data.loc[:, col_left] = aggregated_data['Participant_ID'].map(median_dict['Median_Pupil_Dilation_Left'])
    aggregated_data.loc[:, col_right] = aggregated_data['Participant_ID'].map(
        median_dict['Median_Pupil_Dilation_Right'])

#------------------------------------------------------------------------------------------------------------





#------------------------------------------------------------------------------------------------------------
##done
HR_median_map = calibration_data_raw.groupby('Participant_ID')['Polar_HearRateBPM'].median().to_dict()
HR_mean_map = calibration_data_raw.groupby('Participant_ID')['Polar_HearRateBPM'].mean().to_dict()
HR_std_map = calibration_data_raw.groupby('Participant_ID')['Polar_HearRateBPM'].std().to_dict()
aggregated_data['Calibration_Median_Resting_HeartRate'] = aggregated_data['Participant_ID'].map(HR_median_map)
aggregated_data['Calibration_Mean_Resting_HeartRate'] = aggregated_data['Participant_ID'].map(HR_mean_map)
aggregated_data['Calibration_SD_Resting_HeartRate'] = aggregated_data['Participant_ID'].map(HR_std_map)


HR_interval_median_map = calibration_data_raw.groupby('Participant_ID')['Polar_HeartRate_RR_Interval'].median().to_dict()
HR_interval_mean_map = calibration_data_raw.groupby('Participant_ID')['Polar_HeartRate_RR_Interval'].mean().to_dict()
HR_interval_std_map = calibration_data_raw.groupby('Participant_ID')['Polar_HeartRate_RR_Interval'].std().to_dict()
aggregated_data['Calibration_Median_Resting_HeartRate_RR_Interval'] = aggregated_data['Participant_ID'].map( HR_interval_median_map)  # quite a bit of noise/ spikey data in the RR_interval
aggregated_data['Calibration_Mean_Resting_HeartRate_RR_Interval'] = aggregated_data['Participant_ID'].map(HR_interval_mean_map)
aggregated_data['Calibration_SD_Resting_HeartRate_RR_Interval'] = aggregated_data['Participant_ID'].map(HR_interval_std_map)

#------------------------------------------------------------------------------------------------------------





#------------------------------------------------------------------------------------------------------------
#done
print(f"RAW DF: {len(calibration_data_raw.index)}")

for participant_id, group in calibration_data_raw.groupby('Participant_ID'):
    rr_intervals = group['Polar_HeartRate_RR_Interval']
    rmssd_participant = np.sqrt(np.mean(np.diff(rr_intervals) ** 2))
    aggregated_data.loc[
        aggregated_data['Participant_ID'] == participant_id, 'Calibration_RR_Interval_RAW_RMSSD'] = rmssd_participant
#------------------------------------------------------------------------------------------------------------





#------------------------------------------------------------------------------------------------------------
#done
# filtered_data = calibration_data_raw
filtered_data = calibration_data_raw[(calibration_data_raw['Polar_HeartRate_RR_Interval'] > 200) & (
            calibration_data_raw['Polar_HeartRate_RR_Interval'] < 2000)]
#------------------------------------------------------------------------------------------------------------





#------------------------------------------------------------------------------------------------------------
#done
HR_interval_median_map_ABS_Threshold = filtered_data.groupby('Participant_ID')['Polar_HeartRate_RR_Interval'].median().to_dict()
HR_interval_mean_map_ABS_Threshold = filtered_data.groupby('Participant_ID')['Polar_HeartRate_RR_Interval'].mean().to_dict()
HR_interval_std_map_ABS_Threshold = filtered_data.groupby('Participant_ID')['Polar_HeartRate_RR_Interval'].std().to_dict()
aggregated_data['Calibration_Median_Resting_HeartRate_RR_Interval_CLEANED_ABS_Threshold'] = aggregated_data['Participant_ID'].map(HR_interval_median_map_ABS_Threshold)
aggregated_data['Calibration_Mean_Resting_HeartRate_RR_Interval_CLEANED_ABS_Threshold'] = aggregated_data['Participant_ID'].map(HR_interval_mean_map_ABS_Threshold)
aggregated_data['Calibration_SD_Resting_HeartRate_RR_Interval_CLEANED_ABS_Threshold'] = aggregated_data['Participant_ID'].map(HR_interval_std_map_ABS_Threshold)
#------------------------------------------------------------------------------------------------------------





#------------------------------------------------------------------------------------------------------------
print(f"ABS DF: {len(filtered_data.index)}")
# Done

for participant_id, group in filtered_data.groupby('Participant_ID'):
    rr_intervals = group['Polar_HeartRate_RR_Interval']
    rmssd_participant = np.sqrt(np.mean(np.diff(rr_intervals) ** 2))
    aggregated_data.loc[aggregated_data[
                            'Participant_ID'] == participant_id, 'Calibration_RR_Interval_CLEANED_ABS_RMSSD'] = rmssd_participant
#------------------------------------------------------------------------------------------------------------





#------------------------------------------------------------------------------------------------------------
# Done
max_iterations = 20


def apply_relative_threshold(data, age):
    # print(len(data))
    # print(age)
    threshold = -age / 3 + 45
    # print(threshold)

    for _ in range(max_iterations):
        removed_indices = []
        for i in range(1, len(data) - 1):
            curr_val = data.iloc[i]['Polar_HeartRate_RR_Interval']
            prev_val = data.iloc[i - 1]['Polar_HeartRate_RR_Interval']
            next_val = data.iloc[i + 1]['Polar_HeartRate_RR_Interval']
            mean_val = (prev_val + next_val) / 2
            relative_change = (abs(curr_val - mean_val) / curr_val) * 100

            if relative_change > threshold:
                removed_indices.append(i)
        if len(removed_indices) == 0:
            print('Data Cleaning Complete!')
            break
        data = data.drop(data.index[removed_indices])
        print(f'Iteration {_} of Data Cleaning, {len(removed_indices)} values removed')
    return data

relative_filtered_data = pd.DataFrame()
age_column = 'Participant_Age'
for participant_id, group in filtered_data.groupby('Participant_ID'):
    print(f'Applying Relative Threshold for Participant {participant_id}')
    age = group[age_column].iloc[0]  # Assuming age is the same for all rows of a participant
    cleaned_group = apply_relative_threshold(group, age)
    relative_filtered_data = pd.concat([relative_filtered_data, cleaned_group])

#------------------------------------------------------------------------------------------------------------




#------------------------------------------------------------------------------------------------------------
# Done
HR_interval_median_map_REL_Threshold = relative_filtered_data.groupby('Participant_ID')['Polar_HeartRate_RR_Interval'].median().to_dict()
HR_interval_mean_map_REL_Threshold = relative_filtered_data.groupby('Participant_ID')['Polar_HeartRate_RR_Interval'].mean().to_dict()
HR_interval_std_map_REL_Threshold = relative_filtered_data.groupby('Participant_ID')['Polar_HeartRate_RR_Interval'].std().to_dict()
aggregated_data['Calibration_Median_Resting_HeartRate_RR_Interval_CLEANED_REL_Threshold'] = aggregated_data['Participant_ID'].map(HR_interval_median_map_REL_Threshold)
aggregated_data['Calibration_Mean_Resting_HeartRate_RR_Interval_CLEANED_REL_Threshold'] = aggregated_data['Participant_ID'].map(HR_interval_mean_map_REL_Threshold)
aggregated_data['Calibration_SD_Resting_HeartRate_RR_Interval_CLEANED_REL_Threshold'] = aggregated_data['Participant_ID'].map(HR_interval_std_map_REL_Threshold)
#------------------------------------------------------------------------------------------------------------





#------------------------------------------------------------------------------------------------------------
#done
print(f"REL DF: {len(relative_filtered_data.index)}")

# pd.set_option('display.max_columns', None)
# display(relative_filtered_data)

for participant_id, group in filtered_data.groupby('Participant_ID'):
    rr_intervals = group['Polar_HeartRate_RR_Interval']
    rmssd_participant = np.sqrt(np.mean(np.diff(rr_intervals) ** 2))
    aggregated_data.loc[aggregated_data[
                            'Participant_ID'] == participant_id, 'Calibration_RR_Interval_CLEANED_REL_RMSSD'] = rmssd_participant


#------------------------------------------------------------------------------------------------------------






#------------------------------------------------------------------------------------------------------------
# Done
GSR_Conductance_median_map = calibration_data_raw.groupby('Participant_ID')['Shimmer_D36A_GSR_Skin_Conductance_uS'].median().to_dict()
GSR_Conductance_mean_map = calibration_data_raw.groupby('Participant_ID')['Shimmer_D36A_GSR_Skin_Conductance_uS'].mean().to_dict()
GSR_Conductance_std_map = calibration_data_raw.groupby('Participant_ID')['Shimmer_D36A_GSR_Skin_Conductance_uS'].std().to_dict()
aggregated_data['Calibration_Median_GSR_Conductance'] = aggregated_data['Participant_ID'].map(GSR_Conductance_median_map)
aggregated_data['Calibration_Mean_GSR_Conductance'] = aggregated_data['Participant_ID'].map(GSR_Conductance_mean_map)
aggregated_data['Calibration_SD_GSR_Conductance'] = aggregated_data['Participant_ID'].map(GSR_Conductance_std_map)

GSR_Resistance_median_map = calibration_data_raw.groupby('Participant_ID')['Shimmer_D36A_GSR_Skin_Resistance_kOhms'].median().to_dict()
GSR_Resistance_mean_map = calibration_data_raw.groupby('Participant_ID')['Shimmer_D36A_GSR_Skin_Resistance_kOhms'].mean().to_dict()
GSR_Resistance_std_map = calibration_data_raw.groupby('Participant_ID')['Shimmer_D36A_GSR_Skin_Resistance_kOhms'].std().to_dict()
aggregated_data['Calibration_Median_GSR_Resistance'] = aggregated_data['Participant_ID'].map(GSR_Resistance_median_map)
aggregated_data['Calibration_Mean_GSR_Resistance'] = aggregated_data['Participant_ID'].map(GSR_Resistance_mean_map)
aggregated_data['Calibration_SD_GSR_Resistance'] = aggregated_data['Participant_ID'].map(GSR_Resistance_std_map)
#------------------------------------------------------------------------------------------------------------






#------------------------------------------------------------------------------------------------------------
# Done
filtered_data_conductance = (
    calibration_data_raw)[(calibration_data_raw['Shimmer_D36A_GSR_Skin_Resistance_kOhms'] > 0) &
    (calibration_data_raw['Shimmer_D36A_GSR_Skin_Resistance_kOhms'] < 2500) &
    (calibration_data_raw['Shimmer_D36A_GSR_Skin_Conductance_uS'] >= 0.1)]

#------------------------------------------------------------------------------------------------------------






#------------------------------------------------------------------------------------------------------------
# done
conductance_median_map_ABS_Threshold = filtered_data_conductance.groupby('Participant_ID')['Shimmer_D36A_GSR_Skin_Conductance_uS'].median().to_dict()
conductance_mean_map_ABS_Threshold = filtered_data_conductance.groupby('Participant_ID')['Shimmer_D36A_GSR_Skin_Conductance_uS'].mean().to_dict()
conductance_std_map_ABS_Threshold = filtered_data_conductance.groupby('Participant_ID')['Shimmer_D36A_GSR_Skin_Conductance_uS'].std().to_dict()
aggregated_data['Calibration_Median_GSR_Conductance_CLEANED_ABS_Threshold'] = aggregated_data['Participant_ID'].map(conductance_median_map_ABS_Threshold)
aggregated_data['Calibration_Mean_GSR_Conductance_CLEANED_ABS_Threshold'] = aggregated_data['Participant_ID'].map(conductance_mean_map_ABS_Threshold)
aggregated_data['Calibration_SD_GSR_Conductance_CLEANED_ABS_Threshold'] = aggregated_data['Participant_ID'].map(conductance_std_map_ABS_Threshold)
#------------------------------------------------------------------------------------------------------------


resistance_median_map_ABS_Threshold = filtered_data_conductance.groupby('Participant_ID')[
    'Shimmer_D36A_GSR_Skin_Resistance_kOhms'].median().to_dict()
resistance_mean_map_ABS_Threshold = filtered_data_conductance.groupby('Participant_ID')[
    'Shimmer_D36A_GSR_Skin_Resistance_kOhms'].mean().to_dict()
resistance_std_map_ABS_Threshold = filtered_data_conductance.groupby('Participant_ID')[
    'Shimmer_D36A_GSR_Skin_Resistance_kOhms'].std().to_dict()
aggregated_data['Calibration_Median_GSR_Resistance_CLEANED_ABS_Threshold'] = aggregated_data['Participant_ID'].map(
    resistance_median_map_ABS_Threshold)
aggregated_data['Calibration_Mean_GSR_Resistance_CLEANED_ABS_Threshold'] = aggregated_data['Participant_ID'].map(
    resistance_mean_map_ABS_Threshold)
aggregated_data['Calibration_SD_GSR_Resistance_CLEANED_ABS_Threshold'] = aggregated_data['Participant_ID'].map(
    resistance_std_map_ABS_Threshold)

lip_0_median_map = calibration_data_raw.groupby('Participant_ID')['0_Jaw_Forward'].median().to_dict()
lip_0_mean_map = calibration_data_raw.groupby('Participant_ID')['0_Jaw_Forward'].mean().to_dict()
lip_0_std_map = calibration_data_raw.groupby('Participant_ID')['0_Jaw_Forward'].std().to_dict()
aggregated_data['Calibration_Median_0_Jaw_Forward'] = aggregated_data['Participant_ID'].map(lip_0_median_map)
aggregated_data['Calibration_Mean_0_Jaw_Forward'] = aggregated_data['Participant_ID'].map(lip_0_mean_map)
aggregated_data['Calibration_SD_0_Jaw_Forward'] = aggregated_data['Participant_ID'].map(lip_0_std_map)

lip_1_median_map = calibration_data_raw.groupby('Participant_ID')['1_Jaw_Right'].median().to_dict()
lip_1_mean_map = calibration_data_raw.groupby('Participant_ID')['1_Jaw_Right'].mean().to_dict()
lip_1_std_map = calibration_data_raw.groupby('Participant_ID')['1_Jaw_Right'].std().to_dict()
aggregated_data['Calibration_Median_1_Jaw_Right'] = aggregated_data['Participant_ID'].map(lip_1_median_map)
aggregated_data['Calibration_Mean_1_Jaw_Right'] = aggregated_data['Participant_ID'].map(lip_1_mean_map)
aggregated_data['Calibration_SD_1_Jaw_Right'] = aggregated_data['Participant_ID'].map(lip_1_std_map)

lip_2_median_map = calibration_data_raw.groupby('Participant_ID')['2_Jaw_Left'].median().to_dict()
lip_2_mean_map = calibration_data_raw.groupby('Participant_ID')['2_Jaw_Left'].mean().to_dict()
lip_2_std_map = calibration_data_raw.groupby('Participant_ID')['2_Jaw_Left'].std().to_dict()
aggregated_data['Calibration_Median_2_Jaw_Left'] = aggregated_data['Participant_ID'].map(lip_2_median_map)
aggregated_data['Calibration_Mean_2_Jaw_Left'] = aggregated_data['Participant_ID'].map(lip_2_mean_map)
aggregated_data['Calibration_SD_2_Jaw_Left'] = aggregated_data['Participant_ID'].map(lip_2_std_map)

lip_3_median_map = calibration_data_raw.groupby('Participant_ID')['3_Jaw_Open'].median().to_dict()
lip_3_mean_map = calibration_data_raw.groupby('Participant_ID')['3_Jaw_Open'].mean().to_dict()
lip_3_std_map = calibration_data_raw.groupby('Participant_ID')['3_Jaw_Open'].std().to_dict()
aggregated_data['Calibration_Median_3_Jaw_Open'] = aggregated_data['Participant_ID'].map(lip_3_median_map)
aggregated_data['Calibration_Mean_3_Jaw_Open'] = aggregated_data['Participant_ID'].map(lip_3_mean_map)
aggregated_data['Calibration_SD_3_Jaw_Open'] = aggregated_data['Participant_ID'].map(lip_3_std_map)

lip_4_median_map = calibration_data_raw.groupby('Participant_ID')['4_Mouth_Ape_Shape'].median().to_dict()
lip_4_mean_map = calibration_data_raw.groupby('Participant_ID')['4_Mouth_Ape_Shape'].mean().to_dict()
lip_4_std_map = calibration_data_raw.groupby('Participant_ID')['4_Mouth_Ape_Shape'].std().to_dict()
aggregated_data['Calibration_Median_4_Mouth_Ape_Shape'] = aggregated_data['Participant_ID'].map(lip_4_median_map)
aggregated_data['Calibration_Mean_4_Mouth_Ape_Shape'] = aggregated_data['Participant_ID'].map(lip_4_mean_map)
aggregated_data['Calibration_SD_4_Mouth_Ape_Shape'] = aggregated_data['Participant_ID'].map(lip_4_std_map)

lip_5_median_map = calibration_data_raw.groupby('Participant_ID')['5_Mouth_O_Shape'].median().to_dict()
lip_5_mean_map = calibration_data_raw.groupby('Participant_ID')['5_Mouth_O_Shape'].mean().to_dict()
lip_5_std_map = calibration_data_raw.groupby('Participant_ID')['5_Mouth_O_Shape'].std().to_dict()
aggregated_data['Calibration_Median_5_Mouth_O_Shape'] = aggregated_data['Participant_ID'].map(lip_5_median_map)
aggregated_data['Calibration_Mean_5_Mouth_O_Shape'] = aggregated_data['Participant_ID'].map(lip_5_mean_map)
aggregated_data['Calibration_SD_5_Mouth_O_Shape'] = aggregated_data['Participant_ID'].map(lip_5_std_map)

lip_6_median_map = calibration_data_raw.groupby('Participant_ID')['6_Mouth_Pout'].median().to_dict()
lip_6_mean_map = calibration_data_raw.groupby('Participant_ID')['6_Mouth_Pout'].mean().to_dict()
lip_6_std_map = calibration_data_raw.groupby('Participant_ID')['6_Mouth_Pout'].std().to_dict()
aggregated_data['Calibration_Median_6_Mouth_Pout'] = aggregated_data['Participant_ID'].map(lip_6_median_map)
aggregated_data['Calibration_Mean_6_Mouth_Pout'] = aggregated_data['Participant_ID'].map(lip_6_mean_map)
aggregated_data['Calibration_SD_6_Mouth_Pout'] = aggregated_data['Participant_ID'].map(lip_6_std_map)

lip_7_median_map = calibration_data_raw.groupby('Participant_ID')['7_Mouth_Lower_Right'].median().to_dict()
lip_7_mean_map = calibration_data_raw.groupby('Participant_ID')['7_Mouth_Lower_Right'].mean().to_dict()
lip_7_std_map = calibration_data_raw.groupby('Participant_ID')['7_Mouth_Lower_Right'].std().to_dict()
aggregated_data['Calibration_Median_7_Mouth_Lower_Right'] = aggregated_data['Participant_ID'].map(lip_7_median_map)
aggregated_data['Calibration_Mean_7_Mouth_Lower_Right'] = aggregated_data['Participant_ID'].map(lip_7_mean_map)
aggregated_data['Calibration_SD_7_Mouth_Lower_Right'] = aggregated_data['Participant_ID'].map(lip_7_std_map)

lip_8_median_map = calibration_data_raw.groupby('Participant_ID')['8_Mouth_Lower_Left'].median().to_dict()
lip_8_mean_map = calibration_data_raw.groupby('Participant_ID')['8_Mouth_Lower_Left'].mean().to_dict()
lip_8_std_map = calibration_data_raw.groupby('Participant_ID')['8_Mouth_Lower_Left'].std().to_dict()
aggregated_data['Calibration_Median_8_Mouth_Lower_Left'] = aggregated_data['Participant_ID'].map(lip_8_median_map)
aggregated_data['Calibration_Mean_8_Mouth_Lower_Left'] = aggregated_data['Participant_ID'].map(lip_8_mean_map)
aggregated_data['Calibration_SD_8_Mouth_Lower_Left'] = aggregated_data['Participant_ID'].map(lip_8_std_map)

lip_9_median_map = calibration_data_raw.groupby('Participant_ID')['9_Mouth_Smile_Right'].median().to_dict()
lip_9_mean_map = calibration_data_raw.groupby('Participant_ID')['9_Mouth_Smile_Right'].mean().to_dict()
lip_9_std_map = calibration_data_raw.groupby('Participant_ID')['9_Mouth_Smile_Right'].std().to_dict()
aggregated_data['Calibration_Median_9_Mouth_Smile_Right'] = aggregated_data['Participant_ID'].map(lip_9_median_map)
aggregated_data['Calibration_Mean_9_Mouth_Smile_Right'] = aggregated_data['Participant_ID'].map(lip_9_mean_map)
aggregated_data['Calibration_SD_9_Mouth_Smile_Right'] = aggregated_data['Participant_ID'].map(lip_9_std_map)

lip_10_median_map = calibration_data_raw.groupby('Participant_ID')['10_Mouth_Smile_Left'].median().to_dict()
lip_10_mean_map = calibration_data_raw.groupby('Participant_ID')['10_Mouth_Smile_Left'].mean().to_dict()
lip_10_std_map = calibration_data_raw.groupby('Participant_ID')['10_Mouth_Smile_Left'].std().to_dict()
aggregated_data['Calibration_Median_10_Mouth_Smile_Left'] = aggregated_data['Participant_ID'].map(lip_10_median_map)
aggregated_data['Calibration_Mean_10_Mouth_Smile_Left'] = aggregated_data['Participant_ID'].map(lip_10_mean_map)
aggregated_data['Calibration_SD_10_Mouth_Smile_Left'] = aggregated_data['Participant_ID'].map(lip_10_std_map)

lip_11_median_map = calibration_data_raw.groupby('Participant_ID')['11_Mouth_Sad_Right'].median().to_dict()
lip_11_mean_map = calibration_data_raw.groupby('Participant_ID')['11_Mouth_Sad_Right'].mean().to_dict()
lip_11_std_map = calibration_data_raw.groupby('Participant_ID')['11_Mouth_Sad_Right'].std().to_dict()
aggregated_data['Calibration_Median_11_Mouth_Sad_Right'] = aggregated_data['Participant_ID'].map(lip_11_median_map)
aggregated_data['Calibration_Mean_11_Mouth_Sad_Right'] = aggregated_data['Participant_ID'].map(lip_11_mean_map)
aggregated_data['Calibration_SD_11_Mouth_Sad_Right'] = aggregated_data['Participant_ID'].map(lip_11_std_map)

lip_12_median_map = calibration_data_raw.groupby('Participant_ID')['12_Mouth_Sad_Left'].median().to_dict()
lip_12_mean_map = calibration_data_raw.groupby('Participant_ID')['12_Mouth_Sad_Left'].mean().to_dict()
lip_12_std_map = calibration_data_raw.groupby('Participant_ID')['12_Mouth_Sad_Left'].std().to_dict()
aggregated_data['Calibration_Median_12_Mouth_Sad_Left'] = aggregated_data['Participant_ID'].map(lip_12_median_map)
aggregated_data['Calibration_Mean_12_Mouth_Sad_Left'] = aggregated_data['Participant_ID'].map(lip_12_mean_map)
aggregated_data['Calibration_SD_12_Mouth_Sad_Left'] = aggregated_data['Participant_ID'].map(lip_12_std_map)

lip_13_median_map = calibration_data_raw.groupby('Participant_ID')['13_Cheek_Puff_Right'].median().to_dict()
lip_13_mean_map = calibration_data_raw.groupby('Participant_ID')['13_Cheek_Puff_Right'].mean().to_dict()
lip_13_std_map = calibration_data_raw.groupby('Participant_ID')['13_Cheek_Puff_Right'].std().to_dict()
aggregated_data['Calibration_Median_13_Cheek_Puff_Right'] = aggregated_data['Participant_ID'].map(lip_13_median_map)
aggregated_data['Calibration_Mean_13_Cheek_Puff_Right'] = aggregated_data['Participant_ID'].map(lip_13_mean_map)
aggregated_data['Calibration_SD_13_Cheek_Puff_Right'] = aggregated_data['Participant_ID'].map(lip_13_std_map)

lip_14_median_map = calibration_data_raw.groupby('Participant_ID')['14_Cheek_Puff_Left'].median().to_dict()
lip_14_mean_map = calibration_data_raw.groupby('Participant_ID')['14_Cheek_Puff_Left'].mean().to_dict()
lip_14_std_map = calibration_data_raw.groupby('Participant_ID')['14_Cheek_Puff_Left'].std().to_dict()
aggregated_data['Calibration_Median_14_Cheek_Puff_Left'] = aggregated_data['Participant_ID'].map(lip_14_median_map)
aggregated_data['Calibration_Mean_14_Cheek_Puff_Left'] = aggregated_data['Participant_ID'].map(lip_14_mean_map)
aggregated_data['Calibration_SD_14_Cheek_Puff_Left'] = aggregated_data['Participant_ID'].map(lip_14_std_map)

lip_15_median_map = calibration_data_raw.groupby('Participant_ID')['15_Mouth_Lower_Inside'].median().to_dict()
lip_15_mean_map = calibration_data_raw.groupby('Participant_ID')['15_Mouth_Lower_Inside'].mean().to_dict()
lip_15_std_map = calibration_data_raw.groupby('Participant_ID')['15_Mouth_Lower_Inside'].std().to_dict()
aggregated_data['Calibration_Median_15_Mouth_Lower_Inside'] = aggregated_data['Participant_ID'].map(lip_15_median_map)
aggregated_data['Calibration_Mean_15_Mouth_Lower_Inside'] = aggregated_data['Participant_ID'].map(lip_15_mean_map)
aggregated_data['Calibration_SD_15_Mouth_Lower_Inside'] = aggregated_data['Participant_ID'].map(lip_15_std_map)

lip_16_median_map = calibration_data_raw.groupby('Participant_ID')['16_Mouth_Upper_Inside'].median().to_dict()
lip_16_mean_map = calibration_data_raw.groupby('Participant_ID')['16_Mouth_Upper_Inside'].mean().to_dict()
lip_16_std_map = calibration_data_raw.groupby('Participant_ID')['16_Mouth_Upper_Inside'].std().to_dict()
aggregated_data['Calibration_Median_16_Mouth_Upper_Inside'] = aggregated_data['Participant_ID'].map(lip_16_median_map)
aggregated_data['Calibration_Mean_16_Mouth_Upper_Inside'] = aggregated_data['Participant_ID'].map(lip_16_mean_map)
aggregated_data['Calibration_SD_16_Mouth_Upper_Inside'] = aggregated_data['Participant_ID'].map(lip_16_std_map)

lip_17_median_map = calibration_data_raw.groupby('Participant_ID')['17_Mouth_Lower_Overlay'].median().to_dict()
lip_17_mean_map = calibration_data_raw.groupby('Participant_ID')['17_Mouth_Lower_Overlay'].mean().to_dict()
lip_17_std_map = calibration_data_raw.groupby('Participant_ID')['17_Mouth_Lower_Overlay'].std().to_dict()
aggregated_data['Calibration_Median_17_Mouth_Lower_Overlay'] = aggregated_data['Participant_ID'].map(lip_17_median_map)
aggregated_data['Calibration_Mean_17_Mouth_Lower_Overlay'] = aggregated_data['Participant_ID'].map(lip_17_mean_map)
aggregated_data['Calibration_SD_17_Mouth_Lower_Overlay'] = aggregated_data['Participant_ID'].map(lip_17_std_map)

lip_18_median_map = calibration_data_raw.groupby('Participant_ID')['18_Mouth_Upper_Overlay'].median().to_dict()
lip_18_mean_map = calibration_data_raw.groupby('Participant_ID')['18_Mouth_Upper_Overlay'].mean().to_dict()
lip_18_std_map = calibration_data_raw.groupby('Participant_ID')['18_Mouth_Upper_Overlay'].std().to_dict()
aggregated_data['Calibration_Median_18_Mouth_Upper_Overlay'] = aggregated_data['Participant_ID'].map(lip_18_median_map)
aggregated_data['Calibration_Mean_18_Mouth_Upper_Overlay'] = aggregated_data['Participant_ID'].map(lip_18_mean_map)
aggregated_data['Calibration_SD_18_Mouth_Upper_Overlay'] = aggregated_data['Participant_ID'].map(lip_18_std_map)

lip_19_median_map = calibration_data_raw.groupby('Participant_ID')['19_Cheek_Suck'].median().to_dict()
lip_19_mean_map = calibration_data_raw.groupby('Participant_ID')['19_Cheek_Suck'].mean().to_dict()
lip_19_std_map = calibration_data_raw.groupby('Participant_ID')['19_Cheek_Suck'].std().to_dict()
aggregated_data['Calibration_Median_19_Cheek_Suck'] = aggregated_data['Participant_ID'].map(lip_19_median_map)
aggregated_data['Calibration_Mean_19_Cheek_Suck'] = aggregated_data['Participant_ID'].map(lip_19_mean_map)
aggregated_data['Calibration_SD_19_Cheek_Suck'] = aggregated_data['Participant_ID'].map(lip_19_std_map)

lip_20_median_map = calibration_data_raw.groupby('Participant_ID')['20_Mouth_LowerRight_Down'].median().to_dict()
lip_20_mean_map = calibration_data_raw.groupby('Participant_ID')['20_Mouth_LowerRight_Down'].mean().to_dict()
lip_20_std_map = calibration_data_raw.groupby('Participant_ID')['20_Mouth_LowerRight_Down'].std().to_dict()
aggregated_data['Calibration_Median_20_Mouth_LowerRight_Down'] = aggregated_data['Participant_ID'].map(
    lip_20_median_map)
aggregated_data['Calibration_Mean_20_Mouth_LowerRight_Down'] = aggregated_data['Participant_ID'].map(lip_20_mean_map)
aggregated_data['Calibration_SD_20_Mouth_LowerRight_Down'] = aggregated_data['Participant_ID'].map(lip_20_std_map)

lip_21_median_map = calibration_data_raw.groupby('Participant_ID')['21_Mouth_LowerLeft_Down'].median().to_dict()
lip_21_mean_map = calibration_data_raw.groupby('Participant_ID')['21_Mouth_LowerLeft_Down'].mean().to_dict()
lip_21_std_map = calibration_data_raw.groupby('Participant_ID')['21_Mouth_LowerLeft_Down'].std().to_dict()
aggregated_data['Calibration_Median_21_Mouth_LowerLeft_Down'] = aggregated_data['Participant_ID'].map(lip_21_median_map)
aggregated_data['Calibration_Mean_21_Mouth_LowerLeft_Down'] = aggregated_data['Participant_ID'].map(lip_21_mean_map)
aggregated_data['Calibration_SD_21_Mouth_LowerLeft_Down'] = aggregated_data['Participant_ID'].map(lip_21_std_map)

lip_22_median_map = calibration_data_raw.groupby('Participant_ID')['22_Mouth_UpperRight_Up'].median().to_dict()
lip_22_mean_map = calibration_data_raw.groupby('Participant_ID')['22_Mouth_UpperRight_Up'].mean().to_dict()
lip_22_std_map = calibration_data_raw.groupby('Participant_ID')['22_Mouth_UpperRight_Up'].std().to_dict()
aggregated_data['Calibration_Median_22_Mouth_UpperRight_Up'] = aggregated_data['Participant_ID'].map(lip_22_median_map)
aggregated_data['Calibration_Mean_22_Mouth_UpperRight_Up'] = aggregated_data['Participant_ID'].map(lip_22_mean_map)
aggregated_data['Calibration_SD_22_Mouth_UpperRight_Up'] = aggregated_data['Participant_ID'].map(lip_22_std_map)

lip_23_median_map = calibration_data_raw.groupby('Participant_ID')['23_Mouth_UpperLeft_Up'].median().to_dict()
lip_23_mean_map = calibration_data_raw.groupby('Participant_ID')['23_Mouth_UpperLeft_Up'].mean().to_dict()
lip_23_std_map = calibration_data_raw.groupby('Participant_ID')['23_Mouth_UpperLeft_Up'].std().to_dict()
aggregated_data['Calibration_Median_23_Mouth_UpperLeft_Up'] = aggregated_data['Participant_ID'].map(lip_23_median_map)
aggregated_data['Calibration_Mean_23_Mouth_UpperLeft_Up'] = aggregated_data['Participant_ID'].map(lip_23_mean_map)
aggregated_data['Calibration_SD_23_Mouth_UpperLeft_Up'] = aggregated_data['Participant_ID'].map(lip_23_std_map)

lip_24_median_map = calibration_data_raw.groupby('Participant_ID')['24_Mouth_Philtrum_Right'].median().to_dict()
lip_24_mean_map = calibration_data_raw.groupby('Participant_ID')['24_Mouth_Philtrum_Right'].mean().to_dict()
lip_24_std_map = calibration_data_raw.groupby('Participant_ID')['24_Mouth_Philtrum_Right'].std().to_dict()
aggregated_data['Calibration_Median_24_Mouth_Philtrum_Right'] = aggregated_data['Participant_ID'].map(lip_24_median_map)
aggregated_data['Calibration_Mean_24_Mouth_Philtrum_Right'] = aggregated_data['Participant_ID'].map(lip_24_mean_map)
aggregated_data['Calibration_SD_24_Mouth_Philtrum_Right'] = aggregated_data['Participant_ID'].map(lip_24_std_map)

lip_25_median_map = calibration_data_raw.groupby('Participant_ID')['25_Mouth_Philtrum_Left'].median().to_dict()
lip_25_mean_map = calibration_data_raw.groupby('Participant_ID')['25_Mouth_Philtrum_Left'].mean().to_dict()
lip_25_std_map = calibration_data_raw.groupby('Participant_ID')['25_Mouth_Philtrum_Left'].std().to_dict()
aggregated_data['Calibration_Median_25_Mouth_Philtrum_Left'] = aggregated_data['Participant_ID'].map(lip_25_median_map)
aggregated_data['Calibration_Mean_25_Mouth_Philtrum_Left'] = aggregated_data['Participant_ID'].map(lip_25_mean_map)
aggregated_data['Calibration_SD_25_Mouth_Philtrum_Left'] = aggregated_data['Participant_ID'].map(lip_25_std_map)

lip_26_median_map = calibration_data_raw.groupby('Participant_ID')['26_Max'].median().to_dict()
lip_26_mean_map = calibration_data_raw.groupby('Participant_ID')['26_Max'].mean().to_dict()
lip_26_std_map = calibration_data_raw.groupby('Participant_ID')['26_Max'].std().to_dict()
aggregated_data['Calibration_Median_26_Max'] = aggregated_data['Participant_ID'].map(lip_26_median_map)
aggregated_data['Calibration_Mean_26_Max'] = aggregated_data['Participant_ID'].map(lip_26_mean_map)
aggregated_data['Calibration_SD_26_Max'] = aggregated_data['Participant_ID'].map(lip_26_std_map)

# reoredered_columns = ['ESM_Unity_Frame','ESM_Unity_Timestamp', 'ESM_Fear_Value', 'ESM_Bored_Value', 'ESM_Joy_Value', 'ESM_Relaxation_Value', 'ESM_Presence_Value']
data_header_calibration_measures = ['Calibration_Median_Resting_HeartRate', 'Calibration_Mean_Resting_HeartRate',
                                    'Calibration_SD_Resting_HeartRate',
                                    'Calibration_Median_Resting_HeartRate_RR_Interval',
                                    'Calibration_Mean_Resting_HeartRate_RR_Interval',
                                    'Calibration_SD_Resting_HeartRate_RR_Interval',
                                    'Calibration_Median_Resting_HeartRate_RR_Interval_CLEANED_ABS_Threshold',
                                    'Calibration_Mean_Resting_HeartRate_RR_Interval_CLEANED_ABS_Threshold',
                                    'Calibration_SD_Resting_HeartRate_RR_Interval_CLEANED_ABS_Threshold',
                                    'Calibration_Median_Resting_HeartRate_RR_Interval_CLEANED_REL_Threshold',
                                    'Calibration_Mean_Resting_HeartRate_RR_Interval_CLEANED_REL_Threshold',
                                    'Calibration_SD_Resting_HeartRate_RR_Interval_CLEANED_REL_Threshold',
                                    'Calibration_RR_Interval_RAW_RMSSD', 'Calibration_RR_Interval_CLEANED_ABS_RMSSD',
                                    'Calibration_RR_Interval_CLEANED_REL_RMSSD',
                                    'Calibration_Median_GSR_Conductance', 'Calibration_Mean_GSR_Conductance',
                                    'Calibration_SD_GSR_Conductance', 'Calibration_Median_GSR_Resistance',
                                    'Calibration_Mean_GSR_Resistance', 'Calibration_SD_GSR_Resistance',
                                    'Calibration_Median_GSR_Conductance_CLEANED_ABS_Threshold',
                                    'Calibration_Mean_GSR_Conductance_CLEANED_ABS_Threshold',
                                    'Calibration_SD_GSR_Conductance_CLEANED_ABS_Threshold',
                                    'Calibration_Median_GSR_Resistance_CLEANED_ABS_Threshold',
                                    'Calibration_Mean_GSR_Resistance_CLEANED_ABS_Threshold',
                                    'Calibration_SD_GSR_Resistance_CLEANED_ABS_Threshold',
                                    'Calibration_Median_0_Jaw_Forward', 'Calibration_Mean_0_Jaw_Forward',
                                    'Calibration_SD_0_Jaw_Forward', 'Calibration_Median_1_Jaw_Right',
                                    'Calibration_Mean_1_Jaw_Right', 'Calibration_SD_1_Jaw_Right',
                                    'Calibration_Median_2_Jaw_Left', 'Calibration_Mean_2_Jaw_Left',
                                    'Calibration_SD_2_Jaw_Left', 'Calibration_Median_3_Jaw_Open',
                                    'Calibration_Mean_3_Jaw_Open', 'Calibration_SD_3_Jaw_Open',
                                    'Calibration_Median_4_Mouth_Ape_Shape', 'Calibration_Mean_4_Mouth_Ape_Shape',
                                    'Calibration_SD_4_Mouth_Ape_Shape', 'Calibration_Median_5_Mouth_O_Shape',
                                    'Calibration_Mean_5_Mouth_O_Shape', 'Calibration_SD_5_Mouth_O_Shape',
                                    'Calibration_Median_6_Mouth_Pout', 'Calibration_Mean_6_Mouth_Pout',
                                    'Calibration_SD_6_Mouth_Pout',
                                    'Calibration_Median_7_Mouth_Lower_Right', 'Calibration_Mean_7_Mouth_Lower_Right',
                                    'Calibration_SD_7_Mouth_Lower_Right', 'Calibration_Median_8_Mouth_Lower_Left',
                                    'Calibration_Mean_8_Mouth_Lower_Left', 'Calibration_SD_8_Mouth_Lower_Left',
                                    'Calibration_Median_9_Mouth_Smile_Right', 'Calibration_Mean_9_Mouth_Smile_Right',
                                    'Calibration_SD_9_Mouth_Smile_Right', 'Calibration_Median_10_Mouth_Smile_Left',
                                    'Calibration_Mean_10_Mouth_Smile_Left', 'Calibration_SD_10_Mouth_Smile_Left',
                                    'Calibration_Median_11_Mouth_Sad_Right', 'Calibration_Mean_11_Mouth_Sad_Right',
                                    'Calibration_SD_11_Mouth_Sad_Right', 'Calibration_Median_12_Mouth_Sad_Left',
                                    'Calibration_Mean_12_Mouth_Sad_Left', 'Calibration_SD_12_Mouth_Sad_Left',
                                    'Calibration_Median_13_Cheek_Puff_Right', 'Calibration_Mean_13_Cheek_Puff_Right',
                                    'Calibration_SD_13_Cheek_Puff_Right', 'Calibration_Median_14_Cheek_Puff_Left',
                                    'Calibration_Mean_14_Cheek_Puff_Left', 'Calibration_SD_14_Cheek_Puff_Left',
                                    'Calibration_Median_15_Mouth_Lower_Inside',
                                    'Calibration_Mean_15_Mouth_Lower_Inside', 'Calibration_SD_15_Mouth_Lower_Inside',
                                    'Calibration_Median_16_Mouth_Upper_Inside',
                                    'Calibration_Mean_16_Mouth_Upper_Inside', 'Calibration_SD_16_Mouth_Upper_Inside',
                                    'Calibration_Median_17_Mouth_Lower_Overlay',
                                    'Calibration_Mean_17_Mouth_Lower_Overlay',
                                    'Calibration_SD_17_Mouth_Lower_Overlay',
                                    'Calibration_Median_18_Mouth_Upper_Overlay',
                                    'Calibration_Mean_18_Mouth_Upper_Overlay', 'Calibration_SD_18_Mouth_Upper_Overlay',
                                    'Calibration_Median_19_Cheek_Suck', 'Calibration_Mean_19_Cheek_Suck',
                                    'Calibration_SD_19_Cheek_Suck', 'Calibration_Median_20_Mouth_LowerRight_Down',
                                    'Calibration_Mean_20_Mouth_LowerRight_Down',
                                    'Calibration_SD_20_Mouth_LowerRight_Down',
                                    'Calibration_Median_21_Mouth_LowerLeft_Down',
                                    'Calibration_Mean_21_Mouth_LowerLeft_Down',
                                    'Calibration_SD_21_Mouth_LowerLeft_Down',
                                    'Calibration_Median_22_Mouth_UpperRight_Up',
                                    'Calibration_Mean_22_Mouth_UpperRight_Up',
                                    'Calibration_SD_22_Mouth_UpperRight_Up', 'Calibration_Median_23_Mouth_UpperLeft_Up',
                                    'Calibration_Mean_23_Mouth_UpperLeft_Up', 'Calibration_SD_23_Mouth_UpperLeft_Up',
                                    'Calibration_Median_24_Mouth_Philtrum_Right',
                                    'Calibration_Mean_24_Mouth_Philtrum_Right',
                                    'Calibration_SD_24_Mouth_Philtrum_Right',
                                    'Calibration_Median_25_Mouth_Philtrum_Left',
                                    'Calibration_Mean_25_Mouth_Philtrum_Left', 'Calibration_SD_25_Mouth_Philtrum_Left',
                                    'Calibration_Median_26_Max', 'Calibration_Mean_26_Max', 'Calibration_SD_26_Max',
                                    'Calibration_PupilDilation_Left_0', 'Calibration_PupilDilation_Right_0',
                                    'Calibration_PupilDilation_Left_16', 'Calibration_PupilDilation_Right_16',
                                    'Calibration_PupilDilation_Left_32',
                                    'Calibration_PupilDilation_Right_32', 'Calibration_PupilDilation_Left_48',
                                    'Calibration_PupilDilation_Right_48', 'Calibration_PupilDilation_Left_64',
                                    'Calibration_PupilDilation_Right_64', 'Calibration_PupilDilation_Left_80',
                                    'Calibration_PupilDilation_Right_80', 'Calibration_PupilDilation_Left_96',
                                    'Calibration_PupilDilation_Right_96',
                                    'Calibration_PupilDilation_Left_112', 'Calibration_PupilDilation_Right_112',
                                    'Calibration_PupilDilation_Left_128', 'Calibration_PupilDilation_Right_128',
                                    'Calibration_PupilDilation_Left_144', 'Calibration_PupilDilation_Right_144',
                                    'Calibration_PupilDilation_Left_160', 'Calibration_PupilDilation_Right_160',
                                    'Calibration_PupilDilation_Left_176',
                                    'Calibration_PupilDilation_Right_176', 'Calibration_PupilDilation_Left_192',
                                    'Calibration_PupilDilation_Right_192', 'Calibration_PupilDilation_Left_208',
                                    'Calibration_PupilDilation_Right_208', 'Calibration_PupilDilation_Left_224',
                                    'Calibration_PupilDilation_Right_224', 'Calibration_PupilDilation_Left_240',
                                    'Calibration_PupilDilation_Right_240',
                                    'Calibration_PupilDilation_Left_255', 'Calibration_PupilDilation_Right_255']

aggregated_data = place_columns_after_named_column(aggregated_data, 'Fear_Baseline', data_header_calibration_measures)

merged_data = aggregated_data


#####################################End of Calibration Part of things###############################################################