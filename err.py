#!/usr/bin/python
import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget, QToolBar
from PyQt5.QtCore import Qt
import pandas as pd
import numpy as np
import re
from datetime import datetime
import matplotlib
matplotlib.use('Qt5Agg')  # Switch to Qt5Agg for interactive plotting
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# Base class for error types
class ErrorType:
    def __init__(self, err_type):
        self.type = err_type
        self.kk = 0
        self.k = 0
        self.imped1 = 0
        self.imped2 = 0
        self.imped3 = 0
        self.imped4 = 0
        self.device = "NA"
        self.sample = "NA"
        self.device_num = "NA"
        self.wire_num = "NA"
        self.bond_num = "NA"
        self.time = None
        self.time2 = None
        self.date = None

    def parse_line(self, line):
        pass

    def reset_state(self):
        self.k = 0
        self.imped1 = 0
        self.imped2 = 0
        self.imped3 = 0
        self.imped4 = 0
        self.device = "NA"
        self.sample = "NA"
        self.device_num = "NA"
        self.wire_num = "NA"
        self.bond_num = "NA"
        self.time = None
        self.time2 = None
        self.date = None

    def get_row(self, kk):
        return {
            '#': self.device,
            'device_numer': self.device_num,
            'wire_number': self.wire_num,
            'bond_number': self.bond_num,
            'Type': self.type,
            '1st': self.imped1,
            '2nd': self.imped2,
            '3rd': self.imped3,
            '4th': self.imped4,
            'Samples': self.sample,
            'Time': self.time,
            'Time2': self.time2,
            'Date': self.date,
            'line': kk,
        }

# Derived classes for specific error types
class NSOP(ErrorType):
    def __init__(self):
        super().__init__("NSOP")

    def parse_line(self, line, i):
        if re.search(r"<142>", line):
            self.reset_state()
            self.kk = i + 1
            return True
        return False

class SHTL(ErrorType):
    def __init__(self):
        super().__init__("SHTL")

    def parse_line(self, line, i):
        if re.search(r"<144>", line):
            self.reset_state()
            self.kk = i + 1
            return True
        return False

class NSOL(ErrorType):
    def __init__(self):
        super().__init__("NSOL")

    def parse_line(self, line, i):
        if re.search(r"<143>", line):
            self.reset_state()
            self.kk = i + 1
            return True
        return False

class Ltail(ErrorType):
    def __init__(self):
        super().__init__("Ltail")

    def parse_line(self, line, i):
        if re.search(r"<154>", line):
            self.reset_state()
            self.kk = i + 1
            return True
        return False

class STITCH(ErrorType):
    def __init__(self):
        super().__init__("STITCH")

    def parse_line(self, line, i):
        if re.search(r"<175>", line):
            self.reset_state()
            self.kk = i + 1
            return True
        return False

class BondoffSHTL(ErrorType):
    def __init__(self):
        super().__init__("bondoff_SHTL")

    def parse_line(self, line, i):
        if re.search(r"<186>", line):
            self.reset_state()
            self.kk = i + 1
            return True
        return False

class EHSERDES(ErrorType):
    def __init__(self):
        super().__init__("EH_SERDES_BUS_ERROR")

    def parse_line(self, line, i):
        if re.search(r"<1563>\s+EH_SERDES_BUS_ERROR", line):
            self.reset_state()
            self.kk = i + 1
            return True
        return False

class BonderRebooted(ErrorType):
    def __init__(self):
        super().__init__("BONDER REBOOTED")

    def parse_line(self, line, i):
        if re.search(r"BONDER REBOOTED", line):
            self.reset_state()
            self.kk = i + 1
            return True
        return False

class PlotWindow(QMainWindow):
    def __init__(self, fig, date):
        super().__init__()
        self.setWindowTitle(f"NSOP Occurrences - {date}")
        self.setGeometry(100, 100, 800, 600)

        # Create canvas and toolbar
        self.canvas = FigureCanvas(fig)
        self.toolbar = NavigationToolbar(self.canvas, self)  # Add navigation toolbar for zoom/pan
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Connect close event to save
        self.canvas.mpl_connect('close_event', lambda event: self.save_plot(date))

    def save_plot(self, date):
        self.canvas.figure.savefig(f'nsop_occurrences_{date}.png', bbox_inches='tight')
        print(f"Saved plot as nsop_occurrences_{date}.png")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Error Analysis Tool")
        self.setGeometry(100, 100, 400, 200)

        # Create central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Add buttons
        self.load_button = QPushButton("Load File and Analyze", self)
        self.load_button.clicked.connect(self.load_and_analyze)
        layout.addWidget(self.load_button)

        self.quit_button = QPushButton("Quit", self)
        self.quit_button.clicked.connect(self.close)
        layout.addWidget(self.quit_button)

    def load_and_analyze(self):
        fName, _ = QFileDialog.getOpenFileName(self, "Select File", "", "Text Files (*.txt);;All Files (*)")
        if fName:
            self.parse_and_plot(fName)

    def parse_and_plot(self, fName):
        with open(fName, 'r', encoding="utf8") as f:
            lines = f.readlines()
        nline = len(lines)
        ls = []
        error_types = [NSOP(), SHTL(), NSOL(), Ltail(), STITCH(), BondoffSHTL(), EHSERDES(), BonderRebooted()]
        current_error = None

        for i in range(1, nline):
            if not current_error:
                for error in error_types:
                    if error.parse_line(lines[i], i):
                        current_error = error
                        break
            else:
                current_error.k += 1
                if re.search(r"\#{2}", lines[i]) or (i == nline - 1):
                    ls.append(current_error.get_row(current_error.kk))
                    current_error = None
                elif re.search(r"\b\d{2}:\d{2}:\d{2}", lines[i]):
                    mt = re.search(r"\b\d{2}:\d{2}:\d{2}", lines[i]).group(0)
                    nl = lines[i].split()
                    mt_idx = nl.index(mt)
                    if current_error:
                        current_error.time = nl[mt_idx]
                        current_error.time2 = current_error.time[:-3]
                        dat = nl[mt_idx - 2] + ' ' + nl[mt_idx - 1] + ' ' + nl[mt_idx + 1]
                        current_error.date = datetime.strptime(dat, '%b %d %Y').date()
                elif re.search(r"\[ON\s?samples:", lines[i]):
                    match = re.search(r"\[ON\s?samples:\s*(.*)", lines[i])
                    if match and current_error:
                        current_error.sample = match.group(1).strip().rstrip(']')
                elif re.search(r"BITS\s?measurement:", lines[i]):
                    imped = lines[i].strip('BITS measurement:[ ')
                    imped = imped.strip('\n')
                    imped = imped.strip('[')
                    imped = imped.strip(']')
                    imped = imped.split(',')
                    if current_error:
                        if len(imped) == 2:
                            current_error.imped1 = imped[0]
                            current_error.imped2 = imped[1]
                            current_error.imped3 = 0
                            current_error.imped4 = 0
                        elif len(imped) == 4:
                            current_error.imped1 = imped[0]
                            current_error.imped2 = imped[1]
                            current_error.imped3 = imped[2]
                            current_error.imped4 = imped[3]
                elif re.search(r"\[device:", lines[i]):
                    dev = lines[i].strip('[device:')
                    dev = dev.strip('\n')
                    dev = dev.strip(']')
                    dev = dev.split(',')
                    if current_error:
                        current_error.device_num = dev[0]
                        current_error.wire_num = dev[1].strip('wire: ')
                        current_error.bond_num = dev[2].strip('bond: ')
                elif re.search(r"Filter:", lines[i]):
                    if current_error:
                        current_error.device = lines[i].strip('Filter:')
                        current_error.device = current_error.device.strip('\n')

        df1 = pd.DataFrame(ls, columns=["#", "device_numer", "wire_number", "bond_number", "Type", "1st", "2nd", "3rd", "4th", "Samples", "Time", "Time2", "Date", "line"])
        df1.to_excel(fName + 'SJ' + '.xlsx', index=False)

        # Plot NSOP occurrences
        df_nsop = df1[df1['Type'] == 'NSOP'].copy()
        df_nsop.loc[:, 'Datetime'] = pd.to_datetime(df_nsop['Date'].astype(str) + ' ' + df_nsop['Time'], format='%Y-%m-%d %H:%M:%S')
        df_nsop.loc[:, 'Minute_of_day'] = df_nsop['Datetime'].dt.hour * 60 + df_nsop['Datetime'].dt.minute

        unique_dates = df_nsop['Date'].unique()
        plot_windows = []  # Store plot windows to keep them alive
        for date in unique_dates:
            df_day = df_nsop[df_nsop['Date'] == date]
            minute_counts = {minute: 0 for minute in range(1440)}
            total_nsop = 0
            for minute in df_day['Minute_of_day']:
                if 0 <= minute < 1440:
                    minute_counts[minute] += 1
                    total_nsop += 1

            minutes = [min for min, count in minute_counts.items() if count > 0]
            counts = [count for min, count in minute_counts.items() if count > 0]
            fig = Figure(figsize=(12, 6))
            ax = fig.add_subplot(111)
            ax.scatter(minutes, counts, marker='^', s=50, label=f'NSOP Occurrences - {date} (Total: {total_nsop})', color='blue')
            ax.set_xlabel('1440 minutes of Day (00:00 to 23:59)')
            ax.set_ylabel('Number of NSOP Occurrences')
            ax.set_title(f'NSOP Occurrences on {date}')
            ax.grid(True)
            ax.legend()
            ax.set_ylim(0, max(counts) + 1 if counts else 1)

            # Open a new plot window
            plot_window = PlotWindow(fig, date)
            plot_window.show()
            plot_windows.append(plot_window)  # Keep reference to prevent garbage collection
            QApplication.processEvents()  # Process events to ensure the window is displayed

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())