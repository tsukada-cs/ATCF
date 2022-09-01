#%%
import os, glob

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import date2num

import TCtools
# %%
for year in range(2021, 2022):
    f_fpaths = sorted(glob.glob(f"sample_data/{year}/f*.dat"))

    for i, f_fpath in enumerate(f_fpaths):
        sid = os.path.basename(f_fpath)[1:-4]
        dirname = os.path.dirname(f_fpath)
        bdeck_fname = f"/b{sid}.dat"
        b_fpath =  dirname + bdeck_fname

        fdeck = TCtools.ATCF()
        bdeck = TCtools.ATCF()
        try:
            fdeck.load(f_fpath, deck="f")
            bdeck.load(b_fpath, deck="b")
        except FileNotFoundError:
            print(b_fpath + " has not found")
            continue

        withv = fdeck.data.isel(t=fdeck.data["v"].notnull())

        tafb = withv.isel(t=(withv["format"]=="10") * (withv["fixsite"]=="TAFB"))
        sab = withv.isel(t=(withv["format"]=="10") * (withv["fixsite"]=="SAB"))
        dvto = withv.isel(t=withv["format"]=="20")
        airc = withv.isel(t=withv["format"]=="50")
        drps = withv.isel(t=withv["format"]=="60")

        fig, (ax1,ax2) = plt.subplots(1,2, figsize=(12,5), facecolor="w")
        ax1.plot(date2num(bdeck.data.t), bdeck.data["vmax"], "-", c="gray", lw=2, ms=4, label="Best track")
        ax1.scatter(date2num(tafb.t), tafb["v"], c="g", marker="^", s=20, label="DVTS (TAFB)")
        ax1.scatter(date2num(sab.t), sab["v"], c="magenta", marker="s", s=20, label="DVTS (SAB)")
        ax1.scatter(date2num(dvto.t), dvto["v"], c="b", marker="^", s=20, label="DVTO")
        ax1.set_xticklabels(ax1.get_xticks(), rotation=30)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        ax1.grid(ls="--", c="lightgray")
        ax1.legend()
        ax1.set_title(f"Dvorak techniques: {sid[:4]} ({sid[4:]})", loc="left")
        ax1.set(ylim=(0,80), xlabel=f"Time ({sid[4:]})", ylabel="Wind speed (m/s)")

        ax2.plot(date2num(bdeck.data.t), bdeck.data["vmax"], "-", c="gray", lw=2, ms=4, label="Best track")
        ax2.scatter(date2num(airc.t), airc["v"], c="r", s=20, label="AIRC")
        ax2.scatter(date2num(drps.t), drps["v"], c="g", marker="^", s=20, label="DRPS")
        ax2.set_xticklabels(ax2.get_xticks(), rotation=30)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
        ax2.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        ax2.grid(ls="--", c="lightgray")
        ax2.legend()
        ax2.set_title(f"Aircraft observations: {sid[:4]} ({sid[4:]})", loc="left")
        ax2.set(ylim=(0,80), xlabel=f"Date ({sid[4:]})", ylabel="Wind speed (m/s)")

        fig.savefig(f"{dirname}/{sid}.jpeg", dpi=200, bbox_inches="tight", pad_inches=0.1)
        plt.close()
        break
# %%
