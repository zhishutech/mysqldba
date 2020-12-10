# MySQL Snapshot（MySQL数据库快照）

>
> 当MySQL数据库出现性能瓶颈时，可根据预设条件对当前数据库状态做一份快照，方便DBA进行排查。
>
> 本程序用Python开发，运行在Python 3.6环境中。
>

## 1. 安装部署
** 1.1 设置Python运行环境
说明：
```python
pip3.6 install -r pip3.6-requirements.txt
```

** 1.2 在MySQL里创建专用账号
```
CREATE USER snapshot@'%' IDENTIFIED WITH mysql_native_password by '76950ed38752421e29c397beff9157ac';
GRANT SELECT, PROCESS, REPLICATION CLIENT ON *.* TO `snapshot`@`%`;
GRANT SELECT, EXECUTE ON `sys`.* TO `snapshot`@`%`;
```
**备注：**
1. 必须使用 mysql_native_password，Python 3.6还不支持 caching_sha2_password 插件。
2. 创建账号的允许连接IP及密码请自行修改。

** 1.3 运行程序（示例）


```python
cd /data/mysqldba/mysql-snapshot;
python3.6 ./snapshot.py --host=127.0.0.1 --port=3306 --user=snapshot --password='37b7412fef6f48b' --conditions="{'Threads_connected': 500, 'Threads_running': 20, 'Innodb_row_lock_current_waits': 5, 'Slow_queries': 5, 'Innodb_buffer_pool_wait_free': 5, 'cpu_user':10, 'cpu_sys':10, 'cpu_iowait':5, 'sys_iops':5000, 'sql_delay':60}" --interval=30 --storedir=/data/mysqldba/mysql-snapshot/logs
```

触发条件说明：

- 'Threads_connected':500，MySQL实例总连接数超过500
- 'Threads_running':20，MySQL实例当前活跃线程数超过20
- 'Innodb_row_lock_current_waits':5，MySQL实例当前活跃行锁等待数超过5
- 'Slow_queries':5，MySQL实例1秒内新增慢查询数大于5
- 'Innodb_buffer_pool_wait_free':1，MySQL实例每秒产生ibp等待事件大于5
- 'cpu_user':10，系统CPU %user消耗超过10%
- 'cpu_sys':10，系统CPU %sys消耗超过10%
- 'cpu_iowait':5，系统CPU %iowait消耗超过5%
- 'sys_iops':5000，系统磁盘iops（读 + 写）总和超过5000
- 'sql_delay':60，MySQL主从复制延迟时间超过60秒（取值自Seconds_Behind_Master，5.6后很不靠谱，不建议使用，未来会改进）

其他参数说明：
- host、user、port、password均是指连接MySQL实例的几个相关参数，不多解释
- interval=N，单位：秒，每隔N秒检查一次状态，判断达到触发条件的话就创建一份状态快照
- storedir，指定快照日志存储的路径，默认路径：/data/mysqldba/mysql-snapshot/logs

**生成快照文件**

规则：

- 在日志目录`storedir`下，每次达到触发条件时，创建相应的时间戳目录
- 在新建的目录中，保存MySQL当时的状态信息，主要包括：系统负载数据，MySQL连接、事务、锁、错误日志、慢查询日志等信息


```shell
[root@~]# ls -l
-rw-r--r--. 1 root root 13635 Dec  9 02:30 innodb_status
-rw-r--r--. 1 root root 42188 Dec  9 02:30 interrupts
-rw-r--r--. 1 root root 10841 Dec  9 02:31 iostat
-rw-r--r--. 1 root root  1312 Dec  9 02:30 meminfo
-rw-r--r--. 1 root root 28560 Dec  9 02:31 mpstat
-rw-r--r--. 1 root root  8841 Dec  9 02:30 netstat
-rw-r--r--. 1 root root  6246 Dec  9 02:30 processlist
-rw-r--r--. 1 root root 29247 Dec  9 02:30 ps
-rw-r--r--. 1 root root  1415 Dec  9 02:30 slave_status
-rw-r--r--. 1 root root   612 Dec  9 02:30 slowlog
-rw-r--r--. 1 root root 13120 Dec  9 02:30 status
-rw-r--r--. 1 root root  1079 Dec  9 02:30 top
-rw-r--r--. 1 root root 21676 Dec  9 02:30 transactions
-rw-r--r--. 1 root root 18300 Dec  9 02:30 variables
-rw-r--r--. 1 root root  2950 Dec  9 02:31 vmstat
```

如果在创建快照是加上tcpdump的结果（默认没启用），可以修改源码文件 ```snapshot.py``` 约 85~88 行，修改成如下内容即可：
```Python
#旧
"""
                sys_func_list = [mysql_slow_log, mysql_error_log, system_message, system_dmesg, system_top, system_iostat, system_mpstat,
                         system_mem_info, system_interrupts, system_ps, system_netstat, system_vmstat]
                sys_arg_list = [slow_log, error_log, '/var/log/messages', '/var/log/dmesg', '', self.interval, self.interval,
                        '', '', '', '', self.interval]
"""

#新
                sys_func_list = [mysql_slow_log, mysql_error_log, system_message, system_dmesg, system_top, system_iostat, system_mpstat,
                         system_mem_info, system_interrupts, system_ps, system_netstat, system_vmstat, system_tcpdump]
                sys_arg_list = [slow_log, error_log, '/var/log/messages', '/var/log/dmesg', '', self.interval, self.interval,
                        '', '', '', '', self.interval, self.conn_setting['port']]
```


说明：有bug请提交[issue](https://github.com/zhishutech/mysqldba/issues)，谢谢。

本人QQ：573242930
