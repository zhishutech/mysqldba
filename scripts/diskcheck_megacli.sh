#!/bin/bash
#zabbix监控硬盘信息脚本
#By xiangjunyu 20151101

. ~/.bash_profile > /dev/null

#获取磁盘信息
/opt/MegaRAID/MegaCli/MegaCli64 -Pdlist -a0|grep -Ei '(Slot Number|Media Error Count|Other Error Count|Predictive Failure Count|Raw Size|Firmware state)'|sed -e "s:\[0x.*Sectors\]::g" >/tmp/pdinfo.txt

#将每块磁盘信息拆分，进行逐盘分析
split -l 6 -d /tmp/pdinfo.txt /tmp/pdinfo

#获取磁盘数量（实际数量=PDNUM+1）
PDNUM=`/opt/MegaRAID/MegaCli/MegaCli64 -PDGetNum -aAll|grep Physical|awk '{ print $8 }'`

#磁盘分块后文件名规范统一化
for((i=0;i<${PDNUM};i++))
do
mv /tmp/pdinfo0${i} /tmp/pdinfo${i} >/dev/null 2>&1
#ls /tmp/pdinfo${i}
done
SLOT_NUM=$2
DATAFORMATE()
{
while read LINE
    do
        if [[ ${LINE} == Slot* ]];
            then
            SLOTNUMNAME=`echo ${LINE}|awk -F: '{ print $1 }'`
            SLOTNUM=`echo ${LINE}|awk -F: '{ print $2 }'`
        elif [[ ${LINE} == Media* ]];
            then
            MECNAME=`echo ${LINE}|awk -F: '{ print $1 }'`
            MEC=`echo ${LINE}|awk -F: '{ print $2 }'`
        elif  [[ ${LINE} == Other* ]];
            then
            OECNAME=`echo ${LINE}|awk -F: '{ print $1 }'`
            OEC=`echo ${LINE}|awk -F: '{ print $2 }'`
        elif  [[ ${LINE} == Predictive* ]];
            then
            PFCNAME=`echo ${LINE}|awk -F: '{ print $1 }'`
            PFC=`echo ${LINE}|awk -F: '{ print $2 }'`
        elif [[ ${LINE} == Raw* ]];
            then
            RAWNAME=`echo ${LINE}|awk -F: '{ print $1 }'`
            SIZE=`echo ${LINE}|awk -F: '{ print $2 }'`
        elif [[ ${LINE} == Firmware* ]];
            then
            FIRMWARENAME=`echo ${LINE}|awk -F: '{ print $1 }'`
            FIRMWARESTATUS=`echo ${LINE}|awk -F: '{ print $2 }'`
        fi
    done </tmp/pdinfo${SLOT_NUM}
}

#检测阵列等级状态
CHECKRAIDLEVEL()
{
/opt/MegaRAID/MegaCli/MegaCli64  -LDInfo -Lall -aALL|grep Degraded
if [ $? = 0 ]
then
echo -1
else
echo 0
fi
}
OPTION=$1
case $OPTION in
    mec) DATAFORMATE
         echo ${MEC}
         ;;
    oec) DATAFORMATE
         echo ${OEC}
         ;;
    pfc) DATAFORMATE
         echo ${PFC}
         ;;
    firm)
         DATAFORMATE
         if [[ "$FIRMWARESTATUS{}" = "Unconfigured(bad)" ]]
         then
             echo -1
         elif [[ "$FIRMWARESTATUS{}" = "Failed" ]]
         then
             echo -1
         else
            echo 0
        fi
         ;;
    rdlevel)
         CHECKRAIDLEVEL
         ;;
    *) echo "Please select option: mec $slot_num ;oec $slot_num;pfc $slot_num;firm $slot_num;rdlevel"
esac

rm -rf /tmp/pdinfo*
