#!/usr/bin/env python
#coding=utf-8
from ctypes import *
from socket import *
import paramiko
import subprocess
import multiprocessing
import threading
import time
import json
import sys
import re
import os
import struct 
import _cffi_backend
import mul_process_package

hoolog = "D:/Autotest/Logs/hoonetmeter.txt"

class CpePCMain:
	port = None
	threadDict = {}
	mqueue = multiprocessing.Queue()

	def __init__(self, port=40001):
		self.port  = port

	def run(self):
		if not self.startHooMeter():
			print "HooNetMeter does not work normally."
			return
		print "Server is starting"
		serversock = socket(AF_INET, SOCK_STREAM)
		serversock.bind(('', self.port))
		serversock.listen(1)
		quitThread = threading.Thread(target = self._quitapp, args = ('quit',)) 
		quitThread.start()
		while True: 
			conn, address = serversock.accept()
			try:
				#conn.settimeout(500) 
				recvThread = threading.Thread(target = self._recvSock, args = (conn, None)) 
				recvThread.setDaemon(True)
				recvThread.start()
				print "New connection is ready"
				while True:
					try:
						next_msg = self.mqueue.get() 
					except self.mqueue.Empty:
						print " ", conn.getpeername() , 'queue empty'  
						break
					else:  
						data = json.dumps(next_msg)
						header = struct.pack("i",int(len(data)+4))
						print "Feedback>>> " , next_msg
						conn.send(header+data) 
						if (next_msg[0]=='quit'):
							break
			except Exception,e:
				print e,'Time out'
				break
			conn.close()
		serversock.close()

	def _quitapp(self, test): 
		while True:
			data = raw_input('> ')
			if data == 'quit':
				self.mqueue.put(['quit'])
				os.system("taskkill /f /im HooNetMeter.exe" + " 1>NUL 2>&1") 
				time.sleep(2)
				os._exit(0)

	def _recvSock(self, sock, test): 
		dataBuffer = bytes()
		while True:  
			try:
				data = sock.recv(1024)  
				if data:  
					dataBuffer += data
					while True:
						if len(dataBuffer)<4:
							break;
						length = struct.unpack("i",dataBuffer[0:4])
						if len(dataBuffer)<length[0]:
							break;
						body=dataBuffer[4:length[0]]
						if not self.parseCmd(body):
							print "Normally close socket."  
							self.mqueue.put(['quit'])
							time.sleep(3)
							sock.close()
							return;
						dataBuffer=dataBuffer[length[0]:]
				else: 
					print "No data received, closing socket."  
					sock.close()
					break
			except Exception,e:
				#print e
				print "Socket Disconnected."
				sock.close()
				break

	def parseCmd(self, data):
		print 'Received CMD:',data
		try:
			command = json.loads(data)
		except Exception,e:
			print e
			return False
		if command[0]=='quit':
			return False
		try:
			opProcess = multiprocessing.Process(args=(command,self.mqueue),target=self.processCmd)
			opProcess.start()
			self.threadDict[command[0]]=opProcess
		except Exception,e:
			print 'parseCmd:',e
			return False
		return True

	def processCmd(self, command, queue):
		try:
			result = CpeControl().main(command)
			#print 'result to be return:',result
			queue.put([command[0],command[1],result])
		except Exception,e:
			print 'processCmd:',e
			return False

	def startHooMeter(self,prc_name='HooNetMeter'):
		try:
			os.system("taskkill /f /im " + prc_name+".exe" + " 1>NUL 2>&1") 
			time.sleep(2)
			if os.path.exists(hoolog):
				os.remove(hoolog)
			for i in range(5):
				if self.checkHooMeter(prc_name):
					return True
				else:
					subprocess.Popen(prc_name+".exe")
				time.sleep(1)
			return False
		except Exception,e:
			print e
			return False

	def checkHooMeter(self,prc_name):
		psapi = windll.psapi		#PSAPI.DLL
		kernel = windll.kernel32	#Kernel32.DLL
		arr = c_ulong * 256
		lpidProcess= arr()
		cb = sizeof(lpidProcess)
		cbNeeded = c_ulong()
		hModule = c_ulong()
		count = c_ulong()
		modname = c_buffer(30)
		PROCESS_QUERY_INFORMATION = 0x0400
		PROCESS_VM_READ = 0x0010
		#Call Enumprocesses to get hold of process id's
		psapi.EnumProcesses(byref(lpidProcess), cb, byref(cbNeeded))
		#Number of processes returned
		nReturned = cbNeeded.value/sizeof(c_ulong())
		pidProcess = [i for i in lpidProcess][:nReturned]
		for pid in pidProcess:
			#Get handle to the process based on PID
			hProcess = kernel.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
			if hProcess:
				psapi.EnumProcessModules(hProcess, byref(hModule), sizeof(hModule), byref(count))
				psapi.GetModuleBaseNameA(hProcess, hModule.value, modname, sizeof(modname))
				processName = "".join([ i for i in modname if i != '\x00'])
				#-- Clean up
				for i in range(modname._length_):
					modname[i]='\x00'
				kernel.CloseHandle(hProcess)
				if prc_name in processName:
					print processName, "is started."
					return True
		return False

class CpeControl:
	client  = None

	def main(self, command):
		try:
			if(command[1]=="ATTACH"):
				return self.operation_attach(command[0],command[2])
			else:
				return self.operataion_service(command[0],command[1],command[2])
		except Exception,e:
			return [False,repr(e)]

	#Attach Operation#
	def operation_attach(self, cpeip, params):
		#[serverip, cpetype, earfcn, pci]
		if not self.accessible(cpeip,300): #5 minutes
			return [False,'CPE %s is not accessible'%cpeip]
		client = self.sshsession(cpeip)
		if not client: 
			return [False,'CPE %s SSH login fails'%cpeip]
		isodu = True if params[1]=='ODU' else False
		showac = "at at!=showac;" if isodu else "atcmd /dev/ttyACM0 115200 at!=showac"
		atcfun0 = "at at+cfun=0;" if isodu else "atcmd /dev/ttyACM0 115200 at+cfun=0"
		atcfun1 = "at at+cfun=1;" if isodu else "atcmd /dev/ttyACM0 115200 at+cfun=1"
		forcecell = "at at!=\"forcecell dl-earfcn="+str(params[2])+" pci="+str(params[3])+"\";" if isodu else "atcmd /dev/ttyACM0 115200 at!=\"forcecell dl-earfcn="+str(params[2])+" pci="+str(params[3])+"\""
		tag = False
		for n in range(1,4):
			stdin,stdout,stderr=client.exec_command(atcfun0)
			time.sleep(3)
			stdin,stdout,stderr=client.exec_command(forcecell)
			time.sleep(3)
			stdin,stdout,stderr=client.exec_command(atcfun1)
			time.sleep(15)
			#print "The %sth restart:" %n
			for m in range(4):
				stdin,stdout,stderrc=client.exec_command(showac)
				showac_output = stdout.read()
				if "CONNECTED" in showac_output:
					#print "CPE Attach Success"
					tag = True
					break
				else:
					m =m+1
					#print "showac not CONNECTED: %s" % m
				time.sleep(10)
			if tag: break
		if not tag: 
			return [False,'CPE %s attach fails'%cpeip]
		time.sleep(10)
		tag = False
		stdin,stdout,stderr=client.exec_command("ping -c 10 %s"% params[0])
		ping_output = stdout.read()
		client.close()
		#print ping_output
		if "bytes from" in ping_output:
			return [True, 'CPE %s Ping|SSH|Attach|Traffic OK'%cpeip]
		else:
			return [False,'CPE %s traffic fails'%cpeip]

	def sshsession(self, cpeip, user='root', passwd='Si8a&2vV9', port=22):
		'''打开到CPE的SSH会话'''
		try:
			client=paramiko.SSHClient()
			client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			client.connect(cpeip, int(port), user, passwd)
		except Exception, e:
			print e
			return False
		return client

	def accessible(self, cpeip, timeout=600):
		'''确认CPE是否在规定时间内可被接入(Ping+SSH)'''
		starttime = time.time()
		while time.time() - starttime < int(timeout): 
			if self.accesscheck(cpeip): 
				#print 'CPE %s ok'%cpeip
				return True
			time.sleep(10)
		return False

	def accesscheck(self, cpeip, count=8):
		'''单次判断CPE是否可被接入(Ping+SSH)'''
		pingcmd = 'ping %s -n %d' %(cpeip, int(count))
		try:
			p = subprocess.Popen(pingcmd,stdin = subprocess.PIPE,stdout = subprocess.PIPE,stderr = subprocess.PIPE,shell = True)
		except Exception,e:
			print 'subprocess:',e
		out = p.stdout.read()
		data = unicode(eval(repr(out)),"gbk")
		#print data
		result = re.findall(r'Ping(.*)Ping', data, re.M|re.S)
		if not result: return False
		lines = result[0].split('\r\n')
		if len(lines) <= 3: return False
		lines = lines[1:-2]
		ttls = re.findall(r'TTL=',result[0])
		#print "Ping result: %s of %s success." % (len(ttls),len(lines))
		if float(len(ttls))/float(len(lines)) < 0.5:
			return False
		try:
			localssh=paramiko.SSHClient()
			localssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			localssh.connect(cpeip, 22, 'root', 'Si8a&2vV9')
			time.sleep(1)
			localssh.close()
		except Exception, e:
			return False
		return True

	#Service Operation#
	def operataion_service(self, cpeip, svctype, params):
		cpeipinfo = cpeip.split('.')
		#self.pklfile = "D:/Autotest/Logs/"+cpeipinfo[3]+".process.pkl"
		test = FtpPerformance()
		pids = test.ftp_service(cpeipinfo[3],svctype,params)
		del test
		ret = self.check_throughput(int(params[1]))
		self.stop_ftp_service(pids)
		if not ret[0] and not isinstance(ret[1], list):
			return ret
		tput = self.get_statistics(ret[1])
		print "\nThroughout Info:",tput,"\n"
		return [ret[0], tput]

	def stop_ftp_service(self, pids, prc_name='curl.exe'):
		''' Stop background FTP '''
		#pids = self._unpickle_processes()
		for onepid in pids:
			os.system('taskkill /f /pid %s 1>NUL 2>&1' % onepid) 
		os.system('taskkill /f /im %s 1>NUL 2>&1' % prc_name) 

	def check_throughput(self, svctime, interval=10):
		result = []
		zerocount = 0
		lastline = ''
		time.sleep(30)
		starttime = time.time()
		while time.time() - starttime < int(svctime): 
			time.sleep(int(interval))
			newline = self.get_lastline()
			if not newline: 
				zerocount += 1
				result.append(['wrong log',0,0])
				if zerocount >= 5:
					return [False,result]
				continue
			record = re.findall(r'(\d+\/\d+\/\d+\s+\d+:\d+:\d+)\s+(\d+)\s+(\d+)\s+\d+', newline)
			if not record or len(record) != 1:
				zerocount += 1
				result.append(['wrong log',0,0])
				if zerocount >= 5:
					return [False,result]
				result.append([newline,0,0])
				continue
			result.append([record[0][0],float(record[0][1])/(interval*1024),float(record[0][2])/(interval*1024)])
			if float(record[0][1])/interval < 50*1024: #DL<50kbps
				zerocount += 1
				if zerocount >= 5:
					print 'Throughput too low'
					return [False,result]
			else:
				zerocount = 0
			if not lastline:
				lastline = newline
				continue
			if lastline == newline:
				continue
			lastline = newline
		return [True,result]

	def get_statistics(self, datalist):
		if not datalist: return []
		dlmax = 0
		dlmin = 1000000
		dlsum = 0
		ulmax = 0
		ulmin = 1000000 #1Gbps
		ulsum = 0
		for rec in datalist:
			if rec[1] > dlmax: dlmax = rec[1]
			if rec[1] < dlmin: dlmin = rec[1]
			dlsum += rec[1]
			if rec[2] > ulmax: ulmax = rec[2]
			if rec[2] < ulmin: ulmin = rec[2]
			ulsum += rec[2]
		return [[round(dlsum/len(datalist)/1024,2),round(dlmax/1024,2),round(dlmin/1024,2)],\
				[round(ulsum/len(datalist)/1024,2),round(ulmax/1024,2),round(ulmin/1024,2)]]

	def get_lastline(self):
		last_line = ''
		try:
			with open(hoolog, 'r') as f:
				off = -50
				while True:
					#seek(off, 2)表示文件指针：从文件末尾(2)开始向前50个字符(-50)
					f.seek(off, 2) 
					lines = f.readlines() 
					if len(lines)>=2: #判断是否最后至少有两行，这样保证了最后一行是完整的
						last_line = lines[-1] 
						break
					#如果off为50时得到的readlines只有一行，不能保证最后一行是完整的
					#所以off翻倍重新运行，直到readlines不止一行
					off *= 2
		except Exception, e:
			print e
		return last_line

class FtpPerformance:
	def _upload_curl(self, remotefile, localfile, serverip, ftpuser, ftppd):
		'''To run curl for FTP upload repeatedly'''
		curlargs = '-T %s ftp://%s/%s -u %s:%s -s'%(localfile, serverip, remotefile, ftpuser,ftppd)
		print 'Upload: curl %s' % curlargs
		while True:  
			curlprc = subprocess.Popen("curl.exe %s" % curlargs, stderr=subprocess.PIPE)
			curlprc.stderr.readline()

	def _download_curl(self, remotefile, localfile, serverip, ftpuser, ftppd):
		'''To run curl for FTP download repeatedly'''
		curlargs = 'ftp://%s/%s -u %s:%s -o %s -s'%(serverip, remotefile,ftpuser,ftppd,localfile)
		print 'Download: curl %s' % curlargs
		while True:
			curlprc = subprocess.Popen("curl.exe %s" % curlargs, stderr=subprocess.PIPE)
			curlprc.stderr.readline()

	def ftp_service(self,cpeid,svctype,params):
		if len(params) <12: return []
		serverip = params[0]
		#svctime  = params[1]
		ftpuser  = params[2]
		ftppd    = params[3]
		dlthread = params[4]
		dlpath_s = params[5]
		dlpath_c = params[6]
		dlprefix = params[7]
		ulthread = params[8]
		ulpath_s = params[9]
		ulpath_c = params[10]
		ulprefix = params[11]
		if dlpath_c and dlpath_c[-1]=='/': dlpath_c=dlpath_c[:-1]
		if ulpath_c and ulpath_c[-1]=='/': ulpath_c=ulpath_c[:-1]
		if int(dlthread)>10 or int(ulthread)>10: return []
		if os.path.exists("D:/Autotest/Logs/.result.pkl"):
			os.remove("D:/Autotest/Logs/.result.pkl")
		pids = []
		if svctype == "DOWNLOAD":    #Download
			for i in range(int(dlthread)):
				filename  = dlprefix + "%s" %i
				remotefile = filename if dlpath_s=='' else dlpath_s+'/'+filename
				localfile  = dlpath_c+'/'+cpeid+'_'+filename
				ftptest = multiprocessing.Process(args=(remotefile, localfile, serverip, ftpuser, ftppd,),target=self._download_curl)
				ftptest.start()
				time.sleep(2)
				pids.append(ftptest.pid)
		elif svctype == "UPLOAD":    #Upload
			for i in range(int(ulthread)):
				filename  = ulprefix + "%s" %i
				remotefile = cpeid+'_'+filename if ulpath_s=='' else ulpath_s+'/'+cpeid+'_'+filename
				localfile  = ulpath_c+'/'+filename
				ftptest = multiprocessing.Process(args=(remotefile, localfile, serverip, ftpuser, ftppd,),target=self._upload_curl)
				ftptest.start()
				time.sleep(2)
				pids.append(ftptest.pid)
		else:                    #Download + Upload
			for i in range(int(dlthread)):
				filename  = dlprefix + "%s" %i
				remotefile = filename if dlpath_s=='' else dlpath_s+'/'+filename
				localfile  = dlpath_c+'/'+cpeid+'_'+filename
				ftptest = multiprocessing.Process(args=(remotefile, localfile, serverip, ftpuser, ftppd,),target=self._download_curl)
				ftptest.start()
				time.sleep(2)
				pids.append(ftptest.pid)
			for i in range(int(ulthread)):
				filename  = ulprefix + "%s" %i
				remotefile = cpeid+'_'+filename if ulpath_s=='' else ulpath_s+'/'+cpeid+'_'+filename
				localfile  = ulpath_c+'/'+filename
				ftptest = multiprocessing.Process(args=(remotefile, localfile, serverip, ftpuser, ftppd,),target=self._upload_curl)
				ftptest.start()
				time.sleep(2)
				pids.append(ftptest.pid)
		return pids

if __name__ == "__main__":
	multiprocessing.freeze_support()
	if len(sys.argv)>=2: hoolog = sys.argv[1]
	print 'HooNetMeter Log:',hoolog
	CpePCMain().run()