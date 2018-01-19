#!/usr/bin/env python
#coding=utf-8
import paramiko
import os
import subprocess
import string
import time
import datetime
import math
import multiprocessing
import threading
import Queue
import pickle
import json
import sys
import re
import getopt
import struct 
from socket import *

class SockThread(threading.Thread):
	ADDR = None
	msg_queue  = None
	out_queue  = None
	clientsock = 0
	recvThread = 0
	isworking  = 0

	def __init__(self, threadName, host='192.168.254.24', port=40001):
		super(SockThread, self).__init__(name=threadName)
		self.ADDR = (host, port)

	def __del__(self):
		if self.msg_queue:
			del self.msg_queue
		if self.clientsock:
			self.clientsock.close()

	def run(self):
		'''Start Thread, Socket, Queues'''
		self.msg_queue  = Queue.Queue()
		self.out_queue  = Queue.Queue()
		self.clientsock = socket(AF_INET, SOCK_STREAM)
		try:
			self.clientsock.connect(self.ADDR) 
		except Exception,e:    
			print "Socket connection setup failure."
			self.isworking = -1
			return 
		self.recvThread = threading.Thread(target = self._recvSock, args = (self.clientsock, None)) 
		self.recvThread.setDaemon(True)
		self.recvThread.start()
		self.isworking = 1
		while True:
			try:
				next_msg = self.msg_queue.get() 
			except Queue.Empty:  
				print 'queue empty'  
			else:  
				print "Sending>>> " , next_msg
				data = json.dumps(next_msg)
				header = struct.pack("i",int(len(data)+4))
				self.clientsock.send(header+data) 
				if(next_msg[0]=='quit'):
					time.sleep(3)
					break
		self.clientsock.close()

	def _recvSock(self, sock, test): 
		dataBuffer = bytes()
		while True:  
			try:
				data = sock.recv(1024)  
				if data:  
					dataBuffer += data
					while True:
						if len(dataBuffer)<4:
							break
						length = struct.unpack("i",dataBuffer[0:4])
						if len(dataBuffer)<length[0]:
							break
						body=dataBuffer[4:length[0]]
						if not self.processRet(body):
							print "Normally close socket."  
							sock.close()
							return
						dataBuffer=dataBuffer[length[0]:]
				else:  
					print "Close socket."  
					sock.close()
					break
			except:
				print "Socket receiving Error.."
				sock.close()
				break

	def processRet(self, data):
		try:
			ret = json.loads(data)
		except Exception,e:
			print e
			return False
		self.out_queue.put(ret)
		return True

	def sendCommand(self, command):
		if not command: return
		if not self.msg_queue:
			time.sleep(3)
		self.msg_queue.put(command)
	
	def dosendcmd(self, command, socktask):
		while (socktask.isworking == 0):
			time.sleep(3)
		if (socktask.isworking == 1):
			socktask.sendCommand(command)
			
	def getresult(self, socktask):
		output = socktask.out_queue.get()
		print 'Feedback:', output
		time.sleep(5)
		return output
		
if __name__ == "__main__":
	socktask = SockThread('connectionToCPEPC','192.168.254.174')
	socktask.setDaemon(True)
	socktask.start()
	while(socktask.isworking==0):
		time.sleep(3)
	if(socktask.isworking==1):
		command = ['109.10.10.24','ATTACH',['192.168.254.220','ODU',44450,84]]
		socktask.sendCommand(command)
		output = socktask.out_queue.get()
		print 'Feedback:',output
		time.sleep(3)

		params = ['192.168.254.220',120,'ftpuser','test888',3,'','D:/Autotest/Ftpdat/','autodn',2,'','D:/Autotest/Ftpdat/','autoup']
		# command = ['109.10.10.24','BOTH',params]
		command = ['109.10.10.24','ATTACH',['192.168.254.220','ODU',44450,86]]
		socktask.sendCommand(command)
		output = socktask.out_queue.get()
		print 'Feedback:',output
		time.sleep(3)

		command = ['quit']
		socktask.sendCommand(command)
		time.sleep(3)