#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import QTimer,QDateTime, QFile, QTextStream, Qt
from PyQt5.QtGui import QFont

import sys
import json
import random
import argparse
import datetime
import os
import time
import colorsys
import traceback
import threading
from math import sin, cos, sqrt, atan2, radians


from pathlib import Path
import XPlaneUdp


#LISTEN_PORT = 49006
SEND_PORT = 49000
XPLANE_IP = "192.168.0.130"


# Egna  funktioner
current_milli_time = lambda: int(round(time.time() * 1000))


parser = argparse.ArgumentParser()

parser.add_argument("--ip", help="Ip address of X-plane")
args = parser.parse_args()

if args.ip:
    XPLANE_IP = args.ip
print ("Connecting to ", XPLANE_IP)

def signal_handler(sig, frame):
        print("You pressed Ctrl+C!")
        running = False
        sys.exit(0)
        os._exit(0)

def updateSlider(self, lamp, dataref, type=1):
    value = self.xp.getDataref(dataref,10)
    
    if (type == 1):
        value = value*100 + 100
    if (type == 2):
        value = value*100
    #print("udpate slider", value)
    lamp.setValue(int(value))

def updateText(self, lamp, dataref):
    value = self.xp.getDataref(dataref,1)
    lamp.setText(str(int(value))+"%")

def updateLamp(self, lamp, dataref, color):
    font = QFont("Sans")
    font.setPointSize(12)
    lamp.setFont(font)
    if (self.xp.getDataref(dataref,10) >0):
        lamp.setStyleSheet("background-color: "+color)
    else:
        lamp.setStyleSheet("background-color: #AAAAAA")
    
def connectButton(self, button, dataref):
    font = button.font()
    font.setPointSize(12)
    button.setFont(font)
    button.pressed.connect(lambda: self.buttonPressed(dataref))
    button.released.connect(lambda: self.buttonReleased(dataref))
    
def connectButtonCommand(self, button, dataref):
    font = button.font()
    font.setPointSize(12)
    button.setFont(font)
    button.pressed.connect(lambda: self.buttonPressedCommand(dataref))
    
    
def connectOnButton(self, button, dataref):
    font = button.font()
    font.setPointSize(12)
    button.setFont(font)
    button.pressed.connect(lambda: self.buttonPressed(dataref))
def connectOffButton(self, button, dataref):
    font = button.font()
    font.setPointSize(12)
    button.setFont(font)
    button.pressed.connect(lambda: self.buttonReleased(dataref))

def connectValueButton(self, button, dataref, value):
    button.pressed.connect(lambda: self.buttonPressedValue(dataref, value))


def getDistanceGPS(lat1,lon1, lat2, lon2):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    #print("Result:", distance)
    return distance
def get_dist(banan):
    return banan.get("distance")
    
class ColorButton():
    def __init__(self, parent, button, dataref, color, type, lampDR=""):
        font = button.font()
        font.setPointSize(12)
        button.setFont(font)
        self.parent = parent
        self.button = button
        self.dataref = dataref
        self.color = color
        self.type = type
        if (lampDR==""):
            self.lampdataref = self.dataref
        else:
            self.lampdataref = lampDR
        
        if (type == 0):
            button.pressed.connect(self.onClickedToggle)
        if (type == 1):
            button.pressed.connect(self.buttonPressed)
            button.released.connect(self.buttonReleased)
        
    def onClickedToggle(self):
        prevvalue = self.parent.xp.getDataref(self.dataref, 1)
        if (prevvalue == 1):
            self.parent.xp.sendDataref(self.dataref, 0)
        else:
            self.parent.xp.sendDataref(self.dataref, 1)
            
    def buttonPressed(self):
        print("buttonPressed2:", self.dataref)
        self.parent.xp.sendDataref(self.dataref, 1)
        
    def buttonReleased(self):
        print("buttonReleased2:", self.dataref)
        self.parent.xp.sendDataref(self.dataref, 0)  
        
    def updateColor(self):
        if (self.parent.xp.getDataref(self.lampdataref,2) >0):
            self.button.setStyleSheet("background-color: "+self.color)
        else:
            self.button.setStyleSheet("background-color: #bbbbbb")
        

class RunGUI(QMainWindow):
    def __init__(self,):
        super(RunGUI,self).__init__()

        
        self.buttonList = []
        self.xp = XPlaneUdp.XPlaneUdp(XPLANE_IP,SEND_PORT)
        self.xp.getDataref("sim/flightmodel/position/indicated_airspeed",1)
        
        self.lat = self.xp.getDataref("sim/flightmodel/position/latitude",1)
        self.lon = self.xp.getDataref("sim/flightmodel/position/longitude",1)
        
        self.readApt()
        
        self.initUI()
        
    def initUI(self):
        #self.root = Tk() # for 2d drawing
        
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.ui = uic.loadUi(os.path.join(current_dir, "../ui/main.ui"), self)
        print(self.ui)
        #self.setGeometry(200, 200, 300, 300)
        #self.resize(640, 480)
        self.setWindowTitle("Viggen Instruktörssystem")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        connectButton(self, self.ui.button_start,"JAS/io/frontpanel/di/start")
        connectButton(self, self.ui.button_master,"JAS/io/frontpanel/di/master")
        
        connectButton(self, self.ui.button_systest,"JAS/io/vu22/di/syst")
        connectButton(self, self.ui.button_lamptest,"JAS/io/vu22/di/lampprov")
        #connectButton(self, self.ui.mot_fack,"JAS/system/mot/fack")
        #connectButton(self, self.ui.mot_rems,"JAS/system/mot/rems")
        
        
        connectValueButton(self, self.ui.luft_in,"sim/cockpit2/controls/speedbrake_ratio", 0)
        connectValueButton(self, self.ui.luft_ut,"sim/cockpit2/controls/speedbrake_ratio", 1)
        
        # connectButtonCommand(self, self.ui.button_reload_acf,"sim/operation/reload_aircraft_no_art")
        
        #self.buttonList.append( ColorButton(self,self.ui.buttonlamp_antikoll, "sim/cockpit/electrical/nav_lights_on", "yellow", 0) )
        
        self.buttonList.append( ColorButton(self,self.ui.button_afk, "JAS/io/frontpanel/di/afk", "orange", 1, lampDR="JAS/io/frontpanel/lo/afk") )
        self.buttonList.append( ColorButton(self,self.ui.button_hojd, "JAS/io/frontpanel/di/hojd", "orange", 1, lampDR="JAS/io/frontpanel/lo/hojd") )
        self.buttonList.append( ColorButton(self,self.ui.button_att, "JAS/io/frontpanel/di/att", "orange", 1, lampDR="JAS/io/frontpanel/lo/att") )
        self.buttonList.append( ColorButton(self,self.ui.button_spak, "JAS/io/frontpanel/di/spak", "orange", 1, lampDR="JAS/io/frontpanel/lo/spak") )
        self.buttonList.append( ColorButton(self,self.ui.button_a15, "JAS/io/aj37/di/a15", "orange", 1, lampDR="JAS/io/aj37/lo/a15") )
        
        
        #self.buttonList.append( ColorButton(self,self.ui.dap_button_pluv, "JAS/system/dap/lamp/pluv", "green", 0) )

        self.ui.button_tanka.clicked.connect(self.buttonTankaFull)
        self.ui.button_tanka_50.clicked.connect(self.buttonTanka50)
        
        self.ui.auto_afk_text.valueChanged.connect(self.autoAFK)
        self.ui.auto_hojd_text.valueChanged.connect(self.autoHOJD)

        self.ui.land_set_all.clicked.connect(self.Land_set_all)
        
        self.ui.button_land_update.clicked.connect(self.updateAirportBox)

        self.ui.comboBox_airports.currentTextChanged.connect(self.airportBoxOnChange)

        #Snabbval
        ## ESKN
        self.ui.snabb_eskn_1.clicked.connect(self.ESKN1)
        self.ui.snabb_eskn_2.clicked.connect(self.ESKN2)
        self.ui.snabb_eskn_3.clicked.connect(self.ESKN3)
        self.ui.snabb_eskn_4.clicked.connect(self.ESKN4)



        connectValueButton(self, self.ui.land_hb,"JAS/ti/land/bibana", 0)
        connectValueButton(self, self.ui.land_bi,"JAS/ti/land/bibana", 1)
        connectValueButton(self, self.ui.land_rikt_n,"JAS/ti/land/rikt", 0)
        connectValueButton(self, self.ui.land_rikt_inv,"JAS/ti/land/rikt", 1)

        font = QFont("Sans")
        font.setPointSize(12)
        self.setFont(font)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.loop)
        self.timer.start(100)



    def updateGUI(self):
        for button in self.buttonList:
            button.updateColor()
        # if (self.xp.dataList["JAS/lamps/hojd"] >0):
        #     self.ui.lamps_hojd.setStyleSheet("background-color: orange")
        # else:
        #     self.ui.lamps_hojd.setStyleSheet("background-color: white")
        
        updateLamp(self, self.ui.lamps_master1, "JAS/io/frontpanel/lo/master1", "red")
        updateLamp(self, self.ui.lamps_master2, "JAS/io/frontpanel/lo/master2", "red")
        
        
        updateLamp(self, self.ui.lamps_hojdvarn, "JAS/io/frontpanel/lo/hojdvarn", "red")
        
        updateLamp(self, self.ui.lamps_airbrake, "JAS/io/frontpanel/lo/airbrake", "lightgreen")
        
        
        updateLamp(self, self.ui.lamps_park, "sim/cockpit2/controls/parking_brake_ratio", "red")
        updateLamp(self, self.ui.lamps_gears, "sim/cockpit/switches/gear_handle_status", "lightgreen")
        
        
        updateText(self, self.ui.text_fuel, "JAS/fuel/pct")
        updateSlider(self, self.ui.slider_roll, "sim/joystick/yoke_roll_ratio", type=2)
        updateSlider(self, self.ui.slider_rudder, "sim/joystick/yoke_heading_ratio", type=2)
        updateSlider(self, self.ui.slider_pitch, "sim/joystick/yoke_pitch_ratio", type=2)
        updateSlider(self, self.ui.slider_throttle, "sim/cockpit2/engine/actuators/throttle_ratio_all", type=2)
        # 
        #self.ui.auto_afk_text.setValue(self.xp.getDataref("JAS/autopilot/afk",1))
        
        # VAT tablån
        # updateLamp(self, self.ui.vat_lamp_normsty, "JAS/io/vat/lo/normsty", "orange")


        
    def buttonPressedValue(self, dataref, value):
        print("buttonPressed:", dataref)
        self.xp.sendDataref(dataref, value)
                             
    def buttonPressedCommand(self, dataref):
        print("buttonPressedCommand:", dataref)
        self.xp.sendCommand(dataref)
                    
    def buttonPressed(self, dataref):
        print("buttonPressed:", dataref)
        self.xp.sendDataref(dataref, 1)
        
    def buttonReleased(self, dataref):
        print("buttonReleased:", dataref)
        self.xp.sendDataref(dataref, 0)   
             
    def buttonTankaFull(self):
        self.xp.sendDataref("sim/flightmodel/weight/m_fuel1", 2200)
    def buttonTanka50(self):
        self.xp.sendDataref("sim/flightmodel/weight/m_fuel1", 1100)
        
    def autoAFK(self):
        newvalue = float(self.ui.auto_afk_text.value()) / 1.85200
        self.xp.sendDataref("JAS/autopilot/afk", newvalue)
        
    def autoHOJD(self):
        newvalue = float(self.ui.auto_hojd_text.value()) / 0.3048
        self.xp.sendDataref("JAS/autopilot/alt", newvalue)


    def airportBoxOnChange(self):
        print("chagne box", self.ui.comboBox_airports.currentText())
        self.ui.comboBox_airports.setCurrentText(self.ui.comboBox_airports.currentText().upper())

        for apt in self.airportList:
            if (self.ui.comboBox_airports.currentText() == apt["id"] ):
                self.xp.sendDataref("JAS/ti/land/index", apt["index"])
                print("found airport", apt["id"], apt["index"])

    def updateAirportBox(self):

        self.lat = self.xp.getDataref("sim/flightmodel/position/latitude",1)

        self.lon = self.xp.getDataref("sim/flightmodel/position/longitude",1)
        print("updateAirportBox", self.lat, self.lon)
        if (self.lat < 0.1 and self.lat > -0.1):
            print("ingen egen plats", self.lat, self.lon)
            # return
        if (self.lon < 0.1 and self.lon > -0.1):
            print("ingen egen plats", self.lat, self.lon)
            # return
        self.airportListClose = []
        for apt in self.airportList:
            apt["distance"] = getDistanceGPS(self.lat,self.lon, apt["lat"], apt["lon"])
            self.airportListClose.append(apt)

        self.airportListClose.sort(key=get_dist)
        print("nÃ¤rmaste ", self.airportListClose[0])
        self.namelist = []
        for apt in self.airportListClose:
            banan = str(apt["id"])
            self.namelist.append(banan)
        self.ui.comboBox_airports.clear()
        self.ui.comboBox_airports.addItems(self.namelist)

    def readApt(self):

        self.airportList = []
        with open("../apt.csv", "r") as apt_file:
            data = apt_file.read().split("\n")
            print("Airports found: ",len(data))
            apt_file.close()
            i = 0
            for d in data:
                apt = {}
                col = d.split(";")
                if (len(col)>3):
                    apt["id"] = col[0]
                    apt["alt"] = float(col[1])
                    apt["lat"] = float(col[2])
                    apt["lon"] = float(col[3])
                    apt["index"] = i
                    i = i +1
                    self.airportList.append(apt)
        self.airportDict = {}
        for apt in self.airportList:
            self.airportDict[apt["id"]] = {}
            self.airportDict[apt["id"]]["id"] = apt["id"]
            self.airportDict[apt["id"]]["alt"] = apt["alt"]
            self.airportDict[apt["id"]]["lat"] = apt["lat"]
            self.airportDict[apt["id"]]["lon"] = apt["lon"]
            self.airportDict[apt["id"]]["index"] = apt["index"]
            

    def Land_set_all(self):
        self.xp.sendDataref("JAS/ti/menu/menu", 3)

        return
    def ESKN1(self):
        self.xp.sendDataref("JAS/ti/land/index", self.airportDict["ESKN"]["index"])
        self.xp.sendDataref("JAS/ti/land/bana", 0)
        self.xp.sendDataref("JAS/ti/land/bibana", 0)
        self.xp.sendDataref("JAS/ti/land/rikt", 1)
        return
    def ESKN2(self):
        self.xp.sendDataref("JAS/ti/land/index", self.airportDict["ESKN"]["index"])
        self.xp.sendDataref("JAS/ti/land/bana", 0)
        self.xp.sendDataref("JAS/ti/land/bibana", 0)
        self.xp.sendDataref("JAS/ti/land/rikt", 0)
        return
    def ESKN3(self):
        self.xp.sendDataref("JAS/ti/land/index", self.airportDict["ESKN"]["index"])
        self.xp.sendDataref("JAS/ti/land/bana", 1)
        self.xp.sendDataref("JAS/ti/land/bibana", 1)
        self.xp.sendDataref("JAS/ti/land/rikt", 1)
        return
    def ESKN4(self):
        self.xp.sendDataref("JAS/ti/land/index", self.airportDict["ESKN"]["index"])
        self.xp.sendDataref("JAS/ti/land/bana", 1)
        self.xp.sendDataref("JAS/ti/land/bibana", 1)
        self.xp.sendDataref("JAS/ti/land/rikt", 0)
        return

    def loop(self):
        self.xp.readData()
        self.updateGUI()
        
        #print(self.xp.dataList)
        self.timer.start(10)
        pass
        

if __name__ == "__main__":

    try:
        app = QApplication(sys.argv)
        win = RunGUI()
        win.show()
        sys.exit(app.exec_())
    except Exception as err:
        exception_type = type(err).__name__
        print(exception_type)
        print(traceback.format_exc())
        os._exit(1)
    print ("program end")
    os._exit(0)
