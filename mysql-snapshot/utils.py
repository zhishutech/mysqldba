# coding:gbk

import time
import threading
import getpass
import argparse
import sys
import os
import datetime
import subprocess
import psutil
from collections import Counter

class FuncThread(threading.Thread):

    def __init__(self, func, *args, **kwargs):
        super(FuncThread, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.finished = False
        self.result = None

    def run(self):
        self.result = self.func(*self.args, **self.kwargs)
        self.finished = True

    def is_finished(self):
        return self.finished

    def get_result(self):
        return self.result


def do_in_thread(func, *args, **kwargs):
    ft = FuncThread(func, *args, **kwargs)
    ft.start()
    return ft


def handle_timeout(func, timeout, *args, **kwargs):
    interval = 1

    ret = None
    while timeout > 0:
        begin_time = time.time()
        ret = func(*args, **kwargs)
        if ret:
            break
        time.sleep(interval)
        timeout -= time.time() - begin_time

    return ret


def create_unique_dir(dirname, snaptime):
    result_dir = dirname + '/' + snaptime
    # if filedir is not exist than create
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)
    return result_dir


def parse_args():
    """parse args for snapshot"""

    parser = argparse.ArgumentParser(description='Snapshot your Database and Server', add_help=False)
    connect_setting = parser.add_argument_group('connect setting')
    connect_setting.add_argument('-h', '--host', dest='host', type=str,
                                 help='Host the MySQL database server located', default='127.0.0.1')
    connect_setting.add_argument('-u', '--user', dest='user', type=str,
                                 help='MySQL Username to log in as', default='root')
    connect_setting.add_argument('-p', '--password', dest='password', type=str, nargs='*',
                                 help='MySQL Password to use', default='')
    connect_setting.add_argument('-P', '--port', dest='port', type=int,
                                 help='MySQL port to use', default=3306)

    parser.add_argument('--interval', dest='interval', type=int, default=10,
                        help="interval time to check snapshot condition")
    parser.add_argument('--help', dest='help', action='store_true', help='help information', default=False)
    parser.add_argument('--conditions', dest='conditions', default=False,
                        help="Specify trigger conditions")
    parser.add_argument('--storedir', dest='storedir', default=False,
                        help="Specify datadir to store snapshot files")
    return parser


def command_line_args(args):
    need_print_help = False if args else True
    parser = parse_args()
    args = parser.parse_args(args)
    if args.help or need_print_help:
        parser.print_help()
        sys.exit(1)
    if not args.conditions:
        raise ValueError('Lack of parameter: conditions')
    if not args.storedir:
        raise ValueError('Lack of parameter: storedir')
    if not args.password:
        args.password = getpass.getpass()
    else:
        args.password = args.password[0]
    return args


def dt2str(data):
    if isinstance(data, datetime.datetime):
        return data.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return str(data)


def mysql_variables(dbaction, filedir):
    filename = filedir + '/' + 'variables'
    sql = 'show global variables'
    var_obj, desc = dbaction.data_inquiry(sql)
    with open(filename, 'w') as f:
        for item in var_obj:
            var_string = item[0] + ':' + item[1] + '\n'
            f.write(var_string)


def mysql_status(dbaction, filedir):
    filename = filedir + '/' + 'status'
    sql = 'show global status'
    status_obj, desc = dbaction.data_inquiry(sql)
    with open(filename, 'w') as f:
        for item in status_obj:
            status_string = item[0] + ':' + item[1] + '\n'
            f.write(status_string)


def mysql_innodb_status(dbaction, filedir):
    filename = filedir + '/' + 'innodb_status'
    sql = 'show engine innodb status'
    status_obj, desc = dbaction.data_inquiry(sql)
    status_list = str(status_obj[0]).split('\\n')[1:-1]
    with open(filename, 'w') as f:
        for item in status_list:
            status_string = item + '\n'
            f.write(status_string)


def mysql_slave_status(dbaction, filedir):
    filename = filedir + '/' + 'slave_status'
    sql = 'show slave status'
    status_obj, desc = dbaction.data_inquiry(sql)
    desc_list = []
    if status_obj:
        with open(filename, 'w') as f:
            for item in desc:
                desc_list.append(item[0])
            for index, item in enumerate(status_obj[0]):
                row_string = desc_list[index] + ':' + str(item) + '\n'
                f.write(row_string)


def mysql_processlist(dbaction, filedir):
    filename = filedir + '/' + 'processlist'
    sql = 'show full processlist'
    processlist_obj, desc = dbaction.data_inquiry(sql)
    with open(filename, 'w') as f:
        for item in desc:
            desc_string = item[0] + '    '
            f.write(desc_string)
        f.write('\n')
        for item in processlist_obj:
            processlist_string = map(lambda x: str(x) + '     ', item)
            f.write(''.join(processlist_string) + '\n')


def mysql_transactions(dbaction, filedir):
    filename = filedir + '/' + 'transactions'
    desc_list = []
    sql = 'select * from information_schema.innodb_trx'
    trans_obj, desc = dbaction.data_inquiry(sql)
    if trans_obj:
        with open(filename, 'w') as f:
            for item in desc:
                desc_list.append(item[0])
            for index, trans in enumerate(trans_obj):
                row_string = '**************   rows:  %s **************** \n' % str(index)
                f.write(row_string)
                for index, item in enumerate(trans):
                    trans_string = desc_list[index] + ':' + dt2str(item) + '\n'
                    f.write(trans_string)


def mysql_lock_info(dbaction, filedir):
    filename = filedir + '/' + 'innodb_locks'
    desc_list = []
    sql = 'select * from sys.innodb_lock_waits'
    lock_obj, desc = dbaction.data_inquiry(sql)
    if lock_obj:
        with open(filename, 'w') as f:
            for item in desc:
                desc_list.append(item[0])
            for index, trans in enumerate(lock_obj):
                row_string = '**************   rows:  %s **************** \n' % str(index)
                f.write(row_string)
                for index, item in enumerate(trans):
                    trans_string = desc_list[index] + ':' + dt2str(item) + '\n'
                    f.write(trans_string)


def mysql_error_log(errorlog, filedir):
    error_file = '/%s/errorlog' % filedir
    start_pos = os.path.getsize(errorlog)
    time.sleep(10)
    stop_pos = os.path.getsize(errorlog)
    offset_size = int(stop_pos) - int(start_pos)
    if offset_size:
        f = open(errorlog, "r")
        f.seek(int(start_pos), 0)
        error_text = f.read(offset_size)
        f.close()
        fp = open(error_file, "w+")
        error_list = error_text.strip('\n').split('\n')
        for line in error_list:
            line = line + '\n'
            fp.write(line)
        fp.close()


def mysql_slow_log(slowlog, filedir):
    slow_file = '/%s/slowlog' % filedir
    start_pos = os.path.getsize(slowlog)
    time.sleep(10)
    stop_pos = os.path.getsize(slowlog)
    offset_size = int(stop_pos) - int(start_pos)
    if offset_size:
        f = open(slowlog, "r")
        f.seek(int(start_pos), 0)
        slow_text = f.read(offset_size)
        f.close()
        fp = open(slow_file, "w+")
        slow_list = slow_text.strip('\n').split('\n')
        for line in slow_list:
            line = line + '\n'
            fp.write(line)
        fp.close()


def system_disk_space(filedir):
    cmd = 'df -k >> /%s/disk-space' % filedir
    pro = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    pro.terminate()


def system_message(message, filedir):
    message_file = '/%s/message' % filedir
    start_pos = os.path.getsize(message)
    time.sleep(10)
    stop_pos = os.path.getsize(message)
    offset_size = int(stop_pos) - int(start_pos)
    if offset_size:
        f = open(message, "r")
        f.seek(int(start_pos), 0)
        message_text = f.read(offset_size)
        f.close()
        fp = open(message_file, "w+")
        message_list = message_text.strip('\n').split('\n')
        for line in message_list:
            line = line + '\n'
            fp.write(line)
        fp.close()


def system_dmesg(dmesg, filedir):
    dmesg_file = '/%s/dmesg' % filedir
    start_pos = os.path.getsize(dmesg)
    time.sleep(10)
    stop_pos = os.path.getsize(dmesg)
    offset_size = int(stop_pos) - int(start_pos)
    if offset_size:
        f = open(dmesg, "r")
        f.seek(int(start_pos), 0)
        dmesg_text = f.read(offset_size)
        f.close()
        fp = open(dmesg_file, "w+")
        dmesg_list = dmesg_text.strip('\n').split('\n')
        for line in dmesg_list:
            line = line + '\n'
            fp.write(line)
        fp.close()


def system_top(filedir):
    cmd = 'top -bn5 >> /%s/top' % filedir
    pro = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if pro.poll() != None:
        ErrCode = "error"
    else:
        ErrCode = "success"
        time.sleep(10)
    pro.terminate()
    print(ErrCode)


def system_iostat(filedir):
    cmd = 'iostat -m -x 1 >> /%s/iostat' % filedir
    pro = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if pro.poll() != None:
        ErrCode = "error"
    else:
        ErrCode = "success"
        time.sleep(10)
    pro.terminate()
    print(ErrCode)


def system_mpstat(filedir):
    cmd = 'mpstat -I SUM -P ALL 1 >> /%s/mpstat' % filedir
    pro = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if pro.poll() != None:
        ErrCode = "error"
    else:
        ErrCode = "success"
        time.sleep(10)
    pro.terminate()
    print(ErrCode)


def system_tcpdump(filedir):
    cmd = 'tcpdump -i any -s 4096 -w /%s/tcpdump port 3306' % filedir
    pro = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if pro.poll() != None:
        ErrCode = "error"
    else:
        ErrCode = "success"
        time.sleep(10)
    pro.terminate()
    print(ErrCode)


def system_mem_info(filedir):
    cmd = 'cat /proc/meminfo >> %s/meminfo' % filedir
    pro = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    pro.terminate()


def system_interrupts(filedir):
    cmd = 'cat /proc/interrupts >> %s/interrupts' % filedir
    pro = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    pro.terminate()


def system_ps(filedir):
    cmd = 'ps -eaF >> %s/ps' % filedir
    pro = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    pro.terminate()


def system_netstat(filedir):
    cmd = 'netstat -antp >> %s/netstat' % filedir
    pro = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    pro.terminate()


def system_vmstat(filedir):
    cmd = 'vmstat 1 >> %s/vmstat' % filedir
    pro = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if pro.poll() != None:
        ErrCode = "error"
    else:
        ErrCode = "success"
        time.sleep(10)
    print(ErrCode)
    pro.terminate()


def check_conditions(check_dict, condition_dict):
    print(check_dict)
    print(condition_dict)
    result = dict(Counter(check_dict) - Counter(condition_dict))
    return result


def get_mysql_status(dbaction):
    status_dict = {}
    sql = 'show global status;'
    status_obj, desc = dbaction.data_inquiry(sql)
    for item in status_obj:
        status_dict[item[0]] = item[1]
    return status_dict


def get_origin_status(status_dict, origin_status_list):
    origin_status_dict = {}
    for item in origin_status_list:
        origin_status_dict[item] = int(status_dict[item])
    return origin_status_dict


def get_origin_sys_status(status_dict, origin_status_list):
    origin_status_dict = {}
    for item in origin_status_list:
        origin_status_dict[item] = float(status_dict[item])
    return origin_status_dict


def get_diff_status(status_dict1, status_dict2, diff_status_list):
    diff_status_dict = {}
    for item in diff_status_list:
        diff_status_dict[item] = int(status_dict2[item]) - int(status_dict1[item])
    return diff_status_dict


def get_sys_diff_status(status_dict1, status_dict2, diff_status_list):
    diff_status_dict = {}
    for item in diff_status_list:
        diff_status_dict[item] = float(status_dict2[item]) - float(status_dict1[item])
    return diff_status_dict

def get_sys_status():
    sys_status_dict = {}
    sys_status_dict['cpu_user'] = psutil.cpu_times_percent().user
    sys_status_dict['cpu_sys'] = psutil.cpu_times_percent().system
    sys_status_dict['cpu_iowait'] = psutil.cpu_times_percent().iowait
    sys_status_dict['sys_iops'] = psutil.disk_io_counters().read_count + psutil.disk_io_counters().write_count
    return sys_status_dict


def get_slave_status(dbaction):
    slave_status_dict = {}
    sql = 'show slave status'
    status_obj, desc = dbaction.data_inquiry(sql)
    if status_obj:
        if not status_obj[0][32]:
            sql_delay = 99999
        else:
            sql_delay = status_obj[0][32]
        slave_status_dict['sql_delay'] = sql_delay
    else:
        slave_status_dict['sql_delay'] = 0
    return slave_status_dict


def get_log_dir(dbaction):
    sql = 'show global variables'
    slow_log = ''
    error_log = ''
    var_obj, desc = dbaction.data_inquiry(sql)
    for item in var_obj:
        if item[0] == 'slow_query_log_file':
            slow_log = item[1]
        elif item[0] == 'log_error':
            error_log = item[1]
        else:
            continue
    return slow_log,error_log
