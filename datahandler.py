#!/usr/bin/env python

from gps import *
from time import sleep
from configparser import ConfigParser
import threading
from influxdb import InfluxDBClient
import logging
import time
import pynmea2
import datetime
import socket
import math


#  Config Parser Init:
logging.basicConfig(filename='SoariBox.log', level=logging.WARNING)
config_file = ConfigParser()
config_file.read("config.ini")
# General Settings:
debug = config_file.getboolean('GENERAL', 'debug')
#  GPS Settings:
gps_sleep_time = config_file.getfloat('GPS', 'gps_refresh_speed')
gps_source = config_file.get('GPS', 'gps_source')
#  NMEA out settings:
nmea_out_enabled = config_file.get('NMEA', 'nmea_out_enabled')
UDP_IP = config_file.get('NMEA', 'UDP_IP')
UDP_PORT = int(config_file.get('NMEA', 'UDP_PORT'))
nmea_refresh_speed = float(config_file.get('NMEA', 'nmea_refresh_speed'))
# influxDB Config:
influx_host = config_file.get('INFLUXDB', 'influx_host')
influx_port = int(config_file.get('INFLUXDB', 'influx_port'))
influx_user = config_file.get('INFLUXDB', 'influx_user')
influx_pass = config_file.get('INFLUXDB', 'influx_pass')
influx_db = config_file.get('INFLUXDB', 'influx_db')
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
                time.sleep(gps_sleep_time)  # tune this, you might not get values that quickly
        except StopIteration:
            pass


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
#            else:
#                datastorage['gps_track'] = 0.0

            if hasattr(latestdata, 'alt'):
                datastorage['gps_altitude'] = latestdata.alt
#            else:
#                datastorage['gps_altitude'] = 0.0
        sleep(gps_sleep_time)


def start_influx_gps_logging(*args):
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
            if debug:
                print(influx_json_body)
                logging.debug('Data written to Influx_DB')
                print('Data written to InFluxDB')

            time.sleep(influx_logging_speed)


def start_flarm_gps(*args):
    logging.debug('Flarm not yet implemented')


def nmea_out(*args):
    print('Started NMEA Output Thread')
    logging.debug('NMEA output on' + str(UDP_IP) + ':' + str(UDP_PORT))
    while True:
        while int(datastorage['gps_fix_mode']) < 3:
            print('Waiting for Fix')
            sleep(1)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while datastorage['gps_fix_mode'] == 3 and str(datastorage['gps_track']) != 'nan':
            nmea_time_buf = datastorage['gps_time_utc']
            nmea_time = nmea_time_buf[11:13] + nmea_time_buf[14:16] + nmea_time_buf[17:19] + "." + nmea_time_buf[20:23]
            nmea_date = nmea_time_buf[8:10] + nmea_time_buf[5:7] + nmea_time_buf[2:4]
            print(nmea_time_buf)
            print(nmea_date)
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
            nmea_RMC = pynmea2.RMC('GP', 'RMC', (nmea_time, 'A', nmea_lat, NS, nmea_lon, EW, str(gps_speed_kn), nmea_track, nmea_date, '', ''))
#to be implemented            nmea_GSA = pynmea2.GSA('GP', 'GSA', ('A', '3', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '1.0', '1.0', '1.0'))
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

            sleep(nmea_refresh_speed)


def decdeg2dms(dd):
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


def handle_unhandled(exc_type, exc_value, exc_traceback):
    now = datetime.datetime.now()
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.critical(now.strftime("%Y-%m-%d %H:%M:%S") + 'Unhandled exception:', exc_info=(exc_type, exc_value, exc_traceback))


def patch_threading_excepthook():
    """Installs our exception handler into the threading modules Thread object
    Inspired by https://bugs.python.org/issue1230540
    """
    old_init = threading.Thread.__init__

    def new_init(self, *args, **kwargs):
        old_init(self, *args, **kwargs)
        old_run = self.run

        def run_with_our_excepthook(*args, **kwargs):
            try:
                old_run(*args, **kwargs)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                sys.excepthook(*sys.exc_info())
        self.run = run_with_our_excepthook
    threading.Thread.__init__ = new_init


def starthandler():
    patch_threading_excepthook()
    sys.excepthook = handle_unhandled
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
        if influx_logging == '1':
            x = threading.Thread(target=start_influx_gps_logging, args=(0,))
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
        print("Unhandled exception:", sys.exc_info()[0])
        raise

if __name__ == '__main__':
    starthandler()
