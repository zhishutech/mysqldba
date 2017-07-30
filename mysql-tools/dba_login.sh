#!/bin/bash
##
## MySQL DBA登入服务器后, 建议关注的一些重要信息, 欢迎分享及补充。
## 
## 叶金荣, 知数堂培训联合创始人, 资深MySQL专家, MySQL布道师, Oracle MySQL ACE
## 
## created by yejinrong@zhishutang.com
## 2017/5/22
##

echo
echo "Welcome to MySQL Server, make sure all of the check result is OK"
echo

. ~/.bash_profile
#1. check who is login
echo "#1# check who is login"
w
echo
echo

#2. check system's load and others
echo "#2# check disk free"
df -hT | grep -v 'Filesystem.*Type.*Size'|sort -rn -k 6|head -n 3
echo
echo

echo "#3# check memory and swap"
echo "show memory & swap usage, check if memory leak"
free -h
echo
echo

#3. check which prog's load is high
echo "#4# check which prog's load is high"
ps -eo pid,pcpu,size,rss,cmd | sort -rn -k 2 | head -n 5 | grep -iv 'PID.*CPU.*SIZE'
echo
echo

#4. check mysql status
echo "#5# check MySQL status"
mysqladmin pr | egrep -v 'Sleep|\-\-\-\-\-' | sort -rn -k 12 | head -n 5
