#! /usr/bin/python
# 
# wifimon 
# Copyright by Noah Bieler
#
"""wifimon

wifimon monitors your wifi connection and sits in your systray
"""

# Imports
#import os, sys
import re       # regular expression
import time     # for sleep()
import signal   # To catch sig int (ctrl-c)
import sys      # To catch sig int (ctrl-c)

from PyQt4 import QtGui, QtCore

# All the configurations
class Conf:
    def __init__(self):
        self.interface = "no interface assigned!"
        self.percentage = -1
        self.intervall = 10
        #self.statfile = "/proc/net/wireless"
        self.statfile = "test_wlan"
        #self.statfile = "test_nowlan"
        self.iconPath = "./img/"

# Read in the configuration file
def read_conf():
    return 0
    
# The icon in the systray
class WifiIcon(QtGui.QWidget):
    start = QtCore.pyqtSignal()
    show_tray = QtCore.pyqtSignal()
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.createActions()
        self.createTrayIcon()
        self.trayIcon.show()

    def createActions(self):

        self.quitAction = QtGui.QAction(self.tr("&Quit"), self)
        QtCore.QObject.connect(self.quitAction, QtCore.SIGNAL("triggered()"),
                    QtGui.qApp, QtCore.SLOT("quit()"))
        self.start.connect(self.run)

    def createTrayIcon(self):
        self.trayIconMenu = QtGui.QMenu(self)
        self.trayIconMenu.addAction(self.quitAction)

        self.trayIcon = QtGui.QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)
        #pathToIcon = "/usr/share/icons/default.kde4/22x22/devices/network-wireless-connected-100.png"
        pathToIcon = conf.iconPath + "wifi_50.svg"
        self.trayIcon.setIcon(QtGui.QIcon(pathToIcon))
        self.show_tray.connect(self.trayIcon.show)

    # Read in the satus of the connection
    def get_status(self):
    
        # open status file and discard first two lines
        f = open(conf.statfile)
        f.readline()
        f.readline()
    
        l = f.readline()
        if (len(l) != 0):
            print(l)
            m = re.search("(\S+\d):[ ]+(\d+)[ ]+(\d+)\.", l)
            conf.interface = m.group(1)
            #status = m.group(2)
            conf.percentage = int(m.group(3))
    
        return 0
    
    # Display the status
    def display_status(self):
    
        if (conf.percentage >= 0):
            print("%s @ %d" % (conf.interface, conf.percentage))
            filePercentage = (int(conf.percentage / 25) + 1) * 25
            pathToIcon = conf.iconPath + "wifi_" + str(filePercentage) + ".svg"
            self.trayIcon.setIcon(QtGui.QIcon(pathToIcon))
        else:
            print("No wifi connection detected!")
            pathToIcon = conf.iconPath + "wifi_none.svg"
            self.trayIcon.setIcon(QtGui.QIcon(pathToIcon))
    
        print(pathToIcon)
        return 0

    # main loop
    def run(self):
        while True:
            self.get_status()
            self.display_status()
            time.sleep(conf.intervall)

# What to do, in the case of interruption
def signal_handler(signal, frame):
    print("\nProgram was interrupted!")
    sys.exit(0)


if (__name__ == "__main__"):
    signal.signal(signal.SIGINT, signal_handler)
    conf = Conf()
    read_conf()
    
    app = QtGui.QApplication(sys.argv)
    icon = WifiIcon()
    icon.start.emit()
    icon.show_tray.emit()
    app.exec_()
    sys.exit()

