#%%
import os
import argparse

import numpy as np

from atcf import ATCF

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--fpath", type=str)
parser.add_argument("-o", "--odir", type=str, default="./unified")
args = parser.parse_args()
#%% pure text
from atcf import ATCF
atcf = ATCF()
atcf.load(args.fpath)
independent_times = np.array(sorted(list(set(atcf.df["t"]))))

with open(args.fpath) as f:
    doc = f.readlines()

new_doc = [""]*independent_times.size
insert_col = 95
text_head_dict = {"  34": 0, "  50": 34, "  64": 68}
for i, focus_time in enumerate(independent_times):
    same_time_lines = atcf.df.where(atcf.df["t"]==focus_time).dropna(how="all")
    insert_text = ",  34,    ,     ,     ,     ,     ,  50,    ,     ,     ,     ,     ,  64,    ,     ,     ,     ,     "
    for j in range(same_time_lines.shape[0]):
        line_number = same_time_lines.index[j]
        line = doc[line_number]
        rad = line[62:66]
        if rad != "   0":
            rad_code_r1_r2_r3_r4 = line[61:95]
            insert_text = insert_text[:text_head_dict[rad]] + rad_code_r1_r2_r3_r4 + insert_text[text_head_dict[rad]+len(rad_code_r1_r2_r3_r4):]
    new_doc[i] = line[:insert_col] + insert_text + line[insert_col:]

odir = args.odir
os.makedirs(odir, exist_ok=True)
opath = odir+"/"+os.path.basename(args.fpath)[:-4]+".dat"
with open(opath, "w") as f:
    f.writelines(new_doc)

# %% as csv
# import pandas as pd

# atcf = ATCF()
# atcf.load(args.fpath)
# independent_times = np.array(sorted(list(set(atcf.df["t"]))))

# insert_idx = 17
# insert_columns = ["R34_windcode", "R34_r1", "R34_r2", "R34_r3", "R34_r4", "R50_windcode", "R50_r1", "R50_r2", "R50_r3", "R50_r4", "R65_windcode", "R65_r1", "R65_r2", "R65_r3", "R65_r4", "R100_windcode", "R100_r1", "R100_r2", "R100_r3", "R100_r4"]
# insert_length = len(insert_columns)
# new_columns = np.r_[atcf.df.columns[:insert_idx], insert_columns, atcf.df.columns[insert_idx:]]

# new_df = pd.DataFrame(np.full([independent_times.size, new_columns.size], ""), columns=new_columns)

# for i, focus_time in enumerate(independent_times):
#     same_time_lines = atcf.df.where(atcf.df["t"]==focus_time).dropna(how="all")
#     for j in range(same_time_lines.shape[0]):
#         line = same_time_lines.iloc[j]
#         if j == 0:
#             new_df.iloc[i,:insert_idx] = line[:insert_idx]
#             new_df.iloc[i,insert_idx+insert_length:] = line[insert_idx:]
#         if rad != 0:
#             rad = int(line["rad"])
#             new_df[f"R{rad}_windcode"].iloc[i] = line["windcode"]

# odir = args.odir
# os.makedirs(odir, exist_ok=True)
# new_df.to_csv(odir+"/"+os.path.basename(args.fpath)[:-4]+".csv", index=False)