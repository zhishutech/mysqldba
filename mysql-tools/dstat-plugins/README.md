## 如何使用
`[root@izbp12nspj47ypto9t6vyez dstat-plugins]# cp * /usr/share/dstat/`

## 环境变量
`export DSTAT_MYSQL=" -uroot -pxuclxucl -S /tmp/mysql3306.sock"`
`export DSTAT_MYSQL_USER='root'`
`export DSTAT_MYSQL_PWD='xuclxucl'`
`export DSTAT_MYSQL_HOST='127.0.0.1'`
`export DSTAT_MYSQL_PORT=3306`

## dstat
`dstat --list`可以看到新增的`--innodb-checkpoint` `--innodb-list` `--mysql5-rowlockwaits`
- innodb-checkpoint:查看checkpoint落后
- innodb-list:查看unpurged list和free list
- mysql5-rowlockwaits:查看mysql行锁等待

## 示例
```
[root@izbp12nspj47ypto9t6vyez mysql-tools]# dstat --innodb-checkpoint --innodb-list --mysql5-rowlockwaits
--------------------innodb-checkpoint-lags-------------------- --innodb-list-length- -------innodb-lock-waits-------
        LSN1                 LSN4                 LAG         | unpurged     free   | current_waits    total_waits  
         1410769156           1410769147                    9 |       41          0 |              0               0
         1410769156           1410769147                    9 |       41          0 |              0               0
         1410769156           1410769147                    9 |       41          0 |              0               0
         1410769156           1410769147                    9 |       41          0 |              0               0
```
