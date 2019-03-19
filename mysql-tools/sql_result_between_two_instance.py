#!/usr/bin/env python
# -*- coding: utf-8 -*-#
# auth:xucl

import sys
import time
from datetime import datetime
import MySQLdb
import hashlib

class DBUtil:
    def __init__(self, src_host=None, src_port=None, src_user=None, src_passwd=None, src_db=None, tar_host=None, tar_port=None, tar_user=None, tar_passwd=None, tar_db=None):
        self.src_host = src_host
        self.src_port = src_port
        self.src_user = src_user
        self.src_passwd = src_passwd
        self.src_db = src_db
        self.tar_host = tar_host
        self.tar_port = tar_port
        self.tar_user = tar_user
        self.tar_passwd = tar_passwd
        self.tar_db = tar_db
    
    def __enter__(self):
        self._conn1 = MySQLdb.connect(host=self.src_host, port=self.src_port, user=self.src_user, passwd=self.src_passwd, db=self.src_db)
        self._conn2 = MySQLdb.connect(host=self.tar_host, port=self.tar_port, user=self.tar_user, passwd=self.tar_passwd, db=self.tar_db)
        self._cursor1 = self._conn1.cursor()
        self._cursor2 = self._conn2.cursor()
        return self
	 
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn1.close()
	self._conn1 = None
        self._conn2.close()
	self._conn2 = None
        

    def get_sql_md5(self, sql):
        self._cursor1.execute(sql)
        result1 = self._cursor1.fetchmany(size=1000)
	m1 = hashlib.md5()
        m1.update(str(result1).encode('utf-8'))
        hash1 = m1.hexdigest() 

        self._cursor2.execute(sql)
        result2 = self._cursor2.fetchmany(size=1000)
        m2 = hashlib.md5()
        m2.update(str(result2).encode('utf-8'))
        hash2 = m2.hexdigest()      
        
        if hash1 ==  hash2:
	    return True
	else:
	    return (sql, False)


if __name__ == '__main__':
    with DBUtil('127.0.0.1', 3306, 'xucl', 'xuclxucl', 'xucl', '127.0.0.1', 3307, 'xucl', 'xuclxucl', 'xucl') as client:
	with open('sql.txt', 'r') as f:
	    sql_list = f.readlines()
	    for sql in sql_list:
		print(client.get_sql_md5(sql.strip('\n')))
