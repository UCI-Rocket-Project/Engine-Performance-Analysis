# #########################################
# ### Engine Performance Analysis (EDA) ###
# #########################################

# File:                 EPA.py
# Version:              1.1
# Version notes:        - changed thrust detection algorithm to the "at least
#                       12" method
#                       - made plot colors easier to understand
#                       - added legends in plots
# Author:               Jonathan Palafoutas
# Date created:         2020-12-02
# Date last edited:     2020-12-11
# Description:          Calculate various performance parameters from .TDMS
#                       files recorded during static test fires.
# Contact:              jpalafou@uci.edu
     
# To do:                - cannot view more than one plot at a time
#                       - support for .tdms files with no integer index
#                       ([ex] lc.tdms instead of lc_1.tdms)
#                       - more calculations
#                       - support for SI units
#                       - fix potential unit issues in enginecalcs()
#                       - automate saving plots as .png files
#                       - legend gets cut off when saving plot unless I use a
#                       Python studio such as Spyder

# ------------------------------------------------------------------------------
# User-defined variables (check before running)

# Where to find TDMS files
TDMS_path = "/Users/jonathan/Google Drive/11 Spring 2021/UCI Rocket Project/STF3 DATA POG/"
n = 3 # file number to read from .TDMS directory ([ex] "load_30.TDMS")

pre_lc = "lc_" # prefix of load cell data file names ([ex] "load_30.TDMS")
pre_pt = "pt_" # prefix of pressure transducer data file names
pre_tc = "tc_" # prefix of thermocouple data file names

# LabView channel names for each sensor (most likely don't touch this)
time_name = "Time"

lc_LNG_name =       "LNG Tank"
lc_LOX_name =       "LOX Tank"
lc_engine_name =    "Thrust"

pt_LNG1_name =      "LNG PT1"
pt_LNG2_name =      "LNG Injector"
pt_LOX1_name =      "LOX PT1"
pt_LOX2_name =      "LOX Injector 1"
pt_LOX3_name =      "LOX Injector 2"
pt_He1_name =       "He PT1"

tc_engine1_name =   "Temperature_0"
tc_engine2_name =   "Temperature_2"
tc_He_name =        "Temperature_3"

# Identification of thrust curve
thrust_threshold = 0 # lbf (a value greater than this is considered part of
#                       the thrust curve, [ex] "at least 12")

# DO NOT EDIT PAST THIS LINE

# ------------------------------------------------------------------------------
# Enable libiraries (first step of setting up)
from os import system, name
import numpy as np
import pandas as pd
import nptdms
import datetime as dt
from plotnine import *

# ------------------------------------------------------------------------------
# Function definitions
def clearScreen():
    if name == "nt":
        _ = system("cls") # for windows
    else:
        _ = system("clear") # for mac

def startsame(earlyvec, latevec):
    dif = earlyvec[0] - latevec[0] # initial difference
    dif = abs(dif.total_seconds())
    i = 0
    while 1:
        dif_next = earlyvec[i+1] - latevec[0]
        dif_next = abs(dif_next.total_seconds())
        if dif_next > dif:
            return i
            break
        dif = dif_next
        i = i + 1

def endsame(earlyvec, latevec):
    # initial difference
    dif = earlyvec[len(earlyvec)-1] - latevec[len(latevec)-1]
    dif = abs(dif.total_seconds())
    i = len(latevec)-1
    while 1:
        dif_next = earlyvec[len(earlyvec)-1] - latevec[i-1]
        dif_next = abs(dif_next.total_seconds())
        if dif_next > dif:
            return i
            break
        dif = dif_next
        i = i - 1

# ------------------------------------------------------------------------------
# Print text to tell user that the application has begun

clearScreen()
print("")
print("\t███████╗██████╗  █████╗ " + "\n" +
    "\t██╔════╝██╔══██╗██╔══██╗" + "\n" +
    "\t█████╗  ██████╔╝███████║" + "\n" +
    "\t██╔══╝  ██╔═══╝ ██╔══██║" + "\n" +
    "\t███████╗██║     ██║  ██║" + "\n" +
    "\t╚══════╝╚═╝     ╚═╝  ╚═╝")
print("\tEngine Performance Analysis (v1.1)")
print("\tJonathan Palafoutas")
print("")
print("\t"+pre_lc+str(n)+", "+pre_pt+str(n)+", "+pre_tc+str(n))
print("")
print("Setting up ...")
print("\tLibraries enabled")

# ------------------------------------------------------------------------------
# Import LabView data (second step of setting up)

# Load cells
lc = nptdms.TdmsFile(TDMS_path + pre_lc + str(n) + ".TDMS")
lc_time = lc["Untitled"][time_name][:]
lc_LNG  = lc["Untitled"][lc_LNG_name][:]
lc_LOX  = lc["Untitled"][lc_LOX_name][:]
lc_engine = lc["Untitled"][lc_engine_name][:]

print("\tLoad cell data imported")

# Pressure transducers
pt = nptdms.TdmsFile(TDMS_path + pre_pt + str(n) + ".TDMS")
pt_time = pt["Untitled"][time_name][:]
pt_LNG1 = pt["Untitled"][pt_LNG1_name][:]
pt_LNG2 = pt["Untitled"][pt_LNG2_name][:]
pt_LOX1 = pt["Untitled"][pt_LOX1_name][:]
pt_LOX2 = pt["Untitled"][pt_LOX2_name][:]
pt_LOX3 = pt["Untitled"][pt_LOX3_name][:]

print("\tPressure transducer data imported")

# Thermocouples
tc = nptdms.TdmsFile(TDMS_path + pre_tc + str(n) + ".TDMS")
tc_time = tc["Untitled"][time_name][:]
tc_engine1 = tc["Untitled"][tc_engine1_name][:]
tc_engine2 = tc["Untitled"][tc_engine2_name][:]
tc_He = tc["Untitled"][tc_He_name][:]

print("\tThermocouple data imported")

# ------------------------------------------------------------------------------
# Create sensor data frames

# Load cell data frame
lc_data = {\
"Time":lc_time,\
"Thrust":lc_engine,\
"LNG Tank Weight":lc_LNG,\
"LOX Tank Weight":lc_LOX}
lc_df = pd.DataFrame(lc_data)

# Pressure transducer data frame
pt_data = {\
"Time":pt_time,\
"LNG Tank PT": pt_LNG1,\
"LOX Tank PT":pt_LOX1,
"LNG Injector PT":pt_LNG2,\
"LOX Injector PT 1":pt_LOX2,\
"LOX Injector PT 2":pt_LOX3}
pt_df = pd.DataFrame(pt_data)

# Thermocouple data frame
tc_data = {\
"Time":tc_time,\
"Engine Thermocouple 1":tc_engine1,\
"Engine Thermocouple 2":tc_engine2,\
"He Thermocouple":tc_He}
tc_df = pd.DataFrame(tc_data)

# ------------------------------------------------------------------------------
# Make each data frame start and stop at approximately the same time

# Resize data frames to begin at the same time
# Find the vector that begins at the latest time
if lc_df['Time'][0] >= pt_df['Time'][0]:
    if lc_df['Time'][0] >= tc_df['Time'][0]:
        latevec = lc_df['Time']
    else:
        latevec = tc_df['Time']
elif pt_df['Time'][0] >= tc_df['Time'][0]:
    latevec = pt_df['Time']
else:
    latevec = tc_df['Time']

# Apply new start index
i1 = startsame(lc_df['Time'], latevec)
lc_df = lc_df[i1:].reset_index(drop=True)

i2 = startsame(pt_df['Time'], latevec)
pt_df = pt_df[i2:].reset_index(drop=True)

i3 = startsame(tc_df['Time'], latevec)
tc_df = tc_df[i3:].reset_index(drop=True)

# Resize data frames to begin at the same time
# Find the vector that ends at the earliest time
if lc_df['Time'][len(lc_df)-1] <= pt_df['Time'][len(pt_df)-1]:
    if lc_df['Time'][len(lc_df)-1] <= tc_df['Time'][len(tc_df)-1]:
        earlyvec = lc_df['Time']
    else:
        earlyvec = tc_df['Time']
elif pt_df['Time'][len(pt_df)-1] <= tc_df['Time'][len(tc_df)-1]:
    earlyvec = pt_df['Time']
else:
    earlyvec = tc_df['Time']

# # Apply new start index
i1 = endsame(earlyvec, lc_df['Time'])
lc_df = lc_df[0:i1].reset_index(drop=True)

i2 = endsame(earlyvec, pt_df['Time'])
pt_df = pt_df[0:i2].reset_index(drop=True)

i3 = endsame(earlyvec, tc_df['Time'])
tc_df = tc_df[0:i3].reset_index(drop=True)

print("\tAdjusted start and end time")

# ------------------------------------------------------------------------------
# Reindex and interpolate data frames, then combine to make large data frame

# Set data frame index to a datetime index
lc_df = lc_df.set_index('Time')
pt_df = pt_df.set_index('Time')
tc_df = tc_df.set_index('Time')

# Reindex + interpolate lc and pt into data
index_lc_pt = pt_df.index.union(lc_df.index)

lc_df = lc_df.reindex(index_lc_pt).interpolate(method='time')
pt_df = pt_df.reindex(index_lc_pt).interpolate(method='time')

data = pd.concat([lc_df, pt_df], axis=1)

# Same process for including tc
index_data_tc = tc_df.index.union(data.index)

data = data.reindex(index_data_tc).interpolate(method='time')
tc_df = tc_df.reindex(index_data_tc).interpolate(method='time')

data = pd.concat([data, tc_df], axis=1)

# Now we have data!
print("\tInterpolated data to combine into one data frame")

# Remove NaN
is_NaN = data.isnull()
row_has_NaN = is_NaN.any(axis=1)
rows_with_NaN = data[row_has_NaN]
data = data.dropna()

print("\tRemoved " + str(len(rows_with_NaN)) + " rows with null values")

# Write data frame to a csv file (comment out if you don't want to do this)
# createcsv(data)

# We are done with the setup
print("Setting up complete!")
print()

# ------------------------------------------------------------------------------
# Identify thrust curve region

data_trust_ind = data["Thrust"] > thrust_threshold
data_thrust = data[data_trust_ind]

# ------------------------------------------------------------------------------
# Calculations

# Reset data_thrust index
data_thrust = data_thrust.reset_index()

# Convert time to dt values
data_thrust["Time"] = data_thrust["Time"] - data_thrust["Time"][0]

data_thrust["Time"]= data_thrust["Time"].astype("timedelta64[ns]").astype(int)\
    / 1000000000

# call enginecalcs()

# ------------------------------------------------------------------------------
# Interactive function definitions

def createcsv(path):
    data.to_csv(path)
    print("\tWrote csv to " + path)
    print()

def enginecalcs():
    # Calculate average thrust
    avg_thrust = np.mean(data_thrust["Thrust"])
    print("\tAverage thrust = " + str(avg_thrust) + " lbf")

    # Calculate average flow rate and specific impulse
    g = 32.2 # ft/s^2
    m_dot = (-data_thrust["LNG Tank Weight"][len(data_thrust)-1] -\
        data_thrust["LOX Tank Weight"][len(data_thrust)-1] +\
        data_thrust["LNG Tank Weight"][0] +\
        data_thrust["LOX Tank Weight"][0])/data_thrust["Time"]\
        [len(data_thrust)-1]
    m_dot = m_dot/g # convert to slugs
    print("\tAverage mass flow rate = " + str(m_dot) + " slugs/s")

    ISP = avg_thrust/(m_dot*g)
    print("\tISP = " + str(ISP) + " s")
    print()

def plot_thrust_curve():
    thrustcurve = ggplot(data_thrust, aes(x="Time", y="Thrust")) + \
    geom_line() + \
    xlab("Time (s)") + ylab("Thrust (lbf)") + \
    ggtitle("Thrust curve") + theme_bw()
    print(thrustcurve)
    print()

def plot_tank_weight():
    df = pd.melt(data_thrust, id_vars = ["Time"], \
                 value_vars=["LNG Tank Weight", \
                             "LOX Tank Weight"])
    df = df.rename(columns={"variable": "Legend"})
    tanks = ggplot(df) + geom_line(aes(x="Time", y="value", \
                                       color = "Legend")) + \
    xlab("Time (s)") + ylab("Weight (lbf)") + \
    ggtitle("Propellant tank weights") + theme_bw()
    print(tanks)
    print()

def plot_tank_pressure():
    df = pd.melt(data_thrust, id_vars = ["Time"], \
                 value_vars=["LNG Tank PT", \
                             "LOX Tank PT"])
    df = df.rename(columns={"variable": "Legend"})
    tank_pressure = ggplot(df) + geom_line(aes(x="Time", y="value", \
                                       color = "Legend")) + \
    xlab("Time (s)") + ylab("Pressure (psi)") + \
    ggtitle("Propellant tank pressures") + theme_bw()
    print(tank_pressure)
    print()

def plot_inj_pressure():
    df = pd.melt(data_thrust, id_vars = ["Time"], \
                 value_vars=["LNG Injector PT", \
                             "LOX Injector PT 1", \
                                 "LOX Injector PT 2"])
    df = df.rename(columns={"variable": "Legend"})
    inj_pressure = ggplot(df) + geom_line(aes(x="Time", y="value", \
                                              color = "Legend")) + \
    xlab("Time (s)") + ylab("Pressure (psi)") + \
    ggtitle("Injector pressures") + theme_bw()
    print(inj_pressure)
    print()

def plot_thermocouples():
    df = pd.melt(data_thrust, id_vars = ["Time"], \
                 value_vars=["Engine Thermocouple 1", \
                             "Engine Thermocouple 2"])
    df = df.rename(columns={"variable": "Legend"})
    tc_plot = ggplot(df) + geom_line(aes(x="Time", y="value", \
                                              color = "Legend")) + \
    xlab("Time (s)") + ylab("Temperature (C)") + \
    ggtitle("Engine temperatures") + theme_bw()
    print(tc_plot)
    print()
    
def plot_thermocouples_He():
    tc_plot = ggplot(data_thrust) + geom_line(aes(x="Time", \
    y="He Thermocouple")) + \
    xlab("Time (s)") + ylab("Temperature (C)") + \
    ggtitle("Helium line temperature") + theme_bw()
    print(tc_plot)
    print()
