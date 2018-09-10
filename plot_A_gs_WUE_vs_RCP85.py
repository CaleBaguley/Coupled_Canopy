#!/usr/bin/env python

"""
Compare transpiration sensitivity to PFT difference in g1 vs. inc. temp/VPD

This makes the plot in the sci reports paper, but with the low temp ramp down
turned off.

That's all folks.
"""
__author__ = "Martin De Kauwe"
__version__ = "1.0 (23.07.2015)"
__email__ = "mdekauwe@gmail.com"

import sys
import numpy as np
import os
import math
import matplotlib.pyplot as plt
import pandas as pd

from farq import FarquharC3
from solve_coupled_An_gs_leaf_temp_transpiration import CoupledModel
from utils import vpd_to_rh, get_dewpoint, calc_esat
import constants as c

def get_values(vpd, Ca, tair, par, pressure, C):
    kpa_2_pa = 1000.
    pa_2_kpa = 1.0 / kpa_2_pa

    #print rh, vpd
    gs_store = np.zeros(0)
    et_store = np.zeros(0)
    An_store = np.zeros(0)
    tair_store = np.zeros(0)
    Cs_store = np.zeros(0)
    Ci_store = np.zeros(0)
    gs_conv = c.MOL_WATER_2_G_WATER * c.G_TO_KG * c.SEC_TO_DAY #* 14 * 2
    an_conv = c.UMOL_TO_MOL * c.MOL_C_TO_GRAMS_C * c.SEC_TO_HLFHR #* 14 * 2
    for i,cax in enumerate(Ca):

        (An, gsw, et, LE, Cs, Ci) = C.main(tair, par, vpd, wind, pressure, cax)

        gs_store = np.append(gs_store, gsw) # mol H20 m-2 s-1
        An_store = np.append(An_store, An) # umol m-2 s-1


    return gs_store, An_store

if __name__ == '__main__':



    df = pd.read_csv("/Users/mdekauwe/Desktop/RCP8.5_co2.csv")

    # Parameters

    # A stuff
    JV_ratio = 2.
    Vcmax25 = 60.0          # ENF CABLE value
    Jmax25 = Vcmax25 * JV_ratio
    Rd25 = 0.92
    Eaj = 30000.0
    Eav = 60000.0
    deltaSj = 650.0
    deltaSv = 650.0
    Hdv = 200000.0
    Hdj = 200000.0
    Q10 = 1.92
    D0 = None
    gamma = None
    g0 = 0.0
    g1 = 2.
    # Misc stuff
    leaf_width = 0.01

    # Cambell & Norman, 11.5, pg 178
    # The solar absorptivities of leaves (-0.5) from Table 11.4 (Gates, 1980)
    # with canopies (~0.8) from Table 11.2 reveals a surprising difference.
    # The higher absorptivityof canopies arises because of multiple reflections
    # among leaves in a canopy and depends on the architecture of the canopy.
    SW_abs = 0.8 # use canopy absorptance of solar radiation

    # variables though obviously fixed here.
    par = 1500.0
    wind = 2.5
    pressure = 101325.0
    vpd = 1.5
    tair = 25
    Ca = df.CO2.values

    JV_ratio = 2.02 #high jv
    Vcmax25 = 60.0          # ENF CABLE value
    Jmax25 = Vcmax25 * JV_ratio
    CM = CoupledModel(g0, g1, D0, gamma, Vcmax25, Jmax25, Rd25,
                     Eaj, Eav,deltaSj, deltaSv, Hdv, Hdj, Q10, leaf_width,
                     SW_abs, gs_model="medlyn")


    (gs_high_jv, an_high_jv) = get_values(vpd, Ca, tair, par, pressure, CM)

    JV_ratio = 1.67 #high jv
    Vcmax25 = 60.0          # ENF CABLE value
    Jmax25 = Vcmax25 * JV_ratio
    CM = CoupledModel(g0, g1, D0, gamma, Vcmax25, Jmax25, Rd25,
                     Eaj, Eav,deltaSj, deltaSv, Hdv, Hdj, Q10, leaf_width,
                     SW_abs, gs_model="medlyn")


    (gs_low_jv, an_low_jv) = get_values(vpd, Ca, tair, par, pressure, CM)


    JV_ratio = (2.0+1.67) / 2. #avg jv
    Vcmax25 = 60.0          # ENF CABLE value
    Jmax25 = Vcmax25 * JV_ratio
    CM = CoupledModel(g0, g1, D0, gamma, Vcmax25, Jmax25, Rd25,
                     Eaj, Eav,deltaSj, deltaSv, Hdv, Hdj, Q10, leaf_width,
                     SW_abs, gs_model="medlyn")


    (gs, an) = get_values(vpd, Ca, tair, par, pressure, CM)



    fig = plt.figure(figsize=(17,4))
    fig.subplots_adjust(hspace=0.1)
    fig.subplots_adjust(wspace=0.3)
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.family'] = "sans-serif"
    plt.rcParams['font.sans-serif'] = "Helvetica"
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['font.size'] = 14
    plt.rcParams['legend.fontsize'] = 14
    plt.rcParams['xtick.labelsize'] = 14
    plt.rcParams['ytick.labelsize'] = 14

    almost_black = '#262626'
    # change the tick colors also to the almost black
    plt.rcParams['ytick.color'] = almost_black
    plt.rcParams['xtick.color'] = almost_black

    # change the text colors also to the almost black
    plt.rcParams['text.color'] = almost_black

    # Change the default axis colors from black to a slightly lighter black,
    # and a little thinner (0.5 instead of 1)
    plt.rcParams['axes.edgecolor'] = almost_black
    plt.rcParams['axes.labelcolor'] = almost_black

    #colour_list = brewer2mpl.get_map('Accent', 'qualitative', 8).mpl_colors
    # CB palette  with grey:
    # from http://jfly.iam.u-tokyo.ac.jp/color/image/pallete.jpg
    colour_list = ["#CC79A7", "#E69F00", "#0072B2", "#009E73", "#F0E442",
                "#56B4E9", "#D55E00", "#000000"]

    ax1 = fig.add_subplot(131)
    ax2 = fig.add_subplot(132)
    ax3 = fig.add_subplot(133)


    ax1.fill_between(df.year, an_low_jv/an_low_jv[0], an_high_jv/an_high_jv[0],
                     color="lightblue", label="Uncertainty due to JV ratio")
    ax1.legend(numpoints=1, loc="upper left", fontsize=10)
    ax2.fill_between(df.year, gs_low_jv/gs_low_jv[0], gs_high_jv/gs_high_jv[0],
                     color="lightblue")

    ax1.plot(df.year, an/an[0], "b-")
    ax2.plot(df.year, gs/gs[0], "b-")
    ax3.plot(df.year, (an / gs) / (an[0] / gs[0]), "g-", lw=3, label="WUE")
    ax3.plot(df.year, Ca / Ca[0], "b--", label="CO$_2$")
    ax3.legend(numpoints=1, loc="best")

    ax1.set_ylabel("$A_{\mathrm{n}}$ response to CO$_2$")
    ax2.set_ylabel("$g_{\mathrm{s}}$ response to CO$_2$")
    ax3.set_ylabel("Response to CO$_2$")
    ax2.set_xlabel("Year")

    #ax1.set_xlim(1900, 2015)
    #ax2.set_xlim(1900, 2015)
    #ax3.set_xlim(1900, 2015)
    #ax1.set_ylim(1.0, 1.5)
    #ax2.set_ylim(1.0, 1.1)
    #ax3.set_ylim(1.0, 1.35)

    fig.savefig("/Users/%s/Desktop/A_gs_wue_vs_RCP85_CO2.pdf" % (os.getlogin()),
                bbox_inches='tight', pad_inches=0.1)
