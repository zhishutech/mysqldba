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
> - undo不能被及时purge，undu表空间不断增长；
> - 持有行锁，其他事务被阻塞。
> 应该及时提交或回滚这些事务，或者直接kill释放之。
>
> 参考：
> - FAQ系列 | 如何避免ibdata1文件大小暴涨
> - 是谁，把InnoDB表上的DML搞慢的？
```
select b.host, b.user, b.db, b.time, b.COMMAND, 
 a.trx_id, a. trx_state from 
 information_schema.innodb_trx a left join 
 information_schema.PROCESSLIST b on a.trx_mysql_thread_id = b.id;
```


* ## 检查哪些表没有显式创建主键索引
> 优化建议：
> - 选择自增列做主键；
> - 或者其他具备单调递增特点的列做主键；
> - 主键最好不要有业务用途，避免后续会更新。
>
> 参考：
> - [MySQL FAQ]系列 — 为什么InnoDB表要建议用自增列做主键
```
SELECT
a.TABLE_SCHEMA,
a.TABLE_NAME
FROM
(
SELECT
TABLE_SCHEMA,
TABLE_NAME
FROM
information_schema. TABLES
WHERE
TABLE_SCHEMA NOT IN (
'mysql',
'information_schema',
'performance_schema'
)
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


* ## 查某个表在innodb buffer pool中的new block、old block比例
```
select table_name, count(*), sum(NUMBER_RECORDS), 
 if(IS_OLD='YES', 'old', 'new') as old_block from
 information_schema.innodb_buffer_page where 
 table_name = '`test`.`ts1`' group by old_block;
```
