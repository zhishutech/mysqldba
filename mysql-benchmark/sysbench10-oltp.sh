#!/bin/bash
##
## 用sysbench执行MySQL OLTP基准测试的脚本。
##
## 叶金荣, 知数堂培训联合创始人, 资深MySQL专家, MySQL布道师, Oracle MySQL ACE
##
## 几个注意事项：
## 1、运行sysbench的客户机和MySQL DB服务器尽量不要在同一台主机上，也包括一台宿主机上启动两个虚机的情形；
## 2、测试表的数量不宜太少，至少要求20个表以上；
## 3、每个表的数据量不宜太少，通常至少要求1千万以上，当然了，也要根据DB服务器的配置适当调整；
## 4、每次进行基准压测的时长不宜过短，通常要求持续15分钟以上；
## 5、每轮测试完毕后，中间至少暂停5分钟，或者确认系统负载完全恢复空跑状态为止；
## 6、测试DB服务器要是专用的，不能和其他业务混跑，否则测试结果就不靠谱了；
## 7、其余未尽事宜，后续再行补充。
##
## created by yejinrong@zhishutang.com
## 2017/6/3
##
## sysbench项目地址： https://github.com/akopytov/sysbench
##

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
#清理之前的遗留记录
rm -rf $BASEDIR/logs*
# 记录所有错误及标准输出到 sysbench.log 中
exec 3>&1 4>&2 1>> sysbench.log 2>&1

#时间单位秒
DBIP=192.168.1.109
DBPORT=3109
DBUSER='proxysql'
DBPASSWD='123456'
NOW=`date +'%Y%m%d%H%M'`
DBNAME="sysbench"
REPORT_INTERVAL=1
TBLCNT=10
WARMUP=300
DURING=1800
ROWS=10000000
MAXREQ=1000000

# 并发压测的线程数，根据机器配置实际情况进行调整
THERAD_NUMBER="8 64 128"

#初始次数
round=0
# 一般至少跑3轮测试，我正常都会跑10轮以上
while [ $round -lt 4 ]
do
#每回合日志位置：
rounddir=$BASEDIR/logs-round${round}
mkdir -p ${rounddir}

for thread in `echo "${THERAD_NUMBER}"`
do
#常用可选项：
#oltp_read_only
#oltp_read_write
#oltp_update_non_index
sysbench /usr/share/sysbench/oltp_read_only.lua \
  --mysql-host=$DBIP \
  --mysql-port=$DBPORT \
  --mysql-user=$DBUSER \
  --mysql-password=$DBPASSWD \
  --mysql-db=$DBNAME \
  --db-driver=mysql \
  --tables=$TBLCNT \
  --table-size=$ROWS \
  --report-interval=$REPORT_INTERVAL \
  --threads=${thread} \
  --rand-type=uniform \
  --time=$DURING run >> ${rounddir}/sysbench_${thread}.log


sleep 300
done

round=`expr $round + 1`
sleep 300
done
