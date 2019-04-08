| metric name                    | 指标说明                                  | 取值      | 类型    |
| ------------------------------ | ----------------------------------------- | --------- | ------- |
| mysql_alive                    | mysql存活状态，1为存活，0为宕机           | 自定义    | GAUGE   |
| responsetime                   | 响应时间，单位：秒                        | 自定义    | GAUGE   |
| uptime                         | 存活时间，单位：秒                        | status    | GAUGE   |
| role                           | 实例角色，1为master，0为slave             | 自定义    | GAUGE   |
| read_only                      | 只读                                      | variables | GAUGE   |
| super_read_only                | 管理员只读                                | variables | GAUGE   |
| aborted_client                 | 已连接断开数                              | status    | COUNTER |
| aborted_connections            | 为连接断开数                              | status    | COUNTER |
| threads_connected              | 已连接线程数                              | status    | GAUGE   |
| threads_running                | 活跃线程数                                | status    | GAUGE   |
| threads_created                | 历史上创建过的线程数                      | status    | COUNTER |
| Max_used_connections           | 历史最大连接数                            | status    | GAUGE   |
| max_user_connections           | 最大用户连接数                            | variables | GAUGE   |
| max_connections                | 最大连接数                                | variables | GAUGE   |
| innodb_buffer_pool_size        | innodb_buffer_pool大小                    | variables | GAUGE   |
| qps                            | 每秒查询数，queries/s                     | 自定义    | GAUGE   |
| tps                            | 每秒事务数，commit+rollback/s             | 自定义    | GAUGE   |
| created_tmp_disk_tables        | 创建磁盘临时表数                          | status    | COUNTER |
| created_tmp_files              | 创建临时文件数                            | status    | COUNTER |
| created_tmp_tables             | 创建内存临时表数                          | status    | COUNTER |
| select_full_join               | 全表join数                                | status    | COUNTER |
| select_full_range              | 全表range数                               | status    | COUNTER |
| select_scan                    | 全表扫描数                                | status    | COUNTER |
| Slow_queries                   | 慢查询数                                  | status    | COUNTER |
| table_locks_immediate          | 立即锁表次数                              | status    | GAUGE   |
| table_locks_waited             | 等待表锁次数                              | status    | COUNTER |
| innodb_row_lock_current_waits  | 当前行锁等待数                            | status    | GAUGE   |
| innodb_row_lock_time           | 行锁等待时间                              | status    | COUNTER |
| innodb_row_lock_time_avg       | 平均行锁等待时间                          | status    | GAUGE   |
| innodb_row_lock_waits          | 行锁等待次数                              | status    | COUNTER |
| bytes_received                 | 接受字节数                                | status    | COUNTER |
| bytes_sent                     | 发送字节数                                | status    | COUNTER |
| innodb_buffer_pool_wait_free   | 等待buffer_pool分配新page数               | status    | COUNTER |
| innodb_log_waits               | 等待刷redo log次数                        | status    | COUNTER |
| history_list_length            | 等待被purge的队列长度，来自innodb status  | 自定义    | GAUGE   |
| loglsn                         | 当前lsn值                                 | 自定义    | GAUGE   |
| logflushlsn                    | 刷新到redo的lsn值                         | 自定义    | GAUGE   |
| checkpointlsn                  | check point lsn值                         | 自定义    | GAUGE   |
| open_files                     | 当前打开文件数                            | status    | GAUGE   |
| opened_files                   | 历史打开文件数                            | status    | COUNTER |
| open_tables                    | 当前打开表数                              | status    | GAUGE   |
| opened_tables                  | 历史打开表数                              | status    | COUNTER |
| table_open_cache               | 表缓存数                                  | variables | GAUGE   |
| Open_table_definitions         | 当前打开表定义数                          | status    | GAUGE   |
| opened_table_definitions       | 历史打开表定义数                          | status    | COUNTER |
| table_definition_cache         | 表定义数                                  | variables | GAUGE   |
| Handler_read_key               | 读取索引次数                              | status    | COUNTER |
| Handler_read_next              | 读取下一个值次数                          | status    | COUNTER |
| Handler_read_rnd               | 随机读次数                                | status    | COUNTER |
| Handler_read_rnd_next          | 全表扫描或者排序或者读下一行              | status    | COUNTER |
| sort_merge_pass                | 归并排序次数                              | status    | COUNTER |
| binlog_cache_disk_use          | 使用磁盘存储binlog                        | status    | COUNTER |
| slave_io_running               | slave上io线程状态，来源show slave status  | 自定义    | GAUGE   |
| slave_sql_running              | slave上sql线程状态,来源show slave status  | 自定义    | GAUGE   |
| Seconds_behind_master          | slave延迟（暂时），后期改为pt-slave-delay | 自定义    | GAUGE   |
| innodb_flush_log_at_trx_commit | innodb_flush_log_at_trx_commit            | variables | GAUGE   |
| sync_binlog                    | sync_binlog                               | variables | GAUGE   |
| Com_select                     | select次数                                | status    | COUNTER |
| Com_update                     | update次数                                | status    | COUNTER |
| Com_insert                     | insert次数                                | status    | COUNTER |
| Com_delete                     | delete次数                                | status    | COUNTER |
| Com_commit                     | commit次数                                | status    | COUNTER |
| Com_rollback                   | rollback次数                              | status    | COUNTER |

