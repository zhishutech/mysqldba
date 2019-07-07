## 关于

> - 作者：叶金荣, 知数堂培训（http:/zhishutang.com）联合创始人, 资深MySQL专家, MySQL布道师, Oracle MySQL ACE
> - 分享工作、教学中用到的&收集到的一些实用SQL脚本命令，有需自取
> - 这些脚本在MySQL 5.7/8.0版本下均测试通过
> - 最后更新时间：2019-7-7
> - QQ群：579036588
> - 微信公众号：「老叶茶馆」、「知数堂」、「pai3306」

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

* ## 查看某个数据库里所有表的索引统计情况，重点是关注 stat_pct 列值较低的索引
```
# 工作方式
# 1、扫描所有索引统计信息
# 2、包含主键列的辅助索引统计值，对比主键索引列的统计值，得到一个百分比stat_pct
# 3、根据stat_pct排序，值越低说明辅助索引统计信息越不精确，越是需要关注

set @statdb = 'yejr';
select 
a.database_name ,
a.table_name ,
a.index_name ,
a.stat_value SK,
b.stat_value PK, 
round((a.stat_value/b.stat_value)*100,2) stat_pct
from 
(
select 
b.database_name  ,
b.table_name  ,
b.index_name ,  
b.stat_value
from 
(
select database_name  ,
table_name  ,
index_name ,  
max(stat_name) stat_name 
from innodb_index_stats 
where   database_name = @statdb
and stat_name not in ( 'size' ,'n_leaf_pages' )
group by 
database_name  ,
table_name  ,
index_name   
) a join innodb_index_stats b on a.database_name=b.database_name
and a.table_name=b.table_name
and a.index_name=b.index_name
and a.stat_name=b.stat_name 
and b.index_name !='PRIMARY'
) a left join 
(
select 
b.database_name  ,
b.table_name  ,
b.index_name ,  
b.stat_value
from 
(
select database_name  ,
table_name  ,
index_name ,  
max(stat_name) stat_name 
from innodb_index_stats 
where   database_name = @statdb
and stat_name not in ( 'size' ,'n_leaf_pages' )
group by 
database_name  ,
table_name  ,
index_name   
) a join innodb_index_stats b 
on a.database_name=b.database_name
and a.table_name=b.table_name
and a.index_name=b.index_name
and a.stat_name=b.stat_name
and b.index_name ='PRIMARY'
) b 
on a.database_name=b.database_name
and a.table_name=b.table_name
where b.stat_value is not null 
and  a.stat_value >0
order by stat_pct;

+---------------+-------------------+--------------+--------+--------+----------+
| database_name | table_name        | index_name   | SK     | PK     | stat_pct |
+---------------+-------------------+--------------+--------+--------+----------+
| zhishutang    | t_json_vs_vchar   | c1vc         |  37326 |  39825 |    93.73 |
| zhishutang    | t_json_vs_vchar   | c2vc         |  37371 |  39825 |    93.84 |
| zhishutang    | t1                | name         | 299815 | 299842 |    99.99 |
| zhishutang    | t4                | c2           |      2 |      2 |   100.00 |
+---------------+-------------------+--------------+--------+--------+----------+
```
