# 听说JOIN的列类型一定要一样？
### 导读
> 我们在制定表DDL设计规范时，通常都会要求一条：如果有两个表要做JOIN，那么关联条件列类型最好完全一样，才能保证查询效率，真的如此吗？

相信不少朋友主动或被动告知这样一个规范要求（其实我也制定过这个规范），当多表JOIN时，关联条件列类型最好是完全一样的，这样才可以确保查询效率。果真如此吗？

### 关于多表JOIN的几点结论及建议
为了节省大家时间，我先把几点结论写在前面，没耐心的同学可忽略后面测试过程。
- 当被驱动表的列是字符串类型，而驱动表的列类型是非字符串时，则会发生类型隐式转换，无法使用索引；
- 当被驱动表和驱动表的列都是字符串类型，两边无论是 CHAR 还是 VARCHAR，均不会发生类型隐式转换，都可以使用索引；
- 当被驱动表的列是字符串且其字符集比驱动表的列采用的字符集更小或无法被包含时（latin比utf8mb4小，gb2312 比 utf8mb4 小，另外 gb2312 虽然比 latin1 大，但并不兼容，也不行，详见下方测试 ），则会发生类型隐式转换，无法使用索引；
- 综上，虽然有很多场景下，JOIN列类型不一致也能用到索引，但保不准啥时候就掉坑了。因此，最后回答一下本文题目，**JOIN列的类型定义完全一致，包括长度、字符集**。

几点说明
- 测试表t1、t2表均为**UTF8MB4字符集**。
- 字符串类型列char_col默认设置**VARCHAR(20)**。
- 测试MySQL 版本 5.7.18。

**场景1：驱动表列是MEDIUMINT/INT/BIGINT**

子场景 | 驱动表(t1)列 | 被驱动表(t2)列 | 是否可用索引
---|---|---|---
case1.1 | INT | INT | 可用
case1.2 |  INT | CHAR(20) | **不可用**
case1.3 |  INT | VARCHAR(20) | **不可用**
case1.4 | INT | MEDIUMINT | 可用
case1.5 | INT | BIGINT | 可用
case1.6 | MEDIUMINT | INT | 可用
case1.7 | MEDIUMINT | BIGINT | 可用
case1.8 | BIGINT | MEDIUMINT | 可用
case1.9 | BIGINT | INT | 可用

**场景2：驱动列是CHAR(20)**

子场景 | 驱动表(t1)列 | 被驱动表(t2)列 | 是否可用索引
---|---|---|---
case2.1 | CHAR(20) | CHAR(20) | 可用
case2.2 | CHAR(20) UTF8 | CHAR(20) | 可用
case2.3 | CHAR(20) | CHAR(20) UTF8 | **不可用**
case2.4 | CHAR(20) UTF8MB4 | CHAR(20) LATIN1 | **不可用**
case2.5 | CHAR(20) UTF8MB4 | CHAR(20) GB2312 | **不可用**
case2.6 | CHAR(20)  LATIN1 | CHAR(20) UTF8MB4 | 可用
case2.7 | CHAR(20) GB2312 | CHAR(20) UTF8MB4 | 可用
case2.8 | CHAR(20) GB2312 | CHAR(20) LATIN1 | **SQL报错，要先转字符集**
case2.9 | CHAR(20) LATIN1 | CHAR(20) GB2312 | **SQL报错，要先转字符集**
case2.10 | CHAR(20) | VARCHAR(20) | 可用
case2.11 | CHAR(20) | VARCHAR(30) | 可用
case2.12 | CHAR(20) | CHAR(30) | 可用
case2.13 | CHAR(20) | VARCHAR(260) | 可用

**场景3：驱动列是VARCHAR(20)**

子场景 | 驱动表(t1)列 | 被驱动表(t2)列 | 是否可用索引
---|---|---|---
case3.1 | VARCHAR(20) | CHAR(20) | 可用
case3.2 | VARCHAR(20) | VARCHAR(20) | 可用
case3.3 | VARCHAR(20) | VARCHAR(260) | 可用

**场景4：驱动列是VARCHAR(260)/VARCHAR(270)**

子场景 | 驱动表(t1)列 | 被驱动表(t2)列 | 是否可用索引
---|---|---|---
case4.1 | VARCHAR(260) | CHAR(20) | 可用
case4.2 | VARCHAR(260) | VARCHAR(20) | 可用
case4.3 | VARCHAR(260) | VARCHAR(260) | 可用
case4.4 | VARCHAR(260) | VARCHAR(270) | 可用
case4.5 | VARCHAR(270) | VARCHAR(260) | 可用

**场景5：驱动列是VARCHAR(30)**

子场景 | 驱动表(t1)列 | 被驱动表(t2)列 | 是否可用索引
---|---|---|---
case5.1 | CHAR(30) | CHAR(20) | 可用
case5.2 | CHAR(30) | VARCHAR(20) | 可用

**场景6：最后有排序的情况**
最后的排序列不属于驱动表
```
yejr@imysql.com[yejr]> EXPLAIN SELECT * FROM t1 LEFT JOIN
	t2 ON (t1.int_col = t2.int_col) WHERE
	t1.id >= 5000 ORDER BY t2.id\G
*************************** 1. row ***************************
id: 1
select_type: SIMPLE
table: t1
partitions: NULL
type: range
possible_keys: PRIMARY
key: PRIMARY
key_len: 8
ref: NULL
rows: 51054
filtered: 100.00
Extra: Using where; Using temporary; Using filesort
*************************** 2. row ***************************
id: 1
select_type: SIMPLE
table: t2
partitions: NULL
type: ref
possible_keys: int_col
key: int_col
key_len: 4
ref: yejr.t1.int_col
rows: 10
filtered: 100.00
Extra: NULL
```
小结：**当最后的排序列不属于驱动表时，则会生成临时表，且又有额外排序**。

最后的排序列属于驱动表
```
yejr@imysql.com[yejr]> EXPLAIN SELECT * FROM t1 LEFT JOIN
	t2 ON (t1.int_col = t2.int_col) WHERE
	t1.id >= 5000 ORDER BY t1.id\G
*************************** 1. row ***************************
id: 1
select_type: SIMPLE
table: t1
partitions: NULL
type: range
possible_keys: PRIMARY
key: PRIMARY
key_len: 8
ref: NULL
rows: 51054
filtered: 100.00
Extra: Using where
*************************** 2. row ***************************
id: 1
select_type: SIMPLE
table: t2
partitions: NULL
type: ref
possible_keys: int_col
key: int_col
key_len: 4
ref: yejr.t1.int_col
rows: 10
filtered: 100.00
Extra: NULL
```
小结：**当最后的排序列属于驱动表时，则不会生成临时表，也不需要额外排序**。

更多的组合测试场景，请各位亲自行完成哈。

### 附录 ###
测试表DDL
```
CREATE TABLE `t1` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `int_col` int(20) unsigned NOT NULL DEFAULT '0',
  `char_col` char(20) NOT NULL DEFAULT '',
...
  PRIMARY KEY (`id`),
  KEY `int_col` (`int_col`),
  KEY `char_col` (`char_col`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4

CREATE TABLE `t2` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `int_col` int(8) unsigned NOT NULL DEFAULT '0',
  `char_col` char(20) NOT NULL DEFAULT '',
...
  PRIMARY KEY (`id`),
  KEY `int_col` (`int_col`),
  KEY `char_col` (`char_col`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
```

修改列字符集定义的DDL样例
```
/*
- 只修改长度
*/
ALTER TABLE t1 MODIFY char_col 
	VARCHAR(260) NOT NULL DEFAULT '';

/*
- 同时修改字符集
*/
ALTER TABLE t2 MODIFY char_col
	VARCHAR(20) CHARACTER SET UTF8 NOT NULL DEFAULT '';
```

修改完列定义后，还记得要重新执行 ANALYZE TABLE 重新统计索引信息哟。
```
yejr@imysql.com[yejr]> ANALYZE TABLE t1, t2;
+---------+---------+----------+----------+
| Table   | Op      | Msg_type | Msg_text |
+---------+---------+----------+----------+
| yejr.t1 | analyze | status   | OK       |
| yejr.t2 | analyze | status   | OK       |
+---------+---------+----------+----------+
```

执行测试的SQL样例
```
/*
- char_col 可以自行替换成 int_col
- 加上 t1.id >= 5000 是为了避免预估扫描数据量太多，变成全表扫描
*/
EXPLAIN SELECT * FROM t1 LEFT JOIN
	t2 ON (t1.char_col = t2.char_col) WHERE
	t1.id >= 5000\G
```

**参考**

- [UTF8字符集的表怎么直接转UTF8MB4？](http://mp.weixin.qq.com/s?__biz=MjM5NzAzMTY4NQ==&mid=2653930515&idx=1&sn=edc341d36f076e379ea71903e31762a0&chksm=bd3b5e798a4cd76fd63e7f6c9f47eaca47cf66761c6c24479d170a16b1934f139278896658e5&scene=21#wechat_redirect)
- [细说ANALYZE TABLE](http://mp.weixin.qq.com/s?__biz=MjM5NzAzMTY4NQ==&mid=2653930467&idx=1&sn=2511653a476245e96389655fd670671e&chksm=bd3b59898a4cd09f2e2823d75f9d0f3acd76442b547bede0178130bc202f79927c1ac1b6dde3&scene=21#wechat_redirect)
- [优化系列 | DELETE子查询改写优化](http://mp.weixin.qq.com/s?__biz=MjM5NzAzMTY4NQ==&mid=2653928676&idx=1&sn=c8d1f5f12f234738bdf6da844ab4994e&scene=21#wechat_redirect)
- [MySQL优化案例系列 — 分页优化](http://mp.weixin.qq.com/s?__biz=MjM5NzAzMTY4NQ==&mid=207345129&idx=1&sn=0c0ab0a302f0c963845544545ce7f893&scene=21#wechat_redirect)
- [MySQL优化案例系列 — discuz!热帖翻页优化](http://mp.weixin.qq.com/s?__biz=MjM5NzAzMTY4NQ==&mid=207345129&idx=2&sn=a37781cc9a73d145c11f396d289c9955&scene=21#wechat_redirect)
