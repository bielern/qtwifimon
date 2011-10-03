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
import shutil   # For copy()
import argparse # for parsing the arguments
import logging  # For the debug messages
#logging.basicConfig(level=logging.DEBUG)  # and turn them off

from PyQt4 import QtGui, QtCore


# print verbose
#def v_print(message):
#    if conf.verbose == True:
#        print(message)


class Conf:
    """All the configurations"""
    #def __init__(self):
    # We have to initialize after having parsed the arguments
    def init(self):
        #self.debug = False
        self.verbose = False
        self.interface = "no interface assigned!"
        self.percentage = -1
        self.interval = 1
        self.statfile = "/proc/net/wireless"
        #self.statfile = "test_wlan"
        #self.statfile = "test_nowlan"
        self.iconPath = "./img/"
        #self.iconPath = "img/"
        #self.devfile = "/proc/net/dev"
        #self.interfaces = []
        #self.monitor_wired = False
        self.parse_conf_file()

    #def get_interfaces(self):
    #    with open(self.devfile) as f:
    #        f.readline()
    #        f.readline()

    #        while line = f.readline:
    #            match = re.match("(\S+):", line)
    #            if match.group(1) != "lo":
    #                self.interfaces.append(match.group(1))

    #    f.close()

    def print_parser_err(self, option, value):
        print("Unknown value %s for option %s" % (value, option))

    def parse_conf_file(self):
        logging.debug("Parse configuration file")
        xdg_home = os.getenv("XDG_CONFIG_HOME")
        if not xdg_home:
            home =  os.getenv("HOME")
            xdg_home = os.path.join(home, ".config")
        conf_dir = os.path.join(xdg_home, "wifimon")
        if not os.path.isdir(conf_dir):
            os.mkdir(conf_dir, 0o755)
        self.conf_file = os.path.join(conf_dir, "wifimon.rc")

        if not os.path.isfile(self.conf_file):
            logging.debug("Will copy default configuration file")
            shutil.copy("./default_config", self.conf_file)

        with open(self.conf_file) as f:
            raw_line = f.readline()
            logging.debug("Raw line: %s" % raw_line)
            while raw_line:
                line = re.sub("[ ]*#[ \S]*", "", raw_line)
                line = line.strip()
                logging.debug("line without comments: <%s>" % line)
                if line:
                    fields = line.split("=")
                    if len(fields) != 2:
                        print("Error in parsing the configuration file!")
                    else:
                        raw_option = fields[0].lower()
                        raw_value = fields[1].lower()
                        option = raw_option.strip()
                        value = raw_value.strip()
                        logging.debug("Option: %s; Value: %s" % (option, value))
                        #if option == "debug":
                        #    if value == "true" or value == "1":
                        #        self.debug = True
                        #        #logging.basicConfig(level=logging.DEBUG)
                        #    elif value == "false" or value == "0":
                        #        self.debug = False
                        #        #logging.basicConfig(level=logging.WARNING)
                        #    else:
                        #        self.print_parser_err(option, value)
                        #elif option == "verbose":
                        #    if value == "true" or value == "1":
                        #        self.verbose = True
                        #    elif value == "false" or value == "0":
                        #        self.verbose = False
                        #    else:
                        #        self.print_parser_err(option, value)
                        if option == "interval":
                            number = re.sub("[^0-9]*", "", value)
                            logging.debug("Number: %s" % number)
                            if number:
                                self.interval = int(number)
                            else:
                                self.print_parser_err(option, value)
                        elif option == "icons":
                            if os.path.isdir(value):
                                self.iconPath = value
                            else:
                                print("Path %s does not exist!" % value)
                                #exit(1)
                        else:
                            print("Unkown option %s" % option)
                            
                raw_line = f.readline()

        f.close()
        #if self.debug:
        #    logging.basicConfig(level=logging.DEBUG)
        #else:
        #    logging.basicConfig()


class WifiMonitor(QtCore.QObject):
    """Monitors the state of the wireless interface"""
    signal_display_status = QtCore.pyqtSignal(int, str, str)
    def __init__(self, parent = None):
        QtCore.QObject.__init__(self, parent)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(conf.interval * 1000)
        self.timer.timeout.connect(self.update_status)
        self.start()
        logging.debug("Constructed WifiMonitor")

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()

    # Read in the satus of the connection
    def update_status(self):
        logging.debug("I will update the status")
        percentage = -1
        interface = ""
        # open status file and discard first two lines
        with open(conf.statfile) as f:
            f.readline()
            f.readline()
            line = f.readline()

        if line:
            logging.debug(line)
            m = re.search("(\S+\d):[ ]+(\d+)[ ]+(\d+)\.", line)
            interface = m.group(1)
            percentage = int(m.group(3))
    
        f.close()

        command = "iwlist " + interface
        command = command + " scanning | grep ESSID | cut -d'\"' -f2"
        stdout_handle = os.popen(command)
        essid = stdout_handle.read().strip()
        self.signal_display_status.emit(percentage, interface, essid)
        

class WifiStatusIcon(QtGui.QSystemTrayIcon):
    """The sys tray icon displaying the connection strength"""
    def __init__(self, parent = None):
        QtGui.QSystemTrayIcon.__init__(self, parent)
        self.createActions()
        self.createTrayIcon()
        logging.debug("Created Status Icon")

    def createActions(self):
        self.quitAction = QtGui.QAction(self.tr("&Quit"), self)
        self.quitAction.triggered.connect(QtGui.qApp.quit)

    def createTrayIcon(self):
        self.trayIconMenu = QtGui.QMenu()
        self.trayIconMenu.addAction(self.quitAction)
        self.setContextMenu(self.trayIconMenu)
        pathToIcon = conf.iconPath + "wifi_none.svg"
        print("will set icon")
        try:
            self.setIcon(QtGui.QIcon(pathToIcon))
        except:
            print("Icon not found")
            #exit(1)
            self.instance().quit()
        print("icon set")

    def show_wifi_status(self, percentage, interface, essid):
        if percentage >= 0:
            logging.info("%s: %s @ %d" % (interface, essid, percentage))
            if percentage:
                filePercentage = (int((percentage - 1) / 25) + 1) * 25
            else:
                filePercentage = 0
            pathToIcon = os.path.join(conf.iconPath, 
                                      "wifi_{0}.svg".format(filePercentage))
            self.message = interface + ": " + essid + " @ "
            self.message = self.message + str(percentage) + "%"
        else:
            logging.info("No wifi connection detected!")
            pathToIcon = os.path.join(conf.iconPath, "wifi_none.svg")
            self.message = "Not connected to any wifi"
    
        self.setIcon(QtGui.QIcon(pathToIcon))
        self.setToolTip(self.message)
        logging.debug("Will display icon: " + pathToIcon)


# Displays the state of the wireless connection
class WifiStatusWidget(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        logging.debug("Constructed WifiStatusWidget")

    # Display the status
    def show_wifi_status(self, percentage, interface, essid):
        if percentage >= 0:
            logging.info("widget: %s: %s @ %d" % (interface, essid, percentage))
        else:
            logging.info("No wifi connection detected!")


class WifiMonitorApplication(QtGui.QApplication):
    """The app containing all widgets and the monitoring instance"""
    def __init__(self, args):
        QtGui.QApplication.__init__(self, args)
        self.parse()
        conf.init()
        self.wifi_monitor = WifiMonitor()
        self.status_icon = WifiStatusIcon()
        self.wifi_monitor.signal_display_status.connect(self.status_icon.
                                                        show_wifi_status)
        self.status_icon.show()
        
        #self.status_widget = WifiStatusWidget()
        #for widget in (self.status_widget, self.status_icon):
        #    self.wifi_monitor.signal_display_status.connect(widget.show_wifi_status)
        #    widget.show()

    def parse(self):
        parser = argparse.ArgumentParser(
                            description = "Monitors your wifi.",
                            epilog = """The configurations file can usually be 
                                     found in ~/.config/wifimon/wifimon.rc""")
        parser.add_argument("-v", "--verbose", 
                            help="set the level of verbosity (default: error)",
                            default="error",
                            choices=["error", "info", "debug"])
        parser.add_argument("-i", "--interval",
                            help="intervall to update the icon in seconds",
                            type=int,
                            default=1,
                            nargs=1)
        args = parser.parse_args()
        if args.interval:
            conf.interval = int(args.interval)
        if args.verbose:
            if args.verbose == "error":
                logging.basicConfig(level=logging.ERROR)
            elif args.verbose == "info":
                logging.basicConfig(level=logging.INFO)
            elif args.verbose == "debug":
                print("debug")
                logging.basicConfig(level=logging.DEBUG)

        print(args)


def signal_int_handler(signal, frame):
    app.instance().quit()

if (__name__ == "__main__"):
    conf = Conf()
    app = WifiMonitorApplication(sys.argv)
    signal.signal(signal.SIGINT, signal_int_handler)
    logging.debug("Start GUI")
    app.exec_()
