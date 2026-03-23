import graphviz

dot = graphviz.Digraph(
    name="dan_script_flow_detailed",
    format="png",
    graph_attr={
        "rankdir": "TB", "fontname": "Helvetica", "fontsize": "12",
        "splines": "spline", "nodesep": "0.4", "ranksep": "0.6",
        "bgcolor": "white", "compound": "true", "dpi": "150",
    },
    node_attr={
        "fontname": "Helvetica", "fontsize": "9",
        "style": "filled", "shape": "box", "margin": "0.15,0.08",
    },
    edge_attr={"fontname": "Helvetica", "fontsize": "8"},
)

C = {
    "p0": ("#fce4ec", "#c62828"), "p1": ("#e3f2fd", "#1565c0"),
    "p2": ("#fff3e0", "#e65100"), "p3": ("#e8f5e9", "#2e7d32"),
    "p4": ("#f3e5f5", "#6a1b9a"), "p5": ("#fff8e1", "#f57f17"),
    "p6": ("#e0f7fa", "#00695c"), "p7": ("#fce4ec", "#ad1457"),
    "save": ("#f5f5f5", "#424242"),
}

def mc(parent, name, label, ck, nodes):
    bg, border = C[ck]
    with parent.subgraph(name=f"cluster_{name}") as c:
        c.attr(label=label, style="filled,rounded", fillcolor=bg,
               color=border, penwidth="2", fontcolor=border,
               fontsize="10", fontname="Helvetica-Bold")
        for nid, nl in nodes:
            c.node(nid, nl, fillcolor=bg, color=border)

def sn(nid, lbl):
    bg, border = C["save"]
    dot.node(nid, lbl, shape="cylinder", fillcolor=bg, color=border, fontcolor="#424242")

# ═══ PHASE 0 ═══
mc(dot, "p0", "Phase 0: CSV Preprocessing (in-place file fixes)", "p0", [
    ("FIX1", "L96-111: for each *_Calibration_Data_RAW.csv\n(excl BLINK) - str.replace() header fix:\n'...IntervalShimmer...' -> '...Interval,Shimmer...'"),
    ("FIX2", "L135-143: remove_extra_comma_from_files()\nfor each *_Calibration_Data_RAW.csv (excl BLINK)\nstrip trailing empty fields from every row"),
])
dot.edge("FIX1", "FIX2")

# ═══ PHASE 1 ═══
mc(dot, "p1", "Phase 1: Load Raw Data Sources", "p1", [
    ("Q_DEMOG", "L150: pd.read_csv()\nScanning_Session_Questionnaire.csv\n-> questionnaire_demog"),
    ("Q_PRE", "L165: pd.read_csv()\nPre_Study_Questionnaire.csv\n-> questionnaire_pre"),
    ("Q_B1", "L168: pd.read_csv()\nBlock1_Questionnaire.csv\n-> questionnaire_block1"),
    ("Q_B2", "L173: pd.read_csv()\nBlock2_Questionnaire.csv\n-> questionnaire_block2"),
    ("Q_B3", "L178: pd.read_csv()\nBlock3_Questionnaire.csv\n-> questionnaire_block3"),
    ("Q_POST", "L184: pd.read_csv()\nPost_Study_Questionnaire.csv\n-> questionnaire_post"),
    ("VR_Q", "L191: load_multiple_files_into_dataframe()\n*_compiled*.csv -> pd.concat(ignore_index=True)\n-> vr_questionnaire_data"),
    ("CAL", "L196: load_with_exclusion()\n*_Calibration_Data.csv (excl _BLINK)\npd.concat(ignore_index=True)\n-> calibration_data"),
    ("CAL_RAW", "L197: load_with_exclusion()\n*_Calibration_Data_RAW.csv (excl _BLINK)\npd.concat(ignore_index=True)\n-> calibration_data_raw"),
    ("PHYS", "L203: load_multiple_files()\n*_RAW_DATA_*.csv -> pd.concat(ignore_index=True)\n-> phys_data_raw"),
])

# ═══ PHASE 2 ═══
mc(dot, "p2", "Phase 2: Value Replacement (numeric codes -> labels)", "p2", [
    ("REP_DEMOG", "L152-162: questionnaire_demog\n.replace() on Gender: 1->Female...5->Prefer not to say\n.replace() on FP_Skin_Type: 1->Type 1...6->Type 6"),
    ("REP_B1", "L169-171: questionnaire_block1\n.replace() Avatar_Condition: 1->N, 2->G, 3->P"),
    ("REP_B2", "L174-176: questionnaire_block2\n.replace() Avatar_Condition: 1->N, 2->G, 3->P"),
    ("REP_B3", "L179-181: questionnaire_block3\n.replace() Avatar_Condition: 1->N, 2->G, 3->P"),
    ("REP_POST", "L185-188: questionnaire_post\n.replace() emotion_most_differences: 1->Yes, 2->No\n.replace() embodiment_most_differences: 1->Yes, 2->No"),
])

# ═══ PHASE 3 ═══
mc(dot, "p3", "Phase 3: Questionnaire Merging Pipeline", "p3", [
    ("RENAME_VR",
     "L256-259: vr_questionnaire_data.rename(inplace):\n"
     "  P# -> Participant_ID\n"
     "  AvatarCondition -> Avatar_Condition\n"
     "  Scene Name -> Scene_Name\n"
     "  Unity Frame -> Unity_Frame"),
    ("MERGE1",
     "L263: merged_data = pd.merge(\n"
     "  vr_questionnaire_data, questionnaire_demog,\n"
     "  on='Participant_ID', how='left',\n"
     "  suffixes=('', '_questionnaire'))"),
    ("MERGE2",
     "L268: merged_data = pd.merge(\n"
     "  merged_data, questionnaire_pre,\n"
     "  on='Participant_ID', how='left',\n"
     "  suffixes=('', '_questionnaire'))"),
    ("CONCAT_BLOCKS",
     "L270-271: questionnaire_all_sessions =\n"
     "  pd.concat([block1, block2, block3])\n"
     "  NOTE: ignore_index NOT set\n"
     "  -> preserves original per-file indices"),
    ("SORT_BLOCKS",
     "L274: .sort_values(\n"
     "  by=['Participant_ID', 'Block_Number'])"),
    ("RESET_IDX",
     "L275: .reset_index(drop=True, inplace=True)\n"
     "  -> clean 0..N-1 integer index\n"
     "  (needed because concat without\n"
     "  ignore_index left duplicate indices)"),
    ("MERGE_POST_BLOCKS",
     "L278: questionnaire_all_sessions =\n"
     "  pd.merge(questionnaire_all_sessions,\n"
     "    questionnaire_post,\n"
     "    on=['Participant_ID'], how='left',\n"
     "    suffixes=('', '_questionnaire'))\n"
     "  NOTE: joins on Participant_ID only\n"
     "  -> post data broadcast to all 3 blocks"),
    ("MERGE3",
     "L281: merged_data = pd.merge(\n"
     "  merged_data, questionnaire_all_sessions,\n"
     "  on=['Participant_ID','Avatar_Condition'],\n"
     "  how='left', suffixes=('','_questionnaire'))"),
])
dot.edge("RENAME_VR", "MERGE1")
dot.edge("MERGE1", "MERGE2")
dot.edge("CONCAT_BLOCKS", "SORT_BLOCKS")
dot.edge("SORT_BLOCKS", "RESET_IDX")
dot.edge("RESET_IDX", "MERGE_POST_BLOCKS")
dot.edge("MERGE_POST_BLOCKS", "MERGE3")
dot.edge("MERGE2", "MERGE3")

# ═══ PHASE 4 ═══
mc(dot, "p4", "Phase 4: Compute Scores / Rename / Reorder / Save", "p4", [
    ("B5",
     "L296-304: Add cols to merged_data:\n"
     "  B5_Extroversion_Score (avg 8, 3 rev)\n"
     "  B5_Agreeableness_Score (avg 9, 4 rev)\n"
     "  B5_Conscientiousness_Score (avg 9, 4 rev)\n"
     "  B5_Neuroticism_Score (avg 8, 3 rev)\n"
     "  B5_Openness_Score (avg 10, 2 rev)"),
    ("ITQ",
     "L308-314: Add cols:\n"
     "  ITQ_Focus_Score (sum 7)\n"
     "  ITQ_Involvement_Score (sum 7)\n"
     "  ITQ_Games_Score (sum 2)\n"
     "  ITQ_Total_Score (sum all 18)"),
    ("EMB",
     "L324-328: Add cols:\n"
     "  Appearance (avg 8)\n"
     "  Response (avg 6)\n"
     "  Ownership (avg 6)\n"
     "  Multi-Sensory (avg 6)\n"
     "  Embodiment_Score (avg of 4 sub-scores)"),
    ("MPS",
     "L331-333: Add cols:\n"
     "  MPS_Phys_Presence_Score (avg 5)\n"
     "  MPS_Social_Presence_Score (avg 5)\n"
     "  MPS_Self_Presence_Score (avg 5)"),
    ("SSQ",
     "L336-339: Add cols:\n"
     "  POST_SSQ_Nausea (sum * 9.54)\n"
     "  POST_SSQ_Occulomotor_Disturbance (sum * 7.58)\n"
     "  POST_SSQ_Disorientation (sum * 13.92)\n"
     "  POST_SSQ_Total (sum * 3.74)"),
    ("RENAME_M",
     "L342-358: merged_data.rename(inplace) 17 cols:\n"
     "  SAM_Arousal -> SAM_Arousal_VR\n"
     "  SAM_Pleasure -> SAM_Pleasure_VR\n"
     "  SAM_Dominance -> SAM_Dominance_VR\n"
     "  Emotion_Excite -> Excitement_VR ... etc\n"
     "  Embodiment_Presence_E_BO_1 -> Embodiment_BO_VR\n"
     "  Embodiment_Presence_MPS_PHYS_5 -> MPS_Phys_Presence_VR\n"
     "  ... (17 total renames)"),
    ("RO1",
     "L361-362: place_columns_after_named_column(\n"
     "  merged_data, 'Avatar_Condition',\n"
     "  ['Block_Number'])\n"
     "  -> moves Block_Number after Avatar_Condition"),
    ("RO2",
     "L364-368: place_columns_after_named_column(\n"
     "  merged_data, 'Scene_Name',\n"
     "  [B5 items+scores, VR/Game exp, Dog,\n"
     "   S_Attr, ITQ items+scores,\n"
     "   Gender, Age, FP_Skin_Type])\n"
     "  -> 65 cols moved after Scene_Name"),
    ("RO3",
     "L371-372: place_columns_after_named_column(\n"
     "  merged_data, 'FP_Skin_Type',\n"
     "  [Baseline_SSQ_*, SAM_*_Baseline,\n"
     "   Excitement...Fear_Baseline])\n"
     "  -> 26 cols moved after FP_Skin_Type"),
    ("RO4",
     "L375-376: place_columns_after_named_column(\n"
     "  merged_data, 'Fear_Baseline',\n"
     "  [SAM_*_VR, Excitement_VR...Fear_VR,\n"
     "   Embodiment_*_VR, MPS_*_VR])\n"
     "  -> 17 cols moved after Fear_Baseline"),
    ("RO5",
     "L379-381: place_columns_after_named_column(\n"
     "  merged_data, 'MPS_Self_Presence_VR',\n"
     "  [SAM/Appeal/Likability Exposure,\n"
     "   A_Attr, MPS items+scores,\n"
     "   Embodiment items+subscores,\n"
     "   POST_SSQ items+scores]) ~60 cols"),
    ("RO6",
     "L384-385: place_columns_after_named_column(\n"
     "  merged_data, 'POST_SSQ_Total',\n"
     "  [avatar_differences_description,\n"
     "   emotion/embodiment rank cols]) 11 cols"),
    ("CHK_DUP",
     "L387: check_duplicate_columns(merged_data)\n"
     "  -> prints warning if duplicate col names"),
])
for a, b in [("B5","ITQ"),("ITQ","EMB"),("EMB","MPS"),("MPS","SSQ"),
             ("SSQ","RENAME_M"),("RENAME_M","RO1"),("RO1","RO2"),
             ("RO2","RO3"),("RO3","RO4"),("RO4","RO5"),("RO5","RO6"),
             ("RO6","CHK_DUP")]:
    dot.edge(a, b)

sn("SAVE_Q", "L390: SAVE\nAggregation/Final_Questionaire_Aggregation_51ps.csv\n(index=False)")

# ═══ PHASE 5 ═══
mc(dot, "p5", "Phase 5: Calibration Data Processing", "p5", [
    ("ALIAS_AGG",
     "L501: aggregated_data = merged_data\n"
     "  (alias - same object, not copy)"),
    ("PD",
     "L550-567: For each grayscale val\n"
     "  [0,16,32,...,240,255] (17 values):\n"
     "  1. Filter calibration_data where\n"
     "     Shown_Gray_Scale_Value == val\n"
     "  2. .set_index('Participant_ID')\n"
     "     [Median_Pupil_Dilation_Left/Right]\n"
     "     .to_dict()\n"
     "  3. aggregated_data['Participant_ID']\n"
     "     .map(dict) -> new cols:\n"
     "     Calibration_PupilDilation_{L/R}_{val}\n"
     "  -> 34 new columns total"),
    ("HR_BPM",
     "L583-588: calibration_data_raw\n"
     "  .groupby('Participant_ID')\n"
     "  ['Polar_HearRateBPM']\n"
     "  -> .median()/.mean()/.std() -> .to_dict()\n"
     "  -> .map() onto aggregated_data\n"
     "  3 new cols: Calibration_{Med/Mean/SD}_\n"
     "  Resting_HeartRate"),
    ("HR_RR_RAW",
     "L590-599: calibration_data_raw\n"
     "  .groupby('Participant_ID')\n"
     "  ['Polar_HeartRate_RR_Interval']\n"
     "  -> median/mean/std -> .to_dict() -> .map()\n"
     "  3 new cols: ..._RR_Interval"),
    ("HR_RMSSD_RAW",
     "L606-610: for participant_id, group in\n"
     "  calibration_data_raw.groupby('Participant_ID'):\n"
     "  rr = group['Polar_HeartRate_RR_Interval']\n"
     "  RMSSD = sqrt(mean(diff(rr)^2))\n"
     "  -> set via .loc[] boolean mask\n"
     "  1 new col: Calibration_RR_Interval_RAW_RMSSD"),
    ("FILTER_ABS",
     "L615-616: filtered_data =\n"
     "  calibration_data_raw[\n"
     "    (RR_Interval > 200) &\n"
     "    (RR_Interval < 2000)]\n"
     "  -> rows outside 200-2000ms dropped"),
    ("HR_RR_ABS",
     "L618-629: filtered_data\n"
     "  .groupby('Participant_ID')\n"
     "  ['Polar_HeartRate_RR_Interval']\n"
     "  -> median/mean/std -> .map()\n"
     "  3 new cols: ...CLEANED_ABS_Threshold"),
    ("HR_RMSSD_ABS",
     "L633-637: for each participant in\n"
     "  filtered_data.groupby:\n"
     "  RMSSD on ABS-cleaned RR\n"
     "  -> .loc[] mask\n"
     "  1 new col: ...CLEANED_ABS_RMSSD"),
    ("BUILD_REL",
     "L639-645: relative_filtered_data = empty DF\n"
     "  For each participant in filtered_data\n"
     "  .groupby('Participant_ID'):\n"
     "    age = group['Participant_Age'].iloc[0]\n"
     "    cleaned = apply_relative_threshold(\n"
     "      group, age)  [iterative row removal\n"
     "      up to 20 iters, threshold=-age/3+45]\n"
     "    relative_filtered_data =\n"
     "      pd.concat([..., cleaned])"),
    ("HR_RR_REL",
     "L647-658: relative_filtered_data\n"
     "  .groupby('Participant_ID')\n"
     "  ['Polar_HeartRate_RR_Interval']\n"
     "  -> median/mean/std -> .map()\n"
     "  3 new cols: ...CLEANED_REL_Threshold"),
    ("HR_RMSSD_REL",
     "L665-669: BUG? Uses filtered_data (ABS)\n"
     "  not relative_filtered_data (REL)\n"
     "  for RMSSD loop -> writes to\n"
     "  Calibration_RR_Interval_CLEANED_REL_RMSSD"),
    ("GSR_RAW",
     "L676-695: calibration_data_raw\n"
     "  .groupby('Participant_ID')\n"
     "  GSR Conductance (uS): med/mean/std\n"
     "  GSR Resistance (kOhms): med/mean/std\n"
     "  -> .to_dict() -> .map()\n"
     "  6 new cols"),
    ("FILTER_GSR",
     "L697-700: filtered_data_conductance =\n"
     "  calibration_data_raw[\n"
     "    (Resistance > 0) &\n"
     "    (Resistance < 2500) &\n"
     "    (Conductance >= 0.1)]"),
    ("GSR_ABS",
     "L702-726: filtered_data_conductance\n"
     "  .groupby('Participant_ID')\n"
     "  Conductance + Resistance:\n"
     "  med/mean/std -> .map()\n"
     "  6 new cols: ...CLEANED_ABS_Threshold"),
    ("FACE",
     "L728-916: calibration_data_raw\n"
     "  .groupby('Participant_ID')\n"
     "  For EACH of 27 blend shapes\n"
     "  (0_Jaw_Forward ... 26_Max):\n"
     "  -> .median()/.mean()/.std()\n"
     "  -> .to_dict() -> .map()\n"
     "  81 new cols (27 x 3)"),
    ("REORDER_CAL",
     "L919: aggregated_data =\n"
     "  place_columns_after_named_column(\n"
     "    aggregated_data, 'Fear_Baseline',\n"
     "    data_header_calibration_measures)\n"
     "  -> moves ~130 calibration cols\n"
     "    right after Fear_Baseline"),
    ("ALIAS_BACK",
     "L921: merged_data = aggregated_data\n"
     "  (reassign alias back)"),
])
for a, b in [("ALIAS_AGG","PD"),("PD","HR_BPM"),("HR_BPM","HR_RR_RAW"),
             ("HR_RR_RAW","HR_RMSSD_RAW"),("HR_RMSSD_RAW","FILTER_ABS"),
             ("FILTER_ABS","HR_RR_ABS"),("HR_RR_ABS","HR_RMSSD_ABS"),
             ("HR_RMSSD_ABS","BUILD_REL"),("BUILD_REL","HR_RR_REL"),
             ("HR_RR_REL","HR_RMSSD_REL"),("HR_RMSSD_REL","GSR_RAW"),
             ("GSR_RAW","FILTER_GSR"),("FILTER_GSR","GSR_ABS"),
             ("GSR_ABS","FACE"),("FACE","REORDER_CAL"),
             ("REORDER_CAL","ALIAS_BACK")]:
    dot.edge(a, b)

sn("SAVE_CAL", "SAVE (implicit)\nFinal_Aggregate_Calibration_51ps.csv")

# ═══ PHASE 6 ═══
mc(dot, "p6", "Phase 6: Physiological Data Aggregation", "p6", [
    ("RELOAD",
     "L1146: merged_data = pd.read_csv(\n"
     "  'Final_Aggregate_Calibration_51ps.csv')"),
    ("ASSIGN_EXP",
     "L1140: exposure_data = phys_data_raw\n"
     "  (alias - same object)"),
    ("PARSE_TS",
     "L1142-1144: exposure_data.loc[:,\n"
     "  'Unity_Timestamp'] =\n"
     "  pd.to_datetime(..., format=\n"
     "  '%Y-%m-%dT%H:%M:%S.%fZ')\n"
     "  .fillna(pd.to_datetime(...,\n"
     "  format='%d-%m-%Y - %H:%M:%S.%f'))\n"
     "  -> parse string -> datetime objects"),
    ("AGG1",
     "L1199-1218: 'Exposure_Full_Time_Window'\n"
     "  merged_data.progress_apply(axis=1):\n"
     "  Filter exposure_data by:\n"
     "    Participant_ID + Avatar_Condition\n"
     "    + Scene_Name\n"
     "  -> calculate_all():\n"
     "    stats(36 cols, filter !=-1)\n"
     "    + stats_with_range(4 cols)\n"
     "    + rmssd(RR 200-2000)\n"
     "    + cumulative(EDA, Dil_L, Dil_R)\n"
     "  -> 200+ new columns"),
    ("AGG2",
     "L1222-1242: 'Exposure_Dog_Stimuli_Study_Phase'\n"
     "  Same + Study_Phase == 'Dog Stimuli'\n"
     "  -> 200+ new columns"),
    ("AGG3",
     "L1246-1265: 'Exposure_Dog_AOI_Tagged'\n"
     "  Same + AOI_TAG == 'Dog'\n"
     "  -> 200+ new columns"),
    ("AGG4",
     "L1269-1310: 'Exposure_Mirror_AOI_Tagged'\n"
     "  Same + AOI_TAG == 'Mirror'\n"
     "  -> 200+ new columns"),
    ("AGG5",
     "L1316-1336: 'Exposure_60s_Before'\n"
     "  Filter incl BlankScene:\n"
     "    (Shown_Scene==Scene_Name) |\n"
     "    (Shown_Scene=='BlankScene')\n"
     "  calculate_all_before_start():\n"
     "    finds min timestamp for scene,\n"
     "    windows 60s before start\n"
     "  -> 200+ new columns"),
])
for a, b in [("RELOAD","ASSIGN_EXP"),("ASSIGN_EXP","PARSE_TS"),
             ("PARSE_TS","AGG1"),("AGG1","AGG2"),("AGG2","AGG3"),
             ("AGG3","AGG4"),("AGG4","AGG5")]:
    dot.edge(a, b)

sn("SAVE_AGG1", "L1220: SAVE Final_Aggregate_\nExposure_Full_Time_Window_51ps.csv")
sn("SAVE_AGG2", "L1244: SAVE Final_Aggregate_\nExposure_Dog_Stimuli_Study_Phase_51ps.csv")
sn("SAVE_AGG3", "L1267: SAVE Final_Aggregate_\nExposure_Dog_AOI_Tagged_51ps.csv")
sn("SAVE_AGG4", "L1312: SAVE Final_Aggregate_\nExposure_Mirror_AOI_Tagged_51ps.csv")
sn("SAVE_AGG5", "L1338: SAVE Final_Aggregate_\nExposure_60s_Before_51ps.csv")
sn("SAVE_FULL", "L1340: SAVE\nFinal_Aggregation_Full_51ps.csv")

# ═══ PHASE 7 ═══
mc(dot, "p7", "Phase 7: Pie Chart Visualization", "p7", [
    ("PIE",
     "L1344-1400: For each AvatarCondition (N,G,P):\n"
     "  Filter exposure_data by condition\n"
     "  Count Unity_Frame per AOI_TAG:\n"
     "    [Mirror, Dog, Environment(sum)]\n"
     "  -> plt.pie(autopct='%1.1f%%')\n"
     "  -> fig.savefig(Condition_{ac}_Pie_Short.png)"),
])

# ═══ CROSS-PHASE EDGES ═══
dot.edge("FIX2", "Q_DEMOG", style="dashed", label="preprocessed CSVs")
dot.edge("Q_DEMOG", "REP_DEMOG")
dot.edge("Q_B1", "REP_B1")
dot.edge("Q_B2", "REP_B2")
dot.edge("Q_B3", "REP_B3")
dot.edge("Q_POST", "REP_POST")
dot.edge("REP_DEMOG", "MERGE1")
dot.edge("VR_Q", "RENAME_VR")
dot.edge("Q_PRE", "MERGE2")
dot.edge("REP_B1", "CONCAT_BLOCKS")
dot.edge("REP_B2", "CONCAT_BLOCKS")
dot.edge("REP_B3", "CONCAT_BLOCKS")
dot.edge("REP_POST", "MERGE_POST_BLOCKS")
dot.edge("MERGE3", "B5")
dot.edge("CHK_DUP", "SAVE_Q")
dot.edge("SAVE_Q", "ALIAS_AGG")
dot.edge("CAL", "PD", label="calibration_data")
dot.edge("CAL_RAW", "HR_BPM", label="calibration_data_raw")
dot.edge("ALIAS_BACK", "SAVE_CAL", style="dashed")
dot.edge("SAVE_CAL", "RELOAD", style="dashed", label="reads CSV from disk")
dot.edge("PHYS", "ASSIGN_EXP", label="phys_data_raw")
dot.edge("AGG1", "SAVE_AGG1")
dot.edge("AGG2", "SAVE_AGG2")
dot.edge("AGG3", "SAVE_AGG3")
dot.edge("AGG4", "SAVE_AGG4")
dot.edge("AGG5", "SAVE_AGG5")
dot.edge("AGG5", "SAVE_FULL")
dot.edge("SAVE_FULL", "PIE")
dot.edge("PHYS", "PIE", label="exposure_data\n(alias of phys_data_raw)")

# ═══ RENDER ═══
out = "/home/qing/PycharmProjects/Forge/.worktrees/dataframe-node-impl/Forge/VR and Scene experiment (3 avatar x 4 scenes)"
p = dot.render(filename="dan_script_flowchart_detailed", directory=out, cleanup=True)
print(f"Saved to: {p}")

