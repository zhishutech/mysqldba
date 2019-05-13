# -*- coding: utf-8 -*-#

# -------------------------------------------------------------------------------
# Name:         snapshot
# Description:  
# Author:       xucl
# Date:         2019-04-17
# -------------------------------------------------------------------------------

from utils import *
from db_pool import DBAction

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
        dbaction = DBAction(conn_setting)
        while True:
            status_dict1 = get_mysql_status(dbaction)
            time.sleep(1)
            status_dict2 = get_mysql_status(dbaction)
            origin_status_list = ['Threads_connected', 'Threads_running', 'Innodb_row_lock_current_waits']
            diff_status_list = ['Slow_queries']

            origin_status_dict = get_origin_status(status_dict1, origin_status_list)
            diff_status_dict = get_diff_status(status_dict1, status_dict2, diff_status_list)

            check_dict = dict(origin_status_dict, **diff_status_dict)
            collect_flag = check_conditions(check_dict, condition_dict)

            time_now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
            filedir = create_unique_dir(self.stordir, time_now)
            if collect_flag:
                do_in_thread(mysql_variables, dbaction, filedir)
                do_in_thread(mysql_status, dbaction, filedir)
                do_in_thread(mysql_innodb_status, dbaction, filedir)
                do_in_thread(mysql_slave_status, dbaction, filedir)
                do_in_thread(mysql_processlist, dbaction, filedir)
                do_in_thread(mysql_transactions, dbaction, filedir)
                do_in_thread(mysql_lock_info, dbaction, filedir)
                do_in_thread(mysql_error_log, '/storage/single/mysql3306/data/error.log', filedir)
                do_in_thread(mysql_slow_log, '/storage/single/mysql3306/data/slow.log', filedir)
                do_in_thread(system_message, '/var/log/messages', filedir)
                do_in_thread(system_dmesg, '/var/log/dmesg', filedir)
                do_in_thread(system_top, filedir)
                do_in_thread(system_iostat, filedir)
                do_in_thread(system_mpstat, filedir)
                do_in_thread(system_tcpdump, filedir)
                do_in_thread(system_mem_info, filedir)
                do_in_thread(system_interrupts, filedir)
                do_in_thread(system_ps, filedir)
                do_in_thread(system_netstat, filedir)
                do_in_thread(system_vmstat, filedir)
            time.sleep(self.interval)


if __name__ == '__main__':
    args = command_line_args(sys.argv[1:])
    conn_setting = {'host': args.host, 'port': args.port, 'user': args.user, 'password': args.password, 'charset': 'utf8'}
    snapshot = Snapshot(connection_settings=conn_setting, interval=args.interval, conditions=args.conditions,
                        storedir=args.storedir)
    snapshot.run()
