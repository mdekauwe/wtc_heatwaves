#!/usr/bin/env python

"""
Plot (high PAR > 600) A & E, add the modelling on top ... (todo)
"""

import sys
import os
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import numpy as np
from scipy.stats import gaussian_kde

__author__  = "Martin De Kauwe"
__version__ = "1.0 (16.04.2018)"
__email__   = "mdekauwe@gmail.com"

def main(fname):

    wtc = read_file(fname)

    # create hourly values for subsequent averaging of fluxes
    wtc["DateTime_hr"] = wtc["DateTime_hr"].apply(\
                            lambda x: pd.to_datetime(x).round('30min'))
    wtc_m = wtc.groupby(['DateTime_hr', 'chamber','T_treatment',
                         'HWtrt','combotrt'], as_index=False).mean()
    wtc_m = wtc_m.set_index('DateTime_hr')

    st = pd.datetime.strptime('2016-10-20 00:00:00', '%Y-%m-%d %H:%M:%S')
    en = pd.datetime.strptime('2016-11-11 20:00:00', '%Y-%m-%d %H:%M:%S')
    wtc_m = wtc_m[(wtc_m.index >= st) & (wtc_m.index <= en)]

    df_ct = wtc_m[(wtc_m["HWtrt"] == "C") & (wtc_m["PAR"] > 10.0)]
    df_hw = wtc_m[(wtc_m["HWtrt"] == "HW") & (wtc_m["PAR"] > 10.0)]

    PARlimit = 600
    df_ct = df_ct[df_ct["PAR"] > PARlimit]
    df_hw = df_hw[df_hw["PAR"] > PARlimit]

    width  = 9.0
    height = width / 1.618
    fig = plt.figure(figsize=(width, height))
    fig.subplots_adjust(hspace=0.1)
    fig.subplots_adjust(wspace=0.05)
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.family'] = "sans-serif"
    plt.rcParams['font.sans-serif'] = "Helvetica"
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['font.size'] = 14
    plt.rcParams['legend.fontsize'] = 14
    plt.rcParams['xtick.labelsize'] = 14
    plt.rcParams['ytick.labelsize'] = 14

    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)

    x = df_ct.TargTempC_Avg
    y = df_ct.Photo
    x = np.nan_to_num(x)
    y = np.nan_to_num(y)
    xy = np.vstack([x, y])
    z = gaussian_kde(xy)(xy)
    ax1.scatter(x, y,  c=z, s=25, edgecolor='', cmap='Blues', alpha=0.7)

    x = df_hw.TargTempC_Avg
    y = df_hw.Photo
    x = np.nan_to_num(x)
    y = np.nan_to_num(y)
    xy = np.vstack([x, y])
    z = gaussian_kde(xy)(xy)
    ax2.scatter(x, y,  c=z, s=25, edgecolor='', cmap='Reds', alpha=0.7)

    x = df_ct.TargTempC_Avg
    y = df_ct.Trans
    x = np.nan_to_num(x)
    y = np.nan_to_num(y)
    xy = np.vstack([x, y])
    z = gaussian_kde(xy)(xy)
    ax3.scatter(x, y,  c=z, s=25, edgecolor='', cmap='Blues', alpha=0.7)

    x = df_hw.TargTempC_Avg
    y = df_hw.Trans
    x = np.nan_to_num(x)
    y = np.nan_to_num(y)
    xy = np.vstack([x, y])
    z = gaussian_kde(xy)(xy)
    ax4.scatter(x, y,  c=z, s=25, edgecolor='', cmap='Reds', alpha=0.7)

    ax1.set_ylim(0, 12)
    ax2.set_ylim(0, 12)
    ax3.set_ylim(0, 4)
    ax4.set_ylim(0, 4)
    ax1.set_xlim(15, 45)
    ax2.set_xlim(15, 45)
    ax3.set_xlim(15, 45)
    ax4.set_xlim(15, 45)
    ax1.set_ylabel(u'A$_{canopy}$ (μmol m$^{-2}$ d$^{-1}$)')
    ax3.set_ylabel('E$_{canopy}$ (mmol m$^{-2}$ d$^{-1}$)')
    ax3.set_xlabel('Canopy temperature ($^\circ$C)', position=(1.0, 0.5))
    ax1.get_yaxis().set_label_coords(-0.15,0.5)
    ax3.get_yaxis().set_label_coords(-0.15,0.5)

    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax2.get_xticklabels(), visible=False)
    plt.setp(ax2.get_yticklabels(), visible=False)
    plt.setp(ax4.get_yticklabels(), visible=False)
    fig.savefig("plots/exp_plus_modellng.pdf", bbox_inches='tight',
                pad_inches=0.1)
    #plt.show()


def read_file(fname):

    df = pd.read_csv(fname)
    df['dates'] = pd.to_datetime(df['DateTime_hr'], format='%Y-%m-%d %H:%M:%S')
    df = df.set_index('dates')
    df.drop("DateTime_hr", inplace=True)
    df["year"] = df.index.year
    df["month"] = df.index.month
    df["day"] = df.index.day
    df["doy"] = df.index.dayofyear
    df["hour"] = df.index.hour

    return df


if __name__== "__main__":

    fdir = "raw_data"
    fname = "WTC_TEMP-PARRA_CM_WTCFLUX-CANOPYTEMP_20161029-20161115_L0.csv"
    fname = os.path.join(fdir, fname)
    main(fname)
