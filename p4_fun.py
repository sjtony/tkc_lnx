import numpy as np
import matplotlib.pyplot as plt
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
import time
import p3_fun
import math


def calDiff(allData, list_parm):
        start_pulse = list_parm[0]
        end_pulse = list_parm[1]
        matchFilterMid = int(list_parm[2])
        matchFilterHT = int(list_parm[3])

        t_indx = allData[0, :]  # 1st row
        analog = allData[1, :]
        wbms_et = allData[2, :]
        wbms_status = allData[3, :]
        event1_rt = allData[4, :]
        event1_dt = allData[5, :]
        event2_rt = allData[6, :]
        event2_dt = allData[7, :]

        # note here we use median filter to preprocess the analog data
        # analog = p3_fun.medianfilter(analog, 127)

        indexOfWire = p3_fun.cw(wbms_et)  # % pulse could be bond high learn
        n_indexOfWire = len(indexOfWire)  # % pulse could be bond high learn

        i = int(start_pulse)
        j = int(end_pulse)
        analog_mhf = p3_fun.matchFilter(analog, matchFilterMid, matchFilterHT)
        # analog_ori = analog
        # analog_cp = analog.copy()
        # if (np.array_equal(analog, analog_cp)):
                # print('analog_ori --- mutable')
                # nWire = len(analog)
                # t_indx = np.arange(0.0,4.0*nWire,4.0)
                # t_indx = t_indx/1000  #ms as unit
                # f,ax = plt.subplots()
                # p_ch1, = ax.plot(t_indx, analog, lw=1, color='b', label='analog:b')
                # p_ch2, = ax.plot(t_indx, analog_ori, lw=1, color='r', label='analog_ori:g')
                # plt.show()

        # analogWire_medianF = p3_fun.medianfilter(analog,127)
        # analogWire_mvedianF_mhf = p3_fun.matchFilter(analogWire_medianF, matchFilterMid, matchFilterHT)

        # Open a file
        fSave = asksaveasfilename(title="Hi slect a directory and file name for saveas ")  # opens the file selctor
        fo = open(fSave, "w")
        line = "sn  cal0 CAL1 BND1 bond12  bond13  NSOP  bond15  nsol1  NSOL \
        BND1-CAL1 BND1-NSOP NSOP-NSOL bnd2Diff bnd11_std bnd14_std stepStart stepDuration z3[0]"
        fo.write(line + '\n');
        for k in range(i, j + 1):
                #print (k)
                x = analog_mhf[indexOfWire[2 * (k - 1)]:indexOfWire[2 * (k - 1) + 1]]
                y = analog[indexOfWire[2 * (k - 1)]:indexOfWire[2 * (k - 1) + 1]]
                # x = analogWire_mvedianF_mhf[indexOfWire[2 * (k - 1)]:indexOfWire[2 * (k - 1) + 1]]
                # y = analogWire_medianF[indexOfWire[2 * (k - 1)]:indexOfWire[2 * (k - 1) + 1]]


                # there are two bonds for wire bond: first bond  and 2nd bond
                # to calculate the event 1 time
                #  event 1 include cal, nsop and shtl for wire durin apply
                #  event 1 include cal, 3xnsop and shtl for wire durin learn
                event1rtWire = event1_rt[indexOfWire[2 * (k - 1)]: indexOfWire[2 * (k - 1) + 1]]
                indexEvent1rtWire = p3_fun.cw(event1rtWire)
                n_indexEvent1rtWire = len(indexEvent1rtWire)
                # continue here for skip the rest of the code and just go next loop
                # most of the time, it count of event eaual =  if it is the bond-height learn
                if n_indexEvent1rtWire < 4:
                        fo.write(str(k) + '  ' + str(int(n_indexEvent1rtWire)) + '   ' + str(int(n_indexEvent1rtWire)) + \
                                         '   ' + str(int(n_indexEvent1rtWire)) + '   ' + str(int(n_indexEvent1rtWire)) + \
                                         '   ' + str(int(n_indexEvent1rtWire)) + '   ' + str(int(n_indexEvent1rtWire)) + '   ' + str(int(n_indexEvent1rtWire)) + \
                                         '   ' + str(int(n_indexEvent1rtWire)) + '   ' + str(int(n_indexEvent1rtWire)) + '   ' + str(int(n_indexEvent1rtWire)) + \
                                         '   ' + str(int(n_indexEvent1rtWire)) + '   ' + str(int(n_indexEvent1rtWire)) + \
                                         '   ' + str(int(n_indexEvent1rtWire)) + \
                                         '   ' + str(int(n_indexEvent1rtWire)) + '   ' + str(int(n_indexEvent1rtWire)) + \
                                         '   ' + str(int(n_indexEvent1rtWire)) + '   ' + str(float(n_indexEvent1rtWire)) + \
                                         '   ' + str(float(n_indexEvent1rtWire)) + '\n')
                        continue

                x1 = x[1280:]  # to eliminate first 5ms data due to EFO and decay change
                y1 = y[1280:]  # to eliminate first 5ms data due to EFO and decay change
                # calculate first 256 data average
                cal0 = np.mean(y1[0:256])
                # to calculate nsol data
                # below is for wire break
                maxi = x1.argmax()
                maxv = x1[maxi]
                # got edge index and back to 2ms and calculated mean value
                # got edge index and forward  to 1ms and calculated mean value ( use 1ms time )
                nsol1 = np.mean(y1[(maxi + 128):(maxi + 128 + 256)])
                nsol2 = np.mean(y1[-256:])  # use last 256

                # calculate the larget rise edge, usually 2nd bond touch
                mini = x1.argmin()
                minv = x1[mini]
                # got edge index and back to 2ms and calculated mean value
                bnd15 = np.mean(y1[(mini - 256 * 3):(mini - 256 * 2)])

                # with origianl wire clamp time but new piezo tetsing
                # to process bonded data of 0.1pf process pp (415 wires) from Tom
                y2 = y[indexEvent1rtWire[1]:indexEvent1rtWire[2]]
                # step change
                #x2 = x[250 * 12:indexEvent1rtWire[2]]
                # calculate the firt bond rise edge
                # it is not good enough to use minimum value, need to check width of pulse
                # convert to 1 for bigger than TH and zero for less than TH
                #stp_pulse = x[250 * 12:indexEvent1rtWire[2]]
                stp_pulse = x[indexEvent1rtWire[1]:indexEvent1rtWire[2]]
                stp_pulseN = convert_one_zero(stp_pulse, -20)
                # to find the index of zero items
                step_range = zero_runs(stp_pulseN)
                step_start = find_index_longest_zero(step_range)

                # mini = x2.argmin()
                mini_left = step_start[0]
                mini_right = step_start[1]
                step_duration = (step_start[1] - step_start[0])/250.0
                # print((mini_left + 250 * 8) / 250)
                # print((mini_right + 250 * 8) / 250)
                # minv = x2[mini]
                # print(minv)
                # got edge index and back to 2ms and calculated mean value
                cal1 = np.mean(y2[(mini_left - 256 * 1):(mini_left - 256)])

                # got edge index and forward  to 1ms and calculated mean value ( use 1ms time )
                bnd11 = np.mean(y2[(mini_right + 256 * 3):(mini_right + 256 * 4)])
                bnd11_std = np.std(y2[(mini_right + 256 * 3):(mini_right + 256 * 4)])

                # plot for debug
                # plt.ion()
                # plt.show()


                # nline = len(y2)
                # t_indx = np.arange(0.0, 4.0 * nline, 4.0)
                # t_indx = t_indx / 1000  # ms as unit
                # plt.figure(k)
                # plt.plot(t_indx, y2, t_indx, x2, t_indx, 10*stp_pulse)
                # plt.draw()
                # plt.pause(0.001)
                # input("Press [enter] to continue.")
                # plt.close()

                # use below one if  do bumping
                ### bnd2 = np.mean(y[(maxi - 256*2 - 1):(maxi - 256)])
                # use below one if  wire bonding
                #analogWire2ndlastEvent1 = y[(indexEvent1rtWire[-4]):(indexEvent1rtWire[-3])]
                # ending time offset 1ms eariler for bnd14 calculation
                # bnd14 is usually called NSOP value
                analogWire2ndlastEvent1 = y[(indexEvent1rtWire[-4]):(indexEvent1rtWire[-3]) - 256]
                bnd14 = np.mean(analogWire2ndlastEvent1)
                bnd14_std = np.std(analogWire2ndlastEvent1)
                # to calculate the analog value before contact declaration and after ( using 1ms)
                        ## note 1  to use below portion code tp5 and tp6 have to be setup differently
                        ## during dump the tp5 and tp6 set as CV and contact signal
                        ## event2_rt for contact declaration, 2 pairs of event for single wire bond
                                # event2rtWire = event2_rt[indexOfWire[2 * (k - 1)]: indexOfWire[2 * (k - 1) + 1]]
                                # indexEvent2rtWire = p3_fun.cw(event2rtWire)
                                # n_indexEvent2rtWire = len(indexEvent2rtWire)
                        ## calculate the value before contact declaration( 1ms )
                                # analogWireContact1msBefore = y[(indexEvent2rtWire[0]) - 256:(indexEvent2rtWire[0])]
                                # bnd12 = np.mean(analogWireContact1msBefore)
                                # bnd12_std = np.std(analogWireContact1msBefore)
                        ## calculate the value after contact declaration( 1ms )
                                # analogWireContact1msAfter = y[(indexEvent2rtWire[0]):(indexEvent2rtWire[0]) + 256]
                                # bnd13 = np.mean(analogWireContact1msAfter)
                                # bnd13_std = np.std(analogWireContact1msAfter)
                        ## to get the different from match filter : the minimum vaue of match filter before contact declaration
                        ## outputMatchFilterBeforeContactDeclaration = x[(indexEvent2rtWire[1]) - 4*256:(indexEvent2rtWire[1])]
                        ## outputMatchFilterBeforeContactDeclaration = x[1280:(indexEvent2rtWire[1])]
                                # outputMatchFilterBeforeContactDeclaration = x[((indexEvent2rtWire[0]) - 1000):(indexEvent2rtWire[0])]
                                # mini_idx_bnd1 = outputMatchFilterBeforeContactDeclaration.argmin()
                                # bond1delta = abs(outputMatchFilterBeforeContactDeclaration[mini_idx_bnd1])

                ## note 2  with new SW, event 1 for cal will finsifhed after first bond contact
                ## so we use the event 1 to calculate analog value before and after cal
                # calculate the value before contact declaration( 1ms )
                analogWireContact1msBefore = y[(indexEvent1rtWire[1]) - 250:(indexEvent1rtWire[1])]
                bnd12 = np.mean(analogWireContact1msBefore)
                bnd12_std = np.std(analogWireContact1msBefore)
                # calculate the value after contact declaration( 1ms )
                analogWireContact1msAfter = y[(indexEvent1rtWire[1]) + 500:(indexEvent1rtWire[1]) + 750]
                bnd13 = np.mean(analogWireContact1msAfter)
                bnd13_std = np.std(analogWireContact1msAfter)


                if (isNaN(cal1)):
                        cal1 = 0
                if (isNaN(bnd11)):
                        bnd11 = 0
                if (isNaN(bnd12)):
                        bnd12 = 0
                if (isNaN(bnd13)):
                        bnd13 = 0
                if (isNaN(bnd14)):
                        bnd14 = 0
                if (isNaN(bnd15)):
                        bnd15 = 0
                # calculate the slope of the analog signal from 2 to 5ms
                # we need to calculate the analog value before 2nd event 1
                x3 = x[250 * 2:250*2 + 125 + 1]
                y3 = y[250 * 2:250*2 + 125 + 1]
                z3= np.polyfit(x, y, 1)         # generae coefficient for linear regression with order 1
                # print (z3[0])


                # write into file
                fo.write(str(k) + '  ' + str(int(cal0)) + '   ' + str(int(cal1)) + \
                                 '   ' + str(int(bnd11)) + '   ' + str(int(bnd12)) + \
                                 '   ' + str(int(bnd13)) + '   ' + str(int(bnd14)) + '   ' + str(int(bnd15)) + \
                                 '   ' + str(int(nsol1)) + '   ' + str(int(nsol2)) + '   ' + str(int(bnd11 - cal1)) + \
                                 '   ' + str(int(bnd11 - bnd14)) + '   ' + str(int(bnd14 - nsol2)) + \
                                 '   ' + str(abs(int(minv))) + \
                                 '   ' + str(int(bnd11_std)) + '   ' + str(int(bnd14_std)) + \
                                 '   ' + str(int(8 + step_start[0]/250)) + '   ' + str(float(step_duration)) + \
                                 '   ' + str(float(int(z3[0]*100)/100.0)) + '\n')
                # fo.write(str(k) + '  ' + str(int(cal0)) + '   ' + str(int(cal1)) + \
                                 # '   ' + str(int(bnd11)) + '   ' + str(int(bnd12)) + \
                                 # '   ' + str(int(bnd13)) + '   ' + str(int(bnd14)) + '   ' + str(int(bnd15)) + \
                                 # '   ' + str(int(nsol1)) + '   ' + str(int(nsol2)) + '   ' + str(int(minv)) + \
                                 # '   ' + str(int( bnd12 - bnd14)) +  '\n')

        fo.close()
        print("Done")


def save_pydata(allData, list_parm):
        start_pulse = list_parm[0]
        end_pulse = list_parm[1]
        matchFilterMid = int(list_parm[2])
        matchFilterHT = int(list_parm[3])

        t_indx = allData[0, :]  # 1st row
        analog = allData[1, :]
        wbms_et = allData[2, :]
        wbms_status = allData[3, :]
        event1_rt = allData[4, :]
        event1_dt = allData[5, :]
        event2_rt = allData[6, :]
        event2_dt = allData[7, :]

        nline = len(analog)
        t_indx = np.arange(0.0,4.0*nline,4.0)
        t_indx = t_indx/1000    #ms as unit


        i = int(start_pulse)
        j = int(end_pulse)
        indexOfWire = p3_fun.cw(wbms_et)  # % pulse could be bond high learn
        analog_mhf = p3_fun.matchFilter(analog, matchFilterMid, matchFilterHT)

        r1 = analog[indexOfWire[2 * (i - 1)]:indexOfWire[2 * (j - 1) + 1]]
        r2 = wbms_et[indexOfWire[2 * (i - 1)]:indexOfWire[2 * (j - 1) + 1]]
        r3 = wbms_status[indexOfWire[2 * (i - 1)]:indexOfWire[2 * (j - 1) + 1]]
        r4 = event1_rt[indexOfWire[2 * (i - 1)]:indexOfWire[2 * (j - 1) + 1]]
        r5 = event1_dt[indexOfWire[2 * (i - 1)]:indexOfWire[2 * (j - 1) + 1]]
        r6 = event2_rt[indexOfWire[2 * (i - 1)]:indexOfWire[2 * (j - 1) + 1]]
        r7 = event2_dt[indexOfWire[2 * (i - 1)]:indexOfWire[2 * (j - 1) + 1]]
        r8 = analog_mhf[indexOfWire[2 * (i - 1)]:indexOfWire[2 * (j - 1) + 1]]
        #to make sure first pulse start from low !!!
        r2[0] = 0
        #to make sure final pulse start end as  low !!!
        r2[-1] = 0

        nline = len(r1)
        t_indx = np.arange(0.0,4.0*nline,4.0)
        t_indx = t_indx/1000    #ms as unit

        allData = np.array([t_indx, r1, r2, r3, r4, r5, r6, r7,r8])
        fSave = asksaveasfilename(title="Hi slect a directory and file name for saveas ")  # opens the file selctor
        np.save(fSave, allData)


def load_pydata():
        fName = askopenfilename(title="Hi slect a numpy data file ")    #opens the file selctor
        print (fName)
        allData = np.load(fName) # loads your saved array into variable a.
        print ('load done')
        return allData


# https://stackoverflow.com/questions/24885092/finding-the-consecutive-zeros-in-a-numpy-array
# import numpy as np

def zero_runs(a):
        # Create an array that is 1 where a is 0, and pad each end with an extra 0.
        iszero = np.concatenate(([0], np.equal(a, 0).view(np.int8), [0]))
        absdiff = np.abs(np.diff(iszero))
        # Runs start and end where absdiff is 1.
        ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
        return ranges


def convert_one_zero(a, thr):
        b = np.copy(a)
        b[b < thr] = 0
        b[b != 0] = 1
        # to set at least one itme =0  make sure extreme case
        b[1] = 0
        return b


def find_index_longest_zero(a):
        b = np.diff(a)
        idx = b.argmax()
        step_idx = a[idx]
        # step_end = a[idx+1]

        return step_idx




def isNaN(num):
        return num != num

# For examp

# In [236]: a = [0, 1, 2, 3, 0, 0, 0, 0, 0, 0, 4, 5, 6, 0, 0, 0, 0, 9, 8, 7, 0, 10, 11]

# In [237]: runs = zero_runs(a)

# In [238]: runs
# Out[238]:
# array([[ 3,  9],
# [12, 16],
# [19, 20]])


# https://www.zhihu.com/question/52684594
# 举个简单的例子，要记住，python默认是按行取元素c = np.array([[1,2,3],[4,5,6]])
# 输出：[[1 2 3] [4 5 6]]我们看看不同的reshapeprint '改成2行3列:'
# print c.reshape(2,3)
# print '改成3行2列:'
# print c.reshape(3,2)
# print '我也不知道几行，反正是1列:'
# print c.reshape(-1,1)
# print '我也不知道几列，反正是1行：'
# print c.reshape(1,-1)
# print '不分行列，改成1串'
# print c.reshape(-1)
# 输出为：改成2行3列:[[1 2 3] [4 5 6]]
# 改成3行2列:[[1 2] [3 4] [5 6]]
# 我也不知道几行，反正是1列:[[1] [2] [3] [4] [5] [6]]
# 我也不知道几列，反正是1行：[[1 2 3 4 5 6]]
# 不分行列，改成1串[1 2 3 4 5 6]
