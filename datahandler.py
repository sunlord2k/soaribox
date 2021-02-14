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
import LatLon
import math

#  General Settings read:
logging.basicConfig(filename='SoariBox.log', encoding='utf-8', level=logging.DEBUG)
config_file = ConfigParser()
config_file.read("config.ini")
debug = config_file.getint('GENERAL', 'debug')
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
                time.sleep(0.2) # tune this, you might not get values that quickly
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
        'gps_lat': '0',
        'gps_time_utc': '0',
        'gps_altitude': '0',
        'gps_speed_ms': '0',
        'gps_speed_kn': '0',
        'gps_sats': '0',
        'gps_fix_mode': '0',
        'gps_track': '0'
    }

    def __init__(self, *args):
        if datastorage['gps_speed_ms'] == 'nan':
            datastorage['gps_speed_ms'] = '0'
#        datastorage['gps_speed_kn'] = datastorage['gps_speed_ms'] * 1.943844

    def fill(self, name, value, *args):
        datastorage['(name)'] = value
        print(datastorage['(name)'])


def start_gps_sensor(*args):
    print('Started GPS thread')
    while True:
        datastorage['gps_long'] = gpsd.fix.longitude
        datastorage['gps_lat'] = gpsd.fix.latitude
        datastorage['gps_time_utc'] = gpsd.fix.time
        datastorage['gps_altitude'] = gpsd.fix.altitude
        datastorage['gps_speed_ms'] = gpsd.fix.speed
        datastorage['gps_sats'] = gpsd.satellites
        datastorage['gps_fix_mode'] = gpsd.fix.mode
        datastorage['gps_track'] = gpsd.fix.track
#        datastorage['gps_fix_mode'] = 2
        logging.debug(datastorage)
        if debug > 0:
            os.system('clear')
            print(' GPS reading')
            print('----------------------------------------')
            print('latitude    ', gpsd.fix.latitude)
            print('longitude   ', gpsd.fix.longitude)
            print('time utc    ', gpsd.utc, ' + ', gpsd.fix.time)
            print('altitude (m)', gpsd.fix.altitude)
            print('eps         ', gpsd.fix.eps)
            print('epx         ', gpsd.fix.epx)
            print('epv         ', gpsd.fix.epv)
            print('ept         ', gpsd.fix.ept)
            print('speed (m/s) ', gpsd.fix.speed)
            print('climb       ', gpsd.fix.climb)
            print('track       ', gpsd.fix.track)
            print('mode        ', gpsd.fix.mode)
            print('sats        ', gpsd.satellites)
        time.sleep(gps_sleep_time)  # Update speed of GPS Date set in in config file


def start_gps_sensor2(*args):
    while True:
        latestdata = gpsp.get_current_value()
        print(latestdata)
        if latestdata['class'] == 'TPV':
            print(latestdata.lon)
            datastorage['gps_long'] = latestdata.lon
            datastorage['gps_lat'] = latestdata.lat
            datastorage['gps_time_utc'] = latestdata.time
            datastorage['gps_altitude'] = latestdata.alt
            datastorage['gps_speed_ms'] = latestdata.speed
            datastorage['gps_sats'] = 10 #  Still under testing
            datastorage['gps_fix_mode'] = latestdata.mode
            datastorage['gps_track'] = 0
        sleep(1)


def start_influx_logging(*args):
    sleep(1)
    print('Strted Influx Thread')
    while datastorage['gps_fix_mode'] < 3:
        print('Waiting for Fix')
        sleep(1)

    while datastorage['gps_fix_mode'] == 3:
        influx_json_body = [
            {
                "measurement": "testcase4",
                "tags": {
                    "host": influx_host
                },
                "fields": {
                    "alt": datastorage['gps_altitude'],
                    "lat": datastorage['gps_lat'],
                    "lon": datastorage['gps_long'],
                    "speed": datastorage['gps_speed_ms']
                    }
                    }
                    ]
        influx_client = InfluxDBClient(influx_host, influx_port, influx_user, influx_pass, influx_db)
        influx_client.write_points(influx_json_body)
        logging.debug('Data written to Influx_DB')
        logging.debug(influx_json_body)
        print(datastorage['gps_track'])
        time.sleep(influx_logging_speed)


def start_flarm_gps(*args):
    logging.debug('Flarm not yet implemented')


def nmea_out(*args):
    print('Started NMEA Output Thread')
    logging.debug('NMEA output on port XYZ started')
    while True:
        while datastorage['gps_fix_mode'] < 3:
            print('Waiting for Fix')
            sleep(1)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while datastorage['gps_fix_mode'] == 3 and str(datastorage['gps_track']) != 'nan':
            nmea_time_buf = datastorage['gps_time_utc']
            nmea_time = nmea_time_buf[11:13] + nmea_time_buf[14:16] + nmea_time_buf[17:19] + "." + nmea_time_buf[20:23]
            nmea_lat = dms(datastorage['gps_lat'])
            nmea_lon = dms(datastorage['gps_long'])
            nmea_lat_temp = datastorage['gps_lat']
            nmea_lon_temp = datastorage['gps_long']
            nmea_lon_test = dec2dms(nmea_lon_temp)
            nmea_lat_test = dec2dms(nmea_lat_temp)
#            nmea_lat_test = '5252.56'
            nmea_track = str(datastorage['gps_track'])
            print('Longitude:', nmea_lon_test)
            print('Latidtude:', nmea_lat_test)
            gps_speed_kn = datastorage['gps_speed_ms'] * 1.943844
            print('Speed', datastorage['gps_speed_ms'])
            print('Track:', datastorage['gps_track'])
    #  NMEA Sentences Generation:
            nmea_GGA = pynmea2.GGA('GP', 'GGA', (nmea_time, nmea_lat_test, 'N', nmea_lon_test, 'E', '1', '12', '1.0', '0.0', 'M', '0.0', 'M', '', ''))
            nmea_RMC = pynmea2.RMC('GP', 'RMC', (nmea_time, 'A', nmea_lat_test, 'N', nmea_lon_test, 'E', str(gps_speed_kn), nmea_track, '261220', '', ''))
            nmea_GSA = pynmea2.GSA('GP', 'GSA', ('A', '3', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '1.0', '1.0', '1.0'))
            print(nmea_GGA)
            print(nmea_RMC)
    #        print(nmea_GSA)
            crlf = "\r\n"
            sock.sendto(bytes(nmea_GGA), (UDP_IP, UDP_PORT))  # Send
            sock.sendto(bytes(crlf), (UDP_IP, UDP_PORT))
            if nmea_track != 'nan':
                sock.sendto(bytes(nmea_RMC), (UDP_IP, UDP_PORT))
                sock.sendto(bytes(crlf), (UDP_IP, UDP_PORT))

    #        sock.sendto(bytes(nmea_GSA), (UDP_IP, UDP_PORT))
    #        sock.sendto(bytes(crlf), (UDP_IP, UDP_PORT))
            print('Data send to UDP')
            sleep(1)


def dms(dec):
    f, d = math.modf(dec)
    s, m = math.modf(abs(f) * 60)
    degstr = str(d)
    minstr = str(m)
    secstr = str(s * 60)
    if secstr[1] == '.':
        secstr = '0' + secstr
    secstrint = int(s * 60)
    returnvalue = degstr[0:2] + minstr[0:2] + '.' + secstr[0:2] + secstr[3:6]
    return (returnvalue)


def dec2dms(dec):
    south = False
    lon = 0
    if(lon < 0):
        lon = lon*-1
        south = True

    lon_deg = math.floor(dec)
    lon_min = math.floor((dec - lon_deg) * 60)
    lon_sec = round((dec*3600 - lon_deg*3600 - lon_min*60), 6)
    degstr = str(lon_deg)
    minstr = str(lon_min)
    secstr = str(lon_sec)
    print('Funktion degstr:', degstr)
    print('Funktion minstr:', minstr)
    print('Funktion secstr', secstr)
    if secstr[1] == '.':
        secstr = '0' + secstr
    if minstr[1] == '.':
        minstr = '0' + minstr
    returnvalue = '0' + degstr[0:2] + minstr[0:2] + '.' + secstr[0:2] + secstr[3:6]
    return (returnvalue)


if __name__ == '__main__':
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
