#!/usr/bin/env python
#coding=utf-8

import logging
import traceback
import pymysql
import warnings
from retry import retry
warnings.filterwarnings("ignore")

from DBUtils.PooledDB import PooledDB

db_pool_ins = None


class DBPool:
    def __init__(self, host=None, port=None, user=None, password=None):
        self.host = host
        self.host = port
        self.host = user
        self.host = password
        self.pool = PooledDB(creator=pymysql, mincached=30, maxcached=50, maxconnections=200, maxusage=0,
                             blocking=True, host=host, port=int(port), user=user, passwd=password,
                             db="information_schema", charset='utf8')      
    def get_connection(self):
        return self.pool.connection()


class DBAction:
    def __init__(self, conn_setting=None):
        host = conn_setting['host']
        port = conn_setting['port']
        user = conn_setting['user']
        password = conn_setting['password']
        global db_pool_ins
        if db_pool_ins is None:
            db_pool_ins = DBPool(host, port, user, password)
        self.conn = db_pool_ins.get_connection()
        self.cursor = self.conn.cursor()

    def close_database(self):
        self.cursor.close()
        self.conn.close()

    def data_operate(self, sql, params=()):
        """
        数据的插入，更新，删除
        """
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
            return True
        except:
            logging.error("sql is %s, params is %s error. %s" % (sql, params, traceback.format_exc()))
            self.conn.rollback()
            raise Exception

    def data_operate_count(self, sql, params=()):
        """
        数据的插入，更新，删除
        :return: 受影响的条数
        """
        count = self.cursor.execute(sql, params)
        self.conn.commit()
        return count

    @retry(delay=1)
    def data_inquiry(self, sql, params=()):
        """
        SELECT 操作
        """
        self.cursor.execute(sql, params)
        result = self.cursor.fetchall()
        description = self.cursor.description
        return result, description

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()
