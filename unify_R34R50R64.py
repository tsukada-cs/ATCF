#%%
import os
import argparse

import numpy as np


parser = argparse.ArgumentParser()
parser.add_argument("-f", "--fpath", type=str)
parser.add_argument("-o", "--odir", type=str, default="./unified")
args = parser.parse_args()

# test_args = (["-f", "/mnt/raid1/data/ATCF/archive/1856/bal041856.dat"])
# args = parser.parse_args(test_args)

#%%
with open(args.fpath) as f:
    doc = np.array(f.readlines())

times = np.array(["0000000000"] * doc.size)
for i, line in enumerate(doc):
    times[i] = line[8:18]

independent_times = np.array(sorted(list(set(times))))

new_doc = [""]*independent_times.size
insert_col = 95
text_head_dict = {"  34": 0, "  50": 34, "  64": 68}
for i, focus_time in enumerate(independent_times):
    same_time_lines = doc[(times==focus_time)]
    insert_text = ",  34,    ,     ,     ,     ,     ,  50,    ,     ,     ,     ,     ,  64,    ,     ,     ,     ,     "
    for line in same_time_lines:
        rad = line[62:66]
        if rad in ("  34", "  50", "  64"):
            rad_code_r1_r2_r3_r4 = line[61:95]
            insert_text = insert_text[:text_head_dict[rad]] + rad_code_r1_r2_r3_r4 + insert_text[text_head_dict[rad]+len(rad_code_r1_r2_r3_r4):]
    new_doc[i] = line[:insert_col] + insert_text + line[insert_col:]

odir = args.odir
os.makedirs(odir, exist_ok=True)
opath = odir+"/"+os.path.basename(args.fpath)[:-4]+".dat"
with open(opath, "w") as f:
    f.writelines(new_doc)