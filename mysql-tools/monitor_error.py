# -*- coding: utf-8 -*-#

# -------------------------------------------------------------------------------
# Name:         monitor_error
# Description:
# Author:       xucl
# Date:         2019-03-28
# -------------------------------------------------------------------------------

import datetime
import json
import configparser
import os

# basic settings
errorlog = "data/error.log"
message = "/var/log/messages"
dmesg = "/var/log/dmesg"
dbid = 1

def get_error_text(error_last_pos):
    f = open(errorlog, "r")
    error_pos = os.path.getsize(errorlog)
    offset_size = int(error_pos) - int(error_last_pos)
    f.seek(int(error_last_pos), 0)
    errortext = f.read(offset_size).strip('\n')
    f.close()
    return errortext, error_pos


def get_message_text(message_last_pos):
    f = open(message, "r")
    meg_pos = os.path.getsize(message)
    offset_size = int(meg_pos) - int(message_last_pos)
    f.seek(int(message_last_pos), 0)
    megtext = f.read(offset_size).strip('\n')
    f.close()
    return megtext, meg_pos


def get_dmesg_text(dmesg_last_pos):
    f = open(dmesg, "r")
    dmesg_pos = os.path.getsize(dmesg)
    offset_size = int(dmesg_pos) - int(dmesg_last_pos)
    f.seek(int(dmesg_last_pos), 0)
    dmesgtext = f.read(offset_size).strip('\n')
    f.close()
    return dmesgtext, dmesg_pos

def update_position(cf, error_pos, meg_pos, dmesg_pos):
    cf.set('error', 'position', str(error_pos))
    cf.set('message', 'position', str(meg_pos))
    cf.set('dmesg', 'position', str(dmesg_pos))
    cf.write(open('last_position', 'w'))

def generate_data(errtext, mestext, dmsgtext):
    monitor_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    errordata = {}
    errordata['dbid'] = dbid
    errordata['time'] = monitor_time
    errordata['error'] = errtext
    errordata['meg'] = mestext
    errordata['dmsg'] = dmsgtext
    errordata = json.dumps(errordata)
    return errordata


if __name__ == "__main__":
    if not os.path.exists('last_position'):
        f = open('last_position', "w")
        init_pos = """
        [error]
		position = 0

		[message]
		position = 0

		[dmesg]
		position = 0
        """
        f.write(init_pos)
        f.close()
    cf = configparser.ConfigParser()
    cf.read('last_position')

    error_last_pos = cf.get('error', 'position')
    message_last_pos = cf.get('message', 'position')
    dmesg_last_pos = cf.get('dmesg', 'position')    
    
    errtext, error_pos = get_error_text(error_last_pos)
    mestext, meg_pos = get_message_text(message_last_pos)
    dmsgtext, dmesg_pos = get_dmesg_text(dmesg_last_pos)
    update_position(cf, error_pos, meg_pos, dmesg_pos)
    errordata = generate_data(errtext, mestext, dmsgtext)
    print(errordata)
