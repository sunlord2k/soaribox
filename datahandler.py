#!/usr/bin/env python

import os
from gps import *
from time import *
from configparser import ConfigParser
import threading
from influxdb import InfluxDBClient
import logging
import time
import pynmea2
import datetime
import socket
import math
import csv
import pandas as pd


#  General Settings read:
logging.basicConfig(filename='SoariBox.log', level=logging.DEBUG)
config_file = ConfigParser()
config_file.read("config.ini")
debug = config_file.getboolean('GENERAL', 'debug')
#  GPS Settings read
gps_sleep_time = config_file.getfloat('GPS', 'gps_refresh_speed')
gps_source = config_file.get('GPS', 'gps_source')
#  NMEA out settings:
nmea_out_enabled = config_file.get('GENERAL', 'nmea_out_enabled')
UDP_IP = "127.0.0.1"
UDP_PORT = 10110
# influxDB Config
influx_host = 'localhost'  # Configparser to be added
influx_port = 8086  # Configparser to be added
influx_user = 'soaribox'  # Configparser to be added
influx_pass = 'soaribox'  # Configparser to be added
influx_db = 'soaribox'  # Configparser to be added
influx_logging = config_file.get('INFLUXDB', 'influx_logging')
influx_logging_speed = config_file.getfloat('INFLUXDB', 'influx_logging_speed')


class GpsPoller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        global gpsd  # bring it in scope
        self.session = gps(mode=WATCH_ENABLE)  # starting the stream of info
        self.current_value = None
        self.running = True  # setting the thread running to true

    def get_current_value(self):
        return self.current_value

    def run(self):
        try:
            while True:
                self.current_value = self.session.next()
                time.sleep(0.2)  # tune this, you might not get values that quickly
        except StopIteration:
            pass

#    def run(self):
#        global gpsd
#        while gpsp.running:
#            gpsd.next()


class data:
    global datastorage
    datastorage = {
        'gps_NMEA': '0',
        'flarm_NMEA': '0',
        'gps_long': '0',
        'gps_long_dec': '0',
        'gps_lat': '0.0',
        'gps_lat_dec': '0',
        'gps_time_utc': '0',
        'gps_altitude': '0',
        'gps_speed_ms': '0',
        'gps_speed_kn': '0',
        'gps_sats': '0',
        'gps_fix_mode': '0',
        'gps_track': '0',
        'test_deg': '0',
        'test_min': '0',
        'test_sec': '0',
        'test_dms': '0'
    }

    def __init__(self, *args):
        if datastorage['gps_speed_ms'] == 'nan':
            datastorage['gps_speed_ms'] = '0'
#        datastorage['gps_speed_kn'] = datastorage['gps_speed_ms'] * 1.943844


def start_gps_sensor(*args):
    print('Started GPS thread')
    while True:
        datastorage['gps_long'] = gpsd.fix.longitude
        datastorage['gps_lat'] = gpsd.fix.latitude
        datastorage['gps_time_utc'] = gpsd.fix.time
        datastorage['gps_altitude'] = gpsd.fix.altitude
        datastorage['gps_speed_ms'] = gpsd.fix.speed
        datastorage['gps_sats'] = gpsd.satellites
        datastorage['gps_fix_mode'] = int(gpsd.fix.mode)
        datastorage['gps_track'] = gpsd.fix.track
#        datastorage['gps_fix_mode'] = 2
        logging.debug(datastorage)
        time.sleep(gps_sleep_time)  # Update speed of GPS Date set in in config file


def start_gps_sensor2(*args):
    while True:
        latestdata = gpsp.get_current_value()
        if latestdata['class'] == 'TPV':
            datastorage['gps_long'] = latestdata.lon
            datastorage['gps_lat'] = float(latestdata.lat)
            datastorage['gps_time_utc'] = latestdata.time
            datastorage['gps_speed_ms'] = latestdata.speed
            datastorage['gps_sats'] = 10  # Still under testing
            datastorage['gps_fix_mode'] = int(latestdata.mode)
            if hasattr(latestdata, 'track'):
                datastorage['gps_track'] = latestdata.track
            else:
                datastorage['gps_track'] = 0.0

            if hasattr(latestdata, 'alt'):
                datastorage['gps_altitude'] = latestdata.alt
            else:
                datastorage['gps_altitude'] = 0.0
        logging.debug(datastorage)
        sleep(gps_sleep_time)


def start_influx_logging(*args):
    while True:
        print('Started Influx Thread')
    #    while datastorage['gps_fix_mode'] < 3:
        while int(datastorage['gps_fix_mode']) < 3 or str(datastorage['gps_track']) == 'nan':
            print('Waiting for Fix')
            sleep(1)

    #    while datastorage['gps_fix_mode'] > 3:
        while datastorage['gps_fix_mode'] == 3 and str(datastorage['gps_track']) != 'nan':
            influx_json_body = [
                {
                    "measurement": "soaribox1",
                    "tags": {
                        "host": influx_host
                    },
                    "fields": {
                        "alt": datastorage['gps_altitude'],
                        "lat": datastorage['gps_lat'],
                        "lon": datastorage['gps_long'],
                        "speed": datastorage['gps_speed_ms'],
                        "long_dec": float(datastorage['gps_long_dec']),
                        "lat_dec": float(datastorage['gps_lat_dec']),
                        "test_deg": float(datastorage['test_deg']),
                        "test_min": float(datastorage['test_min']),
                        "test_sec": float(datastorage['test_sec'])
                        }
                        }
                        ]
            influx_client = InfluxDBClient(influx_host, influx_port, influx_user, influx_pass, influx_db)
            influx_client.write_points(influx_json_body)
            logging.debug('Data written to Influx_DB')
            logging.debug(influx_json_body)
            if debug:
                print(influx_json_body)
                print('Data written to InFluxDB')

            time.sleep(influx_logging_speed)


def start_flarm_gps(*args):
    logging.debug('Flarm not yet implemented')


def nmea_out(*args):
    print('Started NMEA Output Thread')
    logging.debug('NMEA output on port XYZ started')
    while True:
        while int(datastorage['gps_fix_mode']) < 3:
            print('Waiting for Fix')
            sleep(1)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while datastorage['gps_fix_mode'] == 3 and str(datastorage['gps_track']) != 'nan':
            nmea_time_buf = datastorage['gps_time_utc']
            nmea_time = nmea_time_buf[11:13] + nmea_time_buf[14:16] + nmea_time_buf[17:19] + "." + nmea_time_buf[20:23]
            nmea_track = str(datastorage['gps_track'])
            gps_speed_kn = datastorage['gps_speed_ms'] * 1.943844
            nmea_lon, lonneg = decdeg2dms(datastorage['gps_long'])
            nmea_lat, latneg = decdeg2dms(datastorage['gps_lat'])
            if latneg:
                NS = 'S'
            else:
                NS = 'N'
            if lonneg:
                EW = 'W'
            else:
                EW = 'E'

            datastorage['gps_long_dec'] = str(nmea_lon)
            datastorage['gps_lat_dec'] = str(nmea_lat)
    #  NMEA Sentences Generation:
            nmea_GGA = pynmea2.GGA('GP', 'GGA', (nmea_time, nmea_lat, NS, nmea_lon, EW, '1', '12', '1.0', '0.0', 'M', '0.0', 'M', '', ''))
            nmea_RMC = pynmea2.RMC('GP', 'RMC', (nmea_time, 'A', nmea_lat, NS, nmea_lon, EW, str(gps_speed_kn), nmea_track, '261220', '', ''))
            nmea_GSA = pynmea2.GSA('GP', 'GSA', ('A', '3', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '1.0', '1.0', '1.0'))
            crlf = "\r\n"
            sock.sendto(bytes(nmea_GGA), (UDP_IP, UDP_PORT))  # Send
            sock.sendto(bytes(crlf), (UDP_IP, UDP_PORT))
            if nmea_track != 'nan':
                sock.sendto(bytes(nmea_RMC), (UDP_IP, UDP_PORT))
                sock.sendto(bytes(crlf), (UDP_IP, UDP_PORT))

    #        sock.sendto(bytes(nmea_GSA), (UDP_IP, UDP_PORT))
    #        sock.sendto(bytes(crlf), (UDP_IP, UDP_PORT))
            if debug:
                print('Data send to UDP')

            sleep(1)


def decdeg2dms(dd):
    print(dd)
    negative = dd < 0
    dd = abs(dd)
    if dd < 1:
        degrees = '00'
    else:
        if negative:
            degrees = math.ceil(dd)
        else:
            degrees = math.floor(dd)

    minutes = (dd - float(degrees)) * 60
    strminutes = removepoint(minutes)
    strdegrees = removepoint(degrees)
    result = strdegrees[0:2] + strminutes[0:2] + '.' + strminutes[2:8]
    return (result, negative)


def removepoint(val):
    val = str(val)
    val_length = len(val) - 1
    for i in xrange(1, val_length):
        if val[i] == '.':
            val = val[0:i] + val[i+1:val_length+1]
            if i == 1:
                val = '0' + val
    result = val
    return(result)


def starthandler():
    try:
        storage = data()  # Zentraler Datenspeicher
        if gps_source == 'GPS_SENSOR':  # GPS Empfaenger verbungden
            global gpsp
            gpsp = GpsPoller()  # create the thread
            gpsp.daemon = True
            gpsp.start()  # start it up
            Y = threading.Thread(target=start_gps_sensor2, args=(0,))
            Y.daemon = True
            Y.start()
        else:  # GPS Daten vom Flamr werden verwendet
            start_flarm_gps()
    #    start_influx_logging()
        if influx_logging == '1':
            x = threading.Thread(target=start_influx_logging, args=(0,))
            x.daemon = True
            x.start()
            print(nmea_out_enabled)

        if nmea_out_enabled == '1':
            z = threading.Thread(target=nmea_out, args=(1,))
            z.daemon = True
            z.start()
        while True:
            sleep(1)
    except:
        print('The End')


if __name__ == '__main__':
    starthandler()
