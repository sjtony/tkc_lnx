#!/usr/bin/python
import os
# os.environ['QT_QPA_PLATFORM'] = 'wayland'
'''
SJ(sjhe@kns.com)
The purpose of this app is to list out BITS related error in csv file format
and plot NSOP occurrences
'''
import pdb
import pandas as pd
import numpy as np
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
import re
from datetime import date
from datetime import time
from datetime import datetime
import matplotlib.pyplot as plt


# set up regular expressions
# use https://regexper.com to visualise these if required

def parse_file():
    fName = askopenfilename(title="Hi select a file")  # opens the file selector
    print(fName)
    with open(fName, 'r', encoding="utf8") as f:  # to add encoding for some illegal char in the file
        lines = f.readlines()
    nline = len(lines)
    sFlag = False

    fSave_out = fName + 'SJ' + '.xlsx'
    ls = []
    sample = ''
    imped1 = 0
    imped2 = 0
    imped3 = 0
    imped4 = 0
    device = "NA"
    sample = "NA"
    device_num = "NA"
    wire_num = "NA"
    bond_num = "NA"
    line = "# device_numer wire_number bond_number Type 1st    2nd    3rd   4th Samples Time Time2 Date line"
    for i in range(1, nline):
        if (not sFlag):
            if (re.search(r"<142>", lines[i])):
                sFlag = True
                err_type = "NSOP"
                kk = i + 1
                k = 0
                imped1 = 0
                imped2 = 0
            elif (re.search(r"<143>", lines[i])):
                sFlag = True
                err_type = "NSOL"
                kk = i + 1
                k = 0
                imped1 = 0
                imped2 = 0
            elif (re.search(r"<144>", lines[i])):
                sFlag = True
                err_type = "SHTL"
                kk = i + 1
                k = 0
                imped1 = 0
                imped2 = 0
            elif (re.search(r"<154>", lines[i])):
                sFlag = True
                err_type = "Ltail"
                kk = i + 1
                k = 0
                imped1 = 0
                imped2 = 0
            elif (re.search(r"<175>", lines[i])):
                sFlag = True
                err_type = "STITCH"
                kk = i + 1
                k = 0
                imped1 = 0
                imped2 = 0
            elif (re.search(r"<186>", lines[i])):
                sFlag = True
                err_type = "bondoff_SHTL"
                kk = i + 1
                k = 0
                imped1 = 0
                imped2 = 0
            elif (re.search(r"<1563>\s+EH_SERDES_BUS_ERROR", lines[i])):
                sFlag = True
                err_type = "EH_SERDES_BUS_ERROR"
                kk = i + 1
                k = 0
                imped1 = 0
                imped2 = 0
                imped3 = 0
                imped4 = 0
                device = "NA"
                sample = "NA"
            elif (re.search(r"BONDER REBOOTED", lines[i])):
                sFlag = True
                err_type = "BONDER REBOOTED"
                kk = i + 1
                k = 0
                imped1 = 0
                imped2 = 0
                imped3 = 0
                imped4 = 0
                device = "NA"
                sample = "NA"
            else:
                continue
        else:
            k = k + 1
            if (re.search(r"\#{2}", lines[i]) or (i == nline - 1)):
                sFlag = False
                row = {
                    '#': device,
                    'device_numer': device_num,
                    'wire_number': wire_num,
                    'bond_number': bond_num,
                    'Type': err_type,
                    '1st': imped1,
                    '2nd': imped2,
                    '3rd': imped3,
                    '4th': imped4,
                    'Samples': sample,
                    'Time': time,
                    'Time2': time2,
                    'Date': date,
                    'line': kk,
                }
                ls.append(row)
            elif (re.search(r"\b\d{2}:\d{2}:\d{2}", lines[i])):
                mt = re.search(r"\b\d{2}:\d{2}:\d{2}", lines[i]).group(0)
                nl = lines[i].split()
                mt_idx = nl.index(mt)
                time = nl[mt_idx]
                time2 = time[:-3]
                dat = nl[mt_idx - 2] + ' ' + nl[mt_idx - 1] + ' ' + nl[mt_idx + 1]
                date = datetime.strptime(dat, '%b %d %Y').date()
            elif re.search(r"\[ON\s?samples:", lines[i]):
                match = re.search(r"\[ON\s?samples:\s*(.*)", lines[i])
                if match:
                    sample = match.group(1).strip().rstrip(']')
            elif (re.search(r"BITS\s?measurement:", lines[i])):
                imped = lines[i].strip('BITS measurement:[ ')
                imped = imped.strip('\n')
                imped = imped.strip('[')
                imped = imped.strip(']')
                imped = imped.split(',')
                if (len(imped) == 2):
                    imped1 = imped[0]
                    imped2 = imped[1]
                    imped3 = 0
                    imped4 = 0
                elif (len(imped) == 4):
                    imped1 = imped[0]
                    imped2 = imped[1]
                    imped3 = imped[2]
                    imped4 = imped[3]
            elif (re.search(r"\[device:", lines[i])):
                dev = lines[i].strip('[device:')
                dev = dev.strip('\n')
                dev = dev.strip(']')
                dev = dev.split(',')
                device_num = dev[0]
                wire_num = dev[1].strip('wire: ')
                bond_num = dev[2].strip('bond: ')
            elif (re.search(r"Filter:", lines[i])):
                device = lines[i].strip('Filter:')
                device = device.strip('\n')

    df1 = pd.DataFrame(ls, columns=line.split())
    df1.to_excel(fSave_out, index=False)
    return df1


def plot_nsop_occurrences(df):
    # Filter for NSOP type and create a new DataFrame to avoid SettingWithCopyWarning
    df_nsop = df[df['Type'] == 'NSOP'].copy()
    df_nsop.loc[:, 'Datetime'] = pd.to_datetime(df_nsop['Date'].astype(str) + ' ' + df_nsop['Time'],
                                                format='%Y-%m-%d %H:%M:%S')
    df_nsop.loc[:, 'Minute_of_day'] = df_nsop['Datetime'].dt.hour * 60 + df_nsop[
        'Datetime'].dt.minute  # 1440 minutes per day

    # Create a time series with 1440 points per day (24*60)
    unique_dates = df_nsop['Date'].unique()
    for date in unique_dates:
        df_day = df_nsop[df_nsop['Date'] == date]
        minute_counts = {}
        for minute in range(1440):  # 1440 minutes in a day
            minute_counts[minute] = 0

        # Count NSOP occurrences per minute
        total_nsop = 0
        for minute in df_day['Minute_of_day']:
            if 0 <= minute < 1440:  # Ensure minute is within range
                minute_counts[minute] += 1
                total_nsop += 1

        # Plot with triangles (no lines)
        minutes = [min for min, count in minute_counts.items() if count > 0]
        counts = [count for min, count in minute_counts.items() if count > 0]
        plt.figure(figsize=(12, 6))
        plt.scatter(minutes, counts, marker='^', s=50, label=f'NSOP Occurrences - {date} (Total: {total_nsop})',
                    color='blue')
        plt.xlabel('1440 minutes of Day (00:00 to 23:59)')
        #plt.xlabel('Minute of Day (0 to 1439)')
        plt.ylabel('Number of NSOP Occurrences')
        plt.title(f'NSOP Occurrences on {date}')
        plt.grid(True)
        plt.legend()
        plt.ylim(0, max(counts) + 1 if counts else 1)  # Set y-axis limit based on max count

        # Save plot to PNG file
        plt.savefig(f'nsop_occurrences_{date}.png', bbox_inches='tight')
        plt.show()  # Close the figure to free memory


if __name__ == '__main__':
    data = parse_file()
    plot_nsop_occurrences(data)
