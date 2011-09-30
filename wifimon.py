#! /usr/bin/python
# 
# wifimon 
# Copyright by Noah Bieler
#
"""wifimon

wifimon monitors your wifi connection and sits in your systray
"""

# Imports
import re       # regular expression
import time     # for sleep()
import signal   # To catch sig int (ctrl-c)
import sys      # To catch sig int (ctrl-c)
import os       # For creating nice file paths

from PyQt4 import QtGui, QtCore

# All the configurations
class Conf:
    def __init__(self):
        self.interface = "no interface assigned!"
        self.percentage = -1
        self.interval = 1
        self.statfile = "/proc/net/wireless"
        #self.statfile = "test_wlan"
        #self.statfile = "test_nowlan"
        self.iconPath = "./img/"

# Monitors the state of the wireless interface
class WifiMonitor(QtCore.QObject):
    signal_display_status = QtCore.pyqtSignal(int, str)
    def __init__(self, parent = None):
        QtCore.QObject.__init__(self, parent)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(conf.interval * 1000)
        self.timer.timeout.connect(self.update_status)
        self.start()
        print("Constructed WifiMonitor")

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    # Read in the satus of the connection
    def update_status(self):
        print("I will update the status")
        # open status file and discard first two lines
        with open(conf.statfile) as f:
            f.readline()
            f.readline()
            line = f.readline()

        if line:
            print(line)
            m = re.search("(\S+\d):[ ]+(\d+)[ ]+(\d+)\.", line)
            interface = m.group(1)
            percentage = int(m.group(3))
    
        f.close()
        self.signal_display_status.emit(percentage, interface)
        
# The system tray icon
class WifiStatusIcon(QtGui.QSystemTrayIcon):
    def __init__(self, parent = None):
        QtGui.QSystemTrayIcon.__init__(self, parent)
        self.createActions()
        self.createTrayIcon()
        print("Created Status Icon")

    def createActions(self):
        self.quitAction = QtGui.QAction(self.tr("&Quit"), self)
        self.quitAction.triggered.connect(QtGui.qApp.quit)

    def createTrayIcon(self):
        self.trayIconMenu = QtGui.QMenu()
        self.trayIconMenu.addAction(self.quitAction)
        self.setContextMenu(self.trayIconMenu)
        pathToIcon = conf.iconPath + "wifi_none.svg"
        self.setIcon(QtGui.QIcon(pathToIcon))

    def show_wifi_status(self, percentage, interface):
        if percentage >= 0:
            print("%s @ %d" % (interface, percentage))
            if percentage:
                filePercentage = (int((percentage - 1) / 25) + 1) * 25
            else:
                filePercentage = 0
            pathToIcon = os.path.join(conf.iconPath, 
                                      "wifi_{0}.svg".format(filePercentage))
        else:
            print("No wifi connection detected!")
            pathToIcon = os.path.join(conf.iconPath, "wifi_none.svg")
    
        self.setIcon(QtGui.QIcon(pathToIcon))
        self.show()
        print(pathToIcon)


# Displays the state of the wireless connection
class WifiStatusWidget(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        print("Constructed WifiStatusWidget")

    # Display the status
    def show_wifi_status(self, percentage, interface):
        if percentage >= 0:
            print("widget: %s @ %d" % (interface, percentage))
        else:
            print("No wifi connection detected!")

class WifiMonitorApplication(QtGui.QApplication):
    def __init__(self, args):
        QtGui.QApplication.__init__(self, args)
        self.wifi_monitor = WifiMonitor()
        self.status_widget = WifiStatusWidget()
        self.status_icon = WifiStatusIcon()
        for widget in (self.status_widget, self.status_icon):
            self.wifi_monitor.signal_display_status.connect(widget.show_wifi_status)
            widget.show()

if (__name__ == "__main__"):
    conf = Conf()
    
    app = WifiMonitorApplication(sys.argv)
    print("Start GUI")
    app.exec_()
