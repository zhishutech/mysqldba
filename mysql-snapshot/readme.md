# snapshot数据库拍照
**使用**

```python
pip install -r requirements.txt
```

说明：python3.6



**设定触发条件**

示例

```python
python /tmp/snapshot/snapshot.py --host=127.0.0.1 --port=3306 --user=xucl --password=xuclxucl --conditions="{'Threads_connected': 500, 'Threads_running': 20, 'Innodb_row_lock_current_waits': 5, 'Slow_queries': 5, 'cpu_user':10, 'cpu_sys':10, 'cpu_iowait':5, 'sys_iops':500, 'sql_delay':60}" --storedir=/tmp
```



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
