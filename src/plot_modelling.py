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

sys.path.append('Coupled_Canopy')
from farq import FarquharC3
from solve_coupled_An_gs_leaf_temp_transpiration import CoupledModel
from utils import vpd_to_rh, get_dewpoint, calc_esat
import constants as c

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


    # Parameters

    # A stuff
    Vcmax25 = 34.0
    Jmax25 = 60.0
    Rd25 = 0.92
    Eaj = 21640.
    Eav = 51780.
    deltaSj = 633.0
    deltaSv = 640.0
    Hdv = 200000.0
    Hdj = 200000.0
    Q10 = 1.92

    # Misc stuff
    leaf_width = 0.01
    SW_abs = 0.86 # absorptance to short_wave rad [0,1], typically 0.4-0.6


    # variables though obviously fixed here.
    wind = 8.0
    pressure = 101325.0
    g0 = 0.003
    g1 = 2.9
    Ca = 400.
    D0 = 1.5 # kpa # Note used
    gamma = 0.0
    C = CoupledModel(g0, g1, D0, gamma, Vcmax25, Jmax25, Rd25,
                     Eaj, Eav,deltaSj, deltaSv, Hdv, Hdj, Q10, leaf_width,
                     SW_abs, gs_model="medlyn")


    Et_ct = []
    An_ct = []
    Et_hw = []
    An_hw = []
    for i in range(len(df_ct)):

        (An, gsw, et, LE) = C.main(df_ct.Tair_al[i], df_ct.PAR[i], df_ct.VPD[i],
                                   wind, pressure, Ca)
        Et_ct.append(et* c.MOL_2_MMOL) # mmol m-2 s-1
        An_ct.append(An)               # umol m-2 s-1

    Et_hw = []
    An_hw = []
    for i in range(len(df_hw)):

        (An, gsw, et, LE) = C.main(df_hw.Tair_al[i], df_hw.PAR[i], df_hw.VPD[i],
                                   wind, pressure, Ca)
        Et_hw.append(et * c.MOL_2_MMOL) # mmol m-2 s-1
        An_hw.append(An)                # umol m-2 s-1


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
    ax1.scatter(x, An_ct, color='black', s=5, alpha=0.7)

    x = df_hw.TargTempC_Avg
    y = df_hw.Photo
    x = np.nan_to_num(x)
    y = np.nan_to_num(y)
    xy = np.vstack([x, y])
    z = gaussian_kde(xy)(xy)
    ax2.scatter(x, y,  c=z, s=25, edgecolor='', cmap='Reds', alpha=0.7)
    ax2.scatter(x, An_hw, color='black', s=5, alpha=0.7)

    x = df_ct.TargTempC_Avg
    y = df_ct.Trans
    x = np.nan_to_num(x)
    y = np.nan_to_num(y)
    xy = np.vstack([x, y])
    z = gaussian_kde(xy)(xy)
    ax3.scatter(x, y,  c=z, s=25, edgecolor='', cmap='Blues', alpha=0.7)
    ax3.scatter(x, Et_ct, color='black', s=5, alpha=0.7)

    x = df_hw.TargTempC_Avg
    y = df_hw.Trans
    x = np.nan_to_num(x)
    y = np.nan_to_num(y)
    xy = np.vstack([x, y])
    z = gaussian_kde(xy)(xy)
    ax4.scatter(x, y,  c=z, s=25, edgecolor='', cmap='Reds', alpha=0.7)
    ax4.scatter(x, Et_hw, color='black', s=5, alpha=0.7)

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
