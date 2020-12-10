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

#日至保留时长，默认7天
expire_logs_days=7

class Snapshot(object):
    def __init__(self, connection_settings, interval=None, conditions=None, storedir=None):
        global logfile
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
        print("")
        print("starting mysql snapshot")
        print("loging into %s"%logfile)
        print("snapshot file stored in %s"%storedir)

    def run(self):
        condition_dict = eval(self.conditions)

        while True:
            lock = Lock()
            global dbaction

            # 第一次获取MySQL&系统状态
            dbaction = DBAction(self.conn_setting)
            status_dict1 = get_mysql_status(dbaction)
            slow_log, error_log = get_log_dir(dbaction)
            slave_status_dict = get_slave_status(dbaction)

            sys_dict1 = get_sys_status()

            time.sleep(1)

            # 1秒钟后再次获取MySQL状态
            status_dict2 = get_mysql_status(dbaction)

            # 以下指标只需根据原始值判断是否达到触发条件
            origin_status_list = ['Threads_connected', 'Threads_running', 'Innodb_row_lock_current_waits']
            # 以下指标需要根据两次差值进行判断是否达到触发条件
            diff_status_list = ['Slow_queries', 'Innodb_buffer_pool_wait_free']

            # 构造数组
            origin_status_dict = get_origin_status( status_dict1, origin_status_list)

            # 计算两次MySQL状态中的差值
            diff_status_dict = get_diff_status( status_dict1, status_dict2, diff_status_list)

            # 传入要检查的状态指标(MySQL、系统、slave status等)
            check_dict = dict(origin_status_dict, ** diff_status_dict, ** sys_dict1, **slave_status_dict)

            # 检查哪些条件被触发
            collect_flag = check_conditions(check_dict, condition_dict)

            time_now = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')

            if collect_flag:
                filedir = create_unique_dir(self.stordir, time_now)
                lock.acquire()
                thread_objs = []

                # 采集MySQL状态函数&传入参数列表
                mysql_func_list = [mysql_variables, mysql_status, mysql_innodb_status,
                                   mysql_slave_status, mysql_processlist, mysql_transactions, mysql_lock_info]

                #采集系统状态函数&传入参数列表
                """
                sys_func_list = [mysql_slow_log, mysql_error_log, system_message, system_dmesg, system_top, system_iostat, system_mpstat,
                        system_mem_info, system_interrupts, system_ps, system_netstat, system_vmstat, system_tcpdump]
                sys_arg_list = [slow_log, error_log, '/var/log/messages', '/var/log/dmesg', '', self.interval, self.interval,
                        '', '', '', '', self.interval, self.conn_setting['port']]
                """
                sys_func_list = [mysql_slow_log, mysql_error_log, system_message, system_dmesg, system_top, system_mem_info,
                         system_interrupts, system_ps, system_netstat, system_iostat, system_mpstat, system_vmstat]
                sys_arg_list = [slow_log, error_log, '/var/log/messages', '/var/log/dmesg', '', '', '', '', '', '', '', '']

                #循环执行
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

                #清除过期日志，如果不放心可注释掉改成手动清理
                self.clear_expire_logs()

                lock.release()

            # 周期休眠
            time.sleep(self.interval)


    # 清除过期日志
    def clear_expire_logs(self):
        global expire_logs_days
        print("clear logs befor %s days" % expire_logs_days)
        cmd = "cd %s; find ./ -type d -mtime +%s | xargs rm -fr" % (self.stordir, expire_logs_days)
        pro = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        pro.terminate()

if __name__ == '__main__':
    args = command_line_args(sys.argv[1:])
    conn_setting = {'host': args.host, 'port': args.port,
                    'user': args.user, 'password': args.password, 'charset': 'utf8'}
    snapshot = Snapshot(connection_settings=conn_setting, interval=args.interval, conditions=args.conditions,
                        storedir=args.storedir)
    snapshot.run()
