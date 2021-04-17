#!/usr/bin/env python3
import subprocess 
from datetime import datetime, timedelta
import os
import logging
import time
import psutil
import requests

# log filepath
filepath = '/var/log/PyLight/'

# hostname of device
hostname = "192.168.0.41"

# get sunrise and sunset times
r = requests.get(url='https://api.sunrise-sunset.org/json?lat=51.3406321&lng=12.3747329')
sunrise = r.json()['results']['sunrise'][:-3]
sunset = r.json()['results']['sunset'][:-3]

# light on timestamp for a weekday
poweron = '06:00:00'
# power on timestamp for a weekend
poweronweekend = '07:00:00'
# switch light mode timestamp
# time synced with home assistant
#switchtime = '19:00:00'
switchtime = datetime.strftime(datetime.strptime(sunset, "%H:%M:%S") + timedelta(hours=14, minutes=3), "%H:%M:%S")
switchsunset = datetime.strftime(datetime.strptime(sunrise, "%H:%M:%S") + timedelta(hours=2, minutes=0), "%H:%M:%S")

# check if sunrise is before poweron timestamp
if switchtime < poweron:
    switchtime = poweron

# power off timestamp
poweroff = '22:00:00'

def currenttime():
    return (datetime.now().time()).strftime("%H:%M:%S")

def ping(host):
    param = '-c'
    command = ['ping', param, '3', host]
    return subprocess.call(command, stdout=subprocess.PIPE) == 0

def weekday(arg):
    switch = {
            0: "Montag",
            1: "Dienstag",
            2: "Mittwoch",
            3: "Donnerstag",
            4: "Freitag",
            5: "Samstag",
            6: "Sonntag",
            }
    return switch.get(arg, "Ungültiger Tag")

def month(arg):
    switch = {
            1: "Januar",
            2: "Februar",
            3: "Maerz",
            4: "April",
            5: "Mai",
            6: "Juni",
            7: "Juli",
            8: "August",
            9: "September",
            10: "Oktober",
            11: "November",
            12: "Dezember"
            }
    return switch.get(arg, "Ungültiger Monat")

# irsend sometimes hangs up and needs to be killed
def kill_process(name):
    listOfProcessObjects = []
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name'])
            if name.lower() in pinfo['name'].lower() :
                logging.debug(currenttime() + ': ' + 'Killing process irsend!')
                listOfProcessObjects.append(pinfo['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) :
            passi
    for pid in listOfProcessObjects:
        os.kill(pid, 9)

if os.path.isfile(filepath + 'debug.log'):
    filedateday = (datetime.fromtimestamp(os.stat(filepath + 'debug.log').st_mtime)).strftime("%d")
    today = (datetime.now()).strftime('%d')
    currentmonth = month(int((datetime.now()).strftime('%-m')))
    currentyear = (datetime.now()).strftime('%Y')
    if filedateday < today:
        if not os.path.isdir(filepath + currentyear):
            os.system('sudo mkdir ' + filepath + currentyear)
            os.system('sudo chown pi:pi ' + filepath + currentyear)
        if not os.path.isdir(filepath + currentyear + '/' + currentmonth):
            os.system('sudo mkdir ' + filepath + currentyear + '/' + currentmonth)
            os.system('sudo chown pi:pi ' + filepath + currentyear + '/' + currentmonth)
        os.system('sudo mv ' + filepath + 'debug.log ' + filepath + currentyear + '/' + currentmonth + '/' + (datetime.now().date()).strftime("%Y_%d_%m") + '.old')
        os.system('sudo touch ' + filepath + 'debug.log')
        os.system('sudo chown pi:pi ' + filepath + 'debug.log')
else:
    os.system('sudo touch ' + filepath + 'debug.log')
    os.system('sudo chown pi:pi ' + filepath + 'debug.log')

logging.basicConfig(filename=filepath + 'debug.log', level=logging.DEBUG)

time = currenttime()
# weekday: 0 = monday, 6 = sunday
day = datetime.today().weekday()

if os.stat(filepath + 'debug.log').st_size == 0:
    logging.info(currenttime() + ': ' + 'Settings:')
    logging.info(currenttime() + ': ' + 'Hostname: ' + hostname)
    logging.info(currenttime() + ': ' + 'Tag: ' + weekday(day))
    logging.info(currenttime() + ': ' + 'Power on time (weekday): ' + poweron)
    logging.info(currenttime() + ': ' + 'Power on time (weekend): ' + poweronweekend)
    logging.info(currenttime() + ': ' + 'Sunrise: ' + switchsunset)
    logging.info(currenttime() + ': ' + 'Sunset: ' + switchtime)
    logging.info(currenttime() + ': ' + 'Power off time: ' + poweroff)

phoneping = ping(hostname)

if (phoneping):
    
    logging.debug(currenttime() + ': ' + hostname + " verbunden!")
    # Weekend Timer
    if day in [5, 6]:
        if time >= poweronweekend and time < switchsunset:
            logging.debug(currenttime() + ': ' + 'Execute: Power on Weekend [0]')
            os.system("timeout 2 irsend send_once light KEY_POWER")
            kill_process("irsend")
            logging.debug(currenttime() + ': ' + 'Execute: Wechsel zu blau [0]')
            os.system("timeout 1 irsend send_once light KEY_F8")
            if os.path.isfile('/home/pi/cronjobs/colorswitch'):
                logging.debug(currenttime() + ': ' + 'Lösche colorswitch file [0]')
                os.system("sudo rm /home/pi/cronjobs/colorswitch")
            logging.debug(currenttime() + ': ' + 'End [0]')
        elif time >= switchsunset and time < switchtime:
            logging.debug(currenttime() + ': ' + 'Execute: Power on Weekend [1]')
            os.system("timeout 2 irsend send_once light KEY_POWER")
            if not os.path.isfile('/home/pi/cronjobs/colorswitch'):
                kill_process('irsend')
                logging.debug(currenttime() + ': ' + 'Execute: Wechsel zu Farbverlauf [1]')
                os.system("timeout 1 irsend send_once light KEY_FN_F2")
                logging.debug(currenttime() + ': ' + 'Execute: colorswitch file wird erstellt [1]')
                os.system("sudo touch /home/pi/cronjobs/colorswitch")
            logging.debug(currenttime() + ': ' + 'End [1]')
        elif time >= switchtime and time < poweroff:
            logging.debug(currenttime() + ': ' + 'Execute: Power on Weekend [2]')
            os.system("timeout 2 irsend send_once light KEY_POWER")
            kill_process("irsend")
            logging.debug(currenttime() + ': ' + 'Execute: Wechsel zu blau [2]')
            os.system("timeout 1 irsend send_once light KEY_F8")
            if os.path.isfile('/home/pi/cronjobs/colorswitch'):
                logging.debug(currenttime() + ': ' + 'Lösche colorswitch file [2]')
                os.system("sudo rm /home/pi/cronjobs/colorswitch")
            logging.debug(currenttime() + ': ' + 'End [2]')
        else:
            logging.debug(currenttime() + ': ' + 'Power off [3]')
            os.system("timeout 1 irsend send_once light KEY_STOP")
            if os.path.isfile('/home/pi/cronjobs/colorswitch'):
                logging.debug(currenttime() + ': ' + 'Lösche colorswitch file [3]')
                os.system("sudo rm /home/pi/cronjobs/colorswitch")
            logging.debug(currenttime() + ': ' + 'End [3]')
    # Weekday Timer
    else:
        if time >= poweron and time < switchsunset:
            logging.debug(currenttime() + ': ' + 'Execute: Power On Weekday [00]')
            os.system("timeout 2 irsend send_once light KEY_POWER")
            kill_process("irsend")
            logging.debug(currenttime() + ': ' + 'Execute: Wechsel zu blau [00]')
            os.system("timeout 1 irsend send_once light KEY_F8")
            if os.path.isfile('/home/pi/cronjobs/colorswitch'):
                logging.debug(currenttime() + ': ' + 'Lösche colorswitch file [00]')
                os.system("sudo rm /home/pi/cronjobs/colorswitch")
            logging.debug(currenttime() + ': ' + 'End [00]')
        elif time >= switchsunset and time < switchtime:
            logging.debug(currenttime() + ': ' + 'Execute: Power On Weekday [4]')
            os.system("timeout 2 irsend send_once light KEY_POWER")
            if not os.path.isfile('/home/pi/cronjobs/colorswitch'):
                kill_process("irsend")
                logging.debug(currenttime() + ': ' + 'Execute: Wechsel zu Farbverlauf [4]')
                os.system("timeout 2 irsend send_once light KEY_FN_F2")
                logging.debug(currenttime() + ': ' + 'Execute: colorswitch file wird erstellt [4]')
                os.system("touch /home/pi/cronjobs/colorswitch")
            logging.debug(currenttime() + ': ' + 'End [4]')
        elif time >= switchtime and time < poweroff:
            logging.debug(currenttime() + ': ' + 'Execute: Power On Weekday [5]')
            os.system("timeout 2 irsend send_once light KEY_POWER")
            kill_process("irsend")
            logging.debug(currenttime() + ': ' + 'Execute: Wechsel zu blau [5]')
            os.system("timeout 1 irsend send_once light KEY_F8")
            if os.path.isfile('/home/pi/cronjobs/colorswitch'):
                logging.debug(currenttime() + ': ' + 'Lösche colorswitch file [5]')
                os.system("sudo rm /home/pi/cronjobs/colorswitch")
            logging.debug(currenttime() + ': ' + 'End [5]')
        else:
            logging.debug(currenttime() + ': ' + 'Execute: Power Off [6]')
            os.system("timeout 1 irsend send_once light KEY_STOP")
            if os.path.isfile('/home/pi/cronjobs/colorswitch'):
                logging.debug(currenttime() + ': ' + 'Lösche colorswitch file [6]')
                os.system("sudo rm /home/pi/cronjobs/colorswitch")
            logging.debug(currenttime() + ': ' + 'End [6]')
else:
    logging.debug(currenttime() + ': ' + hostname + ' nicht verbunden! [7]')
    logging.debug(currenttime() + ': ' + 'Execute: Power Off [7]')
    os.system("timeout 1 irsend send_once light KEY_STOP")
    if os.path.isfile('/home/pi/cronjobs/colorswitch'):
        logging.debug(currenttime() + ': ' + 'Lösche colorswitch file [7]')
        os.system("sudo rm /home/pi/cronjobs/colorswitch")
    logging.debug(currenttime() + ': ' + 'End [7]')
