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


class configuration:
    def __init__(self, *args):
        #  Config Parser Init:
        logging.basicConfig(filename='SoariBox.log', level=logging.WARNING)
        config_file = ConfigParser()
        config_file.read("config.ini")
        # General Settings:
        self.debug = config_file.getboolean('GENERAL', 'debug')
        #  GPS Settings:
        self.gps_sleep_time = config_file.getfloat('GPS', 'gps_refresh_speed')
        self.gps_source = config_file.get('GPS', 'gps_source')
        #  NMEA out settings:
        self.nmea_out_enabled = config_file.get('NMEA', 'nmea_out_enabled')
        self.UDP_IP = config_file.get('NMEA', 'UDP_IP')
        self.UDP_PORT = int(config_file.get('NMEA', 'UDP_PORT'))
        self.nmea_refresh_speed = float(config_file.get('NMEA', 'nmea_refresh_speed'))
        # influxDB Config:
        self.influx_host = config_file.get('INFLUXDB', 'influx_host')
        self.influx_port = int(config_file.get('INFLUXDB', 'influx_port'))
        self.influx_user = config_file.get('INFLUXDB', 'influx_user')
        self.influx_pass = config_file.get('INFLUXDB', 'influx_pass')
        self.influx_db = config_file.get('INFLUXDB', 'influx_db')
        self.influx_logging = config_file.get('INFLUXDB', 'influx_logging')
        self.influx_logging_speed = config_file.getfloat('INFLUXDB', 'influx_logging_speed')


class watchdog:
    def __init__(self, *args):
        nmea_timeout = 0
        influx_timeout = 0
        gpspoller_timeout = 0
        self.startup_delay = 10
        self.timeout = [0, 0, 0, 0, 0, 0]

    def watch(self):
        for i in range(self.startup_delay, 0, -1):
            global watchdog_Thread_kill_register
            self.startup_delay -= 1
            sleep(1)
            print(self.startup_delay)
            self.alive = [False, False, False, False, False, False]
            self.timeout = [0, 0, 0, 0, 0, 0]
        while watchdog_Thread_kill_register[0] == 0:
            for i in range(0, 4):
                if self.alive[i]:
                    self.alive[i] = False
                    self.timeout[i] = 0
                else:
                    self.timeout[i] += 1
                    print("Watchdog Message: timeout:" + str(self.timeout[i]) + "s")
                    print(watchdog_Thread_kill_register)
                    if self.timeout[i] > 15:
                        watchdog_Thread_kill_register = [1, 1, 1, 1, 1, 1]
                        now = datetime.datetime.now()
                        logging.critical(now.strftime("%Y-%m-%d %H:%M:%S") + "The Watchdog was triggered and is about to kill all Threads")
                        print(watchdog_Thread_kill_register)
                        print("The Watchdog is terminating itself!")
                        break
#                        raise ValueError('The Watchdog killed itself')
            sleep(1)

    def resettimeout(self, ThreadID, *args):
        self.timeout[ThreadID] = 0


class GpsPoller(configuration, threading.Thread):
    def __init__(self, *args):
        threading.Thread.__init__(self)
        global gpsd  # bring it in scope
        self.session = gps(mode=WATCH_ENABLE)  # starting the stream of info
        self.current_value = None
        self.running = True  # setting the thread running to true

    def get_current_value(self):
        return self.current_value

    def run(self):
        global watchdog_Thread_kill_register, nmea_dog
        try:
            while watchdog_Thread_kill_register[1] == 0:
                self.current_value = self.session.next()
                time.sleep(c.gps_sleep_time)  # tune this, you might not get values that quickly
                if watchdog_Thread_kill_register[1] == 1:
                    now = datetime.datetime.now()
                    logging.critical(now.strftime("%Y-%m-%d %H:%M:%S") + "The Watchdog was triggered and killed the GPS Poller thread")
                    break
                nmea_dog.resettimeout(0)

        except StopIteration:
            pass

    def get_id(self):
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id


class nmea_out(configuration):
    def start_gps_sensor2(self, *args):
        global watchdog_Thread_kill_register, nmea_dog
        while watchdog_Thread_kill_register[2] == 0:
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
                if hasattr(latestdata, 'alt'):
                    datastorage['gps_altitude'] = latestdata.alt
            sleep(c.gps_sleep_time)
            if watchdog_Thread_kill_register[2] == 1:
                print("The Watchdog was triggered and killed the GPS to datastorage thread")
                now = datetime.datetime.now()
                logging.critical(now.strftime("%Y-%m-%d %H:%M:%S") + "The Watchdog was triggered and killed the GPS to datastorage thread")
                break
            nmea_dog.resettimeout(1)
            print("GPS sensor Thread alive!")

    def start_influx_gps_logging(self, *args):
        global watchdog_Thread_kill_register, nmea_dog
        while watchdog_Thread_kill_register[3] == 0:
            while int(datastorage['gps_fix_mode']) < 3 or str(datastorage['gps_track']) == 'nan':
                print('InFlux Thread: Waiting for Fix')
                if watchdog_Thread_kill_register[3] == 1:
                    print("The Watchdog was triggered and killed the InFluxDB thread")
                    now = datetime.datetime.now()
                    logging.critical(now.strftime("%Y-%m-%d %H:%M:%S") + "The Watchdog was triggered and killed the InFluxDB thread")
                    break
                nmea_dog.resettimeout(3)
                sleep(1)

        #    while datastorage['gps_fix_mode'] > 3:
            while datastorage['gps_fix_mode'] == 3 and str(datastorage['gps_track']) != 'nan':
                influx_json_body = [
                    {
                        "measurement": "soaribox1",
                        "tags": {
                            "host": c.influx_host
                        },
                        "fields": {
                            "alt": datastorage['gps_altitude'],
                            "lat": datastorage['gps_lat'],
                            "lon": datastorage['gps_long'],
                            "speed": datastorage['gps_speed_ms'],
                            "long_dec": float(datastorage['gps_long_dec']),
                            "lat_dec": float(datastorage['gps_lat_dec'])
                            }
                            }
                            ]
                influx_client = InfluxDBClient(c.influx_host, c.influx_port, c.influx_user, c.influx_pass, c.influx_db)
                influx_client.write_points(influx_json_body)
                if c.debug:
                    print(influx_json_body)
                    logging.debug('Data written to Influx_DB')
                    print('Data written to InFluxDB')
                if watchdog_Thread_kill_register[3] == 1:
                    print("The Watchdog was triggered and killed the InFluxDB thread")
                    now = datetime.datetime.now()
                    logging.critical(now.strftime("%Y-%m-%d %H:%M:%S") + "The Watchdog was triggered and killed the InFluxDB thread")
                    break
                nmea_dog.resettimeout(3)
                time.sleep(c.influx_logging_speed)

    def start_flarm_gps(self, *args):
        logging.debug('Flarm not yet implemented')

    def nmea_out(self, *args):
        global watchdog_Thread_kill_register, nmea_dog
        print('NMEA Thread: Started ')
        logging.debug('NMEA output on' + str(c.UDP_IP) + ':' + str(c.UDP_PORT))
        while watchdog_Thread_kill_register[4] == 0:
            while int(datastorage['gps_fix_mode']) < 3:
                if watchdog_Thread_kill_register[0] == 1:
                    print("The Watchdog was triggered and killed the NMEA out thread")
                    now = datetime.datetime.now()
                    logging.critical(now.strftime("%Y-%m-%d %H:%M:%S") + "The Watchdog was triggered and killed the NMEA out thread")
                    break
                nmea_dog.resettimeout(4)
                print('NMEA Thread: Waiting for Fix')
                sleep(1)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            while datastorage['gps_fix_mode'] == 3 and str(datastorage['gps_track']) != 'nan':
                nmea_time_buf = datastorage['gps_time_utc']
                nmea_time = nmea_time_buf[11:13] + nmea_time_buf[14:16] + nmea_time_buf[17:19] + "." + nmea_time_buf[20:23]
                nmea_date = nmea_time_buf[8:10] + nmea_time_buf[5:7] + nmea_time_buf[2:4]
                nmea_track = str(datastorage['gps_track'])
                gps_speed_kn = datastorage['gps_speed_ms'] * 1.943844
                nmea_lon, lonneg = out.decdeg2dms(datastorage['gps_long'])
                nmea_lat, latneg = out.decdeg2dms(datastorage['gps_lat'])
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
    #  to be implemented            nmea_GSA = pynmea2.GSA('GP', 'GSA', ('A', '3', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '1.0', '1.0', '1.0'))
                crlf = "\r\n"
                print(nmea_GGA)
                nmea_GGA2 = str(nmea_GGA)
                nmea_RMC2 = str(nmea_RMC)
                sock.sendto(str.encode(nmea_GGA2), (c.UDP_IP, c.UDP_PORT))  # Send
                sock.sendto(str.encode(crlf), (c.UDP_IP, c.UDP_PORT))
                if nmea_track != 'nan':
                    sock.sendto(str.encode(nmea_RMC2), (c.UDP_IP, c.UDP_PORT))
                    sock.sendto(str.encode(crlf), (c.UDP_IP, c.UDP_PORT))

        #        sock.sendto(bytes(nmea_GSA), (UDP_IP, UDP_PORT))
        #        sock.sendto(bytes(crlf), (UDP_IP, UDP_PORT))
                if c.debug:
                    print('Data send to UDP')

                sleep(c.nmea_refresh_speed)
                nmea_dog.resettimeout(2)
                if watchdog_Thread_kill_register[0] == 1:
                    print("The Watchdog was triggered and killed the NMEA out thread")
                    now = datetime.datetime.now()
                    logging.critical(now.strftime("%Y-%m-%d %H:%M:%S") + "The Watchdog was triggered and killed the NMEA out thread")
                    break
                nmea_dog.resettimeout(4)

    def decdeg2dms(self, dd):
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
        strminutes = out.removepoint(minutes)
        strdegrees = out.removepoint(degrees)
        result = strdegrees[0:2] + strminutes[0:2] + '.' + strminutes[2:8]
        return (result, negative)

    def removepoint(self, val):
        val = str(val)
        val_length = len(val) - 1
        for i in range(1, val_length):
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


def starthandler(*args):
    patch_threading_excepthook()
    global c, out, datastorage, gps_sensor_alive, nmea_out_alive, nmea_dog, watchdog_Thread_kill_register
    watchdog_Thread_kill_register = [0, 0, 0, 0, 0, 0]
    c = configuration()  # Laden der Configuration Klasse in c
    out = nmea_out()     # Laden der nmea_out Klasse in out
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
    }
    sys.excepthook = handle_unhandled
    try:
        print("NMEA out Thread started")
        nmea_dog = watchdog()
        dog = threading.Thread(target=nmea_dog.watch(), args=(1))
        dog.daemon = True
        dog.start()
    except:
        print("Unhandled exception:", sys.exc_info()[0])
        raise

    try:
        if c.gps_source == 'GPS_SENSOR':  # GPS Empfaenger verbungden
            global gpsp
            gpsp = GpsPoller()  # create the thread
            gpsp.daemon = True
            gpsp.start()  # start it up
            Y = threading.Thread(target=out.start_gps_sensor2, args=(0,))
            Y.daemon = True
            Y.start()
        else:  # GPS Daten vom Flamr werden verwendet
            start_flarm_gps()
    except:
        print("Unhandled exception:", sys.exc_info()[0])
        raise

    try:
        if c.influx_logging == '1':
            x = threading.Thread(target=out.start_influx_gps_logging, args=(0,))
            x.daemon = True
            x.start()
            print(c.nmea_out_enabled)
            print("InfluX Thread Started")
    except:
        print("Unhandled exception:", sys.exc_info()[0])
        raise

    try:
        if c.nmea_out_enabled == '1':
            z = threading.Thread(target=out.nmea_out, args=(1,))
            z.daemon = True
            z.start()
    except:
        print("Unhandled exception:", sys.exc_info()[0])
        raise

#    while True:
#        sleep(1)
    print('The End')
    print("Unhandled exception:", sys.exc_info()[0])
#    raise


if __name__ == '__main__':
#    while True:
    starthandler()
    print("This is te real End!")
