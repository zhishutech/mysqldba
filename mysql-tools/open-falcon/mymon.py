#! /bin/env python
# coding:gbk
# author:xucl
import configparser
import requests
import pymysql
import time, datetime
import json
import os

from mymon_utils import map_value, get_var_metric, get_sta_metric, get_statusdiff_metric, get_innodb_metric, get_slave_metric, get_other_metric, generate_metric


class DBUtil:
    def __init__(self, user=None, passwd=None, host=None, port=None, db=None, endpoint=None, tags=None):
        self.user = user
        self.passwd = passwd
        self.host = host
        self.port = port
        self.db = db
        self.endpoint = endpoint
        self.tags = tags
        self._conn = None
        self._cursor = None

    def __enter__(self):
        self._conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db)
        self._cursor = self._conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()
        self._conn = None

    def get_status(self):
        self._cursor.execute('show global status;')
        data_list = self._cursor.fetchall()
        data_dict = {}
        for item in data_list:
            data_dict[item[0]] = item[1]
        return data_dict

    def get_innodb_status(self):
        self._cursor.execute('show engine innodb status;')
        innodb_status = self._cursor.fetchall()
        innodb_status_format = str(innodb_status).split('\\n')
        return innodb_status_format
        
    def get_slave_status(self):
        column_list = []
        data_dict = {}
        self._cursor.execute('show slave status;')
        data_list = self._cursor.fetchall()
        if data_list:
            data_list = list(data_list[0])
            for index, desc in enumerate(self._cursor.description):
                data_dict[desc[0]] = data_list[index]
        return data_dict

    def get_variables(self, variable_list):
        self._cursor.execute('show global variables;')
        data_list = self._cursor.fetchall()
        data_dict = {}
        for item in data_list:
            data_dict[item[0]] = item[1]
        metric_list = get_var_metric(self, variable_list, data_dict, ts)
        return metric_list

    def get_status_metric(self, status, data_dict, type):
        metric_list = get_sta_metric(self, status, data_dict, ts, type)
        return metric_list

    def get_custom_status(self, data_dict1, data_dict2):
        metric_list = get_statusdiff_metric(self, data_dict1, data_dict2, ts)
        return metric_list

    def get_custom_metrics(self, data_dict, innodb_status_format, slave_status_format):
        metrc_list = []
        start_time = int(time.time())
        self._cursor.execute("select benchmark(10000000,'select 1+1');")
        end_time = int(time.time())
        rt = end_time - start_time
        innodb_metric_list = get_innodb_metric(self, innodb_status_format, ts)
        slave_metric_list = get_slave_metric(self, slave_status_format, ts)
        othter_metric_list = get_other_metric(self, "reponsetime", rt, ts)
        alive_metrics = get_other_metric(self, "mysql_alive", 1, ts)
        metrc_list.extend(innodb_metric_list)
        metrc_list.extend(slave_metric_list)
        metrc_list.extend(othter_metric_list)
        metrc_list.extend(alive_metrics)
        return metrc_list

    def record_innodb_status(self, innodb_status_format):
        status_file = self.endpoint + '_' + datetime.datetime.now().strftime('%y%m%d') + '_innodb_status'
        innodb_status_format = innodb_status_format[1:-1]
        f = open(status_file, "a+")
        monitor_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        f.write(monitor_time + '\n')
        for item in innodb_status_format:
            f.write(item + '\n')
        f.close()
        
    def record_processlist(self):
        self._cursor.execute('select * from information_schema.processlist;')
        processlist = self._cursor.fetchall()
        processlist_file = self.endpoint + '_' + datetime.datetime.now().strftime('%y%m%d') + '_processlist'
        fp = open(processlist_file, "a+")
        monitor_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        fp.write(monitor_time + '\n')
        for item in processlist:
            fp.write(str(item) + '\n')
        fp.close()    
             

if __name__ == '__main__':

    cf = configparser.ConfigParser()
    cf.read('mymon.cnf')

    hostname = cf.get('mysql', 'HOST')
    port = cf.get('mysql', 'PORT')
    username = cf.get('mysql', 'USERNAME')
    password = cf.get('mysql', 'PASSWORD')
    endpoint = cf.get('mysql', 'ENDPOINT')
    tags = cf.get('mysql', 'TAGS')

    ts = int(time.time())
    payload = []
    try:
        with DBUtil(username, password, hostname, int(port), 'information_schema', endpoint, tags) as client:
            data_dict1 = client.get_status()
            innodb_status_format = client.get_innodb_status()
            slave_status_format = client.get_slave_status()
            time.sleep(1)
            data_dict2 = client.get_status()
            client.record_processlist()

            variables = ['read_only', 'super_read_only', 'innodb_buffer_pool_size', 'table_open_cache', 'table_definition_cache',
                         'innodb_flush_log_at_trx_commit', 'sync_binlog', 'max_connections', 'max_user_connections']
            gague_status = ['Uptime', 'Threads_connected', 'Threads_created', 'Threads_running','Innodb_row_lock_current_waits',
                            'Innodb_row_lock_time_avg', 'Open_files', 'Open_tables','Open_table_definitions', 'Max_used_connections']
            counter_status = ['Aborted_clients', 'Aborted_connects', 'Created_tmp_disk_tables', 'Created_tmp_files', 'Created_tmp_tables',
                              'Select_full_join', 'Select_full_range_join', 'Select_scan', 'Slow_queries', 'Table_locks_immediate',
                              'Table_locks_waited', 'Innodb_row_lock_time', 'Innodb_row_lock_waits', 'Bytes_received', 'Bytes_sent', 'Innodb_buffer_pool_wait_free',
                              'Innodb_log_waits', 'Opened_files', 'Opened_tables', 'Opened_table_definitions', 'Handler_read_key', 
                              'Handler_read_next', 'Handler_read_rnd','Handler_read_rnd_next', 'Sort_merge_passes', 'Binlog_cache_disk_use', 
                              'Com_select', 'Com_update', 'Com_insert', 'Com_delete', 'Com_commit', 'Com_rollback']
            var_metrics = client.get_variables(variables)
            guage_metrics = client.get_status_metric(gague_status, data_dict1, "GAUGE")
            counter_metrics = client.get_status_metric(counter_status, data_dict1, "COUNTER")
            custom_status = client.get_custom_status(data_dict1, data_dict2)
            custom_metrics = client.get_custom_metrics(data_dict1, innodb_status_format, slave_status_format)
            payload.extend(var_metrics)
            payload.extend(guage_metrics)
            payload.extend(counter_metrics)
            payload.extend(custom_status)
            payload.extend(custom_metrics)
            client.record_innodb_status(innodb_status_format)
            
    except:
        alive_metrics = generate_metric(endpoint, "mysql_alive", ts, 60, 0, "GAUGE", tags)
        payload.append(alive_metrics)

    r = requests.post("http://127.0.0.1:1988/v1/push", data=json.dumps())
    print(r.text)
