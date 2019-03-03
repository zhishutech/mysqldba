## 关于

> - 作者：叶金荣, 知数堂培训（http:/zhishutang.com）联合创始人, 资深MySQL专家, MySQL布道师, Oracle MySQL ACE
> - 分享工作、教学中用到的&收集到的一些实用SQL脚本命令，有需自取
> - 这些脚本在MySQL 5.7版本下均测试通过
> - 最后更新时间：2017-6-22
> - QQ群：579036588
> - 微信公众号：「老叶茶馆」、「知数堂」、「云DB」

* ## 查看哪些索引采用部分索引（前缀索引）
> 优化建议：检查部分索引长度是否还可以进一步缩小
```
SELECT TABLE_SCHEMA, TABLE_NAME, INDEX_NAME, 
SEQ_IN_INDEX, COLUMN_NAME, CARDINALITY, SUB_PART
FROM INFORMATION_SCHEMA.STATISTICS WHERE 
SUB_PART > 10 ORDER BY SUB_PART DESC;
```

* ## 查看哪些索引长度超过30字节，重点查CHAR/VARCHAR/TEXT/BLOB等类型
> 优化建议：超过20字节长度的索引，都应该考虑进一步缩短，否则效率不佳
```
select c.table_schema as `db`, c.table_name as `tbl`, 
 c.COLUMN_NAME as `col`, c.DATA_TYPE as `col_type`, 
 c.CHARACTER_MAXIMUM_LENGTH as `col_len`, 
 c.CHARACTER_OCTET_LENGTH as `col_len_bytes`,  
 s.NON_UNIQUE as `isuniq`, s.INDEX_NAME, s.CARDINALITY, 
 s.SUB_PART, s.NULLABLE 
 from information_schema.COLUMNS c inner join information_schema.STATISTICS s 
 using(table_schema, table_name, COLUMN_NAME) where 
 c.table_schema not in ('mysql', 'sys', 'performance_schema', 'information_schema', 'test') and 
 c.DATA_TYPE in ('varchar', 'char', 'text', 'blob') and 
 ((CHARACTER_OCTET_LENGTH > 20 and SUB_PART is null) or 
 SUB_PART * CHARACTER_OCTET_LENGTH/CHARACTER_MAXIMUM_LENGTH >20);
```

* ## 查看未完成的事务列表
> 优化建议：若有长时间未完成的事务，可能会导致：
> - undo不能被及时purge，undo表空间不断增长；
> - 持有行锁，其他事务被阻塞。
> 应该及时提交或回滚这些事务，或者直接kill释放之。
>
> 参考：
> - [FAQ系列 | 如何避免ibdata1文件大小暴涨 http://mp.weixin.qq.com/s/KD2qLrmWY80yFxUtxJVNMA]
> - [是谁，把InnoDB表上的DML搞慢的？ http://mp.weixin.qq.com/s/wEPKgPo1dMsxTedjvulSlQ]
```
select b.host, b.user, b.db, b.time, b.COMMAND, 
 a.trx_id, a. trx_state from 
 information_schema.innodb_trx a left join 
 information_schema.PROCESSLIST b on a.trx_mysql_thread_id = b.id;
```


* ## 查看当前有无行锁等待事件
> 优化建议：
> - 若当前有行锁等待，则有可能导致锁超时被回滚，事务失败；
> - 有时候，可能是因为某个终端/会话开启事务，对数据加锁后，忘记提交/回滚，导致行锁不能释放。
> 
> 参考：
> [是谁，把InnoDB表上的DML搞慢的？ http://mp.weixin.qq.com/s/wEPKgPo1dMsxTedjvulSlQ]
> [FAQ系列 | 是什么导致MySQL数据库服务器磁盘I/O高？ http://mp.weixin.qq.com/s/sAGFo-h1GCBhad1r1cEWTg]
> [[译文]MySQL发生死锁肿么办？ http://mp.weixin.qq.com/s/oUSdfv0qlrxCearFw-_XZw]
> [都是主键惹的祸-记一次死锁分析过程 http://mp.weixin.qq.com/s/7VmlqcqTQH7ITnmUKCdw5Q]
```
SELECT lw.requesting_trx_id AS request_XID, 
 trx.trx_mysql_thread_id as request_mysql_PID,
 trx.trx_query AS request_query, 
 lw.blocking_trx_id AS blocking_XID, 
 trx1.trx_mysql_thread_id as blocking_mysql_PID,
 trx1.trx_query AS blocking_query, lo.lock_index AS lock_index FROM 
 information_schema.innodb_lock_waits lw INNER JOIN 
 information_schema.innodb_locks lo 
 ON lw.requesting_trx_id = lo.lock_trx_id INNER JOIN 
 information_schema.innodb_locks lo1 
 ON lw.blocking_trx_id = lo1.lock_trx_id INNER JOIN 
 information_schema.innodb_trx trx 
 ON lo.lock_trx_id = trx.trx_id INNER JOIN 
 information_schema.innodb_trx trx1 
 ON lo1.lock_trx_id = trx1.trx_id;
```
其实，在MySQL 5.7下，也可以直接查看 sys.innodb_lock_waits 视图：
```
SELECT * FROM sys.innodb_lock_waits\G
```

* ## 检查哪些表没有显式创建主键索引
> 优化建议：
> - 选择自增列做主键；
> - 或者其他具备单调递增特点的列做主键；
> - 主键最好不要有业务用途，避免后续会更新。
>
> 参考：
> - [MySQL FAQ系列 — 为什么InnoDB表要建议用自增列做主键 http://mp.weixin.qq.com/s/GpOzU9AqhWPj6bj9C5yXmw]
```
SELECT
a.TABLE_SCHEMA as `db`,
a.TABLE_NAME as `tbl`
FROM
(
SELECT
TABLE_SCHEMA,
TABLE_NAME
FROM
information_schema.TABLES
WHERE
TABLE_SCHEMA NOT IN (
'mysql',
'sys',
'information_schema',
'performance_schema'
) AND 
TABLE_TYPE = 'BASE TABLE'
) AS a
LEFT JOIN (
SELECT
TABLE_SCHEMA,
TABLE_NAME
FROM
information_schema.TABLE_CONSTRAINTS
WHERE
CONSTRAINT_TYPE = 'PRIMARY KEY'
) AS b ON a.TABLE_SCHEMA = b.TABLE_SCHEMA
AND a.TABLE_NAME = b.TABLE_NAME
WHERE
b.TABLE_NAME IS NULL;
```


* ## 查看表数据列元数据信息
```
select a.table_id, a.name, b.name, b.pos, b.mtype, b.prtype, b.len from 
information_schema.INNODB_SYS_TABLES a left join 
information_schema.INNODB_SYS_COLUMNS b 
using(table_id) where a.name = 'yejr/t1';
```


* ## 查看InnoDB表碎片率
> 优化建议：
```
SELECT TABLE_SCHEMA as `db`, TABLE_NAME as `tbl`, 
1-(TABLE_ROWS*AVG_ROW_LENGTH)/(DATA_LENGTH + INDEX_LENGTH + DATA_FREE) AS `fragment_pct` 
FROM information_schema.TABLES WHERE 
TABLE_SCHEMA = 'yejr' ORDER BY fragment_pct DESC;
```


* ## 查某个表在innodb buffer pool中的new block、old block比例
```
select table_name, count(*), sum(NUMBER_RECORDS), 
 if(IS_OLD='YES', 'old', 'new') as old_block from
 information_schema.innodb_buffer_page where 
 table_name = '`yejr`.`t1`' group by old_block;
```
