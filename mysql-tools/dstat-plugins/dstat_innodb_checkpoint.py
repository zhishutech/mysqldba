#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/2/15 14:02
# @Author  : xucl
# @Email   : xuchenliang123@live.com
# @howtouse: dstat --innodb-checkpoint
global mysql_options
mysql_options = os.getenv('DSTAT_MYSQL')

class dstat_plugin(dstat):
    def __init__(self):
        self.name = 'innodb checkpoint lags'
        self.nick = ('LSN1', 'LSN4', 'LAG')
        self.vars = ('lsn_now', 'lsn_check', 'lsn_lag')
        self.type = 'd'
        self.width = 20
        self.scale = 1000

    def check(self):
        if os.access('/usr/bin/mysql', os.X_OK):
            try:
                self.stdin, self.stdout, self.stderr = dpopen('/usr/bin/mysql -n %s' % mysql_options)
            except IOError:
                raise Exception, 'Cannot interface with MySQL binary'
            return True
        raise Exception, 'Needs MySQL binary'

    def extract(self):
        try:
            self.stdin.write('show engine innodb status\G\n')
            line1 = greppipe(self.stdout, 'Log sequence number')
            line2 = greppipe(self.stdout, 'Last checkpoint at')

            if line1:
            	l1 = line1.split()
                self.set2['lsn_now'] = int(l1[3].rstrip(' '))
            if line2:
		l2 = line2.split()
                self.set2['lsn_check'] = int(l2[3].rstrip(' '))
                self.set2['lsn_lag'] = int(int(l1[3].rstrip(' ')) - int(l2[3].rstrip(' ')))
            #for name in self.vars:
            #    self.val[name] = (self.set2[name] - self.set1[name]) * 1.0 / elapsed
	    self.val['lsn_now'] = (self.set2['lsn_now'])
            self.val['lsn_check'] = (self.set2['lsn_check'])
	    self.val['lsn_lag'] = (self.set2['lsn_lag'])	

        except IOError, e:
            if op.debug > 1: print '%s: lost pipe to mysql, %s' % (self.filename, e)
            for name in self.vars: self.val[name] = -1

        except Exception, e:
            if op.debug > 1: print '%s: exception' % (self.filename, e)
            for name in self.vars: self.val[name] = -1
