#----------------------------------------------------------------------------------------------------
# Dilation Data
Node 1 - Pupil dilation data processing

GUI part:
Dataframe Input - 2 , data datafame (calibration data) and target dataframe (aggregated_data)
User Input - 4, users must specify:
    1. list of possible grayscale_values
    2. col name of grey scale value
    3. col name we want to merge on
    4. col name with median pupil dilation left data
    5. col name with median pupil dilation right data

output - 1 modified target dataframe


backend implementation (variables represent a corresponding user input):

possible_grayscale_values = [...] - user inputted list of possible grayscale values
col_shown_gray_scale_value_name = 'Shown_Gray_Scale_Value' - user inputted string
col_name_to_merge_on = 'Participant_ID' - user inputted string
col_name_of_median_pupil_dilation_left = 'Median_Pupil_Dilation_Left' - user inputted string
col_name_of_median_pupil_dilation_right = 'Median_Pupil_Dilation_Right' - user inputted string

# Iterate through each possible value
for value in possible_grayscale_values:
    # Filter rows where Shown_Gray_Scale_Value equals the current value
    filtered_data = calibration_data[calibration_data[col_shown_gray_scale_value_name] == value]

    # Create a dictionary with Participant_ID as the index and median values as values
    median_dict = filtered_data.set_index(col_name_to_merge_on)[
        [col_name_of_median_pupil_dilation_left, col_name_of_median_pupil_dilation_right]].to_dict()

    # Column names for the existing median value columns
    col_left = f'Calibration_PupilDilation_Left_{value}'
    col_right = f'Calibration_PupilDilation_Right_{value}'

    # Update the existing columns in 'aggregate_data' with the calculated median values
    aggregated_data.loc[:, col_left] = aggregated_data[col_name_to_merge_on].map(median_dict[col_name_of_median_pupil_dilation_left])
    aggregated_data.loc[:, col_right] = aggregated_data[col_name_to_merge_on].map(
        median_dict[col_name_of_median_pupil_dilation_right])





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

#----------------------------------------------------------------------------------------------------




#----------------------------------------------------------------------------------------------------
Node 2:

GUI part:
Dataframe Input - 2 (calibration_data_raw and aggregated_data)
    users must specify the dataframe to be used for the grouping operation and the dataframe have the mapping performed on it
User Input - 4, users must specify:
    1. data dataframe (calibration_data_raw in the case below)
    2. target dataframe (aggregated_data), single grouping value
    3. groupby column (single)
    3. column to get series (single)
    4. checkbox ticking what should be computed: median, mean and std  and a corresponding name for each checkbox so we know what the column name should be
    5. name for each checkbox ticked that the user must enter
output - 1 modified target dataframe


backend implementation (variables represent a corresponding user input):
a = 'Participant_ID'
b = 'Polar_HearRateBPM'
c = ['median', 'mean', 'std'] - filled in based on a checkbox that the user ticks
d = ['output_column_median, output_column_mean, output_column_std'] - for each checkbox ticked, users are forced to type in a name for what they want the output column name to be. We have to
stats = calibration_data_raw.groupby(a)[b].agg(c)

# Merge the statistics into aggregated_data in one operation
aggregated_data = aggregated_data.merge(
    stats.rename(columns={
        c[0]: d[0]
        c[1]: d[1]
        c[2]: d[2]
    }),
    left_on=a,
    right_index=True,
    how='left'
)


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

HR_interval_median_map_ABS_Threshold = filtered_data.groupby('Participant_ID')['Polar_HeartRate_RR_Interval'].median().to_dict()
HR_interval_mean_map_ABS_Threshold = filtered_data.groupby('Participant_ID')['Polar_HeartRate_RR_Interval'].mean().to_dict()
HR_interval_std_map_ABS_Threshold = filtered_data.groupby('Participant_ID')['Polar_HeartRate_RR_Interval'].std().to_dict()
aggregated_data['Calibration_Median_Resting_HeartRate_RR_Interval_CLEANED_ABS_Threshold'] = aggregated_data['Participant_ID'].map(HR_interval_median_map_ABS_Threshold)
aggregated_data['Calibration_Mean_Resting_HeartRate_RR_Interval_CLEANED_ABS_Threshold'] = aggregated_data['Participant_ID'].map(HR_interval_mean_map_ABS_Threshold)
aggregated_data['Calibration_SD_Resting_HeartRate_RR_Interval_CLEANED_ABS_Threshold'] = aggregated_data['Participant_ID'].map(HR_interval_std_map_ABS_Threshold)

HR_interval_median_map_REL_Threshold = relative_filtered_data.groupby('Participant_ID')['Polar_HeartRate_RR_Interval'].median().to_dict()
HR_interval_mean_map_REL_Threshold = relative_filtered_data.groupby('Participant_ID')['Polar_HeartRate_RR_Interval'].mean().to_dict()
HR_interval_std_map_REL_Threshold = relative_filtered_data.groupby('Participant_ID')['Polar_HeartRate_RR_Interval'].std().to_dict()
aggregated_data['Calibration_Median_Resting_HeartRate_RR_Interval_CLEANED_REL_Threshold'] = aggregated_data['Participant_ID'].map(HR_interval_median_map_REL_Threshold)
aggregated_data['Calibration_Mean_Resting_HeartRate_RR_Interval_CLEANED_REL_Threshold'] = aggregated_data['Participant_ID'].map(HR_interval_mean_map_REL_Threshold)
aggregated_data['Calibration_SD_Resting_HeartRate_RR_Interval_CLEANED_REL_Threshold'] = aggregated_data['Participant_ID'].map(HR_interval_std_map_REL_Threshold)

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


conductance_median_map_ABS_Threshold = filtered_data_conductance.groupby('Participant_ID')['Shimmer_D36A_GSR_Skin_Conductance_uS'].median().to_dict()
conductance_mean_map_ABS_Threshold = filtered_data_conductance.groupby('Participant_ID')['Shimmer_D36A_GSR_Skin_Conductance_uS'].mean().to_dict()
conductance_std_map_ABS_Threshold = filtered_data_conductance.groupby('Participant_ID')['Shimmer_D36A_GSR_Skin_Conductance_uS'].std().to_dict()
aggregated_data['Calibration_Median_GSR_Conductance_CLEANED_ABS_Threshold'] = aggregated_data['Participant_ID'].map(conductance_median_map_ABS_Threshold)
aggregated_data['Calibration_Mean_GSR_Conductance_CLEANED_ABS_Threshold'] = aggregated_data['Participant_ID'].map(conductance_mean_map_ABS_Threshold)
aggregated_data['Calibration_SD_GSR_Conductance_CLEANED_ABS_Threshold'] = aggregated_data['Participant_ID'].map(conductance_std_map_ABS_Threshold)


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
#----------------------------------------------------------------------------------------------------




#----------------------------------------------------------------------------------------------------
Node 3 - data filtering with thresholds

GUI part:
Dataframe input - 1 (calibration_data_raw)
User input - 4
    1. Conditions blocks
        a. user inputted column, user inputed condition (greater than, less than, equal to, etc) and numerical value
        b. conditions between condition blocks (&, |, etc) - user inputted (optional if only one condition block)
note: users should be able to add condition blocks to some list and customise them and the conditions between condition blocks.
Output - 1
    1. filtered dataframe


backend implementation (variables represent a corresponding user input) - how will the data be stored so we know how we can actually use it:
data = [(col_name, condition_str, numerical_value), (col_name, condition_str, numerical_value), ... ] - list of tuples where eac tuple represents a full condition block
func = lambda col_name, condition_str, numerical_value : dataframe_input1[col_name] eval(condition_str) numerical_value


filtered_data = calibration_data_raw[(calibration_data_raw['Polar_HeartRate_RR_Interval'] > 200) & (
            calibration_data_raw['Polar_HeartRate_RR_Interval'] < 2000)]

filtered_data_conductance = (
    calibration_data_raw)[(calibration_data_raw['Shimmer_D36A_GSR_Skin_Resistance_kOhms'] > 0) &
    (calibration_data_raw['Shimmer_D36A_GSR_Skin_Resistance_kOhms'] < 2500) &
    (calibration_data_raw['Shimmer_D36A_GSR_Skin_Conductance_uS'] >= 0.1)]
#----------------------------------------------------------------------------------------------------





flesh these last 2 nodes out after implementing node 3 and 4 and the rest of the existing nodes (including their BE implementation)
#----------------------------------------------------------------------------------------------------



Node 4 - compute rmssd node

GUI part:
Dataframe Input - 2 (calibration_data_raw (data dataframe) and aggregated_data (target dataframe))
    users must specify the dataframe to be used for the grouping operation and the dataframe have the mapping performed on it
User Input - 3, users must specify:
    1. user inputs: groupby/merge key column (add a hint that this key is also we we will use to merge back on in the target dataframe), RR interval column, output column name (does this make sense? Run through a toy example to see the inputs make sense according to how the data is processed/the intent of the user)

groupbykey = 'Participant_ID'
datacolumn ='Polar_HeartRate_RR_Interval'
output_column_name = 'Calibration_RR_Interval_RAW_RMSSD'

for participant_id, group in calibration_data_raw.groupby(groupbykey):
    rr_intervals = group[datacolumn]
    rmssd_participant = np.sqrt(np.mean(np.diff(rr_intervals) ** 2))
    aggregated_data.loc[
        aggregated_data[groupbykey] == participant_id, output_column_name] = rmssd_participant




output - 1 modified target dataframe

for participant_id, group in calibration_data_raw.groupby('Participant_ID'):
    rr_intervals = group['Polar_HeartRate_RR_Interval']
    rmssd_participant = np.sqrt(np.mean(np.diff(rr_intervals) ** 2))
    aggregated_data.loc[
        aggregated_data['Participant_ID'] == participant_id, 'Calibration_RR_Interval_RAW_RMSSD'] = rmssd_participant

for participant_id, group in filtered_data.groupby('Participant_ID'):
    rr_intervals = group['Polar_HeartRate_RR_Interval']
    rmssd_participant = np.sqrt(np.mean(np.diff(rr_intervals) ** 2))
    aggregated_data.loc[aggregated_data[
                            'Participant_ID'] == participant_id, 'Calibration_RR_Interval_CLEANED_ABS_RMSSD'] = rmssd_participant


for participant_id, group in filtered_data.groupby('Participant_ID'):
    rr_intervals = group['Polar_HeartRate_RR_Interval']
    rmssd_participant = np.sqrt(np.mean(np.diff(rr_intervals) ** 2))
    aggregated_data.loc[aggregated_data[
                            'Participant_ID'] == participant_id, 'Calibration_RR_Interval_CLEANED_REL_RMSSD'] = rmssd_participant

#----------------------------------------------------------------------------------------------------
Node 5 - Age adaptive RR-Interval Artifact Filter -> returns a dataframe with only rows that passed the cleaning process

GUI part:
Dataframe Input - 2 (calibration_data_raw (data dataframe) and an empty dataframe to store the results in which is then outputted
Dataframe output - newly filled empty dataframe.

User Input - 3, users must specify:
    1. user inputs:
       a. groupby/merge key column,
       b. age column,
       c. RR interval column,

backend:
groupby_column = 'Participant_ID'
age_column = 'Age'
rr_interval_column = 'Polar_HeartRate_RR_Interval'



max_iterations = 20

def apply_relative_threshold(data, age):
    # print(len(data))
    # print(age)
    threshold = -age / 3 + 45
    # print(threshold)

    for _ in range(max_iterations):
        removed_indices = []
        for i in range(1, len(data) - 1):
            curr_val = data.iloc[i][rr_interval_column]
            prev_val = data.iloc[i - 1][rr_interval_column]
            next_val = data.iloc[i + 1][rr_interval_column]
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
for participant_id, group in filtered_data.groupby(groupby_column):
    print(f'Applying Relative Threshold for Participant {participant_id}')
    age = group[age_column].iloc[0]  # Assuming age is the same for all rows of a participant
    cleaned_group = apply_relative_threshold(group, age)
    relative_filtered_data = pd.concat([relative_filtered_data, cleaned_group])








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

#----------------------------------------------------------------------------------------------------
