#!/usr/bin/python3
# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtCore import QTimer,QDateTime, QFile, QTextStream, Qt
from PyQt5.QtGui import QFont, QPainter, QPen, QColor

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
XPLANE_IP = "192.168.0.37"
XPLANE_IP2 = "192.168.0.38"


# Egna  funktioner
current_milli_time = lambda: int(round(time.time() * 1000))


parser = argparse.ArgumentParser()

parser.add_argument("--ip", help="Ip address of X-plane")
parser.add_argument("--ip2", help="Ip address of X-plane")
args = parser.parse_args()

if args.ip:
    XPLANE_IP = args.ip
if args.ip2:
    XPLANE_IP2 = args.ip2
print ("Connecting to ", XPLANE_IP)
print ("Connecting to2 ", XPLANE_IP2)

def signal_handler(sig, frame):
        print("You pressed Ctrl+C!")
        running = False
        sys.exit(0)
        os._exit(0)

def updateSlider(self, lamp, dataref, type=1):
    value = self.xp.getDataref(dataref,20)
    
    if (type == 1):
        value = value*1000 + 1000
    if (type == 2):
        value = value*1000
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
            self.parent.xp2.sendDataref(self.dataref, 0)
        else:
            self.parent.xp.sendDataref(self.dataref, 1)
            self.parent.xp2.sendDataref(self.dataref, 1)
            
    def buttonPressed(self):
        print("buttonPressed2:", self.dataref)
        self.parent.xp.sendDataref(self.dataref, 1)
        self.parent.xp2.sendDataref(self.dataref, 1)
        
    def buttonReleased(self):
        print("buttonReleased2:", self.dataref)
        self.parent.xp.sendDataref(self.dataref, 0)  
        self.parent.xp2.sendDataref(self.dataref, 0)  
        
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
        self.xp2 = XPlaneUdp.XPlaneUdp(XPLANE_IP2,SEND_PORT, listen_port=49007)
        self.xp.getDataref("sim/flightmodel/position/indicated_airspeed",1)
        
        self.lat = self.xp.getDataref("sim/flightmodel/position/latitude",1)
        self.lon = self.xp.getDataref("sim/flightmodel/position/longitude",1)
        
        self.rw1_lat = 0
        self.rw1_lon = 0
        self.rw1_heading = 0
        self.rw2_lat = 0
        self.rw2_lon = 0
        self.rw2_heading = 0
        self.rw3_lat = 0
        self.rw3_lon = 0
        self.rw3_heading = 0
        self.rw4_lat = 0
        self.rw4_lon = 0
        self.rw4_heading = 0
        self.rw5_lat = 0
        self.rw5_lon = 0
        self.rw5_heading =0
        
        
        self.rw6_lat = 0
        self.rw6_lon =0
        self.rw6_heading =0
        
        
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
        
        self.indicator = IndicatorWidget()

        self.ui.indicatorLayout.addWidget(self.indicator)
        self.indicator.setDotPosition(0.5, -0.5)
        
        connectButton(self, self.ui.button_start,"JAS/io/frontpanel/di/start")
        connectButton(self, self.ui.button_master,"JAS/io/frontpanel/di/master")
        
        connectButton(self, self.ui.button_systest,"JAS/io/vu22/di/syst")
        connectButton(self, self.ui.button_lamptest,"JAS/io/vu22/di/lampprov")
        #connectButton(self, self.ui.mot_fack,"JAS/system/mot/fack")
        #connectButton(self, self.ui.mot_rems,"JAS/system/mot/rems")
        
        
        connectValueButton(self, self.ui.luft_in,"sim/cockpit2/controls/speedbrake_ratio", 0)
        connectValueButton(self, self.ui.luft_ut,"sim/cockpit2/controls/speedbrake_ratio", 1)
        
        
        # connectValueButton(self, self.ui.button_tils_on,"JAS/ti/land/lmod", 1)
        # connectValueButton(self, self.ui.button_tils_off,"JAS/ti/land/lmod", 0)
        self.buttonList.append( ColorButton(self,self.ui.button_tils_on, "JAS/io/aj37/di/tils_on", "orange", 1, lampDR="JAS/io/aj37/lo/tils_on") )
        self.buttonList.append( ColorButton(self,self.ui.button_tils_off, "JAS/io/aj37/di/tils_off", "orange", 1, lampDR="JAS/io/aj37/lo/tils_off") )
        
        # connectButtonCommand(self, self.ui.button_reload_acf,"sim/operation/reload_aircraft_no_art")
        
        #self.buttonList.append( ColorButton(self,self.ui.buttonlamp_antikoll, "sim/cockpit/electrical/nav_lights_on", "yellow", 0) )
        
        self.buttonList.append( ColorButton(self,self.ui.button_afk, "JAS/io/frontpanel/di/afk", "orange", 1, lampDR="JAS/io/frontpanel/lo/afk") )
        self.buttonList.append( ColorButton(self,self.ui.button_hojd, "JAS/io/frontpanel/di/hojd", "orange", 1, lampDR="JAS/io/frontpanel/lo/hojd") )
        self.buttonList.append( ColorButton(self,self.ui.button_att, "JAS/io/frontpanel/di/att", "orange", 1, lampDR="JAS/io/frontpanel/lo/att") )
        self.buttonList.append( ColorButton(self,self.ui.button_spak, "JAS/io/frontpanel/di/spak", "orange", 1, lampDR="JAS/io/frontpanel/lo/spak") )
        self.buttonList.append( ColorButton(self,self.ui.button_a15, "JAS/io/frontpanel/di/alfa", "orange", 1, lampDR="JAS/io/frontpanel/lo/a14") )
        
        self.buttonList.append( ColorButton(self,self.ui.buttonLmod, "JAS/ti/land/lmod", "orange", 0, lampDR="JAS/ti/land/lmod") )
        
        
        self.buttonList.append( ColorButton(self,self.ui.zon1, "JAS/io/aj37/lo/zon1", "white", 1, lampDR="JAS/io/aj37/lo/zon1") )
        self.buttonList.append( ColorButton(self,self.ui.zon2, "JAS/io/aj37/lo/zon2", "white", 1, lampDR="JAS/io/aj37/lo/zon2") )
        self.buttonList.append( ColorButton(self,self.ui.zon3, "JAS/io/aj37/lo/zon3", "white", 1, lampDR="JAS/io/aj37/lo/zon3") )
        
        self.buttonList.append( ColorButton(self,self.ui.button_parkbrake, "sim/cockpit2/controls/parking_brake_ratio", "red", 0, lampDR="sim/cockpit2/controls/parking_brake_ratio") )
        #self.buttonList.append( ColorButton(self,self.ui.dap_button_pluv, "JAS/system/dap/lamp/pluv", "green", 0) )

        self.ui.button_tanka.clicked.connect(self.buttonTankaFull)
        self.ui.button_tanka_50.clicked.connect(self.buttonTanka50)
        
        
        self.ui.button_rw1.clicked.connect(self.buttonPressedRw1)
        self.ui.button_rw2.clicked.connect(self.buttonPressedRw2)
        self.ui.button_rw3.clicked.connect(self.buttonPressedRw3)
        self.ui.button_rw4.clicked.connect(self.buttonPressedRw4)
        self.ui.button_rw5.clicked.connect(self.buttonPressedRw5)
        self.ui.button_rw6.clicked.connect(self.buttonPressedRw6)
        
        self.ui.auto_afk_text.valueChanged.connect(self.autoAFK)
        self.ui.auto_hojd_text.valueChanged.connect(self.autoHOJD)

        # self.ui.land_set_all.clicked.connect(self.Land_set_all)
        
        self.ui.button_land_update.clicked.connect(self.updateAirportBox)

        self.ui.comboBox_airports.currentTextChanged.connect(self.airportBoxOnChange)

        #Snabbval
        ## ESKN
        self.ui.snabb_eskn_1.clicked.connect(self.ESKN1)
        self.ui.snabb_eskn_2.clicked.connect(self.ESKN2)
        self.ui.snabb_eskn_3.clicked.connect(self.ESKN3)
        self.ui.snabb_eskn_4.clicked.connect(self.ESKN4)

        font = QFont("Sans")
        font.setPointSize(12)
        self.setFont(font)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.loop)
        self.timer.start(10)



    def updateGUI(self):
        for button in self.buttonList:
            button.updateColor()
        # if (self.xp.dataList["JAS/lamps/hojd"] >0):
        #     self.ui.lamps_hojd.setStyleSheet("background-color: orange")
        # else:
        #     self.ui.lamps_hojd.setStyleSheet("background-color: white")
        
        updateLamp(self, self.ui.lamps_skak, "JAS/io/aj37/lo/skak", "orange")
        
        updateLamp(self, self.ui.lamps_bramgd, "JAS/io/vat/lo/bramgd", "orange")
        
        updateLamp(self, self.ui.lamps_ebk, "JAS/io/aj37/lo/ebk", "orange")
        updateLamp(self, self.ui.lamps_rev, "JAS/io/aj37/lo/reverser", "lightgreen")
        
        updateLamp(self, self.ui.lamps_transsonic, "JAS/io/aj37/lo/transsonik", "red")
        
        updateLamp(self, self.ui.lamps_master1, "JAS/io/frontpanel/lo/master1", "red")
        updateLamp(self, self.ui.lamps_master2, "JAS/io/frontpanel/lo/master2", "red")
        
        
        updateLamp(self, self.ui.lamps_hojdvarn, "JAS/io/frontpanel/lo/hojdvarn", "red")
        
        updateLamp(self, self.ui.lamps_airbrake, "JAS/io/frontpanel/lo/airbrake", "lightgreen")
        
        
        # updateLamp(self, self.ui.lamps_park, "sim/cockpit2/controls/parking_brake_ratio", "red")
        updateLamp(self, self.ui.lamps_gears, "sim/cockpit/switches/gear_handle_status", "lightgreen")
        
        updateLamp(self, self.ui.lamps_gear1, "JAS/io/frontpanel/lo/gear1", "green")
        updateLamp(self, self.ui.lamps_gear2, "JAS/io/frontpanel/lo/gear2", "green")
        updateLamp(self, self.ui.lamps_gear3, "JAS/io/frontpanel/lo/gear3", "green")
        
        
        updateText(self, self.ui.text_fuel, "JAS/fuel/pct")
        # updateSlider(self, self.ui.slider_roll, "sim/joystick/yoke_roll_ratio", type=2)
        updateSlider(self, self.ui.slider_rudder, "sim/joystick/yoke_heading_ratio", type=2)
        # updateSlider(self, self.ui.slider_pitch, "sim/joystick/yoke_pitch_ratio", type=2)
        updateSlider(self, self.ui.slider_throttle, "sim/cockpit2/engine/actuators/throttle_ratio_all", type=2)
        updateSlider(self, self.ui.slider_bromsV, "sim/cockpit2/controls/left_brake_ratio", type=2)
        updateSlider(self, self.ui.slider_bromsH, "sim/cockpit2/controls/right_brake_ratio", type=2)
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
        self.xp.sendDataref("sim/flightmodel/weight/m_fuel1", 4476)
    def buttonTanka50(self):
        self.xp.sendDataref("sim/flightmodel/weight/m_fuel1", 2200)
        
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

                self.calculateAirportData(apt["index"])
                print("found airport", apt["id"], apt["index"])
                self.buttonPressedRw1()

    def calculateAirportData(self, index):
        self.airportIndex = index
        print("calculateAirportData", index)
        ap = self.airportList[index]
        print(ap)
        # self.xp.sendDataref("JAS/ti/land/index", self.airportDict["ESKN"]["index"])
        # self.xp.sendDataref("JAS/ti/land/lat", ap["rw1_lat"])
        # self.xp.sendDataref("JAS/ti/land/lon", ap["rw1_lon"])
        
        
        
        self.rw_alt = ap["alt"] / 3.281
        self.ui.button_rw1.setText("")
        self.ui.button_rw2.setText("")
        self.ui.button_rw3.setText("")
        self.ui.button_rw4.setText("")
        self.ui.button_rw5.setText("")
        self.ui.button_rw6.setText("")
        if (ap["rw1_compass"] != 0.0):
            self.rw1_lat = ap["rw1_lat"]
            self.rw1_lon = ap["rw1_lon"]
            self.rw1_heading = ap["rw1_compass"]
            self.ui.button_rw1.setText(str(ap["rw1_heading"]) )
            
            
            self.rw2_lat = ap["rw1_lat2"]
            self.rw2_lon = ap["rw1_lon2"]
            self.rw2_heading = ap["rw1_compass"] +180
            if self.rw2_heading >360.0:
                self.rw2_heading = self.rw2_heading - 360.0
            
            self.ui.button_rw2.setText(str(int(self.rw2_heading/10) ))
        if (ap["rw2_compass"] != 0.0):
            self.rw3_lat = ap["rw2_lat"]
            self.rw3_lon = ap["rw2_lon"]
            self.rw3_heading = ap["rw2_compass"]
            self.ui.button_rw3.setText(str(ap["rw2_heading"]) )
            
            
            self.rw4_lat = ap["rw2_lat2"]
            self.rw4_lon = ap["rw2_lon2"]
            self.rw4_heading = ap["rw2_compass"] +180
            if self.rw4_heading >360.0:
                self.rw4_heading = self.rw4_heading - 360.0
            
            self.ui.button_rw4.setText(str(int(self.rw4_heading/10) ))
        if (ap["rw3_compass"] != 0.0):
            self.rw5_lat = ap["rw3_lat"]
            self.rw5_lon = ap["rw3_lon"]
            self.rw5_heading = ap["rw3_compass"]
            self.ui.button_rw5.setText(str(ap["rw3_heading"]) )
            
            
            self.rw6_lat = ap["rw3_lat2"]
            self.rw6_lon = ap["rw3_lon2"]
            self.rw6_heading = ap["rw3_compass"] +180
            if self.rw6_heading >360.0:
                self.rw6_heading = self.rw6_heading - 360.0
            
            self.ui.button_rw6.setText(str(int(self.rw6_heading/10) ))
        
        

    def buttonPressedRw1(self):
        print("buttonPressedRw1:")
        # self.xp.sendDataref("JAS/ti/land/lat", self.rw1_lat)
        # self.xp.sendDataref("JAS/ti/land/lon", self.rw1_lon)
        # self.xp.sendDataref("JAS/ti/land/head", self.rw1_heading)
        # self.xp.sendDataref("JAS/ti/land/alt", self.rw_alt)
        self.setTilsData(self.rw1_lat, self.rw1_lon, self.rw1_heading, self.rw_alt)
        
    def buttonPressedRw2(self):
        print("buttonPressedRw2:")

        self.setTilsData(self.rw2_lat, self.rw2_lon, self.rw2_heading, self.rw_alt)
        
    def buttonPressedRw3(self):
        print("buttonPressedRw3:")

        self.setTilsData(self.rw3_lat, self.rw3_lon, self.rw3_heading, self.rw_alt)
        
    def buttonPressedRw4(self):
        print("buttonPressedRw4:")

        self.setTilsData(self.rw4_lat, self.rw4_lon, self.rw4_heading, self.rw_alt)
        
    def buttonPressedRw5(self):
        print("buttonPressedRw5:")

        self.setTilsData(self.rw5_lat, self.rw5_lon, self.rw5_heading, self.rw_alt)
        
    def buttonPressedRw6(self):
        print("buttonPressedRw6:")

        self.setTilsData(self.rw6_lat, self.rw6_lon, self.rw6_heading, self.rw_alt)
        
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
        print("närmaste ", self.airportListClose[0])
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
                    if (len(col)>37):
                        apt["rw1_heading"] = col[4]
                        apt["rw1_compass"] = float(col[5])
                        apt["rw1_surf"] = int(col[6])
                        apt["rw1_lat"] = float(col[7])
                        apt["rw1_lon"] = float(col[8])
                        apt["rw1_lat2"] = float(col[9])
                        apt["rw1_lon2"] = float(col[10])
                        
                        apt["rw2_heading"] = col[11]
                        apt["rw2_compass"] = float(col[12])
                        apt["rw2_surf"] = int(col[13])
                        apt["rw2_lat"] = float(col[14])
                        apt["rw2_lon"] = float(col[15])
                        apt["rw2_lat2"] = float(col[16])
                        apt["rw2_lon2"] = float(col[17])
                        
                        apt["rw3_heading"] = col[18]
                        apt["rw3_compass"] = float(col[19])
                        apt["rw3_surf"] = int(col[20])
                        apt["rw3_lat"] = float(col[21])
                        apt["rw3_lon"] = float(col[22])
                        apt["rw3_lat2"] = float(col[23])
                        apt["rw3_lon2"] = float(col[24])
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
        self.ui.comboBox_airports.setCurrentText("ESKN".upper())
        self.buttonPressedRw2()
        return
    def ESKN2(self):
        self.xp.sendDataref("JAS/ti/land/index", self.airportDict["ESKN"]["index"])
        self.ui.comboBox_airports.setCurrentText("ESKN".upper())
        self.buttonPressedRw1()
        return
    def ESKN3(self):
        self.xp.sendDataref("JAS/ti/land/index", self.airportDict["ESKN"]["index"])
        self.ui.comboBox_airports.setCurrentText("ESKN".upper())
        self.buttonPressedRw4()
        return
    def ESKN4(self):
        self.xp.sendDataref("JAS/ti/land/index", self.airportDict["ESKN"]["index"])
        self.ui.comboBox_airports.setCurrentText("ESKN".upper())
        self.buttonPressedRw3()
        return

    
    def setTilsData(self,lat, lon, head, alt):
        self.xp.sendDataref("JAS/ti/land/lat", lat)
        self.xp.sendDataref("JAS/ti/land/lon", lon)
        self.xp.sendDataref("JAS/ti/land/head", head)
        self.xp.sendDataref("JAS/ti/land/alt", alt)

        self.xp2.sendDataref("JAS/ti/land/lat", lat)
        self.xp2.sendDataref("JAS/ti/land/lon", lon)
        self.xp2.sendDataref("JAS/ti/land/head", head)
        self.xp2.sendDataref("JAS/ti/land/alt", alt)
        

    def loop(self):
        self.xp.readData()
        self.indicator.setDotPosition(self.xp.getDataref("sim/joystick/yoke_roll_ratio",30), -self.xp.getDataref("sim/joystick/yoke_pitch_ratio",30))
        self.updateGUI()
        
        #print(self.xp.dataList)
        self.timer.start(10)
        pass
        
class IndicatorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(120, 120)  # Set the size of the widget to 80x80 pixels
        self.dot_x = 0  # Initialize dot position in the middle
        self.dot_y = 0

    def paintEvent(self, event):
        # Create a QPainter object to handle drawing
        painter = QPainter(self)
        
        # Set the background color
        painter.fillRect(self.rect(), QColor(240, 240, 240))  # Light gray background
        
        # Draw the crosshair in the middle
        pen = QPen(Qt.black, 1)
        painter.setPen(pen)
        # Vertical line
        painter.drawLine(self.width() // 2, 0, self.width() // 2, self.height())
        # Horizontal line
        painter.drawLine(0, self.height() // 2, self.width(), self.height() // 2)

        # Calculate dot position within the 80x80 box
        # Transform dot_x and dot_y from range -1 to 1 into pixel positions
        pixel_x = int((self.dot_x + 1) / 2 * (self.width() - 1))
        pixel_y = int((1 - self.dot_y) / 2 * (self.height() - 1))  # Inverted y-axis
        
        # Draw the dot
        pen = QPen(Qt.red, 8)  # Red dot with thickness of 8 pixels
        painter.setPen(pen)
        painter.drawPoint(pixel_x, pixel_y)

    def setDotPosition(self, x, y):
        # Clamp values to the range -1 to 1
        self.dot_x = max(-1, min(1, x))
        self.dot_y = max(-1, min(1, y))
        # Redraw the widget with the updated dot position
        self.update()
        
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
