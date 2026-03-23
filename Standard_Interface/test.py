import pandas as pd
#
#
# #bugs - try statement fails if our anchor column is part of the cols_to_move list. This happens because static_cols composes of
# #       cols not in cols_to_move, if the anchor is in cols_to_move, then our static_cols won't contain the anchor. Thus, we will be unable
# #       to find the index of the anchor column in static cols. Hence, exception gets thrown.  Should add this as a check in the presenter.
# def place_columns_after_named_column(df, named_column, columns_to_place):
#     # Filter valid columns to move,
#     cols_to_move = [col for col in columns_to_place if col in df.columns]
#
#     # If anchor is missing, return original DF
#     if named_column not in df.columns:
#         print(f"⚠️ Anchor '{named_column}' not found. No changes made.")
#         return df
#
#     # Create the 'static' list (columns NOT being moved)
#     static_cols = [col for col in df.columns if col not in cols_to_move]
#
#     # Find where the anchor is in the static list
#     try:
#         anchor_index = static_cols.index(named_column)
#     except ValueError:
#
#         return df  # Should be caught above, but safety first
#
#     # Reassemble: [Everything before & including anchor] + [Moved Cols] + [Everything else]
#     new_order = static_cols[:anchor_index + 1] + cols_to_move + static_cols[anchor_index + 1:]
#
#     return df[new_order]
#
#
# # 2. Create Dummy Data (Random Order)
data = {
    # The Age column drives the structure (3 groups of 3)
    'Age': [22, 22, 22, 25, 25, 25, 28, 28, 28],

    # Repeating each ID 3 times to match the ages
    'Participant_ID': ['P01', 'P01', 'P01', 'P02', 'P02', 'P02', 'P03', 'P03', 'P03'],

    # Repeating the scores 3 times per person
    # P03 inferred as 90 based on the pattern (100 -> 95 -> 90)
    'Score_Total': [100, 100, 100, 95, 95, 95, 90, 90, 90],

    # P03 inferred as 40 (because Total - B = A)
    'Score_A': [35, 49, 50, 45, 48, 43, 60, 39, 25],

    # Score B seems constant across your examples
    'Score_B': [50, 50, 50, 50, 50, 50, 50, 50, 50],

    'Notes': ['Ok', 'Ok', 'Ok', 'Good', 'Good', 'Good', 'Great', 'Great', 'Great']
}

df = pd.DataFrame(data)
print(df)

group_only = df.groupby('Participant_ID')
for name, group in group_only:
    print(f"\nParticipant: {name}")
    print(group)
    print(type(group_only))

print("----------------------------------------------------")

test = df.groupby('Participant_ID')[['Score_A']]
for name, group in test:
    print(f"\nParticipant: {name}")
    print(group)
    print(type(test))


print(f"test.median() = \n {test.median()} \n test.median().index = {test.median().index}")
print(type(test.median()))
print(test.median().to_dict())


#
# print("--- ORIGINAL ORDER ---")
# print(list(df.columns))
# # Output: ['Score_Total', 'Age', 'Participant_ID', 'Notes', 'Score_A', 'Score_B']
# # 'Score_C_MISSING' does not exist in the dataframe
# mixed_cols = ['Score_A', 'Score_C_MISSING', 'Notes']
#
# df_ex3 = place_columns_after_named_column(df, 'Participant_ID', mixed_cols)
#
# print("\n--- EXAMPLE 3: Handle Missing Column ---")
# print(list(df_ex3.columns))
# # Expected: It moves 'Score_A' and 'Notes', ignores 'Score_C_MISSING', and does not crash.
#
#
# test = [1,2,3]
# print(test[0:2])
#
# print(df)
# print(df[['Score_Total','Age', 'Notes']])
#
