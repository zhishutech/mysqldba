#!/bin/bash
##
## 用sysbench执行MySQL OLTP基准测试的脚本。
## 
## 叶金荣, 知数堂培训联合创始人, 资深MySQL专家, MySQL布道师, Oracle MySQL ACE
## 
## 几个注意事项：
## 1、运行tpcc的客户机和MySQL DB服务器尽量不要在同一台主机上，也包括一台宿主机上启动两个虚机的情形；
## 2、tpcc仓库数不宜太少，通常至少要求1千个以上，当仓库数太少的话，tpcc压测时，warehouse表会成为最大行锁等待瓶颈。
##    当然了，也要根据DB服务器的配置适当调整；
## 3、每次进行基准压测的时长不宜过短，通常要求持续15分钟以上；
## 4、每轮测试完毕后，中间至少暂停5分钟，或者确认系统负载完全恢复空跑状态为止；
## 5、测试DB服务器要是专用的，不能和其他业务混跑，否则测试结果就不靠谱了；
## 6、其余未尽事宜，后续再行补充。
##
## created by yejinrong@zhishutang.com
## 2017/6/3
##
## 老叶改造后的tpcc-mysql项目地址： http://github.com/yejr/tpcc-mysql-autoinc-pk
## 原生tpcc-mysql项目地址： https://github.com/Percona-Lab/tpcc-mysql
##

export LD_LIBRARY_PATH=/usr/local/mysql/lib/

. ~/.bash_profile

# 需要启用DEBUG模式时将下面三行注释去掉即可
#set -u
#set -x
#set -e

BASEDIR="/data/tpcc-mysql/"
cd $BASEDIR

exec 3>&1 4>&2 1>> run_tpcc.log 2>&1

DBIP=10.10.10.1
DBPORT=3306
DBUSER='yejr'
DBPASSWD='yejr'
WAREHOUSE=1000
DBNAME="tpcc${WIREHOUSE}"
WARMUP=300
DURING=900
# 并发压测的线程数，根据机器配置实际情况进行调整
RUN_NUMBER="8 64 128 256 512 768 1024 1664 2048 4096"

# prepare data
# ./tpcc_load $DBIP:$DBPORT $DBNAME $DBUSER $DBPASSWD $WIREHOUSE

round=1
# 一般至少跑3轮测试，我正常都会跑10轮以上
while [ $round -lt 4 ]
do

NOW=`date +'%Y%m%d%H%M'`
rounddir=logs-round${round}
mkdir -p ${rounddir}


for thread in `echo "${RUN_NUMBER}"`
do

./tpcc_start -h ${DBIP -P ${DBPORT} -d ${DBNAME} -u ${DBUSER} -p "${DBPASSWD}" -w ${WAREHOUSE} -c ${THREADS} -r ${WARMUP} \
-l ${DURING} -i 1 > ${rounddir}/tpcc_${THREADS}.log 2>&1

sleep 300
done

round=`expr $round + 1`
sleep 300
done
