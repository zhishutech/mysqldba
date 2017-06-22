* ## 查看哪些索引长度超过30字节，重点查CHAR/VARCHAR/TEXT/BLOB等类型
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


* ## 查某个表在innodb buffer pool中的new block、old block比例
```
select table_name, count(*), sum(NUMBER_RECORDS), 
 if(IS_OLD='YES', 'old', 'new') as old_block from
 information_schema.innodb_buffer_page where 
 table_name = '`test`.`ts1`' group by old_block;
```
