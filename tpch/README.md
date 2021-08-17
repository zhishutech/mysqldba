# tpc-h for mysql

参考文章：https://imysql.com/2012/12/21/tpch-for-mysql-manual.html

本项目是我已经修改后的可以用来运的各个SQL脚本，需要的自取。
有问题的话，请提issue。

## 编译
1. 安装gcc
```
$ yum install -y gcc
```

2. 编译
```
$ cd TPC-H_Tools_v3.0.0/dbgen/
$ make
```
## 使用
1. 创建测试库表
```
$ mysql -f < SQLs/tpch-ddl.sql
```

2. 生成测试数据
```
$ cd TPC-H_Tools_v3.0.0/dbgen/
$ ./dbgen -vf -s 1 #一般建议至少10或50、100等，产生足够数据量
```

3. 导入测试数据
```
mysql> load data infile 'path/region.tbl' into table region;
```
其他表同理。
