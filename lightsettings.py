#!/usr/bin/env python3
import subprocess 
from datetime import datetime
import os
import logging
import time

# log filepath
filepath = '/var/log/PyLight/'

# hostname of device
hostname = "OnePlus3T"

# light on timestamp for a weekday
poweron = '06:00:00'
# power on timestamp for a weekend
poweronweekend = '07:00:00'
# power off timestamp
poweroff = '22:00:00'
# switch light mode timestamp
switchtime = '19:00:00'

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

#time = (datetime.now().time()).strftime("%H:%M:%S")
time = currenttime()
# weekday: 0 = monday, 6 = sunday
day = datetime.today().weekday()

if os.stat(filepath + 'debug.log').st_size == 0:
    logging.info(currenttime() + ': ' + 'Settings:')
    logging.info(currenttime() + ': ' + 'Hostname: ' + hostname)
    logging.debug(currenttime() + ': ' + 'Tag: ' + weekday(day))
    logging.info(currenttime() + ': ' + 'Power on time (weekday): ' + poweron)
    logging.info(currenttime() + ': ' + 'Power on time (weekend): ' + poweronweekend)
    logging.info(currenttime() + ': ' + 'Switch mode time: ' + switchtime)
    logging.info(currenttime() + ': ' + 'Power off time: ' + poweroff)

phoneping = ping(hostname)

if (phoneping):
    
    logging.debug(currenttime() + ': ' + hostname + " verbunden!")
    # Weekend Timer
    if day in [5, 6]:
        if time >= poweronweekend and time < switchtime:
            logging.debug(currenttime() + ': ' + 'Execute: Power on Weekend')
            os.system("timeout 3 irsend send_once light KEY_POWER")
            if not os.path.isfile('/home/pi/cronjobs/colorswitch'):
                time.sleep(3)
                logging.debug(currenttime() + ': ' + 'Execute: Wechsel zu Farbverlauf')
                os.system("timeout 3 irsend send_once light KEY_FN_F2")
                logging.debug(currenttime() + ': ' + 'Execute: colorswitch file wird erstellt')
                os.system("sudo touch /home/pi/cronjobs/colorswitch")
        elif time >= switchtime and time < poweroff:
            logging.debug(currenttime() + ': ' + 'Execute: Power on Weekend')
            os.system("timeout 3 irsend send_once light KEY_POWER")
            logging.debug(currenttime() + ': ' + 'Execute: Wechsel zu blau')
            os.system("timeout 3 irsend send_once light KEY_F8")
            if os.path.isfile('/home/pi/cronjobs/colorswitch'):
                logging.debug(currenttime() + ': ' + 'Lösche colorswitch file')
                os.system("sudo rm /home/pi/cronjobs/colorswitch")
        else:
            logging.debug(currenttime() + ': ' + 'Power off')
            os.system("timeout 3 irsend send_once light KEY_STOP")
            if os.path.isfile('/home/pi/cronjobs/colorswitch'):
                logging.debug(currenttime() + ': ' + 'Lösche colorswitch file')
                os.system("sudo rm /home/pi/cronjobs/colorswitch")
    # Weekday Timer
    else:
        if time >= poweron and time < switchtime:
            logging.debug(currenttime() + ': ' + 'Execute: Power On Weekday')
            os.system("timeout 3 irsend send_once light KEY_POWER")
            if not os.path.isfile('/home/pi/cronjobs/colorswitch'):
                logging.debug(currenttime() + ': ' + 'Execute: Wechsel zu Farbverlauf')
                os.system("timeout 3 irsend send_once light KEY_FN_F2")
                logging.debug(currenttime() + ': ' + 'Execute: colorswitch file wird erstellt')
                os.system("touch /home/pi/cronjobs/colorswitch")
        elif time >= switchtime and time < poweroff:
            logging.debug(currenttime() + ': ' + 'Execute: Power On Weekday')
            os.system("timeout 3 irsend send_once light KEY_POWER")
            logging.debug(currenttime() + ': ' + 'Execute: Wechsel zu blau')
            os.system("timeout 3 irsend send_once light KEY_F8")
        else:
            logging.debug(currenttime() + ': ' + 'Execute: Power Off')
            os.system("timeout 3 irsend send_once light KEY_STOP")
            if os.path.isfile('/home/pi/cronjobs/colorswitch'):
                logging.debug(currenttime() + ': ' + 'Lösche colorswitch file')
                os.system("sudo rm /home/pi/cronjobs/colorswitch")
else:
    logging.debug(currenttime() + ': ' + hostname + ' nicht verbunden!')
    logging.debug(currenttime() + ': ' + 'Execute: Power Off')
    os.system("timeout 3 irsend send_once light KEY_STOP")
    if os.path.isfile('/home/pi/cronjobs/colorswitch'):
        logging.debug(currenttime() + ': ' + 'Lösche colorswitch file')
        os.system("sudo rm /home/pi/cronjobs/colorswitch")
