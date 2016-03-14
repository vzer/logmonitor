#!/usr/bin/env python
#coding=utf-8
#filename:monitorZookeeper
#used：monitor the Zookeeper process
__author__ = 'vzer'

import os
import string
import re
import datetime
import subprocess
import sys
import redis
import socket
import time

def shellCmd(cmd):
    process = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
    (processStdout,processStderr) = process.communicate()
    retcode = process.poll()
    if retcode:
        return (retcode,processStderr)
    return (retcode,processStdout)

def startProcess(processName,cmd,path):
    os.chdir(path)
    try:
        print('Start the %s.....  '%processName)
        (status,result)=shellCmd(cmd)
        if status==0:
            print  result
            print '%s is start ok.'%processName
            return True
        else:
            print 'command is error,Messages:%s'%result
            return False
    except Exception,msg:
        print('commit is error.')
        print(msg)

#查询进程，返回pid号
def queryProcess(processName,cmd):
    print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print 'Query %s Status'%processName
    try:
        (status,result)=shellCmd('/usr/java/jdk1.7.0_65/bin/jps -l|grep '+cmd)
        if status==0:
            pid=re.findall('(\d+) %s'%cmd,result)
            print 'status:ok------pid:%s'%''.join(pid)
            return ''.join(pid)
        else:
            if result=='':
                print 'status: not ok------pid:NULL'
                return ''
            else:
                print'command is error,Messages:%s'%result
                #print (status,result)
    except Exception,msg:
        print('commit is error.')
        print(msg)


def Insertredis(topic,context):
    try:
        rc=redis.Redis(host='10.162.74.244',port=6379,db=0)
        rc.publish(topic,context)
        return 0
    except Exception,msg:
        print msg
        return 1

def buildContext(type=None,ServiceName=None,state=None,pid=None):
    hostname=socket.gethostname()
    ipaddress=socket.gethostbyname(hostname)
    context='*********** XINIU LOG SERVER MONITOR ***********\n\n'
    context=context+'Notification Type: %s\n\n'%type
    context=context+'Service: %s\n'%ServiceName
    context=context+'Host: %s\n'%hostname
    context=context+'Address: %s\n'%ipaddress
    context=context+'State: %s\n\n'%state
    context=context+'Date/Time: %s\n\n'%datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    context=context+'Additional Info:\n'
    if state=='CRITICAL':
        context=context+'%s is death\n'%ServiceName
    elif state=='OK':
        context=context+'%s is starting, new pid is %s\n'%(ServiceName,pid)
    context=context+'************************************************\n'
    return context




if __name__=="__main__":
    '''
    elasticsearchPath='/root'
    elasticsearchName='Elasticsearch'
    elasticsearchQueryCmd='org.elasticsearch.bootstrap.Elasticsearch'
    elasticsearchStartCmd='/etc/init.d/elasticsearch start'
    '''
    Path='/root'
    Name='Elasticsearch'
    QueryCmd='org.elasticsearch.bootstrap.Elasticsearch'
    StartCmd='/etc/init.d/elasticsearch start'

    print '--------------------------%s Monitor-----------------------------'%Name
    pid=queryProcess(Name,QueryCmd)
    print '----------------------------------------------------------------------------'
    if pid=='':
        context=buildContext(type='PROBLEM',ServiceName=Name,state='CRITICAL')
        Insertredis('monitor',context)
        startProcess(Name,StartCmd,Path)
        print '----------------------------------------------------------------------------'
        time.sleep(1)
        pid=queryProcess(Name,QueryCmd)
        context=buildContext(type='RECOVERY',ServiceName=Name,state='OK',pid=pid)
        Insertredis('monitor',context)

    '''print '------------------------------Kafka Monitor---------------------------------'
    pid=queryProcess(kafkaName,kafkaQueryCmd)
    print '----------------------------------------------------------------------------'
    if pid=='':
        startProcess(kafkaName,kafkaStartCmd,kafkaPath)
        print '----------------------------------------------------------------------------'
        pid=queryProcess(kafkaName,kafkaQueryCmd)
    '''