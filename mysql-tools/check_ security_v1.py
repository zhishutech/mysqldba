#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author:郑松华，知数堂SQL优化班老师，网名：骑龟的兔子
#
# 脚本作用说明
# 针对MySQL做安全检查，包括账号、授权，以及几个重要参数的设置
# Last Update, 2020/08/14

import sys
import os
import datetime
import pymysql
import argparse 
import getpass
import pandas as pd  

class Monitor(object):
    
    def __init__(self, connection_settings):
        """
        conn_setting: {'host': 127.0.0.1, 'port': 3306, 'user': user, 'passwd': passwd, 'charset': 'utf8'}
        """ 
        self.conn_setting = connection_settings
        self.connection = pymysql.connect(**self.conn_setting)
        
        pd.set_option('display.max_columns',None)
#显示所有行
        pd.set_option('display.max_rows',None)
#设置数据的显示长度，默认为50
        pd.set_option('max_colwidth',100)
#禁止自动换行(设置为Flase不自动换行，True反之)
        pd.set_option('expand_frame_repr', False)
        

    def process_run(self):
        sql1 = '''
        select now() time ;
        '''  
        cursor1 = self.connection.cursor() 
        cursor1.execute(sql1) 

        res1 = cursor1.fetchall()
        res1 = pd.DataFrame(list(res1), columns=['time'])
        
        print("This is MySQL 5.7 version security Report version 1.0 ")
        print(res1)
        return True

    def process_d02(self):
        sql1 = '''
        select host,user ,  authentication_string , password_expired ,password_last_changed ,password_lifetime ,account_locked  from mysql.user ; 
        '''  
        cursor1 = self.connection.cursor() 
        cursor1.execute(sql1) 

        res1 = cursor1.fetchall()
        res1 = pd.DataFrame(list(res1), columns=['host','user','authentication_string','password_expired','password_last_changed','password_lifetime','account_locked'])
        print("\n") 
        print(" User Account about password , change lifetime ,locked info ") 
        print("\n") 
        print(res1)
        return True    

    def process_d03(self):
        sql1 = '''
        show global variables like '%plu%'; 
        '''  
        cursor1 = self.connection.cursor() 
        cursor1.execute(sql1) 

        res1 = cursor1.fetchall()
        res1 = pd.DataFrame(list(res1), columns=['Variable_name','Value'])
        print("\n") 
        print(" authentication_plugin info  ") 
        print("\n") 
        print(res1)
        return True

    def process_d04(self):
        sql1 = '''
        show global variables like '%vali%'; 
        '''  
        cursor1 = self.connection.cursor() 
        cursor1.execute(sql1) 

        res1 = cursor1.fetchall()
        res1 = pd.DataFrame(list(res1), columns=['Variable_name','Value'])
        print("\n")
        print("\n") 
        print(res1)
        return True   


    def process_d05(self):
        sql1 = '''
        select 
        host
        ,user 
        ,Select_priv           
        ,Insert_priv           
        ,Update_priv           
        ,Delete_priv           
        ,Create_priv           
        ,Drop_priv             
        ,Reload_priv           
        ,Shutdown_priv         
        ,Process_priv          
        ,File_priv             
        ,Grant_priv            
        ,References_priv       
        ,Index_priv            
        ,Alter_priv            
        ,Show_db_priv          
        ,Super_priv            
        ,Create_tmp_table_priv 
        ,Lock_tables_priv      
        ,Execute_priv          
        ,Repl_slave_priv       
        ,Repl_client_priv      
        ,Create_view_priv      
        ,Show_view_priv        
        ,Create_routine_priv   
        ,Alter_routine_priv    
        ,Create_user_priv      
        ,Event_priv            
        ,Trigger_priv          
        ,Create_tablespace_priv
        from mysql.user  
        where host = '%'; 
        '''  
        cursor1 = self.connection.cursor() 
        cursor1.execute(sql1) 

        res1 = cursor1.fetchall()
        res1 = pd.DataFrame(list(res1), columns=['host','user','Select_priv','Insert_priv','Update_priv','Delete_priv','Create_priv'
        ,'Drop_priv','Reload_priv','Shutdown_priv','Process_priv','File_priv','Grant_priv','References_priv','Index_priv','Alter_priv'
        ,'Show_db_priv','Super_priv','Create_tmp_table_priv','Lock_tables_priv','Execute_priv','Repl_slave_priv','Repl_client_priv'
        ,'Create_view_priv','Show_view_priv','Create_routine_priv','Alter_routine_priv','Create_user_priv','Event_priv','Trigger_priv'
        ,'Create_tablespace_priv'
        ])
        print("\n")
        print("  host % priv list  ") 
        print("\n") 
        print(res1)
        return True  

    def process_d06(self):
        sql1 = '''
        show variables like '%general%';
        '''  
        cursor1 = self.connection.cursor() 
        cursor1.execute(sql1) 

        res1 = cursor1.fetchall()
        res1 = pd.DataFrame(list(res1), columns=['Variable_name','Value'])
        print("\n")
        print("  general log on/off status  ") 
        print("\n") 
        print(res1)
        return True      

    def process_d07(self):
        sql1 = '''
        show variables like '%timeout%';
        '''  
        cursor1 = self.connection.cursor() 
        cursor1.execute(sql1) 

        res1 = cursor1.fetchall()
        res1 = pd.DataFrame(list(res1), columns=['Variable_name','Value'])
        print("\n")
        print("  timeout variables list  ") 
        print("\n") 
        print(res1)
        return True     

    def __del__(self):
        pass



def is_valid_datetime(string):
    try:
        datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")
        return True
    except:
        return False


def parse_args():
    """parse args for binlog2sql"""

    parser = argparse.ArgumentParser(description='Parse MySQL binlog to SQL you want', add_help=False)
    connect_setting = parser.add_argument_group('connect setting')
    connect_setting.add_argument('-h', '--host', dest='host', type=str,
                                 help='Host the MySQL database server located', default='127.0.0.1')
    connect_setting.add_argument('-u', '--user', dest='user', type=str,
                                 help='MySQL Username to log in as', default='root')
    connect_setting.add_argument('-p', '--password', dest='password', type=str, nargs='*',
                                 help='MySQL Password to use', default='')
    connect_setting.add_argument('-P', '--port', dest='port', type=int,
                                 help='MySQL port to use', default=3306)
   
    parser.add_argument('--help', dest='help', action='store_true', help='help information', default=False)

    schema = parser.add_argument_group('schema filter')
    schema.add_argument('-d', '--databases', dest='databases', type=str, nargs='*',
                        help='dbs you want to process', default='')
    schema.add_argument('-t', '--tables', dest='tables', type=str, nargs='*',
                        help='tables you want to process', default='')
    return parser


def command_line_args(args):
    need_print_help = False if args else True
    parser = parse_args()
    args = parser.parse_args(args)
    if args.help or need_print_help:
        parser.print_help()
        sys.exit(1)
    if not args.password:
        args.password = getpass.getpass()
    else:
        args.password = args.password[0]
    return args
 
if __name__ == '__main__':
    args = command_line_args(sys.argv[1:])
    conn_setting = {'host': args.host, 'port': args.port, 'user': args.user, 'passwd': args.password, 'charset': 'utf8'}
    mo = Monitor( connection_settings=conn_setting) 
    mo.process_run() 
    mo.process_d02()
    mo.process_d03()
    mo.process_d04()
    mo.process_d05()
    mo.process_d06()
    mo.process_d07()


   # C:/Python38/python.exe check_ security_v1.py --host=127.0.0.1 --port=3306 --user=test --password='test' --database=mysql 
