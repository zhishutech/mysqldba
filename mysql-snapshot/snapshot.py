# -*- coding: utf-8 -*-#

# -------------------------------------------------------------------------------
# Name:         snapshot
# Description:
# Author:       xucl
# Date:         2019-04-17
# -------------------------------------------------------------------------------

from utils import *
from db_pool import DBAction
from threading import Lock


class Snapshot(object):
    def __init__(self, connection_settings, interval=None, conditions=None, storedir=None):
        if not conditions:
            raise ValueError('Lack of parameter: conditions')
        if not storedir:
            raise ValueError('Lack of parameter: storedir')
        self.conn_setting = connection_settings
        if not interval:
            self.interval = 10
        else:
            self.interval = interval
        self.conditions = conditions
        self.stordir = storedir

    def run(self):
        condition_dict = eval(self.conditions)

        while True:
            lock = Lock()
            global dbaction
            dbaction = DBAction(self.conn_setting)
            status_dict1 = get_mysql_status(dbaction)
            sys_dict1 = get_sys_status()
            slow_log, error_log = get_log_dir(dbaction)
            slave_status_dict = get_slave_status(dbaction)

            time.sleep(1)

            status_dict2 = get_mysql_status(dbaction)
            sys_dict2 = get_sys_status()

            origin_status_list = ['Threads_connected', 'Threads_running', 'Innodb_row_lock_current_waits']
            origin_sys_status_list = ['cpu_user', 'cpu_sys', 'cpu_iowait']
            diff_status_list = ['Slow_queries', 'Innodb_buffer_pool_wait_free']
            diff_sys_status = ['sys_iops']

            origin_status_dict = get_origin_status(status_dict1, origin_status_list)
            origin_status_sys_dict = get_origin_sys_status(sys_dict1, origin_sys_status_list)
            diff_status_dict = get_diff_status(status_dict1, status_dict2, diff_status_list)
            diff_sys_status = get_sys_diff_status(sys_dict1, sys_dict2, diff_sys_status)

            check_dict = dict(origin_status_dict, **diff_status_dict, **origin_status_sys_dict, **diff_sys_status, **slave_status_dict)

            collect_flag = check_conditions(check_dict, condition_dict)

            time_now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
            filedir = create_unique_dir(self.stordir, time_now)
            if collect_flag:
                lock.acquire()
                thread_objs = []
                mysql_func_list = [mysql_variables, mysql_status, mysql_innodb_status, mysql_slave_status, mysql_processlist, mysql_transactions, mysql_lock_info]
                sys_func_list = [mysql_error_log, mysql_slow_log, system_message, system_dmesg, system_top, system_iostat, system_mpstat, system_tcpdump, system_mem_info,
                                 system_interrupts, system_ps, system_netstat, system_vmstat]
                sys_arg_list = [slow_log, error_log, '/var/log/messages', '/var/log/dmesg', '', '', '', '', '', '', '', '', '']
                for func in mysql_func_list:
                    dbaction = DBAction(self.conn_setting)
                    t = do_in_thread(func, dbaction, filedir)
                    thread_objs.append(t)

                for index, func in enumerate(sys_func_list):
                    if sys_arg_list[index]:
                        t = do_in_thread(func, sys_arg_list[index], filedir)
                    else:
                        t = do_in_thread(func, filedir)
                    thread_objs.append(t)

                for thread_obj in thread_objs:
                    thread_obj.join()

            lock.release()

            time.sleep(self.interval)


if __name__ == '__main__':
    args = command_line_args(sys.argv[1:])
    conn_setting = {'host': args.host, 'port': args.port, 'user': args.user, 'password': args.password, 'charset': 'utf8'}
    snapshot = Snapshot(connection_settings=conn_setting, interval=args.interval, conditions=args.conditions,
                        storedir=args.storedir)
    snapshot.run()
