#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/2/15 14:02
# @Author  : xucl
# @Email   : xuchenliang123@live.com
# @howtouse: dstat --mysql5-rowlockwaits
global mysql_user
mysql_user = os.getenv('DSTAT_MYSQL_USER') or os.getenv('USER')

global mysql_pwd
mysql_pwd = os.getenv('DSTAT_MYSQL_PWD')

global mysql_host
mysql_host = os.getenv('DSTAT_MYSQL_HOST')

global mysql_port
mysql_port = os.getenv('DSTAT_MYSQL_PORT')

class dstat_plugin(dstat):
    """
    Plugin for MySQL 5 connections.
    """

    def __init__(self):
        self.name = 'innodb lock waits'
        self.nick = ('current_waits', 'total_waits')
        self.vars = ('current_waits', 'waits')
        self.type = 'd'
        self.width = 15
        self.scale = 1

    def check(self): 
        global MySQLdb
        import MySQLdb
        try:
            self.db = MySQLdb.connect(user=mysql_user, passwd=mysql_pwd, host=mysql_host, port=int(mysql_port))
        except Exception, e:
            raise Exception, 'Cannot interface with MySQL server, %s' % e

    def extract(self):
        try:
            c = self.db.cursor()
            c.execute("""show global status like 'Innodb_row_lock_current_waits';""")
            current_waits = c.fetchone()
            c.execute("""show global status like 'Innodb_row_lock_waits';""")
            waits = c.fetchone()
	    if current_waits:
                self.set2['current_waits'] = int(current_waits[1]) 
	    if waits:
		self.set2['waits'] = int(waits[1])
            #for name in self.vars:
            #    self.val[name] = self.set2[name] * 1.0 / elapsed
	    self.val['current_waits'] = self.set2['current_waits']
	    self.val['waits'] = self.set2['waits']
            if step == op.delay:
                self.set1.update(self.set2)

        except Exception, e:
            for name in self.vars:
                self.val[name] = -1

# vim:ts=4:sw=4:et
