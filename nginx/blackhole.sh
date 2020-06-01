#!/bin/bash
## 
## 搜索nginx access log，发现一些不安全的请求URL时，将请求IP加到路由黑洞中
## 本想重新编译nginx + ModSecurity，但编译时报错，懒得折腾，就写个脚本先做简单处理
##
## created by yejinrong@zhishutang.com
## 2020/6/1

. ~/.bash_profile

## 定义nginx log路径
logdir=/logs/nginx

## 记录ip路由黑洞文件
iplist=ip-route.txt

## 扫描最近的1000行日志，可以自定义大小
ln=1000

cd $logdir

exec 3>&1 4>&2 1>> blackhole.log 2>&1

date
## 扫描所有access log
for f in `ls *access*log`
do
## 搜索关键字
  if [ ! -z "`tail -n $ln $f | egrep -i 'base64.*code|union.*select|eval\(|sleep.*28.*29'`" ] ; then
    echo "checking logs..."
    tail -n $ln $f | egrep -i 'base64.*code|union.*select|eval\(|sleep.*28.*29'

## 如果符合条件就加入黑名单
    for ip in `tail -n $ln $f | egrep -i 'base64.*code|union.*select|eval\(|sleep.*28.*29' | awk '{print $1}' | sort -u`
    do
## 排除本机等白名单    
      if [ -z "`grep '^$ip\$' $iplist`" ] && [ $ip != "yejr.run" ] && [ $ip != "127.0.0.1" ] ; then
        echo "adding to blackhole list..."
	/sbin/ip route add blackhole $ip
      fi
    done
  fi
done

# 导出所有列表
/sbin/ip route | grep blackhole  | awk '{print $2}' > $iplist

date
echo
echo
echo
