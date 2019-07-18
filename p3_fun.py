import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.fftpack import fft, fftshift
from scipy.signal import savgol_filter

import math
import time
from tkinter import *
from tkinter.filedialog import askopenfilename
from matplotlib.widgets import CheckButtons
pulseSN = -1
def import_data(answerFS):
        fName = askopenfilename(title="Hi slect a file")    #opens the file selctor
        print (fName)
        with open(fName, 'r') as f:
                lines = f.readlines()
        data = []
        # nline = 1024*128*32
        nline = 1024*128*answerFS
        for i in range(7, nline + 7):
                data.append(int(lines[i]))
        return data

def import_dataU():
        fName = askopenfilename(title="Hi slect a file")    #opens the file selctor
        print (fName)
        with open(fName, 'r') as f:
                lines = f.readlines()
        data = []
        # nline = 1024*128*32
        nline = len(lines)
        print(nline)
        for i in range(7, nline - 131):
                data.append(int(lines[i]))
        return data

def processData(data):
        start = time.time()
        raw_data_ = np.array(data)
        raw_data = raw_data_[::-1]              #flip
        nline = len(raw_data)
        t_indx = np.arange(0.0,4.0*nline,4.0)
        t_indx = t_indx/1000    #ms as unit

        analog = np.bitwise_and(raw_data,1023)

        wbms_et = np.bitwise_and(raw_data, 2**15)
        wbms_et = 300*wbms_et/2**15
        #to make sure first pulse start from low !!!
        wbms_et[0] = 0
        #to make sure final pulse start end as  low !!!
        wbms_et[-1] = 0
        print(cp(wbms_et))
        wbms_status = np.bitwise_and (raw_data, 2**10)
        wbms_status = wbms_status/(2**10)*45

        event2_dt = np.bitwise_and (raw_data, 2**11)
        event2_rt = np.bitwise_and (raw_data, 2**12)
        event1_dt = np.bitwise_and (raw_data, 2**13)
        event1_rt = np.bitwise_and (raw_data, 2**14)

        event2_dt = event2_dt/(2**11)*10
        event2_rt = event2_rt/(2**12)*30
        event1_dt = event1_dt/(2**13)*15
        event1_rt = event1_rt/(2**14)*35
        allData = np.array([t_indx, analog, wbms_et, wbms_status, event1_rt, event1_dt, event2_rt, event2_dt])
        t = time.time() - start
        print("Duration: %s" % t)
        return allData

def plotAll(allData, totalPulse, nPulse):
        # plt.close (1)
        plt.close ('all')
        f,ax = plt.subplots()
        t_indx = allData[0, :]          # 1st row
        analog = allData[1, :]
        wbms_et = allData[2, :]
        wbms_status = allData[3, :]
        event1_rt = allData[4, :]
        event1_dt = allData[5, :]
        event2_rt = allData[6, :]
        event2_dt = allData[7, :]
        # plt.figure(1)
        # ax.plot(t_indx, analog, t_indx, wbms_et, t_indx, wbms_status,t_indx, event1_rt, t_indx, event1_dt, t_indx, event2_rt, t_indx, event2_dt)
        p_ch1, = ax.plot(t_indx, analog, lw=1, color='b', label='analog:b')
        p_ch2, = ax.plot(t_indx, wbms_et, lw=1, color='g', label='wbms_et:g')
        p_ch3, = ax.plot(t_indx, wbms_status, lw=1, color='r', label='wbms_status:r')
        p_ch4, = ax.plot(t_indx, event1_rt, lw=1, color='c', label='event1_rt:c')
        p_ch5, = ax.plot(t_indx, event1_dt, lw=1, color='m', label='event1_dt:m')
        p_ch6, = ax.plot(t_indx, event2_rt, lw=1, color='y', label='event2_rt:y')
        p_ch7, = ax.plot(t_indx, event2_dt, lw=1, color='limegreen', label='event2_dt:')
        plt.subplots_adjust(left=0.2)
        plt.title('All')
        plt.xlabel('Time(ms)')
        plt.ylabel('DSP ADC CNTS')

        lines = [p_ch1, p_ch2, p_ch3, p_ch4, p_ch5, p_ch6, p_ch7]

        # Make checkbuttons with all plotted lines with correct visibility
        rax = plt.axes([0.05, 0.4, 0.1, 0.15])
        labels = [str(line.get_label()) for line in lines]
        visibility = [line.get_visible() for line in lines]
        check = CheckButtons(rax, labels, visibility)


        def func(label):
                index = labels.index(label)
                lines[index].set_visible(not lines[index].get_visible())
                plt.draw()

        check.on_clicked(func)

        # plt.plot(t_indx, analog, t_indx, wbms_et)
        # plt.title('All')
        # plt.xlabel('Time(ms)')
        # plt.ylabel('DSP ADC CNTS')

        # f.canvas.mpl_connect('button_press_event', onclick)
        indexOfWire = cw(wbms_et)       #% retrieve the index number of the pulse
        pn = cp(wbms_et)
        totalPulse.delete(0, END)
        totalPulse.insert(0, str(pn))
        # f.canvas.mpl_connect('key_press_event', lambda event: onclick(event, indexOfWire, t_indx))
        f.canvas.mpl_connect('button_press_event', lambda event: onclick(event, indexOfWire, t_indx, nPulse))
        plt.show()


# def plotPartial(allData, start_pulse, end_pulse):
def plotPartial2(allData, list_parm):
        # try:
                # fig2
        # except NameError:
                # print("No name defined yet")
        # else:
                # plt.close (fig2)
        # fig2 = plt.figure()
        f2,ax2 = plt.subplots()

        start_pulse = list_parm[0]
        end_pulse = list_parm[1]
        matchFilterMid = int(list_parm[2])
        matchFilterHT = int(list_parm[3])

        t_indx = allData[0, :]          # 1st row
        analog = allData[1, :]
        wbms_et = allData[2, :]
        wbms_status = allData[3, :]
        event1_rt = allData[4, :]
        event1_dt = allData[5, :]
        event2_rt = allData[6, :]
        event2_dt = allData[7, :]

        print(cp(wbms_et))

        # indexOfWire = fm2.cw(wbms_et) #% pulse could be bond high learn
        indexOfWire = cw(wbms_et)       #% pulse could be bond high learn
        # indexOfWire = find(diff(wbms_et));    % pulse could be bond high learn
        n_indexOfWire = len(indexOfWire)        #% pulse could be bond high learn

        # fig2 = plt.figure()
        i=int(start_pulse)
        j=int(end_pulse)

        analogWire = analog[indexOfWire[2*(i-1)]:indexOfWire[2*(j-1)+1]]
        wbms_etWire = wbms_et[indexOfWire[2*(i-1)]:indexOfWire[2*(j-1)+1]]
        wbms_statusWire = wbms_status[indexOfWire[2*(i-1)]:indexOfWire[2*(j-1)+1]]
        event2_dtWire = event2_dt[indexOfWire[2*(i-1)]:indexOfWire[2*(j-1)+1]]
        event2_rtWire = event2_rt[indexOfWire[2*(i-1)]:indexOfWire[2*(j-1)+1]]
        event1_dtWire = event1_dt[indexOfWire[2*(i-1)]:indexOfWire[2*(j-1)+1]]
        event1_rtWire = event1_rt[indexOfWire[2*(i-1)]:indexOfWire[2*(j-1)+1]]
        start = time.time()
        analogWire_medianF = medianfilter(analogWire,127)
        calT = time.time() - start
        print("Duration: %s" % calT)
        analogWire_mf = mvfilter(analogWire,64)
        analogWire_mhf = matchFilter(analogWire, matchFilterMid, matchFilterHT)

        nWire = len(analogWire)
        t_indx2 = np.arange(0.0,4.0*nWire,4.0)
        t_indx2 = t_indx2/1000  #ms as unit
        # create two line as threshold for step differnce
        stepThU = np.zeros(nWire) + 20
        stepThD = np.zeros(nWire) - 20

        # plt.plot(t_indx2, analogWire, t_indx2, wbms_etWire, t_indx2, wbms_statusWire, t_indx2, event1_rtWire, t_indx2, event1_dtWire, t_indx2, event2_rtWire, t_indx2, event2_dtWire)
        p_ch1, = ax2.plot(t_indx2, analogWire, lw=1, color='b', label='analog:b')
        p_ch2, = ax2.plot(t_indx2, wbms_etWire, lw=1, color='g', label='wbms_et:g')
        p_ch3, = ax2.plot(t_indx2, wbms_statusWire, lw=1, color='r', label='wbms_status:r')
        p_ch4, = ax2.plot(t_indx2, event1_rtWire, lw=1, color='c', label='event1_rt:c')
        p_ch5, = ax2.plot(t_indx2, event1_dtWire, lw=1, color='m', label='event1_dt:m')
        p_ch6, = ax2.plot(t_indx2, event2_rtWire, lw=1, color='y', label='event2_rt:y')
        p_ch7, = ax2.plot(t_indx2, event2_dtWire, lw=1, color='limegreen', label='event2_dt:')
        plt.subplots_adjust(left=0.2)
        # plt.title('All')
        plt.xlabel('Time(ms)')
        # plt.ylabel('DSP ADC CNTS')

        lines = [p_ch1, p_ch2, p_ch3, p_ch4, p_ch5, p_ch6, p_ch7]

        # Make checkbuttons with all plotted lines with correct visibility
        rax = plt.axes([0.05, 0.4, 0.1, 0.15])
        labels = [str(line.get_label()) for line in lines]
        visibility = [line.get_visible() for line in lines]
        check = CheckButtons(rax, labels, visibility)


        def func(label):
                index = labels.index(label)
                lines[index].set_visible(not lines[index].get_visible())
                plt.draw()

        check.on_clicked(func)

        plt.show()

def plotPartial3(allData, list_parm):
        # plt.close (3)
        f2,ax3 = plt.subplots()

        start_pulse = list_parm[0]
        end_pulse = list_parm[1]
        matchFilterMid = int(list_parm[2])
        matchFilterHT = int(list_parm[3])

        t_indx = allData[0, :]          # 1st row
        analog = allData[1, :]
        wbms_et = allData[2, :]
        wbms_status = allData[3, :]
        event1_rt = allData[4, :]
        event1_dt = allData[5, :]
        event2_rt = allData[6, :]
        event2_dt = allData[7, :]

        # indexOfWire = fm2.cw(wbms_et) #% pulse could be bond high learn
        indexOfWire = cw(wbms_et)       #% pulse could be bond high learn
        # indexOfWire = find(diff(wbms_et));    % pulse could be bond high learn
        n_indexOfWire = len(indexOfWire)        #% pulse could be bond high learn

        # fig3 = plt.figure()
        i=int(start_pulse)
        j=int(end_pulse)

        analogWire = analog[indexOfWire[2*(i-1)]:indexOfWire[2*(j-1)+1]]
        wbms_etWire = wbms_et[indexOfWire[2*(i-1)]:indexOfWire[2*(j-1)+1]]
        wbms_statusWire = wbms_status[indexOfWire[2*(i-1)]:indexOfWire[2*(j-1)+1]]
        event2_dtWire = event2_dt[indexOfWire[2*(i-1)]:indexOfWire[2*(j-1)+1]]
        event2_rtWire = event2_rt[indexOfWire[2*(i-1)]:indexOfWire[2*(j-1)+1]]
        event1_dtWire = event1_dt[indexOfWire[2*(i-1)]:indexOfWire[2*(j-1)+1]]
        event1_rtWire = event1_rt[indexOfWire[2*(i-1)]:indexOfWire[2*(j-1)+1]]
        # analogWire_bk1 = analogWire
        start = time.time()
        analogWire_medianF = medianfilter(analogWire, (matchFilterHT - 1))
        # analogWire_bk2 = analogWire
        calT = time.time() - start
        print("Duration: %s" % calT)
        analogWire_mf = mvfilter(analogWire, matchFilterHT)
        analogWire_mhf = matchFilter(analogWire, matchFilterMid, matchFilterHT)
        analogWire_mhf_bak = matchFilter(analogWire, matchFilterMid, matchFilterHT)
        analogWire_mhf_pulse = convert2pulse(analogWire_mhf_bak, 20, -20)
        # to calculate the step  signal based on signal after median filter
        analogWire_medianF_mhf = matchFilter(analogWire_medianF, matchFilterMid, matchFilterHT)

        # to take note if array being changed after function calling
        if (np.array_equal(analogWire_mhf, analogWire_mhf_pulse)):
                print('mutable')
        if (np.array_equal(analogWire_mhf_pulse, analogWire_mhf_bak)):
                print('issue')

        nWire = len(analogWire)
        t_indx2 = np.arange(0.0,4.0*nWire,4.0)
        t_indx2 = t_indx2/1000  #ms as unit
        # create two line as threshold for step differnce
        stepThU = np.zeros(nWire) + 25
        stepThD = np.zeros(nWire) - 25

        dashes = [10, 5, 100, 5]  # 10 points on, 5 off, 100 on, 5 off
        # plt.plot(t_indx2, analogWire, t_indx2, analogWire_mf, t_indx2, analogWire_mhf, t_indx2, analogWire_medianF, t_indx2, stepThU, '--', t_indx2, stepThD, '--')
        p_ch31, = ax3.plot(t_indx2, analogWire, lw=1, color='b', label='analog:b')
        p_ch32, = ax3.plot(t_indx2, analogWire_mf, lw=1, color='r', label='mvf:g')
        # p_ch32, = ax3.plot(t_indx2, analogWire_mhf_bak + 1, lw=1, color='r', label='mhf_bak:r')
        p_ch33, = ax3.plot(t_indx2, analogWire_mhf, lw=1, color='g', label='mhf:r')
        p_ch34, = ax3.plot(t_indx2, analogWire_medianF, lw=1, color='c', label='medianf:c')
        p_ch35, = ax3.plot(t_indx2, stepThU, lw=0.2, color='indigo', label='thU:indigo')
        p_ch36, = ax3.plot(t_indx2, stepThD, lw=0.2, color='indigo', label='thD:indigo')
        p_ch37, = ax3.plot(t_indx2, analogWire_mhf_pulse, lw=1, color='m', label='mhf_pulse:m')
        p_ch38, = ax3.plot(t_indx2, analogWire_medianF_mhf, lw=1, color='y', label='mhf2:y')
        p_ch35.set_dashes(dashes)
        p_ch36.set_dashes(dashes)
        plt.subplots_adjust(left=0.2)
        # plt.title('All')
        #plt.title("wire pulse nomber between %i and %i", i, j )
        plt.title("pulse number from " + start_pulse + " to " + end_pulse )
        plt.xlabel('Time(ms)')
        # plt.ylabel('DSP ADC CNTS')

        lines = [p_ch31, p_ch32, p_ch33, p_ch34, p_ch35, p_ch36, p_ch37, p_ch38]

        # Make checkbuttons with all plotted lines with correct visibility
        rax = plt.axes([0.05, 0.4, 0.1, 0.15])
        labels = [str(line.get_label()) for line in lines]
        visibility = [line.get_visible() for line in lines]
        check = CheckButtons(rax, labels, visibility)

        def func(label):
                index = labels.index(label)
                lines[index].set_visible(not lines[index].get_visible())
                plt.draw()

        check.on_clicked(func)

        plt.show()


def plotPartial4(allData, list_parm):
        f,ax = plt.subplots()

        start_pulse = list_parm[0]
        end_pulse = list_parm[1]
        matchFilterMid = int(list_parm[2])
        matchFilterHT = int(list_parm[3])

        t_indx = allData[0, :]          # 1st row
        analog = allData[1, :]
        wbms_et = allData[2, :]
        wbms_status = allData[3, :]
        event1_rt = allData[4, :]
        event1_dt = allData[5, :]
        event2_rt = allData[6, :]
        event2_dt = allData[7, :]

        indexOfWire = cw(wbms_et)       #% pulse could be bond high learn
        n_indexOfWire = len(indexOfWire)        #% pulse could be bond high learn

        i=int(start_pulse)
        j=int(end_pulse)

        analogWire = analog[indexOfWire[2*(i-1)]:indexOfWire[2*(j-1)+1]]
        wbms_etWire = wbms_et[indexOfWire[2*(i-1)]:indexOfWire[2*(j-1)+1]]
        wbms_statusWire = wbms_status[indexOfWire[2*(i-1)]:indexOfWire[2*(j-1)+1]]
        event2_dtWire = event2_dt[indexOfWire[2*(i-1)]:indexOfWire[2*(j-1)+1]]
        event2_rtWire = event2_rt[indexOfWire[2*(i-1)]:indexOfWire[2*(j-1)+1]]
        event1_dtWire = event1_dt[indexOfWire[2*(i-1)]:indexOfWire[2*(j-1)+1]]
        event1_rtWire = event1_rt[indexOfWire[2*(i-1)]:indexOfWire[2*(j-1)+1]]

        ##analogWire_var, analogWire_std = calStdVari(analogWire, matchFilterHT)
        analogWire_std = calStdVari(analogWire, matchFilterHT)
        analogWire_mf = mvfilter(analogWire, matchFilterHT)
        analogWire_mf2 = mvfilter(analogWire, matchFilterHT)
        analogWire_mhf = matchFilter(analogWire, matchFilterMid, matchFilterHT)
        analogWire_mhf_bak = matchFilter(analogWire, matchFilterMid, matchFilterHT)
        analogWire_mhf_pulse = convert2pulse(analogWire_mhf_bak, 20, -20)

        # debug
        if (np.array_equal(analogWire_mf, analogWire_mf2)):
                print('analogWire in function mvfilter not mutable')
        if (np.array_equal(analogWire_mhf, analogWire_mhf_pulse)):
                print('mutable')
        if (np.array_equal(analogWire_mhf, analogWire_mhf_bak)):
                print('issue')

        nWire = len(analogWire)
        t_indx2 = np.arange(0.0,4.0*nWire,4.0)
        t_indx2 = t_indx2/1000  #ms as unit
        # create two line as threshold for step differnce
        stepThU = np.zeros(nWire) + 20
        stepThD = np.zeros(nWire) - 20

        dashes = [10, 5, 100, 5]  # 10 points on, 5 off, 100 on, 5 off
        p_ch1, = ax.plot(t_indx2, analogWire, lw=1, color='b', label='analog:b')
        p_ch2, = ax.plot(t_indx2, wbms_etWire, lw=1, color='g', label='wbms_et:g')
        p_ch3, = ax.plot(t_indx2, wbms_statusWire, lw=1, color='r', label='wbms_status:r')
        p_ch4, = ax.plot(t_indx2, event1_rtWire, lw=1, color='c', label='event1_rt:c')
        p_ch5, = ax.plot(t_indx2, event1_dtWire, lw=1, color='m', label='event1_dt:m')
        p_ch6, = ax.plot(t_indx2, event2_rtWire, lw=1, color='y', label='event2_rt:y')
        p_ch7, = ax.plot(t_indx2, event2_dtWire, lw=1, color='limegreen', label='event2_dt:')
        p_ch8, = ax.plot(t_indx2, analogWire_mf, lw=1, color='navy', label='mvf:navy')
        p_ch9, = ax.plot(t_indx2, analogWire_mhf, lw=1, color='blueviolet', label='mhf:blueviolet')
        p_ch10, = ax.plot(t_indx2, stepThU, lw=0.2, color='indigo', label='thU:indigo')
        p_ch11, = ax.plot(t_indx2, stepThD, lw=0.2, color='indigo', label='thD:indigo')
        p_ch12, = ax.plot(t_indx2, analogWire_mhf_pulse, lw=1, color='dodgerblue', label='cliped pulse' )
        p_ch13, = ax.plot(t_indx2, analogWire_std, lw=1, color='k', label='std' )

        p_ch10.set_dashes(dashes)
        p_ch11.set_dashes(dashes)

        plt.subplots_adjust(left=0.2)
        plt.xlabel('Time(ms)')
        plt.title("pulse number from " + start_pulse + " to " + end_pulse )

        lines = [p_ch1, p_ch2, p_ch3, p_ch4, p_ch5, p_ch6, p_ch7, p_ch8, p_ch9, p_ch10, p_ch11, p_ch12, p_ch13]
        # lines = [p_ch1, p_ch2, p_ch3, p_ch4, p_ch5, p_ch6, p_ch7, p_ch8, p_ch9, p_ch10, p_ch11, p_ch12]

        # Make checkbuttons with all plotted lines with correct visibility
        rax = plt.axes([0.02, 0.4, 0.11, 0.3])
        labels = [str(line.get_label()) for line in lines]
        visibility = [line.get_visible() for line in lines]
        check = CheckButtons(rax, labels, visibility)

        def func(label):
                index = labels.index(label)
                lines[index].set_visible(not lines[index].get_visible())
                plt.draw()

        check.on_clicked(func)

        plt.show()


# def fitPlot(allData, start_pulse, end_pulse, t1, t2, deg):
def fitPlot(allData, list_parm2):
        start_pulse = list_parm2[0]
        end_pulse = list_parm2[1]
        t1 = list_parm2[2]
        t2 = list_parm2[3]
        deg = list_parm2[4]
        sgFilterWindow = int(list_parm2[5])
        sgFilterOrder = int(list_parm2[6])

        plt.close (4)
        plt.close (5)
        plt.close (6)
        plt.close (7)
        plt.close (8)

        t_indx = allData[0, :]          # 1st row
        analog = allData[1, :]
        wbms_et = allData[2, :]

        indexOfWire = cw(wbms_et)       #% pulse could be bond high learn
        n_indexOfWire = len(indexOfWire)        #% pulse could be bond high learn

        plt.figure(4)
        i=int(start_pulse)
        j=int(end_pulse)

        analogWire = analog[indexOfWire[2*(i-1)]:indexOfWire[2*(j-1)+1]]

        nWire = len(analogWire)
        t_indx2 = np.arange(0.0,4.0*nWire,4.0)
        t_indx2 = t_indx2/1000  #ms as unit
        t1_indx = int(int(t1)*1000/4)
        t2_indx = int(int(t2)*1000/4)

        x = t_indx2[t1_indx:t2_indx]
        y = analogWire[t1_indx:t2_indx]
        # if (int(deg) != 0):
        z = np.polyfit(x, y, int(deg))          # generae coefficient
        print (z[0])
        # Constructs a polynom p from the given coefficient sequence ordered in decreasing power.
        p = np.poly1d(z)
        print (p)


        # xdata = xp
        # ydata = y
        # popt, pcov = curve_fit(func, xdata, ydata)

        # plt.plot(xdata, func(xdata, *popt), 'r-', label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))
        # plt.plot(x, y, x, np.polyval(p, x), '-r', xdata, func(xdata, *popt), 'b-', label='fit: a=%5.3f, b=%5.3f, c=%5.3f' % tuple(popt))
        plt.plot(x, y, x, np.polyval(p, x), '-r')

        plt.figure(5)

        yhat = savgol_filter(y, sgFilterWindow, sgFilterOrder) # window size 51, polynomial order 3
        plt.plot(x, y, x, yhat)

        plt.title('Savitzky-Golay filter.')
        plt.xlabel('Time(ms)')

        plt.ylabel('DSP ADC CNTS')
        # plt.legend(loc='best')

        plt.figure(6)
        sum, peak = triang_template()

        peak_find = signal.convolve(y, peak, mode='same')/sum

        # How to remove the boundary effects arising due to zero padding in scipy/numpy fft?
        peak_find[0:100] = 0
        peak_find[-100:-1] = 0
        peak_find[-1] = 0
        plt.plot(x, y, x, peak_find)

        plt.title('peak_find')
        plt.xlabel('Time(ms)')

        plt.figure(7)
        y_mvfilter = mvfilter(y, sgFilterWindow)
        plt.plot(x, y, x, y_mvfilter)

        plt.title('moving filter ')
        plt.xlabel('Time(ms)')

        plt.ylabel('DSP ADC CNTS')
        # plt.legend(loc='best')

        plt.figure(8)
        y_diff = np.diff(y, 1)
        y_diff_ = np.insert(y_diff, 0, 0)               # add 0 at the beginning
        # y_diff_ = np.insert(y_diff_, 0, 0)            # add 0 at the beginning

        plt.plot(x, y, x, y_diff_)

        plt.title('Moving diff ')
        plt.xlabel('Time(ms)')

        plt.ylabel('DSP ADC CNTS')
        # plt.legend(loc='best')


        plt.show()

def func(x, a, b, c):
        return a * np.exp(-b * x) + c

def cw(v):
        ''' to compute index of wire pulse'''
        v2 = np.diff(v)
        tuple_w = np.nonzero(v2)
        array_w = tuple_w[0]
        # print (array_w)
        return array_w

def cp(v):
        ''' to compute_pulse from the vector'''
        v2 = np.diff(v)
        n= np.count_nonzero(v2>0)
        return n


def medianfilter(v, n):
        ''' to perform median  filter from the vector'''
        # a=1
        # b=np.ones(n)/n
        v2 = signal.medfilt(v, n)
        return v2

def mvfilter(v, n):
        ''' to perform moving filter from the vector'''
        a=1
        b=np.ones(n)/n
        v2 = signal.lfilter(b,a,v)
        return v2

def matchFilter(v, n, m):
        ''' to perform match filter from the vector
        n for number of data in middle with coefficient  = 0
        m for number of data of 1st and 3rd filter with coefficient  =1 or -1'''
        a=1
        b1=np.ones(n+2*m)
        b2=np.ones(n+m)
        b3=np.ones(m)

        v1 = signal.lfilter(b1,a,v)
        v2 = signal.lfilter(b2,a,v)
        v11 = v1-v2
        v3 = signal.lfilter(b3,a,v)
        v4 = (v11 - v3)/m
        return v4

def findPulseNo(xdata, id, v):
        ''' to print the pule s/n   after click the place'''
        global pulseSN
        pulseNo = int(len(id)/2)
        print (len(id))
        for i in range(0, pulseNo):
        #v for i in range(0, 5):
                if (xdata >= v[id[2*(i-1)]]) and  (xdata <= v[id[2*(i-1)+1]]):
                        print ([i,  xdata])
                        pulseSN = i
                        break
        return i

def onclick(event, id, v, nPulse):
        print([event.xdata, event.ydata])
        if event.xdata is not None:
                pn = findPulseNo(event.xdata, id, v)
                nPulse.delete(0, END)           # delete existing entry
                nPulse.insert(0, str(pn))

# to pay attition to array, since  array in function is mutable,
# def convert2pulse(a, thrP, thrN):
        # a[a < thrN] = thrN
        # a[a > thrP] = thrP
        # return a
# aarray "a" won't be changes as below
def convert2pulse(a, thrP, thrN):
        b=a.copy()
        b[b < thrN] = thrN
        b[b > thrP] = thrP
        return b



def triang_template():
        # a = np.arange(0,50,2, dtype=int)
        # b = np.arange(48,-1,-2, dtype=int)
        # c = np.zeros(20, dtype=int)
        a = signal.triang(21)
        c = np.zeros(10)
        d = np.concatenate([a,c])
        d2 = d[::-1]            #flip
        d2 = -d2
        e = np.concatenate([d, d2])
        # e2 = e[::-1]
        # e = np.concatenate([a, b])
        return sum(d), e


def calStdVari(v, n):
        # v for variable, n for window size
        # for the init window with n samples
        lenth = len(v)
        v1 = v[:n]
        oldavg =  np.mean(v1)
        oldvar =  np.var(v1, ddof=1)
        var_v = np.ones(lenth)
        std_v = np.ones(lenth)
        # to put first n samples the same
        var_v[:n] = np.ones(n) * oldvar
        std_v[:n] = np.ones(n) * math.sqrt(oldvar)
        # to calculate the variance based on welford's method
        # http://jonisalonen.com/2014/efficient-and-accurate-rolling-standard-deviation/

        for i in range(n, lenth):
                old  = v[i-n]
                new  = v[i]
                newavg = oldavg + (new - old)/n

                newvar = oldvar + (new - old)*(new - newavg + old - oldavg )/(n-1)
                var_v[i] = newvar
# testing found the variance could become minus if all the incoming are the same, like sturation time the analog value is 1023
                # print(i)
                # print(lenth)
                # print(old)
                # print(new)
                # print(oldavg)
                # print(newavg)
                # print(oldvar)
                # print(newvar)
                # print(oldvar)
                # print(newvar)
                # print("**********next*******")
                if (newvar < 0 ):
                        newvar = 0
                std_v[i] = math.sqrt(newvar)
                oldavg = newavg
                oldvar = newvar
#return var_v, std_v
        return std_v

