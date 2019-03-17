## MySQL巡检怎么做？

刚到新公司？刚来客户现场？有朋友请你帮忙优化数据库？如何快速对现有的实例有个大概的了解，下面我来带你从MySQL数据库层做一次快速的巡检。

### 一、巡检内容

- 表巡检
  - 大小超过10G的表
  - 索引超过6个的表
  - 碎片率超过50%的表
  - 行数超过1000万行的表
  - 非默认字符集的表
  - 含有大字段的表
  - varchar定义超长的表
  - 无主键/索引的表
- 索引巡检
  - 重复索引
  - 索引列超过5个的索引
  - 无用索引
- 重要参数
  - version
  - innodb_buffer_pool_size
  - innodb_flush_log_at_trx_commit
  - innodb_log_file_size
  - innodb_log_files_in_group
  - innodb_file_per_table
  - innodb_max_dirty_pages_pct
  - sync_binlog
  - max_connections
  - query_cache_type
  - table_open_cache
  - table_definition_cache
- 重要状态指标
  - Uptime
  - Opened_files
  - Opened_table_definitions
  - Opened_tables
  - Max_used_connections
  - Threads_created
  - Threads_connected
  - Aborted_connects
  - Aborted_clients
  - Table_locks_waited
  - Innodb_buffer_pool_wait_free
  - Innodb_log_waits
  - Table_locks_waited
  - Innodb_row_lock_waits
  - Innodb_row_lock_time_avg
  - Binlog_cache_disk_use
  - Created_tmp_disk_tables
- 用户检查
  - 无密码用户
  - %用户
- 权限检查

### 二、检查脚本

git地址：https://github.com/zhishutech/mysqldba/blob/master/mysql-tools/check_mysql.py

### 三、如何使用检查脚本

3.1 创建巡检用户

`grant select,process on *.* to monitor@localhost identified by '123456'`

3.2 巡检脚本填入相应ip、端口号、账号、密码

3.3 执行巡检

### 四、巡检效果

```version : 5.7.23-log
innodb_buffer_pool_size : 134217728
innodb_flush_log_at_trx_commit : 1
innodb_log_file_size : 134217728
innodb_log_files_in_group : 3
innodb_file_per_table : ON
innodb_max_dirty_pages_pct : 50.000000
sync_binlog : 1
max_connections : 512
query_cache_type : OFF
table_open_cache : 1024
table_definition_cache : 1024
Uptime : 1103289
Opened_files : 4741
Opened_table_definitions : 1155
Opened_tables : 34582
Max_used_connections : 8
Threads_created : 8
Threads_connected : 2
Aborted_connects : 67417
Aborted_clients : 674
Table_locks_waited : 0
Innodb_buffer_pool_wait_free : 0
Innodb_log_waits : 0
Innodb_row_lock_waits : 0
Innodb_row_lock_time_avg : 0
Binlog_cache_disk_use : 1
Created_tmp_disk_tables : 256641
historylength : 41
Log sequence number : 1410769049
Log flushed up to : 1410768979
Last checkpoint at : 1410768970
检查无密码用户
结果不存在
检查%用户
user: monitor host: %
检查用户权限
GRANT REPLICATION CLIENT ON *.* TO 'monitor'@'%'
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION
GRANT PROXY ON ''@'' TO 'root'@'localhost' WITH GRANT OPTION
```

