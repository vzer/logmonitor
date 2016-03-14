#!/usr/bin/env python
#coding=utf-8
#filename:monitorLogs
#used：monitor the kafka storm flume

__author__ = 'vzer'
import os
import string
import commands
import socket
import paramiko
import re
import getpass
import logging
import pxssh
import  datetime
import subprocess
import smtplib
from email.mime.text import MIMEText
import  MySQLdb

mailto_list=['zhangcunlei@xiniunet.com ']
mail_host="mail.xiniunet.com"
mail_user="zhangcunlei@xiniunet.com"
mail_pass="wwwlin123"
mail_postfix="xiniunet.com"

#senf mail method
def send_mail(to_list,sub,content):
    me="ElasticSearch-Mail"+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText(content,_subtype='plain',_charset='utf-8')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user,mail_pass)
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except Exception, e:
        print str(e)
        return False

'''
功能：有色输出
参数：
    color:颜色代码
        "Red,Yellow,Blue,Green"
    text:要输出的文本
	flag:输出不换行标识
返回值：
    None

'''
def printColor(color,text,flag = False):
	colour = color.lower()
	if colour == 'red':
		if flag:
			iText = '\033[1;31;40m%s\033[0m' %text
			print (iText),
		else:
			print '\033[1;31;40m%s\033[0m' %text
	elif colour == 'yellow':
		if flag:
			iText = '\033[1;33;40m%s\033[0m'
			print (iText),
		else:
			print '\033[1;33;40m%s\033[0m' %text
	elif colour == 'blue':
		if flag:
			iText = '\033[1;34;40m%s\033[0m' %text
			print (iText),
		else:
			print '\033[1;34;40m%s\033[0m' %text
	elif colour == 'green':
		if flag:
			iText = '\033[1;32;40m%s\033[0m' %text
			print (iText),
		else:
			print '\033[1;32;40m%s\033[0m' %text
	elif colour == 'purple':
		if flag:
			iText = '\033[1;35;40m%s\033[0m' %text
			print (iText),
		else:
			print '\033[1;35;40m%s\033[0m' %text
	else:
		print text

def pxsshWork(hostname,username,password,cmd):
    try:
        sshClient=pxssh.pxssh()
        sshClient.login (hostname, username, password, original_prompt='[$#>]')
        sshClient.sendline (cmd)
        sshClient.prompt()
        result=sshClient.before
        #printColor('green',result)
        sshClient.logout()
        return result
    except pxssh.ExceptionPxssh,msg:
        printColor('red','login failed')
        printColor('red',str(msg))
        return False
    except Exception,msg:
        printColor('red','not kown error')
        printColor('red',str(msg))
        return  False

#查询后台进程，返回pid号
def queryService(hostname,username,password):
    try:
        result=pxsshWork(hostname,username,password,'jps -l |grep com.alibaba.dubbo.container.Main')
        regex=re.compile('jps -l|grep com.alibaba.dubbo.container.Main\r\n(.*)\r\n').findall(result)
        result=''.join(regex)
        printColor('yellow','###########################################################')
        printColor('green',result)
        pid=re.findall('(\d+) com.alibaba.dubbo.container.Main',result)
        return ''.join(pid)
    except Exception,msg:
        printColor('red','not kown error')
        printColor('red',str(msg))
        return False


