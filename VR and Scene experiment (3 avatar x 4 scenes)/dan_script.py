import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv
import os
from scipy.special import softmax
from tqdm.auto import tqdm

tqdm.pandas()

data_path = "DATA/RAW/"
questionnaire_path = "DATA/Questionnaire/"

"""
Qing's notes (not fully tested but it's my guess on what's happening)
-----------------------------
brief summary: - Sequentially loads csv file, only those that pass the filter, as dataframe (2d table) -> 
                 appends to list ->concatenate all dataframes so we get a single massive dataframe 

notes:
1. Think about data frame formatting, what constraints exist for the concatenation of multiple dataframes to go 
   as expected - same number of rows + columns? Must column names match


points of confusion (cleared):
1. filename "for filename in os.listdir(folder_path)" gets us only the file name within the folder_path, not the 
   full path, hence why we have to do to "os.path.join(folder_path, filename)"

-----------------------------
"""


def load_multiple_files_into_dataframe_with_exclusion(folder_path, file_name_text, exclude_text):
    # Initialize an empty list to store individual DataFrames
    df_list = []

    # Iterate through files in the folder
    for filename in os.listdir(folder_path):
        # Check if the file is a CSV file and matches the naming pattern
        if filename.endswith('.csv') and file_name_text in filename and not exclude_text in filename:
            file_path = os.path.join(folder_path, filename)
            print('reading... ' + file_path)
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file_path, index_col=False)

            # Append the DataFrame to the list
            df_list.append(df)

    # Concatenate all DataFrames into one DataFrame
    combined_df = pd.concat(df_list, ignore_index=True)

    return combined_df


"""
Qing's notes (not fully tested but it's my guess on what's happening)
-----------------------------
brief summary - sequentially loads csv file as dataframe (2d table) -> appends to list ->  
                concatenate all dataframes so we get a single massive dataframe 

notes:
1. Think about data frame formatting, what constraints exist for the concatenation of multiple dataframes to go 
   as expected - same number of rows + columns? Must column names match?


points of confusion (cleared):
1. filename "for filename in os.listdir(folder_path)" gets us only the file name within the folder_path, not the 
   full path, hence why we have to do to {os.path.join(folder_path, filename}"

-----------------------------
"""


def load_multiple_files_into_dataframe(folder_path, file_name_text):
    # Initialize an empty list to store individual DataFrames
    df_list = []

    # Iterate through files in the folder
    for filename in os.listdir(folder_path):
        # Check if the file is a CSV file and matches the naming pattern
        if filename.endswith('.csv') and file_name_text in filename:
            file_path = os.path.join(folder_path, filename)
            print('reading... ' + file_path)
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file_path)

            # Append the DataFrame to the list
            df_list.append(df)

    # Concatenate all DataFrames into one DataFrame
    combined_df = pd.concat(df_list, ignore_index=True)

    return combined_df


################################################################################################
# Loop through each CSV file in the directory
for filename in os.listdir(data_path):
    if filename.endswith('_Calibration_Data_RAW.csv') and 'BLINK' not in filename:
        file_path = os.path.join(data_path, filename)
        # Read the contents of the file
        with open(file_path, 'r') as file:
            data = file.read()

        # Correct the header
        corrected_data = data.replace('current_InterBlinkIntervalShimmer_D36A_GSR_Skin_Conductance_uS',
                                      'current_InterBlinkInterval,Shimmer_D36A_GSR_Skin_Conductance_uS')

        # Write the corrected data back to the file
        with open(file_path, 'w') as file:
            file.write(corrected_data)


def remove_extra_comma(file_path):
    # Create a temporary file to store the corrected data
    temp_file_path = file_path + '.tmp'

    with open(file_path, 'r', newline='') as input_file, \
            open(temp_file_path, 'w', newline='') as output_file:

        reader = csv.reader(input_file)
        writer = csv.writer(output_file)

        for row in reader:
            # Remove the last element if it's an empty string (extra comma)
            if row[-1] == '':
                row = row[:-1]
            writer.writerow(row)

    # Replace the original file with the corrected data
    os.remove(file_path)
    os.rename(temp_file_path, file_path)


def remove_extra_comma_from_files(folder_path):
    # Iterate over all CSV files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith('_Calibration_Data_RAW.csv') and 'BLINK' not in file_name:
            file_path = os.path.join(folder_path, file_name)
            remove_extra_comma(file_path)


remove_extra_comma_from_files(data_path)

#--------------------------------------------------------------Beginning of questionnaire processing -------------------------------------------------------------------------------------#

# Questionnaire_Data - loading and value replacement (only modifies the values that exist to a different representaion, it doesn't perform data cleaning)

# scanning_session questionnaire
questionnaire_demog = pd.read_csv(questionnaire_path + "Scanning_Session_Questionnaire.csv")
# ToDO: Anca do the replacement -
questionnaire_demog['Gender'] = questionnaire_demog['Gender'].replace(1, 'Female')
questionnaire_demog['Gender'] = questionnaire_demog['Gender'].replace(2, 'Male')
questionnaire_demog['Gender'] = questionnaire_demog['Gender'].replace(3, 'Non-binary')
questionnaire_demog['Gender'] = questionnaire_demog['Gender'].replace(4, 'Other')
questionnaire_demog['Gender'] = questionnaire_demog['Gender'].replace(5, 'Prefer not to say')
questionnaire_demog['FP_Skin_Type'] = questionnaire_demog['FP_Skin_Type'].replace(1, 'Type 1 - Light Pale White')
questionnaire_demog['FP_Skin_Type'] = questionnaire_demog['FP_Skin_Type'].replace(2, 'Type 2 - White, Fair')
questionnaire_demog['FP_Skin_Type'] = questionnaire_demog['FP_Skin_Type'].replace(3, 'Type 3 - Medium, Whitew to Olive')
questionnaire_demog['FP_Skin_Type'] = questionnaire_demog['FP_Skin_Type'].replace(4, 'Type 4 - Olive Tone')
questionnaire_demog['FP_Skin_Type'] = questionnaire_demog['FP_Skin_Type'].replace(5, 'Type 5 - Light Brown')
questionnaire_demog['FP_Skin_Type'] = questionnaire_demog['FP_Skin_Type'].replace(6, 'Type 6 - Dark Brown')

# pre questionnaire
questionnaire_pre = pd.read_csv(questionnaire_path + "Pre_Study_Questionnaire.csv")

# questionnaire block 1
questionnaire_block1 = pd.read_csv(questionnaire_path + "Block1_Questionnaire.csv")
questionnaire_block1['Avatar_Condition'] = questionnaire_block1['Avatar_Condition'].replace(1, 'N')
questionnaire_block1['Avatar_Condition'] = questionnaire_block1['Avatar_Condition'].replace(2, 'G')
questionnaire_block1['Avatar_Condition'] = questionnaire_block1['Avatar_Condition'].replace(3, 'P')
# questionnaire block 2
questionnaire_block2 = pd.read_csv(questionnaire_path + "Block2_Questionnaire.csv")
questionnaire_block2['Avatar_Condition'] = questionnaire_block2['Avatar_Condition'].replace(1, 'N')
questionnaire_block2['Avatar_Condition'] = questionnaire_block2['Avatar_Condition'].replace(2, 'G')
questionnaire_block2['Avatar_Condition'] = questionnaire_block2['Avatar_Condition'].replace(3, 'P')
# questionnaire block 3
questionnaire_block3 = pd.read_csv(questionnaire_path + "Block3_Questionnaire.csv")
questionnaire_block3['Avatar_Condition'] = questionnaire_block3['Avatar_Condition'].replace(1, 'N')
questionnaire_block3['Avatar_Condition'] = questionnaire_block3['Avatar_Condition'].replace(2, 'G')
questionnaire_block3['Avatar_Condition'] = questionnaire_block3['Avatar_Condition'].replace(3, 'P')

# post questionnaire
questionnaire_post = pd.read_csv(questionnaire_path + "Post_Study_Questionnaire.csv")
questionnaire_post['emotion_most_differences'] = questionnaire_post['emotion_most_differences'].replace(1, 'Yes')
questionnaire_post['emotion_most_differences'] = questionnaire_post['emotion_most_differences'].replace(2, 'No')
questionnaire_post['embodiment_most_differences'] = questionnaire_post['embodiment_most_differences'].replace(1, 'Yes')
questionnaire_post['embodiment_most_differences'] = questionnaire_post['embodiment_most_differences'].replace(2, 'No')

# compiled questionnaire - Emotion Measures
vr_questionnaire_data = load_multiple_files_into_dataframe(data_path, '_compiled')

print("Loaded Questionnaire Data")

# Calibration Data
calibration_data = load_multiple_files_into_dataframe_with_exclusion(data_path, '_Calibration_Data.csv', '_BLINK')
calibration_data_raw = load_multiple_files_into_dataframe_with_exclusion(data_path, '_Calibration_Data_RAW.csv',
                                                                         '_BLINK')

print("Loaded Calibration Data")

# Phys Measures
phys_data_raw = load_multiple_files_into_dataframe(data_path, '_RAW_DATA_')

print("Loaded Phys Data")

print("Loaded VR Questionnaire Data")

#####################################################################################################################

print("Shape of Demog dataframe:", questionnaire_demog.shape)
print("Shape of PRE dataframe:", questionnaire_pre.shape)
print("Shape of Block1 dataframe:", questionnaire_block1.shape)
print("Shape of Block2 dataframe:", questionnaire_block2.shape)
print("Shape of Block3 dataframe:", questionnaire_block3.shape)
print("Shape of POST dataframe:", questionnaire_post.shape)
print("Shape of Calibration Data dataframe:", calibration_data.shape)
print("Shape of Calibration RAW dataframe:", calibration_data_raw.shape)
print("Shape of phys_data_raw dataframe:", phys_data_raw.shape)
print("Shape of vr_questionnaire_data dataframe:", vr_questionnaire_data.shape)


########################################################################################################################

def place_columns_at_front(df, columns_to_place):
    # Create a set of columns in the DataFrame
    df_columns_set = set(df.columns)

    # Check if columns_to_place exist in the DataFrame
    columns_to_place = [col for col in columns_to_place if col in df_columns_set]

    # Move the specified columns to the front
    df = df[columns_to_place + [col for col in df.columns if col not in columns_to_place]]

    return df

def place_columns_after_named_column(df, named_column, columns_to_place):
    # Get the index of the named column
    index_of_named_column = df.columns.get_loc(named_column)

    # Remove the columns to be placed from their original positions
    columns_popped = [df.pop(col) for col in columns_to_place if col in df.columns]

    # Insert the popped columns after the named column
    for col in reversed(columns_popped):
        df.insert(index_of_named_column + 1, col.name, col)

    return df

########################################################################################################################
# calibration_data
# calibration_data_raw
# phys_data_raw

# Vr questionnaire data file has a different column name for PID
vr_questionnaire_data.rename(columns={'P#': 'Participant_ID'}, inplace=True)
vr_questionnaire_data.rename(columns={'AvatarCondition': 'Avatar_Condition'}, inplace=True)
vr_questionnaire_data.rename(columns={'Scene Name': 'Scene_Name'}, inplace=True)
vr_questionnaire_data.rename(columns={'Unity Frame': 'Unity_Frame'}, inplace=True)


# Merge the dataframes on Participant_ID and Game, and specify empty suffixes
merged_data = pd.merge(vr_questionnaire_data, questionnaire_demog, on='Participant_ID', how='left', suffixes=('', '_questionnaire'))

# Check the shape of the merged dataframe
print("Shape of merged dataframe:", merged_data.shape)

merged_data = pd.merge(merged_data, questionnaire_pre, on='Participant_ID', how='left', suffixes=('', '_questionnaire'))

frames = [questionnaire_block1, questionnaire_block2, questionnaire_block3]
questionnaire_all_sessions = pd.concat(frames)

# Reorder the data by participant_id and then Session_Number
questionnaire_all_sessions = questionnaire_all_sessions.sort_values(by=['Participant_ID', 'Block_Number'])
questionnaire_all_sessions.reset_index(drop=True, inplace=True)
print("Shape of questionnaire_all_sessions dataframe:", questionnaire_all_sessions.shape)

questionnaire_all_sessions = pd.merge(questionnaire_all_sessions, questionnaire_post, on=['Participant_ID'], how='left', suffixes=('', '_questionnaire'))
print("Shape of questionnaire_all_sessions dataframe:", questionnaire_all_sessions.shape)

merged_data = pd.merge(merged_data, questionnaire_all_sessions, on=['Participant_ID','Avatar_Condition'], how='left', suffixes=('', '_questionnaire'))
print("Shape of merged dataframe:", merged_data.shape)
########################################################################################################################

#### Questionnaire Scoring
def check_duplicate_columns(df):
    duplicate_columns = df.columns[df.columns.duplicated()]
    if len(duplicate_columns) > 0:
        print("Duplicate Columns:")
        print(duplicate_columns)
    else:
        print("No Duplicate Columns")

#### B5
# Extroversion
merged_data['B5_Extroversion_Score'] = (merged_data['B5_E_1'] + merged_data['B5_E_2'] + merged_data['B5_E_3'] + merged_data['B5_E_4'] + merged_data['B5_E_5'] + (8-merged_data['B5_E_6']) + (8-merged_data['B5_E_7']) + (8-merged_data['B5_E_8'])) / 8
# Agreeableness
merged_data['B5_Agreeableness_Score'] = (merged_data['B5_A_1'] + merged_data['B5_A_2'] + merged_data['B5_A_3'] + merged_data['B5_A_4'] + merged_data['B5_A_5'] + (8-merged_data['B5_A_6']) + (8-merged_data['B5_A_7']) + (8-merged_data['B5_A_8']) + (8-merged_data['B5_A_9'])) / 9
# Conscientiousness
merged_data['B5_Conscientiousness_Score'] = (merged_data['B5_C_1'] + merged_data['B5_C_2'] + merged_data['B5_C_3'] + merged_data['B5_C_4'] + merged_data['B5_C_5'] + (8-merged_data['B5_C_6']) + (8-merged_data['B5_C_7']) + (8-merged_data['B5_C_8']) + (8-merged_data['B5_C_9'])) / 9
# Neuroticism
merged_data['B5_Neuroticism_Score'] = (merged_data['B5_N_1'] + merged_data['B5_N_2'] + merged_data['B5_N_3'] + merged_data['B5_N_4'] + merged_data['B5_N_5'] + (8-merged_data['B5_N_6']) + (8-merged_data['B5_N_7']) + (8-merged_data['B5_N_8'])) / 8
# Openness
merged_data['B5_Openness_Score'] = (merged_data['B5_O_1'] + merged_data['B5_O_2'] + merged_data['B5_O_3'] + merged_data['B5_O_4'] + merged_data['B5_O_5'] + merged_data['B5_O_6'] + merged_data['B5_O_7'] + merged_data['B5_O_8'] + (8-merged_data['B5_O_9']) + (8-merged_data['B5_O_10'])) / 10

#### ITQ
# Focus
merged_data['ITQ_Focus_Score'] = merged_data['ITQ_F_1'] + merged_data['ITQ_F_3'] + merged_data['ITQ_F_7'] + merged_data['ITQ_F_8'] + merged_data['ITQ_F_12'] + merged_data['ITQ_F_15'] + merged_data['ITQ_F_18']
# Involvement
merged_data['ITQ_Involvement_Score'] = merged_data['ITQ_I_2'] + merged_data['ITQ_I_4'] + merged_data['ITQ_I_5'] + merged_data['ITQ_I_10'] + merged_data['ITQ_I_11'] + merged_data['ITQ_I_16'] + merged_data['ITQ_I_17']
# Games
merged_data['ITQ_Games_Score'] = merged_data['ITQ_G_6'] + merged_data['ITQ_G_14']
# Total
merged_data['ITQ_Total_Score'] = merged_data['ITQ_F_1'] + merged_data['ITQ_F_3'] + merged_data['ITQ_F_7'] + merged_data['ITQ_F_8'] + merged_data['ITQ_F_12'] + merged_data['ITQ_F_15'] + merged_data['ITQ_F_18'] + merged_data['ITQ_I_2'] + merged_data['ITQ_I_4'] + merged_data['ITQ_I_5'] + merged_data['ITQ_I_10'] + merged_data['ITQ_I_11'] + merged_data['ITQ_I_16'] + merged_data['ITQ_I_17'] + merged_data['ITQ_G_6'] + merged_data['ITQ_G_14'] + merged_data['ITQ_Dummy_9'] + merged_data['ITQ_Dummy_13']

# data_header_questionnaire_post = ['PPL_FSQ_Total_Score','PPL_FSQ_Challenge_Skill_Score','PPL_FSQ_Absorption_Score',
# 'FSS_Total_Score','FSS_Performance_Fluency_Score','FSS_Absorption_Score','FSS_Demand_Score','FSS_Total_Score_With_Demand',
# 'IMI_Interest_Score','IMI_Effort_Score','IMI_Pressure_Score','IMI_Competence_Score',
# 'MPS_Phys_Presence_Score','MPS_Social_Presence_Score','MPS_Self_Presence_Score',
# 'SSQ_Nausea','SSQ_Occulomotor_Disturbance','SSQ_Disorientation','SSQ_Total']

######## Post measures
#### Embodiment
merged_data['Appearance'] = (merged_data['Embodiment_1'] + merged_data['Embodiment_2'] + merged_data['Embodiment_3'] + merged_data['Embodiment_4'] + merged_data['Embodiment_5'] + merged_data['Embodiment_6'] + merged_data['Embodiment_9'] + merged_data['Embodiment_16']) / 8
merged_data['Response'] = (merged_data['Embodiment_4'] + merged_data['Embodiment_6'] + merged_data['Embodiment_7'] + merged_data['Embodiment_8'] + merged_data['Embodiment_9'] + merged_data['Embodiment_15']) / 6
merged_data['Ownership'] = (merged_data['Embodiment_5'] + merged_data['Embodiment_10'] + merged_data['Embodiment_11'] + merged_data['Embodiment_12'] + merged_data['Embodiment_13'] + merged_data['Embodiment_14']) / 6
merged_data['Multi-Sensory'] = (merged_data['Embodiment_3'] + merged_data['Embodiment_12'] + merged_data['Embodiment_13'] + merged_data['Embodiment_14'] + merged_data['Embodiment_15'] + merged_data['Embodiment_16']) / 6
merged_data['Embodiment_Score'] = (merged_data['Appearance'] + merged_data['Response'] + merged_data['Ownership'] + merged_data['Multi-Sensory']) / 4

#### MPS
merged_data['MPS_Phys_Presence_Score'] = (merged_data['MPS_Phys_Presence_1'] + merged_data['MPS_Phys_Presence_2'] + merged_data['MPS_Phys_Presence_3'] + merged_data['MPS_Phys_Presence_4'] + merged_data['MPS_Phys_Presence_5']) / 5
merged_data['MPS_Social_Presence_Score'] = (merged_data['MPS_Social_Presence_1'] + merged_data['MPS_Social_Presence_2'] + merged_data['MPS_Social_Presence_3'] + merged_data['MPS_Social_Presence_4'] + merged_data['MPS_Social_Presence_5']) / 5
merged_data['MPS_Self_Presence_Score'] = (merged_data['MPS_Self_Presence_1'] + merged_data['MPS_Self_Presence_2'] + merged_data['MPS_Self_Presence_3'] + merged_data['MPS_Self_Presence_4'] + merged_data['MPS_Self_Presence_5']) / 5

#### SSQ
merged_data['POST_SSQ_Nausea'] = (merged_data['POST_SSQ_General_discomfort'] + merged_data['POST_SSQ_Increased_salivation'] + merged_data['POST_SSQ_Sweating'] + merged_data['POST_SSQ_Difficulty_concentrating'] + merged_data['POST_SSQ_Stomach_awareness'] + merged_data['POST_SSQ_Burping'])*9.54
merged_data['POST_SSQ_Occulomotor_Disturbance'] = (merged_data['POST_SSQ_General_discomfort'] + merged_data['POST_SSQ_Fatigue'] + merged_data['POST_SSQ_Headache'] + merged_data['POST_SSQ_Eye_strain'] + merged_data['POST_SSQ_Difficulty_focusing'] + merged_data['POST_SSQ_Difficulty_concentrating'] + merged_data['POST_SSQ_Blurred_vision'])*7.58
merged_data['POST_SSQ_Disorientation'] = (merged_data['POST_SSQ_Difficulty_focusing'] + merged_data['POST_SSQ_Fullness_of_head'] + merged_data['POST_SSQ_Blurred_vision'] + merged_data['POST_SSQ_Dizzy_eyes_open'] + merged_data['POST_SSQ_Dizzy_eyes_closed'] + merged_data['POST_SSQ_Vertigo'])*13.92
merged_data['POST_SSQ_Total'] = (merged_data['POST_SSQ_General_discomfort'] + merged_data['POST_SSQ_Increased_salivation'] + merged_data['POST_SSQ_Sweating'] + merged_data['POST_SSQ_Difficulty_concentrating'] + merged_data['POST_SSQ_Stomach_awareness'] + merged_data['POST_SSQ_Burping']) + (merged_data['POST_SSQ_General_discomfort'] + merged_data['POST_SSQ_Fatigue'] + merged_data['POST_SSQ_Headache'] + merged_data['POST_SSQ_Eye_strain'] + merged_data['POST_SSQ_Difficulty_focusing'] + merged_data['POST_SSQ_Difficulty_concentrating'] + merged_data['POST_SSQ_Blurred_vision']) + (merged_data['POST_SSQ_Difficulty_focusing'] + merged_data['POST_SSQ_Fullness_of_head'] + merged_data['POST_SSQ_Blurred_vision'] + merged_data['POST_SSQ_Dizzy_eyes_open'] + merged_data['POST_SSQ_Dizzy_eyes_closed'] + merged_data['POST_SSQ_Vertigo'])*3.74

### Renaming Columns for Readability
merged_data.rename(columns={'SAM_Arousal': 'SAM_Arousal_VR'}, inplace=True)
merged_data.rename(columns={'SAM_Pleasure': 'SAM_Pleasure_VR'}, inplace=True)
merged_data.rename(columns={'SAM_Dominance': 'SAM_Dominance_VR'}, inplace=True)
merged_data.rename(columns={'Emotion_Excite': 'Excitement_VR'}, inplace=True)
merged_data.rename(columns={'Emotion_Happy': 'Happy_VR'}, inplace=True)
merged_data.rename(columns={'Emotion_Content': 'Content_VR'}, inplace=True)
merged_data.rename(columns={'Emotion_Calm': 'Calm_VR'}, inplace=True)
merged_data.rename(columns={'Emotion_Bored': 'Boredom_VR'}, inplace=True)
merged_data.rename(columns={'Emotion_Sad': 'Sad_VR'}, inplace=True)
merged_data.rename(columns={'Emotion_Stress': 'Stress_VR'}, inplace=True)
merged_data.rename(columns={'Emotion_Fear': 'Fear_VR'}, inplace=True)
merged_data.rename(columns={'Embodiment_Presence_E_BO_1': 'Embodiment_BO_VR'}, inplace=True)
merged_data.rename(columns={'Embodiment_Presence_E_AMC_6': 'Embodiment_AG_VR'}, inplace=True)
merged_data.rename(columns={'Embodiment_Presence_E_LOB_10': 'Embodiment_LO_VR'}, inplace=True)
merged_data.rename(columns={'Embodiment_Presence_MPS_PHYS_5': 'MPS_Phys_Presence_VR'}, inplace=True)
merged_data.rename(columns={'Embodiment_Presence_MPS_SOC_1': 'MPS_Social_Presence_VR'}, inplace=True)
merged_data.rename(columns={'Embodiment_Presence_MPS_SELF_7': 'MPS_Self_Presence_VR'}, inplace=True)

#reorder scanning session data (demog)
reoredered_columns = ['Block_Number']
merged_data = place_columns_after_named_column(merged_data, 'Avatar_Condition', reoredered_columns)

reoredered_columns = ['B5_E_1','B5_E_2','B5_E_3','B5_E_4','B5_E_5','B5_E_6','B5_E_7','B5_E_8','B5_Extroversion_Score','B5_A_1','B5_A_2','B5_A_3','B5_A_4','B5_A_5','B5_A_6','B5_A_7','B5_A_8','B5_A_9','B5_Agreeableness_Score','B5_C_1','B5_C_2','B5_C_3','B5_C_4','B5_C_5','B5_C_6','B5_C_7','B5_C_8','B5_C_9','B5_Conscientiousness_Score','B5_N_1','B5_N_2','B5_N_3','B5_N_4',
'B5_N_5','B5_N_6','B5_N_7','B5_N_8','B5_Neuroticism_Score','B5_O_1','B5_O_2','B5_O_3','B5_O_4','B5_O_5','B5_O_6','B5_O_7','B5_O_8','B5_O_9','B5_O_10','B5_Openness_Score','VR_Experience','Video_Game_Experience','Dog_1','Dog_2','S_Attr_Intellectual','S_Attr_Social','S_Attr_Artistic','S_Attr_Athletic','S_Attr_Physical','S_Attr_Leadership','S_Attr_Common','S_Attr_Emotional','S_Attr_Humor','S_Attr_Discipline',
'ITQ_F_1','ITQ_I_2','ITQ_F_3','ITQ_I_4','ITQ_I_5','ITQ_G_6','ITQ_F_7','ITQ_F_8','ITQ_Dummy_9','ITQ_I_10','ITQ_I_11','ITQ_F_12','ITQ_Dummy_13','ITQ_G_14','ITQ_F_15','ITQ_I_16','ITQ_I_17','ITQ_F_18','ITQ_Focus_Score',
'ITQ_Involvement_Score','ITQ_Games_Score','ITQ_Total_Score','Gender','Age','FP_Skin_Type']
merged_data = place_columns_after_named_column(merged_data, 'Scene_Name', reoredered_columns)

#reorder Pre Study
reoredered_columns = ['Baseline_SSQ_General_discomfort','Baseline_SSQ_Fatigue','Baseline_SSQ_Headache','Baseline_SSQ_Eye_strain','Baseline_SSQ_Difficulty_focusing','Baseline_SSQ_Increased_salivation','Baseline_SSQ_Sweating','Baseline_SSQ_Difficulty_concentrating','Baseline_SSQ_Fullness_of_head','Baseline_SSQ_Blurred_vision','Baseline_SSQ_Dizzy_eyes_open','Baseline_SSQ_Dizzy_eyes_closed','Baseline_SSQ_Vertigo','Baseline_SSQ_Stomach_awareness','Baseline_SSQ_Burping','SAM_Valence_Baseline','SAM_Arousal_Baseline','SAM_Dominance_Baseline','Excitement_Baseline','Happy_Baseline','Content_Baseline','Calm_Baseline','Boredom_Baseline','Sad_Baseline','Stress_Baseline','Fear_Baseline']
merged_data = place_columns_after_named_column(merged_data, 'FP_Skin_Type', reoredered_columns)

#reorder VR Questionnaire
reoredered_columns = ['SAM_Arousal_VR','SAM_Pleasure_VR','SAM_Dominance_VR','Excitement_VR','Happy_VR','Content_VR','Calm_VR','Boredom_VR','Sad_VR','Stress_VR','Fear_VR','Embodiment_BO_VR','Embodiment_AG_VR','Embodiment_LO_VR','MPS_Phys_Presence_VR','MPS_Social_Presence_VR','MPS_Self_Presence_VR']
merged_data = place_columns_after_named_column(merged_data, 'Fear_Baseline', reoredered_columns)

#reoder Blocks data
reoredered_columns = ['SAM_Valence_Avatar_Exposure','SAM_Arousal_Avatar_Exposure','SAM_Dominance_Avatar_Exposure','Appeal_Exposure','Likeability_Exposure','Eeriness_Exposure','Familiarity_Exposure','GeneralRealism_Exposure','AppearanceRealism_Exposure','MovementRealism_Exposure', 'A_Attr_Intellectual', 'A_Attr_Social', 'A_Attr_Artistic',	'A_Attr_Athletic', 'A_Attr_Physical', 'A_Attr_Leadership', 'A_Attr_Common',	'A_Attr_Emotional',	'A_Attr_Humor',	'A_Attr_Discipline','Appearance_Similarity','MPS_Phys_Presence_1','MPS_Phys_Presence_2','MPS_Phys_Presence_3','MPS_Phys_Presence_4','MPS_Phys_Presence_5','MPS_Social_Presence_1','MPS_Social_Presence_2','MPS_Social_Presence_3','MPS_Social_Presence_4','MPS_Social_Presence_5','MPS_Self_Presence_1','MPS_Self_Presence_2','MPS_Self_Presence_3','MPS_Self_Presence_4','MPS_Self_Presence_5','MPS_Phys_Presence_Score','MPS_Social_Presence_Score',
'MPS_Self_Presence_Score','Embodiment_1','Embodiment_2','Embodiment_3','Embodiment_4','Embodiment_5','Embodiment_6','Embodiment_7','Embodiment_8','Embodiment_9','Embodiment_10','Embodiment_11','Embodiment_12','Embodiment_13','Embodiment_14','Embodiment_15','Embodiment_16','Appearance','Response','Ownership','Multi-Sensory','Embodiment_Score','POST_SSQ_General_discomfort','POST_SSQ_Fatigue','POST_SSQ_Headache','POST_SSQ_Eye_strain','POST_SSQ_Difficulty_focusing','POST_SSQ_Increased_salivation','POST_SSQ_Sweating','POST_SSQ_Difficulty_concentrating','POST_SSQ_Fullness_of_head','POST_SSQ_Blurred_vision','POST_SSQ_Dizzy_eyes_open','POST_SSQ_Dizzy_eyes_closed','POST_SSQ_Vertigo','POST_SSQ_Stomach_awareness','POST_SSQ_Burping', 'POST_SSQ_Nausea', 'POST_SSQ_Occulomotor_Disturbance', 'POST_SSQ_Disorientation', 'POST_SSQ_Total']
merged_data = place_columns_after_named_column(merged_data, 'MPS_Self_Presence_VR', reoredered_columns)

#reoder Post Study
reoredered_columns = ['avatar_differences_description','emotion_most_differences','emotion_rank_N','emotion_rank_G','emotion_rank_P','emotion_most_description','embodiment_most_differences','embodiment_rank_N','embodiment_rank_G','embodiment_rank_P','embodiment_most_description']
merged_data = place_columns_after_named_column(merged_data, 'POST_SSQ_Total', reoredered_columns)

check_duplicate_columns(merged_data)


merged_data.to_csv('Aggregation/Final_Questionaire_Aggregation_51ps.csv', index=False)


#----------------------------------------------------------------------------------------end of questionnaire processing part of things----------------------------------------------------------------------------------------------------------------#












#Need to figure out what the intent of this part of the script is. The code is just a way of carrying out their intention, if you can figure out their intent, you'll be able to figure out
# what it is you actually need to code up.

#----------------------------------------------------------------------------------------beginning of calibration part of things ----------------------------------------------------------------------------------------
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

aggregated_data = merged_data

max_iterations = 20

# clean heart rate data by removing anomalous data from a participant's age'
def apply_relative_threshold(data, age):
    threshold = -age / 3 + 45


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


# Dilation Data
---------------------------------------------------------------------------------------------------------------
"""
Code is concerned with eye data: 
Useful background info: uses precomputed data (precomputation is not done in the script as is evident by the fact that calibration_data is loaded 
using the load_multiple_files_into_dataframe_with_exclusion function). Therefore, i'm making the assumption that it's already 
provided for me. 

Data used: 
calibration_data =  load_multiple_files_into_dataframe_with_exclusion(data_path, '_Calibration_Data.csv', '_BLINK')
aggregated_data = merged_data = merged_data.to_csv('Aggregation/Final_Questionaire_Aggregation_51ps.csv', index=False)


Goal:
for each grayscale value in all participants, it copies the value of the 'Median_Pupil_Dilation_Left' and 'Median_Pupil_Dilation_Right', then it 
creates a column named Calibration_PupilDilation_Left_{value} where value is the current greyscale value, or it updates a column with the name of the
form Calibration_PupilDilation_Left_{value}, filling each column with the grayscale value for that specific participant for all participants.
"""


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

------------------------------------------------------------------------------------------------------------


"""


Data used: 
calibration_data_raw = load_multiple_files_into_dataframe_with_exclusion(data_path, '_Calibration_Data_RAW.csv','_BLINK')
merged_data.to_csv('Aggregation/Final_Questionaire_Aggregation_51ps.csv', index=False)


"""


HR_median_map = calibration_data_raw.groupby('Participant_ID')['Polar_HearRateBPM'].median().to_dict()
HR_mean_map = calibration_data_raw.groupby('Participant_ID')['Polar_HearRateBPM'].mean().to_dict()
HR_std_map = calibration_data_raw.groupby('Participant_ID')['Polar_HearRateBPM'].std().to_dict()
aggregated_data['Calibration_Median_Resting_HeartRate'] = aggregated_data['Participant_ID'].map(HR_median_map)
aggregated_data['Calibration_Mean_Resting_HeartRate'] = aggregated_data['Participant_ID'].map(HR_mean_map)
aggregated_data['Calibration_SD_Resting_HeartRate'] = aggregated_data['Participant_ID'].map(HR_std_map)

HR_interval_median_map = calibration_data_raw.groupby('Participant_ID')[
    'Polar_HeartRate_RR_Interval'].median().to_dict()
HR_interval_mean_map = calibration_data_raw.groupby('Participant_ID')['Polar_HeartRate_RR_Interval'].mean().to_dict()
HR_interval_std_map = calibration_data_raw.groupby('Participant_ID')['Polar_HeartRate_RR_Interval'].std().to_dict()
aggregated_data['Calibration_Median_Resting_HeartRate_RR_Interval'] = aggregated_data['Participant_ID'].map(
    HR_interval_median_map)  # quite a bit of noise/ spikey data in the RR_interval
aggregated_data['Calibration_Mean_Resting_HeartRate_RR_Interval'] = aggregated_data['Participant_ID'].map(
    HR_interval_mean_map)
aggregated_data['Calibration_SD_Resting_HeartRate_RR_Interval'] = aggregated_data['Participant_ID'].map(
    HR_interval_std_map)




print(f"RAW DF: {len(calibration_data_raw.index)}")

for participant_id, group in calibration_data_raw.groupby('Participant_ID'):
    rr_intervals = group['Polar_HeartRate_RR_Interval']
    rmssd_participant = np.sqrt(np.mean(np.diff(rr_intervals) ** 2))
    aggregated_data.loc[
        aggregated_data['Participant_ID'] == participant_id, 'Calibration_RR_Interval_RAW_RMSSD'] = rmssd_participant



# filtered_data = calibration_data_raw
filtered_data = calibration_data_raw[(calibration_data_raw['Polar_HeartRate_RR_Interval'] > 200) & (
            calibration_data_raw['Polar_HeartRate_RR_Interval'] < 2000)]

HR_interval_median_map_ABS_Threshold = filtered_data.groupby('Participant_ID')[
    'Polar_HeartRate_RR_Interval'].median().to_dict()
HR_interval_mean_map_ABS_Threshold = filtered_data.groupby('Participant_ID')[
    'Polar_HeartRate_RR_Interval'].mean().to_dict()
HR_interval_std_map_ABS_Threshold = filtered_data.groupby('Participant_ID')[
    'Polar_HeartRate_RR_Interval'].std().to_dict()
aggregated_data['Calibration_Median_Resting_HeartRate_RR_Interval_CLEANED_ABS_Threshold'] = aggregated_data[
    'Participant_ID'].map(HR_interval_median_map_ABS_Threshold)
aggregated_data['Calibration_Mean_Resting_HeartRate_RR_Interval_CLEANED_ABS_Threshold'] = aggregated_data[
    'Participant_ID'].map(HR_interval_mean_map_ABS_Threshold)
aggregated_data['Calibration_SD_Resting_HeartRate_RR_Interval_CLEANED_ABS_Threshold'] = aggregated_data[
    'Participant_ID'].map(HR_interval_std_map_ABS_Threshold)

print(f"ABS DF: {len(filtered_data.index)}")

for participant_id, group in filtered_data.groupby('Participant_ID'):
    rr_intervals = group['Polar_HeartRate_RR_Interval']
    rmssd_participant = np.sqrt(np.mean(np.diff(rr_intervals) ** 2))
    aggregated_data.loc[aggregated_data[
                            'Participant_ID'] == participant_id, 'Calibration_RR_Interval_CLEANED_ABS_RMSSD'] = rmssd_participant

relative_filtered_data = pd.DataFrame()
age_column = 'Participant_Age'
for participant_id, group in filtered_data.groupby('Participant_ID'):
    print(f'Applying Relative Threshold for Participant {participant_id}')
    age = group[age_column].iloc[0]  # Assuming age is the same for all rows of a participant
    cleaned_group = apply_relative_threshold(group, age)
    relative_filtered_data = pd.concat([relative_filtered_data, cleaned_group])

HR_interval_median_map_REL_Threshold = relative_filtered_data.groupby('Participant_ID')[
    'Polar_HeartRate_RR_Interval'].median().to_dict()
HR_interval_mean_map_REL_Threshold = relative_filtered_data.groupby('Participant_ID')[
    'Polar_HeartRate_RR_Interval'].mean().to_dict()
HR_interval_std_map_REL_Threshold = relative_filtered_data.groupby('Participant_ID')[
    'Polar_HeartRate_RR_Interval'].std().to_dict()
aggregated_data['Calibration_Median_Resting_HeartRate_RR_Interval_CLEANED_REL_Threshold'] = aggregated_data[
    'Participant_ID'].map(HR_interval_median_map_REL_Threshold)
aggregated_data['Calibration_Mean_Resting_HeartRate_RR_Interval_CLEANED_REL_Threshold'] = aggregated_data[
    'Participant_ID'].map(HR_interval_mean_map_REL_Threshold)
aggregated_data['Calibration_SD_Resting_HeartRate_RR_Interval_CLEANED_REL_Threshold'] = aggregated_data[
    'Participant_ID'].map(HR_interval_std_map_REL_Threshold)

print(f"REL DF: {len(relative_filtered_data.index)}")

# pd.set_option('display.max_columns', None)
# display(relative_filtered_data)

for participant_id, group in filtered_data.groupby('Participant_ID'):
    rr_intervals = group['Polar_HeartRate_RR_Interval']
    rmssd_participant = np.sqrt(np.mean(np.diff(rr_intervals) ** 2))
    aggregated_data.loc[aggregated_data[
                            'Participant_ID'] == participant_id, 'Calibration_RR_Interval_CLEANED_REL_RMSSD'] = rmssd_participant


------------------------------------------------------------------------------------------------------------------------



GSR_Conductance_median_map = calibration_data_raw.groupby('Participant_ID')[
    'Shimmer_D36A_GSR_Skin_Conductance_uS'].median().to_dict()
GSR_Conductance_mean_map = calibration_data_raw.groupby('Participant_ID')[
    'Shimmer_D36A_GSR_Skin_Conductance_uS'].mean().to_dict()
GSR_Conductance_std_map = calibration_data_raw.groupby('Participant_ID')[
    'Shimmer_D36A_GSR_Skin_Conductance_uS'].std().to_dict()
aggregated_data['Calibration_Median_GSR_Conductance'] = aggregated_data['Participant_ID'].map(
    GSR_Conductance_median_map)
aggregated_data['Calibration_Mean_GSR_Conductance'] = aggregated_data['Participant_ID'].map(GSR_Conductance_mean_map)
aggregated_data['Calibration_SD_GSR_Conductance'] = aggregated_data['Participant_ID'].map(GSR_Conductance_std_map)

GSR_Resistance_median_map = calibration_data_raw.groupby('Participant_ID')[
    'Shimmer_D36A_GSR_Skin_Resistance_kOhms'].median().to_dict()
GSR_Resistance_mean_map = calibration_data_raw.groupby('Participant_ID')[
    'Shimmer_D36A_GSR_Skin_Resistance_kOhms'].mean().to_dict()
GSR_Resistance_std_map = calibration_data_raw.groupby('Participant_ID')[
    'Shimmer_D36A_GSR_Skin_Resistance_kOhms'].std().to_dict()
aggregated_data['Calibration_Median_GSR_Resistance'] = aggregated_data['Participant_ID'].map(GSR_Resistance_median_map)
aggregated_data['Calibration_Mean_GSR_Resistance'] = aggregated_data['Participant_ID'].map(GSR_Resistance_mean_map)
aggregated_data['Calibration_SD_GSR_Resistance'] = aggregated_data['Participant_ID'].map(GSR_Resistance_std_map)

filtered_data_conductance = calibration_data_raw[
    (calibration_data_raw['Shimmer_D36A_GSR_Skin_Resistance_kOhms'] > 0) &
    (calibration_data_raw['Shimmer_D36A_GSR_Skin_Resistance_kOhms'] < 2500) &
    (calibration_data_raw['Shimmer_D36A_GSR_Skin_Conductance_uS'] >= 0.1)]

conductance_median_map_ABS_Threshold = filtered_data_conductance.groupby('Participant_ID')[
    'Shimmer_D36A_GSR_Skin_Conductance_uS'].median().to_dict()
conductance_mean_map_ABS_Threshold = filtered_data_conductance.groupby('Participant_ID')[
    'Shimmer_D36A_GSR_Skin_Conductance_uS'].mean().to_dict()
conductance_std_map_ABS_Threshold = filtered_data_conductance.groupby('Participant_ID')[
    'Shimmer_D36A_GSR_Skin_Conductance_uS'].std().to_dict()
aggregated_data['Calibration_Median_GSR_Conductance_CLEANED_ABS_Threshold'] = aggregated_data['Participant_ID'].map(
    conductance_median_map_ABS_Threshold)
aggregated_data['Calibration_Mean_GSR_Conductance_CLEANED_ABS_Threshold'] = aggregated_data['Participant_ID'].map(
    conductance_mean_map_ABS_Threshold)
aggregated_data['Calibration_SD_GSR_Conductance_CLEANED_ABS_Threshold'] = aggregated_data['Participant_ID'].map(
    conductance_std_map_ABS_Threshold)

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
aggregated_data = place_columns_after_named_column(aggregated_data, 'Fear_Baseline', data_header_calibration_measures)

merged_data = aggregated_data


#####################################End of Calibration Part of things###############################################################

######################################Start of Aggregation of raw data (i believe) - split into 3 sectiosn but not sure why###################################################


def calculate_stats_before_start(row, exposure_data_group_full, columns, sep_row, sep_exposure, time_window,
                                 filter_value=None):
    search_group = exposure_data_group_full[
        (exposure_data_group_full[sep_exposure] == row[sep_row])
    ]
    start_time = search_group["Unity_Timestamp"].min()
    exposure_data_group = exposure_data_group_full[
        (exposure_data_group_full["Unity_Timestamp"] <= start_time) &
        (exposure_data_group_full["Unity_Timestamp"] >= start_time - pd.Timedelta(seconds=time_window))
        ]

    full_val = tuple()

    for column_name in columns:
        window_data = exposure_data_group
        if filter_value is not None:
            window_data = exposure_data_group[exposure_data_group[column_name] != filter_value]

        if (window_data.shape[0] > 0):
            median_value = window_data[column_name].median()
            mean_value = window_data[column_name].mean()
            std_value = window_data[column_name].std()
            min_value = window_data[column_name].min()
            max_value = window_data[column_name].max()
        else:
            median_value = mean_value = std_value = min_value = max_value = np.nan

        full_val += (median_value, mean_value, std_value, min_value, max_value)

    return full_val


def calculate_stats_before_start_with_range(row, exposure_data_group_full, columns, sep_row, sep_exposure, time_window,
                                            ranges):
    search_group = exposure_data_group_full[
        (exposure_data_group_full[sep_exposure] == row[sep_row])
    ]
    start_time = search_group["Unity_Timestamp"].min()
    exposure_data_group = exposure_data_group_full[
        (exposure_data_group_full["Unity_Timestamp"] <= start_time) &
        (exposure_data_group_full["Unity_Timestamp"] >= start_time - pd.Timedelta(seconds=time_window))
        ]

    full_val = tuple()

    for i in range(len(columns)):
        column_name = columns[i]
        lower_bound = ranges[i][0];
        upper_bound = ranges[i][1]

        window_data = exposure_data_group

        if lower_bound is not None:
            window_data = window_data[window_data[column_name] > lower_bound]
        if upper_bound is not None:
            window_data = window_data[window_data[column_name] < upper_bound]

        if (window_data.shape[0] > 0):
            median_value = window_data[column_name].median()
            mean_value = window_data[column_name].mean()
            std_value = window_data[column_name].std()
            min_value = window_data[column_name].min()
            max_value = window_data[column_name].max()
        else:
            median_value = mean_value = std_value = min_value = max_value = np.nan

        full_val += (median_value, mean_value, std_value, min_value, max_value)

    return full_val


def calculate_stats_with_range(row, exposure_data_group, columns, ranges):
    """
    Calculate median, mean, standard deviation, min & max for a specified column in exposure_data_group.

    Returns:
        tuple: A tuple containing median, mean, standard deviation, min & max.
    """

    if len(columns) != len(ranges):
        print("Ranges and Columns Must Match")

    full_val = tuple()

    for i in range(len(columns)):
        column_name = columns[i]
        lower_bound = ranges[i][0];
        upper_bound = ranges[i][1]

        window_data = exposure_data_group

        if lower_bound is not None:
            window_data = window_data[window_data[column_name] > lower_bound]
        if upper_bound is not None:
            window_data = window_data[window_data[column_name] < upper_bound]

        if (window_data.shape[0] > 0):
            median_value = window_data[column_name].median()
            mean_value = window_data[column_name].mean()
            std_value = window_data[column_name].std()
            min_value = window_data[column_name].min()
            max_value = window_data[column_name].max()
        else:
            median_value = mean_value = std_value = min_value = max_value = np.nan

        full_val += (median_value, mean_value, std_value, min_value, max_value)

    return full_val


# A function to calculate median, mean, standard deviation, min and max
def calculate_stats(row, exposure_data_group, columns, filter_value=None):
    full_val = tuple()

    for column_name in columns:
        window_data = exposure_data_group
        if filter_value is not None:
            window_data = exposure_data_group[exposure_data_group[column_name] != filter_value]

        if (window_data.shape[0] > 0):
            median_value = window_data[column_name].median()
            mean_value = window_data[column_name].mean()
            std_value = window_data[column_name].std()
            min_value = window_data[column_name].min()
            max_value = window_data[column_name].max()
        else:
            median_value = mean_value = std_value = min_value = max_value = np.nan

        full_val += (median_value, mean_value, std_value, min_value, max_value)

    return full_val


def calculate_rmssd(row, exposure_data_group):
    window_data = exposure_data_group

    window_data = window_data[window_data["Polar_RR_Interval"] > 200]
    window_data = window_data[window_data["Polar_RR_Interval"] < 2000]

    if window_data.shape[0] > 0:
        rr_intervals = window_data["Polar_RR_Interval"].values
        rr_diff = np.diff(rr_intervals)
        rmssd_value = np.sqrt(np.mean(rr_diff ** 2))
    else:
        rr_intervals = np.nan

    return (rmssd_value,)


def calculate_rmssd_before_start(row, exposure_data_group_full, sep_row, sep_exposure, time_window):
    search_group = exposure_data_group_full[
        (exposure_data_group_full[sep_exposure] == row[sep_row])
    ]
    start_time = search_group["Unity_Timestamp"].min()
    exposure_data_group = exposure_data_group_full[
        (exposure_data_group_full["Unity_Timestamp"] <= start_time) &
        (exposure_data_group_full["Unity_Timestamp"] >= start_time - pd.Timedelta(seconds=time_window))
        ]

    window_data = exposure_data_group

    window_data = window_data[window_data["Polar_RR_Interval"] > 200]
    window_data = window_data[window_data["Polar_RR_Interval"] < 2000]

    if window_data.shape[0] > 0:
        rr_intervals = window_data["Polar_RR_Interval"].values
        rr_diff = np.diff(rr_intervals)
        rmssd_value = np.sqrt(np.mean(rr_diff ** 2))
    else:
        rr_intervals = np.nan

    return (rmssd_value,)


def calculate_cumulative_column(row, exposure_data_group, column, abs=False):
    window_data = exposure_data_group

    # Iterate through the rows in the subset to accumulate EDA values
    column_data = np.abs(window_data[column]) if abs else window_data[column]
    left_side = column_data._values[1:];
    right_side = column_data._values[:-1]
    subtracted = left_side - right_side

    subtracted[subtracted < 0] = 0
    return (np.sum(subtracted),)


def calculate_cumulative_column_before_start(row, exposure_data_group_full, sep_row, sep_exposure, time_window, column,
                                             abs=False):
    search_group = exposure_data_group_full[
        (exposure_data_group_full[sep_exposure] == row[sep_row])
    ]
    start_time = search_group["Unity_Timestamp"].min()
    exposure_data_group = exposure_data_group_full[
        (exposure_data_group_full["Unity_Timestamp"] <= start_time) &
        (exposure_data_group_full["Unity_Timestamp"] >= start_time - pd.Timedelta(seconds=time_window))
        ]

    window_data = exposure_data_group

    column_data = np.abs(window_data[column]) if abs else window_data[column]
    left_side = column_data._values[1:];
    right_side = column_data._values[:-1]
    subtracted = left_side - right_side
    subtracted[subtracted < 0] = 0
    return (np.sum(subtracted),)


exposure_data = phys_data_raw

exposure_data.loc[:, 'Unity_Timestamp'] = pd.to_datetime(exposure_data['Unity_Timestamp'],
                                                         format="%Y-%m-%dT%H:%M:%S.%fZ", errors="coerce").fillna(
    pd.to_datetime(exposure_data['Unity_Timestamp'], format="%d-%m-%Y - %H:%M:%S.%f", errors="coerce"))

STATS = ['Median', 'Mean', 'SD', 'MIN', 'MAX']


############### End of first section ########################

print("Exposure Data Shape: ", exposure_data.shape)
merged_data = pd.read_csv('Aggregation/Final_Aggregate_Calibration_51ps.csv')

column_names = ['pupil_dilation_left', 'pupil_dilation_right', 'current_blinkDuration', 'current_interBlinkInterval',
                'Shimmer_D36A_GSR_Skin_Conductance_uS', 'Shimmer_D36A_GSR_Skin_Resistance_kOhms', 'Polar_HearRateBPM',
                'Polar_RR_Interval', '0_Jaw_Forward', '1_Jaw_Right', '2_Jaw_Left', '3_Jaw_Open', '4_Mouth_Ape_Shape',
                '5_Mouth_O_Shape', '6_Mouth_Pout', '7_Mouth_Lower_Right', '8_Mouth_Lower_Left', '9_Mouth_Smile_Right',
                '10_Mouth_Smile_Left', '11_Mouth_Sad_Right', '12_Mouth_Sad_Left', '13_Cheek_Puff_Right',
                '14_Cheek_Puff_Left', '15_Mouth_Lower_Inside', '16_Mouth_Upper_Inside', '17_Mouth_Lower_Overlay',
                '19_Cheek_Suck', '20_Mouth_LowerRight_Down', '21_Mouth_LowerLeft_Down', '22_Mouth_UpperRight_Up',
                '23_Mouth_UpperLeft_Up', '24_Mouth_Philtrum_Right', '25_Mouth_Philtrum_Left', '26_Max',
                'foveal_corrected_dilation_left', 'foveal_corrected_dilation_right']
column_labels = ['Pupil_Dilation_Left', 'Pupil_Dilation_Right', 'blinkDuration', 'current_interBlinkInterval',
                 'Skin_Conductance_uS', 'Skin_Resistance_kOhms', 'HeartRate_BPM', 'HeartRate_RR_Interval',
                 '0_Jaw_Forward', '1_Jaw_Right', '2_Jaw_Left', '3_Jaw_Open', '4_Mouth_Ape_Shape', '5_Mouth_O_Shape',
                 '6_Mouth_Pout', '7_Mouth_Lower_Right', '8_Mouth_Lower_Left', '9_Mouth_Smile_Right',
                 '10_Mouth_Smile_Left', '11_Mouth_Sad_Right', '12_Mouth_Sad_Left', '13_Cheek_Puff_Right',
                 '14_Cheek_Puff_Left', '15_Mouth_Lower_Inside', '16_Mouth_Upper_Inside', '17_Mouth_Lower_Overlay',
                 '19_Cheek_Suck', '20_Mouth_LowerRight_Down', '21_Mouth_LowerLeft_Down', '22_Mouth_UpperRight_Up',
                 '23_Mouth_UpperLeft_Up', '24_Mouth_Philtrum_Right', '25_Mouth_Philtrum_Left', '26_Max',
                 'Foveal_Corrected_Dilation_Left', 'Foveal_Corrected_Dilation_Right']

range_columns = ['current_blinkDuration', 'Shimmer_D36A_GSR_Skin_Conductance_uS',
                 'Shimmer_D36A_GSR_Skin_Resistance_kOhms', 'Polar_RR_Interval']
ranged_labels = ['Corrected_BlinkDuration', 'Corrected_Skin_Conductance_uS', 'Corrected_Skin_Resistance_kOhms',
                 'Corrected_HeartRate_RR_Interval']
ranges = [[50, 700], [0, None], [0, None], [200, 2000]]

calculated_labels = ['RR_RMSSD', 'Cumulative_EDA', "Cumulative_Dilation_Left", "Cumulative_Dilation_Right"]


def calculate_all(row, exposure_data_group):
    global column_names
    global range_columns
    global ranges

    return calculate_stats(row, exposure_data_group, column_names, -1) + calculate_stats_with_range(row,
                                                                                                    exposure_data_group,
                                                                                                    range_columns,
                                                                                                    ranges) + calculate_rmssd(
        row, exposure_data_group) + calculate_cumulative_column(row, exposure_data_group,
                                                                "Shimmer_D36A_GSR_Skin_Conductance_uS") + calculate_cumulative_column(
        row, exposure_data_group, "foveal_corrected_dilation_left") + calculate_cumulative_column(row,
                                                                                                  exposure_data_group,
                                                                                                  "foveal_corrected_dilation_right")


def calculate_all_before_start(row, exposure_data_group, sep_row, sep_exposure, time_window):
    global column_names
    global range_columns
    global ranges

    return calculate_stats_before_start(row, exposure_data_group, column_names, sep_row, sep_exposure, time_window,
                                        -1) + calculate_stats_before_start_with_range(row, exposure_data_group,
                                                                                      range_columns, sep_row,
                                                                                      sep_exposure, time_window,
                                                                                      ranges) + calculate_rmssd_before_start(
        row, exposure_data_group, sep_row, sep_exposure, time_window) + calculate_cumulative_column_before_start(row,
                                                                                                                 exposure_data_group,
                                                                                                                 sep_row,
                                                                                                                 sep_exposure,
                                                                                                                 time_window,
                                                                                                                 "Shimmer_D36A_GSR_Skin_Conductance_uS") + calculate_cumulative_column_before_start(
        row, exposure_data_group, sep_row, sep_exposure, time_window,
        "foveal_corrected_dilation_left") + calculate_cumulative_column_before_start(row, exposure_data_group, sep_row,
                                                                                     sep_exposure, time_window,
                                                                                     "foveal_corrected_dilation_right")


########################################### An Aggregation Function ####################################################################

Aggregation_Name = "Exposure_Full_Time_Window"

raw_merged_data_lbls = [f'{Aggregation_Name}_{stat}_{lbl}' for lbl in column_labels for stat in STATS]
ranged_merged_data_lbls = [f'{Aggregation_Name}_{stat}_{lbl}' for lbl in ranged_labels for stat in STATS]
merged_calculated_labels = [f'{Aggregation_Name}_{lbl}' for lbl in calculated_labels]

print(f"Running Phys Aggregation for: {Aggregation_Name}...")

merged_data[raw_merged_data_lbls + ranged_merged_data_lbls + merged_calculated_labels] = merged_data.progress_apply(
    lambda row: pd.Series(calculate_all(row, exposure_data[
        (exposure_data['Participant_ID'] == row['Participant_ID']) &
        (exposure_data['AvatarCondition'] == row['Avatar_Condition']) &
        (exposure_data['Shown_Scene'] == row['Scene_Name'])
        ])),
    axis=1
)

print(f"Aggregation: {Aggregation_Name} Completed.")

merged_data.to_csv(f'Aggregation/Final_Aggregate_{Aggregation_Name}_51ps.csv', index=False)

###################################### Copy 1 for Dog Stimuli Phase ################################################################

Aggregation_Name = "Exposure_Dog_Stimuli_Study_Phase"

raw_merged_data_lbls = [f'{Aggregation_Name}_{stat}_{lbl}' for lbl in column_labels for stat in STATS]
ranged_merged_data_lbls = [f'{Aggregation_Name}_{stat}_{lbl}' for lbl in ranged_labels for stat in STATS]
merged_calculated_labels = [f'{Aggregation_Name}_{lbl}' for lbl in calculated_labels]

print(f"Running Phys Aggregation for: {Aggregation_Name}...")

merged_data[raw_merged_data_lbls + ranged_merged_data_lbls + merged_calculated_labels] = merged_data.progress_apply(
    lambda row: pd.Series(calculate_all(row, exposure_data[
        (exposure_data['Participant_ID'] == row['Participant_ID']) &
        (exposure_data['AvatarCondition'] == row['Avatar_Condition']) &
        (exposure_data['Shown_Scene'] == row['Scene_Name']) &
        (exposure_data['Study_Phase'] == 'Dog Stimuli')
        ])),
    axis=1
)

print(f"Aggregation: {Aggregation_Name} Completed.")

merged_data.to_csv(f'Aggregation/Final_Aggregate_{Aggregation_Name}_51ps.csv', index=False)

####################################### Copy 2 for Dog AOI During Exposure #############################################################

Aggregation_Name = "Exposure_Dog_AOI_Tagged"

raw_merged_data_lbls = [f'{Aggregation_Name}_{stat}_{lbl}' for lbl in column_labels for stat in STATS]
ranged_merged_data_lbls = [f'{Aggregation_Name}_{stat}_{lbl}' for lbl in ranged_labels for stat in STATS]
merged_calculated_labels = [f'{Aggregation_Name}_{lbl}' for lbl in calculated_labels]

print(f"Running Phys Aggregation for: {Aggregation_Name}...")

merged_data[raw_merged_data_lbls + ranged_merged_data_lbls + merged_calculated_labels] = merged_data.progress_apply(
    lambda row: pd.Series(calculate_all(row, exposure_data[
        (exposure_data['Participant_ID'] == row['Participant_ID']) &
        (exposure_data['AvatarCondition'] == row['Avatar_Condition']) &
        (exposure_data['Shown_Scene'] == row['Scene_Name']) &
        (exposure_data['AOI_TAG'] == 'Dog')
        ])),
    axis=1
)

print(f"Aggregation: {Aggregation_Name} Completed.")

merged_data.to_csv(f'Aggregation/Final_Aggregate_{Aggregation_Name}_51ps.csv', index=False)

###################################### Copy 3 for Mirror AOI During Exposure #############################################################

Aggregation_Name = "Exposure_Mirror_AOI_Tagged"

raw_merged_data_lbls = [f'{Aggregation_Name}_{stat}_{lbl}' for lbl in column_labels for stat in STATS]
ranged_merged_data_lbls = [f'{Aggregation_Name}_{stat}_{lbl}' for lbl in ranged_labels for stat in STATS]
merged_calculated_labels = [f'{Aggregation_Name}_{lbl}' for lbl in calculated_labels]

print(f"Running Phys Aggregation for: {Aggregation_Name}...")

merged_data[raw_merged_data_lbls + ranged_merged_data_lbls + merged_calculated_labels] = merged_data.progress_apply(
    lambda row: pd.Series(calculate_all(row, exposure_data[
        (exposure_data['Participant_ID'] == row['Participant_ID']) &
        (exposure_data['AvatarCondition'] == row['Avatar_Condition']) &
        (exposure_data['Shown_Scene'] == row['Scene_Name']) &
        (exposure_data['AOI_TAG'] == 'Mirror')
        ])),
    axis=1
)

print(f"Aggregation: {Aggregation_Name} Completed.")

merged_data.to_csv(f'Aggregation/Final_Aggregate_{Aggregation_Name}_51ps.csv', index=False)

########End of 2nd Section######


############################################## Changes to the functions used to apply a previous 60 seconds to the requested range ######################################

Aggregation_Name = "Exposure_60s_Before"

raw_merged_data_lbls = [f'{Aggregation_Name}_{stat}_{lbl}' for lbl in column_labels for stat in STATS]
ranged_merged_data_lbls = [f'{Aggregation_Name}_{stat}_{lbl}' for lbl in ranged_labels for stat in STATS]
merged_calculated_labels = [f'{Aggregation_Name}_{lbl}' for lbl in calculated_labels]

merged_data[raw_merged_data_lbls + ranged_merged_data_lbls + merged_calculated_labels] = merged_data.progress_apply(
    lambda row: pd.Series(calculate_all_before_start(row, exposure_data[
        (exposure_data['Participant_ID'] == row['Participant_ID']) &
        (exposure_data['AvatarCondition'] == row['Avatar_Condition']) &
        ((exposure_data['Shown_Scene'] == row['Scene_Name']) | (exposure_data['Shown_Scene'] == 'BlankScene'))
        ], 'Scene_Name', 'Shown_Scene', 60)),
    axis=1
)

print(f"Aggregation: {Aggregation_Name} Completed.")

merged_data.to_csv(f'Aggregation/Final_Aggregate_{Aggregation_Name}_51ps.csv', index=False)

merged_data.to_csv(f'Aggregation/Final_Aggregation_Full_51ps.csv', index=False)

######################################################## Pi Chart Generator ##############################################################

houses = ["sad_house", "happy_house", "fear_house", "calm_house"]
acs = ["N", "G", "P"]

tags = exposure_data["AOI_TAG"].unique()
print(tags)

tags = ["Mirror", #"Nothing In Focus",
 "Bed", 'Indoor Plants', 'Carpet',
 'Left Drawers', 'Wardrobe', 'Window', 'Bedside Table', 'Ceiling Fan', 'Dog',
 'Other Room', 'Closed Door', 'Curtain', 'Table Lamps', 'Right Drawers',
 'Radio', 'Picture on Shelf', 'Picture on Wall']

def Generate_Pi_Chart(subset):
    global tags

    values = []

    s_count = subset["Unity_Frame"].count()

    for t in tags:
        ele_count = subset[subset["AOI_TAG"] == t]["Unity_Frame"].count()

        values.append(float(ele_count))

    return tags, values

def Generate_Pi_Chart_Two(subset):
    env = [#"Nothing In Focus",
 "Bed", 'Indoor Plants', 'Carpet',
 'Left Drawers', 'Wardrobe', 'Window', 'Bedside Table', 'Ceiling Fan',
 'Other Room', 'Closed Door', 'Curtain', 'Table Lamps', 'Right Drawers',
 'Radio', 'Picture on Shelf', 'Picture on Wall']

    values = []

    s_count = subset["Unity_Frame"].count()

    ele_count = subset[subset["AOI_TAG"] == "Mirror"]["Unity_Frame"].count()
    values.append(float(ele_count))
    ele_count = subset[subset["AOI_TAG"] == "Dog"]["Unity_Frame"].count()
    values.append(float(ele_count))

    ele_count = 0

    for t in env:
        ele_count += subset[subset["AOI_TAG"] == t]["Unity_Frame"].count()

    values.append(float(ele_count))

    return ["Mirror", "Dog", "Environment"], values

for a in acs:
    labels, vals = Generate_Pi_Chart_Two(exposure_data[(exposure_data['AvatarCondition'] == a)])
    fig, ax = plt.subplots()
    wedges, texts, abcdefg = ax.pie(vals, autopct='%1.1f%%', textprops=dict(color="w"))
    ax.legend(wedges, labels,
          title="AOI Tags",
          loc="center left",
          bbox_to_anchor=(1, 0, 0.5, 1))
    ax.set_title(f"Condition: {a}")

    fig.savefig(f"Condition_{a}_Pie_Short.png")

    # print(list(exposure_data))
    # print(exposure_data['Participant_ID'])
    # print(merged_data['Participant_ID'])
    # print(exposure_data['AvatarCondition']); print(merged_data['Avatar_Condition'])
    # print(exposure_data['Shown_Scene']); print(merged_data['Scene_Name'])

    # merged_data[["pp", "xx"]] = ["abc", "bbc"]

    # for x in column_names:
    #     print(exposure_data[x])

    exposure_data = phys_data_raw

    print(phys_data_raw.shape)
    print(exposure_data.shape)

    sub_dt = exposure_data[
        (exposure_data['Participant_ID'] == 12)
    ]

    print(sub_dt.shape)

    sub_dt = exposure_data[
        (exposure_data['Participant_ID'] == 12) &
        (exposure_data['AvatarCondition'] == "P")
        ]

    print(sub_dt.shape)

    sub_dt = exposure_data[
        (exposure_data['Participant_ID'] == 12) &
        (exposure_data['AvatarCondition'] == "P") &
        (exposure_data['Shown_Scene'] == "sad_house")
        ]

    print(sub_dt["Polar_RR_Interval"].mean())
    print(sub_dt["Polar_RR_Interval"].std())
    print(sub_dt["Polar_RR_Interval"].min())
    print(sub_dt["Polar_RR_Interval"].max())
