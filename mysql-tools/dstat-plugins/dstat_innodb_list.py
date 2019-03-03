#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/2/15 14:02
# @Author  : xucl
# @Email   : xuchenliang123@live.com
# @howtouse: dstat --innodb-list
global mysql_options
mysql_options = os.getenv('DSTAT_MYSQL')

class dstat_plugin(dstat):
    def __init__(self):
        self.name = 'innodb list length'
        self.nick = ('unpurged', 'free')
        self.vars = ('u_list', 'f_list')
        self.type = 'd'
        self.width = 10
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
            line1 = greppipe(self.stdout, 'History list length')
            line2 = greppipe(self.stdout, 'free list len')

            if line1:
            	l1 = line1.split()
                self.set2['u_list'] = int(l1[3].rstrip(' '))
            if line2:
		l2 = line2.split()
                self.set2['f_list'] = int((l2[6]).rstrip(','))

            #for name in self.vars:
            #    self.val[name] = (self.set2[name] - self.set1[name]) * 1.0 / elapsed
	    self.val['u_list'] = (self.set2['u_list'])
      	    self.val['f_list'] = (self.set2['f_list'])

        except IOError, e:
            if op.debug > 1: print '%s: lost pipe to mysql, %s' % (self.filename, e)
            for name in self.vars: self.val[name] = -1

        except Exception, e:
            if op.debug > 1: print '%s: exception' % (self.filename, e)
            for name in self.vars: self.val[name] = -1
