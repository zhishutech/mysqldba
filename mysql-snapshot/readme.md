# snapshot数据库拍照
**使用**

```python
pip install -r requirements.txt
```

说明：python3.6



**设定触发条件**

示例

```python
python snapshot.py --host=127.0.0.1 --port=3306 --user=xucl --password=xuclxucl --conditions="{'Threads_connected': 500, 'Threads_running': 20, 'Innodb_row_lock_current_waits': 5, 'Slow_queries': 5, 'Innodb_buffer_pool_wait_free': 5, 'cpu_user':10, 'cpu_sys':10, 'cpu_iowait':5, 'sys_iops':500, 'sql_delay':60}" --interval=30 --storedir=/tmp
```

触发条件说明：

- Threads_connected：MySQL实例连接数
- Threads_running：MySQL实例当前运行连接数
- Innodb_row_lock_current_waits：当前行锁等待
- Slow_queries：每秒记录慢查询数
- Innodb_buffer_pool_wait_free：每秒产生ibp等待事件
- cpu_user：user cpu占用
- cpu_sys：sys cpu占用
- cpu_iowait：cpu iowait占用
- sys_iops：系统iops占用
- sql_delay：主从延迟时间

**生成拍照文件**

规则：

- 在基础目录`storedir`下，每次发生拍照时间创建目录



```shell
(vent) [root@izbp12nspj47ypto9t6vyez 2019_05_13_18_58_14]# pwd
/tmp/2019_05_13_18_58_14
```



```shell
(vent) [root@izbp12nspj47ypto9t6vyez 2019_05_13_18_58_14]# ls
innodb_status  interrupts  iostat  meminfo  mpstat  netstat  processlist  ps  slave_status  status  tcpdump  top  transactions  variables  vmstat
```



说明：有bug请反馈，谢谢。

本人QQ：573242930
