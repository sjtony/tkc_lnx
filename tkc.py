
import numpy as np
import matplotlib.pyplot as plt


# Simple enough, just import everything from tkinter.
from tkinter import *

from tkinter import messagebox
from tkinter import simpledialog
# from guppy import hpy

import p3_fun
import p4_fun


# Here, we are creating our class, Window, and inheriting from the Frame
# class. Frame is a class from the tkinter module. (see Lib/tkinter/__init__)
class Window(Frame):

        # Define settings upon initialization. Here you can specify
        # allData = 0
        # prtData = 0
        def __init__(self, master=None):

                # parameters that you want to send through the Frame class.
                Frame.__init__(self, master)

                #reference to the master widget, which is the tk window
                self.master = master

                #with that, we want to then run init_window, which doesn't yet exist
                self.init_window()

                #Creation of init_window
        def init_window(self):

                # changing the title of our master widget
                self.master.title("GUI")

                # allowing the widget to take the full space of the root window
                self.pack(fill=BOTH, expand=1)

                # creating a menu instance
                menu = Menu(self.master)
                self.master.config(menu=menu)

                # create the file object)
                file = Menu(menu)

                # adds a command to the menu option, calling it exit, and the
                # command it runs on event is client_exit
                file.add_command(label="Import", command=self.OpenFile)
                file.add_separator()
                file.add_command(label="Save_PyData", command=self.SavePyData)
                file.add_separator()
                file.add_command(label="Load_PyData", command=self.LoadPyData)
                file.add_separator()
                file.add_command(label="Exit", command=self.client_exit)

                #added "file" to our menu
                menu.add_cascade(label="File", menu=file)

                # create the file object)
                edit = Menu(menu)

                # adds a command to the menu option, calling it exit, and the
                # command it runs on event is client_exit
                edit.add_command(label="Undo")

                #added "file" to our menu
                menu.add_cascade(label="Edit", menu=edit)

                Label(self, text="totalPluseSN").grid(row=0)
                Label(self, text="pluseSN").grid(row=1)

                Label(self, text="start_pulse").grid(row=2)
                Label(self, text="end_pulse").grid(row=3)

                Label(self, text="matchF_mid").grid(row=4)
                Label(self, text="matchF_h&t").grid(row=5)

                Label(self, text="fitT1").grid(row=6)
                Label(self, text="fitT2").grid(row=7)
                Label(self, text="polyOrder").grid(row=8)
                Label(self, text="sgFilterWindow").grid(row=9)
                Label(self, text="sgFilterOrder").grid(row=10)

                self.totalPulseE0 = Entry(self)
                self.nPulseE1 = Entry(self)

                self.startPulseE2 = Entry(self)
                self.endPulseE3 = Entry(self)

                self.matchFilterMid = Entry(self)
                self.matchFilterHT = Entry(self)
                self.matchFilterMid.insert(END, '128')
                self.matchFilterHT.insert(END, '256')

                self.fitT1E4 = Entry(self)
                self.fitT2E5 = Entry(self)
                self.fitDeg = Entry(self)
                self.fitDeg.insert(END, '1')

                self.sgFilterWindow = Entry(self)
                self.sgFilterWindow.insert(END, '511')          # must be odd number

                self.sgFilterOrder = Entry(self)
                self.sgFilterOrder.insert(END, '3')

                self.totalPulseE0.grid(row=0, column=1)
                self.nPulseE1.grid(row=1, column=1)

                self.startPulseE2.grid(row=2, column=1, pady = 8)
                self.endPulseE3.grid(row=3, column=1)

                self.matchFilterMid.grid(row=4, column=1)
                self.matchFilterHT.grid(row=5, column=1)

                self.fitT1E4.grid(row=6, column=1, pady = 8)
                self.fitT2E5.grid(row=7, column=1)
                self.fitDeg.grid(row=8, column=1)

                self.sgFilterWindow.grid(row=9, column=1)
                self.sgFilterOrder.grid(row=10, column=1)


                Button(self, text='Default_sig', command=self.plotFig2).grid(row=5, column=4, sticky=W, padx=10)
                Button(self, text='Filter_comp', command=self.plotFig3).grid(row=5, column=5, sticky=W, padx=10)
                Button(self, text='MFilter', command=self.plotFig4).grid(row=5, column=6, sticky=W, padx=10)
                Button(self, text='FitP', command=self.fitPlot).grid(row=10, column=4, sticky=W, padx=10)
                Button(self, text='Compute', command=self.Compute).grid(row=12, column=0, sticky=W, padx=10, pady=40)
                Button(self, text='Exit', command=self.client_exit).grid(row=12, column=1, sticky=W, padx=10, pady=20)

        def client_exit(self):
                print ("Byby")
                exit()


        def OpenFile(self):
                # read data from the oldest first to the latest
                # all = [var for var in globals() if var[0] != "_"]
                # for var in all:
                        # del globals()[var]
                if 'plt' in globals():
                        plt.close ('all')
                if 'self.allData' in globals():
                        del self.allData[:]
                        del self.allData
                data = []
                # questionYes = True
                # questionYes = messagebox.askyesno('Message title','Do you know the file size')
                # if (questionYes):
                        # answerFS = None
                        # while (answerFS is None):
                                        # answerFS = simpledialog.askinteger("Input", "file size = ?",
                                                                         # parent=self.master,
                                                                         # minvalue=1, maxvalue=32)
                        # print("Your file size is ", answerFS)
                        # read_again = True
                        # while (read_again):
                                # dat = p3_fun.import_data(answerFS)
                                # data = data + dat
                                # read_again = messagebox.askyesno('Message title','Continue')
                # else:
                read_again = True
                while (read_again):
                        dat = p3_fun.import_dataU()
                        data = data + dat
                        read_again = messagebox.askyesno('Message title','Continue')

                print (len(data))
                self.allData = p3_fun.processData(data)
                del data[:]
                del data
                print (len(self.allData))
                # from guppy import hpy
                # h = hpy()
                p3_fun.plotAll(self.allData, self.totalPulseE0, self.nPulseE1)  #note here we pass entry to funcion, kind of clasee variable (pointer)
                # print (h.heap())

        def SavePyData(self):
                # to save the data for later on use
                print("please slect start and end pulse before doing saving data")
                start_pulse = self.startPulseE2.get()
                end_pulse = self.endPulseE3.get()
                #list_parm = [start_pulse, end_pulse]
                list_parm = [start_pulse, end_pulse, self.matchFilterMid.get(), self.matchFilterHT.get()]
                p4_fun.save_pydata(self.allData, list_parm)

        def LoadPyData(self):
                # to load  the data from previous saved file
                self.allData = p4_fun.load_pydata()
                p3_fun.plotAll(self.allData, self.totalPulseE0, self.nPulseE1)  #note here we pass entry to funcion, kind of clasee variable (pointer)


        def plotFig2(self):
                print("Start: %s\nLast: %s" % (self.startPulseE2.get(), self.endPulseE3.get()))
                start_pulse = self.startPulseE2.get()
                end_pulse = self.endPulseE3.get()
                list_parm = [start_pulse, end_pulse, self.matchFilterMid.get(), self.matchFilterHT.get()]
                p3_fun.plotPartial2(self.allData, list_parm)

        def plotFig3(self):
                print("Start: %s\nLast: %s" % (self.startPulseE2.get(), self.endPulseE3.get()))
                start_pulse = self.startPulseE2.get()
                end_pulse = self.endPulseE3.get()
                list_parm = [start_pulse, end_pulse, self.matchFilterMid.get(), self.matchFilterHT.get()]
                p3_fun.plotPartial3(self.allData, list_parm)

        def plotFig4(self):
                print("Start: %s\nLast: %s" % (self.startPulseE2.get(), self.endPulseE3.get()))
                start_pulse = self.startPulseE2.get()
                end_pulse = self.endPulseE3.get()
                list_parm = [start_pulse, end_pulse, self.matchFilterMid.get(), self.matchFilterHT.get()]
                p3_fun.plotPartial4(self.allData, list_parm)

        def Compute(self):
                print("please slect start and end pulse before doing computation")
                start_pulse = self.startPulseE2.get()
                end_pulse = self.endPulseE3.get()
                list_parm = [start_pulse, end_pulse, self.matchFilterMid.get(), self.matchFilterHT.get()]
                p4_fun.calDiff(self.allData, list_parm)

        def fitPlot(self):
                print("T1: %s\nT2: %s" % (self.fitT1E4.get(), self.fitT2E5.get()))
                start_pulse = self.startPulseE2.get()
                end_pulse = self.endPulseE3.get()
                T1 = self.fitT1E4.get()
                T2 = self.fitT2E5.get()
                deg = self.fitDeg.get()
                list_para2 = [start_pulse, end_pulse, T1, T2, deg, self.sgFilterWindow.get(), self.sgFilterOrder.get()]
                p3_fun.fitPlot(self.allData, list_para2)


# root window created. Here, that would be the only window, but
# you can later have windows within windows.
root = Tk()

# root.geometry("400x300")
root.geometry('%dx%d+%d+%d' % (600, 500, 0, 0))

#creation of an instance
app = Window(root)

#mainloop
root.mainloop()

