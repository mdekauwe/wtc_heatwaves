#!/usr/bin/env python

"""
Plot experiment time course of Acanopy and Ecanopy, i.e. Fig 2(b) and (c)
"""

import sys
import os
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt

__author__  = "Martin De Kauwe"
__version__ = "1.0 (19.03.2018)"
__email__   = "mdekauwe@gmail.com"

def main(fname):

    wtc = read_file(fname)

    # create hourly values for subsequent averaging of fluxes
    wtc["DateTime_hr"] = wtc["DateTime_hr"].apply(\
                            lambda x: pd.to_datetime(x).round('60min'))
    wtc_m1 = wtc.groupby(['DateTime_hr', 'chamber','T_treatment'],
                          as_index=False).mean()

    # merge in the heatwave treatment key: swapped C12 and C08
    chambers = wtc_m1.chamber.astype('category').cat.categories.tolist()
    link_df = pd.DataFrame({'chamber': chambers,
                            'HWtrt': ["C","C","HW","HW","C","C","HW","C",
                                      "HW","HW","C","HW"]})
    wtc_m = pd.merge(wtc_m1, link_df, on="chamber")
    wtc_m["combotrt"] = (wtc_m.T_treatment + "_" +
                         wtc_m.HWtrt).astype('category')

    # average and SEs for each treatment.
    wtc_m2 = wtc_m1.groupby([wtc_m.DateTime_hr,
                            wtc_m.combotrt],
                            as_index=False).agg(['mean', 'sem'])

    wtc_m = wtc_m.set_index('DateTime_hr')
    wtc_m2_two = wtc_m[(wtc_m.index >= "2016-10-30") &
                       (wtc_m.index <= "2016-11-05")].copy()
    wtc_m2_two['dates'] = wtc_m2_two.index
    wtc_m2_two["month"] = wtc_m2_two.index.month

    df_ct = wtc_m2_two[wtc_m2_two["HWtrt"] == "C"]
    df_hw = wtc_m2_two[wtc_m2_two["HWtrt"] == "HW"]

    df_ct = df_ct.groupby(['DateTime_hr']).mean().reset_index()
    df_hw = df_hw.groupby(['DateTime_hr']).mean().reset_index()

    t1 = pd.datetime.strptime(df_ct['year'][0].astype(int).astype(str)+
                              df_ct['month'][0].astype(int).astype(str)+
                              df_ct['day'][0].astype(int).astype(str),
                              "%Y%m%d")
    df_ct['dates'] = pd.date_range(t1, periods=len(df_ct), freq='60Min')
    df_ct = df_ct.set_index('dates')

    t1 = pd.datetime.strptime(df_hw['year'][0].astype(int).astype(str)+
                              df_hw['month'][0].astype(int).astype(str)+
                              df_hw['day'][0].astype(int).astype(str),
                              "%Y%m%d")
    df_hw['dates'] = pd.date_range(t1, periods=len(df_hw), freq='60Min')
    df_hw = df_hw.set_index('dates')

    width  = 9.0
    height = width / 1.618
    fig = plt.figure(figsize=(width, height))
    fig.subplots_adjust(hspace=0.05)
    fig.subplots_adjust(wspace=0.1)
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.family'] = "sans-serif"
    plt.rcParams['font.sans-serif'] = "Helvetica"
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['font.size'] = 14
    plt.rcParams['legend.fontsize'] = 14
    plt.rcParams['xtick.labelsize'] = 14
    plt.rcParams['ytick.labelsize'] = 14

    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    ax1.plot(df_ct.index, df_ct.Photo, ls="-", color="blue")
    ax1.plot(df_hw.index, df_hw.Photo, ls="-", color="red")
    ax2.plot(df_ct.index, df_ct.Trans, ls="-", color="blue")
    ax2.plot(df_hw.index, df_hw.Trans, ls="-", color="red")

    ax1.axvspan("2016-10-30", "2016-11-03", alpha=0.5, color='lightgrey')
    ax2.axvspan("2016-10-30", "2016-11-03", alpha=0.5, color='lightgrey')

    labels = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
    plt.setp(ax1.get_xticklabels(), visible=False)
    ax2.set_xticklabels(labels)
    ax1.set_ylim(-1, 10)
    ax2.set_ylim(0, 3)
    ax1.set_ylabel(u'A$_{canopy}$ (μmol m$^{-2}$ d$^{-1}$)')
    ax2.set_ylabel('E$_{canopy}$ (mmol m$^{-2}$ d$^{-1}$)')
    #ax1.get_yaxis().set_label_coords(-0.08,0.5)
    #ax2.get_yaxis().set_label_coords(-0.08,0.5)

    plt.show()

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
