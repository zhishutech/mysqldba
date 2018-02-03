#!/bin/sh
export LD_LIBRARY_PATH=/usr/local/mysql/lib/

. ~/.bash_profile

# 需要启用DEBUG模式时将下面三行注释去掉即可
#set -u
#set -x
#set -e

BASEDIR="/data/sysbench"
if [ ! -d $BASEDIR ]
then
   mkdir $BASEDIR -p
fi
cd $BASEDIR

# 记录所有错误及标准输出到 sysbench.log 中
#exec 3>&1 4>&2 1>> sysbench_prepare.log 2>&1

DBIP=192.168.1.109
DBPORT=3109
DBUSER='proxysql'
DBPASSWD='123456'
NOW=`date +'%Y%m%d%H%M'`
DBNAME="sysbench"
TBLCNT=10
WARMUP=300
DURING=1800
ROWS=10000000
MAXREQ=1000000

#create db
echo 'now create db'
mysql -h$DBIP -P$DBPORT -u$DBUSER -p$DBPASSWD -e 'create database sysbench'
echo 'create ok'
## prepare data
echo 'now prepare data'
 sysbench /usr/share/sysbench/oltp_read_only.lua \
 --mysql-host=$DBIP \
 --mysql-port=$DBPORT \
 --mysql-user=$DBUSER \
 --mysql-password=$DBPASSWD \
 --mysql-db=$DBNAME \
 --db-driver=mysql \
 --tables=10 \
 --table-size=$ROWS \
 --time=$DURING prepare
