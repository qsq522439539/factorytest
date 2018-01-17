#!/usr/bin/env python
#coding=utf-8
import paramiko
import subprocess
import time
import config
import re

Timeout = int(config.Parsing_XML().getTimeout("args.xml"))

class FactoryTest:
	client  = None
	session = None
	isrecovery = False
	ischeckgps = False

	def doTest(self, enbip, earfcn, pci, mme, plmn, segw, psk, q):
		result = self.main(enbip, earfcn, pci, mme, plmn, segw, psk)
		if result:
			q.put('%sWorks Normally'%enbip)
		else:
			q.put('%shave some errors'%enbip)
			
	def main(self, enbip, earfcn, pci, mme, plmn, segw, psk):
		try:
			if(int(earfcn)>=44490):
				self.usage("EARFCN range error")
				return False
			elif(int(pci)<=0 or int(pci)>=504):
				self.usage("PCI Range error")
				return False
			elif(len(plmn)<=4 or len(plmn)>=7):
				self.usage("PLMN Format error")
				return False
			elif(not self.ipcheck(enbip)):
				self.usage("ENB IP Format Wrong")
				return False
			elif(not self.ipcheck(mme)):
				self.usage("MME IP Format Wrong")
				return False
			elif(not self.ipcheck(segw)):
				self.usage("SeGW IP Format Wrong")
				return False
		except Exception, e:
			self.usage(repr(e))
			return False
		if not self.isrecovery:
			print '*** Configuration Parameters ***'
			print '*** eNBIP:\t%s'%enbip
			print '*** EARFCN:\t%s'%earfcn
			print '*** PCI:\t%s'%pci
			print '*** MME:\t%s'%mme
			print '*** PLMN:\t%s'%plmn
			print '*** SEGW:\t%s'%segw
			print '*** PSK: \t%s\n'%psk
		operation = 'recover' if self.isrecovery else 'configure'
		print self.timeinfo(),'Start to %s eNB %s.'% (operation, enbip)
		#Check Ping connectivity#
		if not self.accessible(enbip, 120): #5 minutes
			self.usage('eNB %s is not accessible.'%enbip, 2)
			return False
		print self.timeinfo(),'eNB %s is accessible(Ping & SSH)'%enbip
		# if self.isrecovery:
		# 	if not self.recoverdata(enbip):
		# 		self.usage('eNB %s recovery fails.'%enbip, 6)
		# 	print self.timeinfo(),'eNB %s data recovery done, rebooting now, wait for ~5 minutes.'%enbip
		# 	if not self.accessible(enbip, 600): #10 minutes
		# 		self.usage('After recovery and reboot, eNB %s is not accessible.'%enbip, 7)
		# 	print self.timeinfo(),'After reboot, eNB %s is accessible(Ping & SSH)'%enbip
		# 	time.sleep(120)
		# 	if not self.recovercheck(enbip):
		# 		self.usage('eNB %s recovery data check failure.'%enbip, 8)
		# 	print self.timeinfo(),'The eNB %s Recovery Success.'%enbip
		# else:
		#Parameter configuration#
		# if not earfcn or not pci:
		# 	self.usage('EARFCN or PCI is not configured')
		if not self.configuredata(enbip, earfcn, pci, mme, plmn, segw, psk):
			self.usage('eNB %s configuration fails.'%enbip, 3)
			return False
		print self.timeinfo(),'eNB %s data configuration success, rebooting now, wait for ~5 minutes.'%enbip
		#Check Ping connectivity Again#
		if not self.accessible(enbip, Timeout): #10 minutes
			self.usage('After reboot, eNB %s is not accessible.'%enbip, 4)
			return False
		print self.timeinfo(),'After reboot, eNB %s is accessible(Ping & SSH)'%enbip
		#ENB Work Status Check#
		if not self.checkeNBstatus(enbip, Timeout): #10 minutes
			self.usage('eNB %s status is abnormal.'%enbip, 5)
			return False
		print self.timeinfo(),'The eNB %s Works Normally'%enbip
		return True

	def sshsession(self, host, user='admin', passwd='admin', port=27149):
		'''打开SSH会话并转如root用户'''
		try:
			self.client=paramiko.SSHClient()
			self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			self.client.connect(host, int(port), user, passwd)
		except Exception, e:
			print e
			return False
		stdin_read,stdout_read,stderr_read=self.client.exec_command("source /etc/profile;")
		self.session = self.client.invoke_shell()
		time.sleep(2)
		self.send_cmd('admin','passwd:')
		self.send_cmd('qpa;10@(')
		self.send_cmd('start-shell','$')
		self.send_cmd('sudo su root')
		if not self.client:
			self.client = None
			self.session= None
			return False
		return True

	def send_cmd(self, cmd, endprompt='#'):
		'''通过SSH发送命令并返回结果'''
		buff = ''
		self.session.send(cmd+'\n')
		while not buff.strip().endswith(endprompt):
			resp = self.session.recv(65535)
			buff +=str(resp)
		#删除命令行本身, 删除空行, 删除末尾的提示符
		buff = buff.replace(cmd,'')
		buff = buff.replace('root@CELL:~#','')
		#buff = re.sub(r'\n+','\n', buff)
		buff = buff.strip()
		return buff

	def send_cmdNcheck(self, cmd, keyword):
		'''发送命令判断返回结果是否包含keyword'''
		output = self.send_cmd(cmd)
		if keyword not in output:
			print 'CMD Error: %s' % cmd
			return False
		return True

	def accessible(self, enbip, timeout=Timeout):
		'''确认基站是否在规定时间内可被接入(Ping+SSH)'''
		starttime = time.time()
		while time.time() - starttime < int(timeout): 
			if self.accesscheck(enbip):
				return True
			time.sleep(10)
		return False

	def accesscheck(self, enbip, count=8):
		'''单次判断基站是否可被接入(Ping+SSH)'''
		pingcmd = 'ping %s -n %d' %(enbip, int(count))
		p = subprocess.Popen(pingcmd,stdin = subprocess.PIPE,stdout = subprocess.PIPE,stderr = subprocess.PIPE,shell = True)
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
			localssh.connect(enbip, 27149, 'admin', 'admin')
			time.sleep(1)
			localssh.close()
		except Exception, e:
			return False
		return True

######################Configure Operation#################################
	def configuredata(self,enbip, earfcn, pci, mme, plmn, segw, psk):
		'''下发配置数据到基站，成功的话重启基站'''
		if not self.sshsession(enbip):
			return False
		#MME Pool Disable
		if not self.send_cmdNcheck('cli -c "oam.set LTE_X_BAICELLS_MME_POOL_ENABLE 0"','OK'):
			return False
		#2nd IPSec Delete
		onecmd = 'mibcli get IPSEC.1.TUNNEL_ENABLE'
		output = self.send_cmd(onecmd)
		if 'TUNNEL_ENABLE:=1' in output:
			if not self.send_cmdNcheck('mibcli deleteobject Device.FAP.Ipsec. 1','Object 1 Deleted'):
				return False
		#1st IPSec Setting
		if not self.send_cmdNcheck('mibcli set IPSEC.0.TUNNEL_GATEWAY:=%s'%segw,'set attribute ok'):
			return False
		mmeipsegs = mme.split('.')
		if len(mmeipsegs)!=4: return False
		rightsubnet = '%s.%s.%s.0/24'%(mmeipsegs[0],mmeipsegs[1],mmeipsegs[2])
		if not self.send_cmdNcheck('mibcli set IPSEC.0.RIGHT_SUBNET:=%s'%rightsubnet,'set attribute ok'):
			return False
		if not self.send_cmdNcheck('mibcli set IPSEC.0.PRE_SHARED_KEY:=%s'%psk,'set attribute ok'):
			return False
		#Quick Setting
		if not self.send_cmdNcheck('cli -c "oam.set LTE_DL_EARFCN %s"'%earfcn,'OK'):
			return False
		if not self.send_cmdNcheck('cli -c "oam.set LTE_UL_EARFCN %s"'%earfcn,'OK'):
			return False
		if not self.send_cmdNcheck('cli -c "oam.set TOGGLE_SWITCH 0"','OK'):
			return False
		if not self.send_cmdNcheck('cli -c "oam.set LTE_PHY_CELLID_LIST %s"'%pci,'OK'):
			return False
		if not self.send_cmdNcheck('cli -c "oam.set LTE_CELL_IDENTITY %s"'%pci,'OK'):
			return False
		if not self.send_cmdNcheck('cli -c \'oam.set LTE_SIGLINK_SERVER_LIST "%s"\''%mme,'OK'):
			return False
		if not self.send_cmdNcheck('mibcli set LTE_CELL_PLMN_LIST.0.LTE_OAM_PLMNID:=%s'%plmn,'set attribute ok'):
			return False
		#GPS Switch
		if self.ischeckgps:
			if not self.send_cmdNcheck('cli -c "oam.set GPS_CONTROL_SWITCH 1"','OK'):
				return False
			if not self.send_cmdNcheck('cli -c "oam.set LTE_GPS_SYNC_ENABLE 1"','OK'):
				return False
		else:
			if not self.send_cmdNcheck('cli -c "oam.set GPS_CONTROL_SWITCH 0"','OK'):
				return False
			if not self.send_cmdNcheck('cli -c "oam.set LTE_GPS_SYNC_ENABLE 0"','OK'):
				return False
		#Reboot
		output = self.send_cmd('(sleep 5;reboot) &')
		if output != '':
			print 'Reboot Failure.'
			return False
		self.client.close()
		return True

	def checkeNBstatus(self, enbip, timeout=Timeout):
		'''确认基站是否在规定时间内状态正常(GPS|MME|CELL)'''
		if not self.sshsession(enbip):
			return False
		starttime = time.time()
		while time.time() - starttime < int(timeout): 
			#if self.checkCLIstatus('GPS_STATUS'):
			if self.ischeckgps:
				if self.checkCLIstatus('GPS_STATUS') and self.checkCLIstatus('MME_STATUS') and self.checkCLIstatus('LTE_FAP_ADMIN_STATE'):
					self.client.close()
					return True
			else:
				if self.checkCLIstatus('MME_STATUS') and self.checkCLIstatus('LTE_FAP_ADMIN_STATE'):
					self.client.close()
					return True
			time.sleep(10)
		self.client.close()
		return False

	def checkCLIstatus(self, cliparameter):
		'''判断基站某个状态是否正常(GPS|MME|CELL)'''
		clicmd = 'cli -c "oam.getwild %s"' % cliparameter
		output = self.send_cmd(clicmd)
		#print output
		if 'OK' not in output:
			#print 'CLI Error: %s' % clicmd
			return False
		result = re.findall(r'(%s)\s+(\d)'%cliparameter, output)
		if not result or len(result)!=1:
			#print 'CLI Content Wrong: %s' % clicmd
			return False
		if int(result[0][1]) != 1:
			#print '%s Status abnormal' % cliparameter
			return False
		return True
######################Configure Operation#################################

######################Recovery Operation#################################
	def recoverdata(self,enbip):
		'''回复基站出厂设置，成功的话重启基站'''
		'''mibcli factoryreset --> ???'''
		if not self.sshsession(enbip):
			return False
		#GPS Switch
		if not self.send_cmdNcheck('cli -c "oam.set GPS_CONTROL_SWITCH 1"','OK'):
			return False
		if not self.send_cmdNcheck('cli -c "oam.set LTE_GPS_SYNC_ENABLE 1"','OK'):
			return False
		#Modify PCI
		if not self.send_cmdNcheck('cli -c "oam.set LTE_PHY_CELLID_LIST 36"','OK'):
			return False
		'''#EARFCN??'''
		if not self.send_cmdNcheck('cli -c "oam.set LTE_DL_EARFCN 44190"','OK'):
			return False
		if not self.send_cmdNcheck('cli -c "oam.set LTE_UL_EARFCN 44190"','OK'):
			return False
		#Configure MME IP
		if not self.send_cmdNcheck('cli -c \'oam.set LTE_SIGLINK_SERVER_LIST "10.0.3.4"\'','OK'):
			return False
		#Cloud EPC
		if not self.send_cmdNcheck('cli -c "oam.set TOGGLE_SWITCH 1"','OK'):
			return False
		#Reboot
		output = self.send_cmd('(sleep 5;reboot) &')
		if output != '':
			print 'Reboot Failure.'
			return False
		self.client.close()
		return True

	def recovercheck(self, enbip):
		'''检查基站参数判断是否是出厂设置'''
		if not self.sshsession(enbip):
			return False
		if not self.send_cmdNcheck('mibcli get IPSEC.0.TUNNEL_ENABLE','TUNNEL_ENABLE:=1'):
			return False
		if not self.send_cmdNcheck('mibcli get IPSEC.1.TUNNEL_ENABLE','TUNNEL_ENABLE:=1'):
			return False
		if not self.send_cmdNcheck('mibcli get IPSEC.0.TUNNEL_GATEWAY','baicells-'):
			return False
		if not self.send_cmdNcheck('mibcli get IPSEC.1.TUNNEL_GATEWAY','baicells-'):
			return False
		self.client.close()
		return True
################################################################

	def ipcheck(self, ipaddr):
		'''检查输入是否符合IP地址格式'''
		result = re.findall(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', ipaddr)
		if not result: return False
		for field in result[0]:
			if(int(field)>=256):
				return False
		return True

	def timeinfo(self):
		'''获取当前时间信息'''
		return time.strftime("%m-%d %H:%M:%S", time.localtime()) 

	def usage(self, errinfo, errcode=1):
		'''参数输入的帮助提示或者打印错误信息并退出程序'''
		print errinfo + ' ' + 'errcode:%s'%errcode

# if __name__ == "__main__":
