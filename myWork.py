#!/usr/bin/env python
# coding=utf-8

import sys
import myWidget
import threading
import multiprocessing
import config as cf
from factory import *
from multiprocessing import Process, Queue
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import _cffi_backend
from enbpc_client import SockThread

q = Queue()

xmlname = 'args.xml'
pingErrorMsg = u'部分基站ping不通或ssh不通，请检查测试环境...'
confiErrorMsg = u'部分基站参数配置出现错误...'
initialEdit = u"未配置参数"

try:
	_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
	def _fromUtf8(s):
		return s

try:
	_encoding = QtGui.QApplication.UnicodeUTF8
	def _translate(context, text, disambig):
		return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
	def _translate(context, text, disambig):
		return QtGui.QApplication.translate(context, text, disambig)
  
class openWnd(QtGui.QWidget, myWidget.Ui_widget):
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.setupUi(self)
		self.IpEdit()
		self.initialStatusEdit()
		self.initialdlSpeedEdit()
		self.initialulSpeedEdit()
		self.createButton()
		palette1 = QtGui.QPalette()
		palette1.setColor(self.backgroundRole(), QtGui.QColor("#454545"))
		self.setPalette(palette1)
		self.setAutoFillBackground(True)
		
	def getparam(self):
		xmldata = cf.Parsing_XML()
		enb_ip = xmldata.get_enb_data(xmlname)
		confi = {}
		#界面可配IP
		if str(self.lineEdit_1.text())!= '':
			confi[str(self.lineEdit_1.text())] = [enb_ip["001"]["earfcn"], enb_ip["001"]["pci"], enb_ip["001"]["mme"],
					             enb_ip["001"]["plmn"], enb_ip["001"]["segw"], enb_ip["001"]["psk"]]
		if str(self.lineEdit_2.text())!= '':
			confi[str(self.lineEdit_2.text())] = [enb_ip["002"]["earfcn"], enb_ip["002"]["pci"], enb_ip["002"]["mme"],
					             enb_ip["002"]["plmn"], enb_ip["002"]["segw"], enb_ip["002"]["psk"]]
		if str(self.lineEdit_3.text())!= '':
			confi[str(self.lineEdit_3.text())] = [enb_ip["003"]["earfcn"], enb_ip["003"]["pci"], enb_ip["003"]["mme"],
					             enb_ip["003"]["plmn"], enb_ip["003"]["segw"], enb_ip["003"]["psk"]]
		if str(self.lineEdit_4.text())!= '':
			confi[str(self.lineEdit_4.text())] = [enb_ip["004"]["earfcn"], enb_ip["004"]["pci"], enb_ip["004"]["mme"],
					             enb_ip["004"]["plmn"], enb_ip["004"]["segw"], enb_ip["004"]["psk"]]
		if str(self.lineEdit_5.text())!= '':
			confi[str(self.lineEdit_5.text())] = [enb_ip["005"]["earfcn"], enb_ip["005"]["pci"], enb_ip["005"]["mme"],
					             enb_ip["005"]["plmn"], enb_ip["005"]["segw"], enb_ip["005"]["psk"]]
		if str(self.lineEdit_6.text())!= '':
			confi[str(self.lineEdit_6.text())] = [enb_ip["006"]["earfcn"], enb_ip["006"]["pci"], enb_ip["006"]["mme"],
					             enb_ip["006"]["plmn"], enb_ip["006"]["segw"], enb_ip["006"]["psk"]]
		if str(self.lineEdit_7.text())!= '':
			confi[str(self.lineEdit_7.text())] = [enb_ip["007"]["earfcn"], enb_ip["007"]["pci"], enb_ip["007"]["mme"],
					             enb_ip["007"]["plmn"], enb_ip["007"]["segw"], enb_ip["007"]["psk"]]
		if str(self.lineEdit_8.text())!= '':
			confi[str(self.lineEdit_8.text())] = [enb_ip["008"]["earfcn"], enb_ip["008"]["pci"], enb_ip["008"]["mme"],
					             enb_ip["008"]["plmn"], enb_ip["008"]["segw"], enb_ip["008"]["psk"]]
		return confi
	
	def IpEdit(self):
		xmldata = cf.Parsing_XML()
		enb_ip = xmldata.get_enb_data(xmlname)
		numlist = xmldata.get_num(xmlname)
		for num in numlist:
			ip = enb_ip[num]["enbip"]
			if num == "001":
				self.lineEdit_1.setText(ip)
			if num == "002":
				self.lineEdit_2.setText(ip)
			if num == "003":
				self.lineEdit_3.setText(ip)
			if num == "004":
				self.lineEdit_4.setText(ip)
			if num == "005":
				self.lineEdit_5.setText(ip)
			if num == "006":
				self.lineEdit_6.setText(ip)
			if num == "007":
				self.lineEdit_7.setText(ip)
			if num == "008":
				self.lineEdit_8.setText(ip)
	
	def setText(self, text):
		num = ''
		if text[0] == self.lineEdit_1.text():
			num = '001'
		elif text[0] == self.lineEdit_2.text():
			num = '002'
		elif text[0] == self.lineEdit_3.text():
			num = '003'
		elif text[0] == self.lineEdit_4.text():
			num = '004'
		elif text[0] == self.lineEdit_5.text():
			num = '005'
		elif text[0] == self.lineEdit_6.text():
			num = '006'
		elif text[0] == self.lineEdit_7.text():
			num = '007'
		elif text[0] == self.lineEdit_8.text():
			num = '008'
		if num == "001":
			self.lineEdit_11.setText(text[1])
		elif num == "002":
			self.lineEdit_12.setText(text[1])
		elif num == "003":
			self.lineEdit_13.setText(text[1])
		elif num == "004":
			self.lineEdit_14.setText(text[1])
		elif num == "005":
			self.lineEdit_15.setText(text[1])
		elif num == "006":
			self.lineEdit_16.setText(text[1])
		elif num == "007":
			self.lineEdit_17.setText(text[1])
		elif num == "008":
			self.lineEdit_18.setText(text[1])
			
	def	setdlspeedtext(self,text):
		num = ''
		if text[0] == self.lineEdit_1.text():
			num = '001'
		elif text[0] == self.lineEdit_2.text():
			num = '002'
		elif text[0] == self.lineEdit_3.text():
			num = '003'
		elif text[0] == self.lineEdit_4.text():
			num = '004'
		elif text[0] == self.lineEdit_5.text():
			num = '005'
		elif text[0] == self.lineEdit_6.text():
			num = '006'
		elif text[0] == self.lineEdit_7.text():
			num = '007'
		elif text[0] == self.lineEdit_8.text():
			num = '008'
		if num == "001":
			self.lineEdit_21.setText(text[1])
		elif num == "002":
			self.lineEdit_22.setText(text[1])
		elif num == "003":
			self.lineEdit_23.setText(text[1])
		elif num == "004":
			self.lineEdit_24.setText(text[1])
		elif num == "005":
			self.lineEdit_25.setText(text[1])
		elif num == "006":
			self.lineEdit_26.setText(text[1])
		elif num == "007":
			self.lineEdit_27.setText(text[1])
		elif num == "008":
			self.lineEdit_28.setText(text[1])
	
	def	setulspeedtext(self,text):
		num = ''
		if text[0] == self.lineEdit_1.text():
			num = '001'
		elif text[0] == self.lineEdit_2.text():
			num = '002'
		elif text[0] == self.lineEdit_3.text():
			num = '003'
		elif text[0] == self.lineEdit_4.text():
			num = '004'
		elif text[0] == self.lineEdit_5.text():
			num = '005'
		elif text[0] == self.lineEdit_6.text():
			num = '006'
		elif text[0] == self.lineEdit_7.text():
			num = '007'
		elif text[0] == self.lineEdit_8.text():
			num = '008'
		if num == "001":
			self.lineEdit_31.setText(text[1])
		elif num == "002":
			self.lineEdit_32.setText(text[1])
		elif num == "003":
			self.lineEdit_33.setText(text[1])
		elif num == "004":
			self.lineEdit_34.setText(text[1])
		elif num == "005":
			self.lineEdit_35.setText(text[1])
		elif num == "006":
			self.lineEdit_36.setText(text[1])
		elif num == "007":
			self.lineEdit_37.setText(text[1])
		elif num == "008":
			self.lineEdit_38.setText(text[1])
		
	def setLabelText(self, text):
		if text[1] == 'not accessible':
			self.label.setText(_fromUtf8(pingErrorMsg))
		if text[1] == 'have some errors':
			self.label.setText(_fromUtf8(confiErrorMsg))

	def initialStatusEdit(self):
		confi = self.getparam()
		for enbip in confi.keys():
			self.setText([enbip, initialEdit])
	
	def initialdlSpeedEdit(self):
		confi = self.getparam()
		for enbip in confi.keys():
			self.setdlspeedtext([enbip, 'null'])
			
	def initialulSpeedEdit(self):
		confi = self.getparam()
		for enbip in confi.keys():
			self.setulspeedtext([enbip, 'null'])
			
	def createButton(self):
		self.connect(self.pushButton1, QtCore.SIGNAL('clicked()'), self.startRunConfi)
		self.connect(self.pushButton3, QtCore.SIGNAL('clicked()'), self.startAccessible)
		self.connect(self.pushButton4, QtCore.SIGNAL('clicked()'), self.startCpeAccess)
		self.connect(self.pushButton2, QtCore.SIGNAL('clicked()'), self.startDotest)
		self.connect(self.pushButton5, QtCore.SIGNAL('clicked()'), self.startDodlultest)
		self.connect(self.pushButton6, QtCore.SIGNAL('clicked()'), self.startBothtest)
		
	def getcpeid(self):
		ue = []
		if str(self.lineEdit_1.text()) != '':
			ueid = '001'
			ue.append(ueid)
		if str(self.lineEdit_2.text()) != '':
			ueid = '002'
			ue.append(ueid)
		if str(self.lineEdit_3.text()) != '':
			ueid = '003'
			ue.append(ueid)
		if str(self.lineEdit_4.text()) != '':
			ueid = '004'
			ue.append(ueid)
		if str(self.lineEdit_5.text()) != '':
			ueid = '005'
			ue.append(ueid)
		if str(self.lineEdit_6.text()) != '':
			ueid = '006'
			ue.append(ueid)
		if str(self.lineEdit_7.text()) != '':
			ueid = '007'
			ue.append(ueid)
		if str(self.lineEdit_8.text()) != '':
			ueid = '008'
			ue.append(ueid)
		return ue
	
	def startAccessible(self):
		self.thread = MyAccessThread()
		self.thread.getConfi(self.getparam())
		self.thread.sinOut.connect(self.setText)
		self.thread.sinOut.connect(self.setLabelText)
		self.thread.start()
		
	def startRunConfi(self):
		self.thread = MyConfiThread()
		self.thread.getConfi(self.getparam())
		self.thread.sinOut.connect(self.setText)
		self.thread.sinOut.connect(self.setLabelText)
		self.thread.start()
	
	def startCpeAccess(self):
		self.thread = MyCpeAccessThread()
		self.thread.getSendingmsg(self.getcpeid())
		self.thread.getsocketip()
		self.thread.sinOut.connect(self.setText)
		self.thread.start()
	
	def startDotest(self):
		self.thread = MyDodltestThread()
		self.thread.getSendingmsg(self.getcpeid())
		self.thread.getsocketip()
		self.thread.sinOut.connect(self.setdlspeedtext)
		self.thread.sinOut2.connect(self.setulspeedtext)
		self.thread.start()
	
	def startDodlultest(self):
		self.thread = MyDodlultestThread()
		self.thread.getSendingmsg(self.getcpeid())
		self.thread.getsocketip()
		self.thread.sinOut.connect(self.setdlspeedtext)
		self.thread.sinOut2.connect(self.setulspeedtext)
		self.thread.start()
		
	def startBothtest(self):
		self.thread = MyBothtestThread()
		self.thread.getSendingmsg(self.getcpeid())
		self.thread.getsocketip()
		self.thread.sinOut.connect(self.setdlspeedtext)
		self.thread.sinOut2.connect(self.setulspeedtext)
		self.thread.start()
		
class MyAccessThread(QThread):
	sinOut = pyqtSignal(list)

	def __init__(self, parent=None):
		super(MyAccessThread, self).__init__(parent)
		
	def getConfi(self, confi):
		self.confi = confi
		
	def run(self):
		for enbip in self.confi.keys():
			self.sinOut.emit([enbip, "start ping test..."])
			check = accessible(enbip)
			if check:
				self.sinOut.emit([enbip, "accessible"])

			else:
				self.sinOut.emit([enbip, "not accessible"])
				
class MyConfiThread(QThread):
	sinOut = pyqtSignal(list)
	
	def __init__(self, parent=None):
		super(MyConfiThread, self).__init__(parent)
	
	def getConfi(self, confi):
		self.confi = confi
		
	def run(self):
		proc_record = []
		for k in self.confi.keys():
			self.sinOut.emit([k,'Start to configuration...'])
		for k in self.confi.keys():
			p = Process(target=FactoryTest().doTest, args=(k, self.confi[k][0], self.confi[k][1], self.confi[k][2],
			                                             self.confi[k][3], self.confi[k][4], self.confi[k][5], q))
			p.start()
			proc_record.append(p)
		for p in proc_record:
			p.join()
		for k in self.confi.keys():
			result = q.get()
			ip = re.search(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', result).group(0)
			msg = result.split(ip)[1]
			self.sinOut.emit([ip, msg])

class MyCpeAccessThread(QThread):
	sinOut = pyqtSignal(list)
	
	def __init__(self, parent=None):
		super(MyCpeAccessThread, self).__init__(parent)
	
	def getSendingmsg(self, ueid):
		xmldata = cf.Parsing_XML()
		self.sendlist = []
		for ue in ueid:
			s = xmldata.Operation(ue, 'ATTACH')
			self.sendlist.append(s)
		return self.sendlist
	
	def cpeipToEnbip(self, cpeip):
		xmldata = cf.Parsing_XML()
		uedata = xmldata.get_ue_data(xmlname)
		enbdata = xmldata.get_enb_data(xmlname)
		for k in uedata.keys():
			if uedata[k]['cpeip'] == cpeip:
				return enbdata[k]['enbip']
	
	def getsocketip(self):
		xmldata = cf.Parsing_XML()
		self.socketip = xmldata.getcontrolpc()
		return self.socketip
			
	def run(self):
		socktask1 = SockThread('connectionToCPEPC', self.socketip[0])
		socktask1.setDaemon(True)
		socktask1.start()
		socktask2 = SockThread('connectionToCPEPC', self.socketip[1])
		socktask2.setDaemon(True)
		socktask2.start()
		for command in self.sendlist:
			if command[-1] == self.socketip[0]:
				SockThread('connectionToCPEPC1',self.socketip[0]).dosendcmd(command[:-1], socktask1)
				time.sleep(3)
			if command[-1] == self.socketip[1]:
				SockThread('connectionToCPEPC2').dosendcmd(command[:-1], socktask2)
				time.sleep(3)
		for command in self.sendlist:
			if command[-1] == self.socketip[0]:
				result = SockThread('connectionToCPEPC1').getresult(socktask1)
			if command[-1] == self.socketip[1]:
				result = SockThread('connectionToCPEPC2').getresult(socktask2)
			print result
			cpeip = result[0]
			enbip = self.cpeipToEnbip(cpeip)
			check = str(result[2][0])
			if check == 'True':
				msg = u'cpe已附着'
				self.sinOut.emit([enbip, msg])
			else:
				msg = u'cpe未附着'
				self.sinOut.emit([enbip, msg])
		command = ['quit']
		SockThread('connectionToCPEPC1', self.socketip[0]).dosendcmd(command, socktask1)
		SockThread('connectionToCPEPC1', self.socketip[0]).dosendcmd(command, socktask2)

class MyDodltestThread(QThread):
	sinOut = pyqtSignal(list)
	sinOut2 = pyqtSignal(list)
	
	def __init__(self, parent=None):
		super(MyDodltestThread, self).__init__(parent)
	
	def getSendingmsg(self, ueid):
		xmldata = cf.Parsing_XML()
		self.sendlist = []
		for ue in ueid:
			s = xmldata.Operation(ue, 'DOWNLOAD')
			self.sendlist.append(s)
		return self.sendlist
	
	def getsocketip(self):
		xmldata = cf.Parsing_XML()
		self.socketip = xmldata.getcontrolpc()
		return self.socketip
	
	def cpeipToEnbip(self, cpeip):
		xmldata = cf.Parsing_XML()
		uedata = xmldata.get_ue_data(xmlname)
		enbdata = xmldata.get_enb_data(xmlname)
		for k in uedata.keys():
			if uedata[k]['cpeip'] == cpeip:
				return enbdata[k]['enbip']
			
	def run(self):
		print self.sendlist
		socktask1 = SockThread('connectionToCPEPC', self.socketip[0])
		socktask1.setDaemon(True)
		socktask1.start()
		socktask2 = SockThread('connectionToCPEPC', self.socketip[1])
		socktask2.setDaemon(True)
		socktask2.start()
		for command in self.sendlist:
			if command[-1] == self.socketip[0]:
				SockThread('connectionToCPEPC1',self.socketip[0]).dosendcmd(command[:-1], socktask1)
				time.sleep(3)
				result = SockThread('connectionToCPEPC1').getresult(socktask1)
				print 'result1:',result
				cpeip = result[0]
				enbip = self.cpeipToEnbip(cpeip)
				check = str(result[2][0])
				if check == 'True':
					msg = '%s, %s, %s'%(result[2][1][0][0],result[2][1][0][1],result[2][1][0][2])
					msg2 = 'null'
					self.sinOut.emit([enbip, msg])
					self.sinOut2.emit([enbip, msg2])
				else:
					msg = 'None'
					msg2 = 'null'
					self.sinOut.emit([enbip, msg])
					self.sinOut2.emit([enbip, msg2])
			if command[-1] == self.socketip[1]:
				SockThread('connectionToCPEPC2').dosendcmd(command[:-1], socktask2)
				time.sleep(3)
				result = SockThread('connectionToCPEPC1').getresult(socktask2)
				print 'result2:', result
				cpeip = result[0]
				enbip = self.cpeipToEnbip(cpeip)
				check = str(result[2][0])
				if check == 'True':
					msg = '%s, %s, %s' % (result[2][1][0][0], result[2][1][0][1], result[2][1][0][2])
					msg2 = 'null'
					self.sinOut.emit([enbip, msg])
					self.sinOut2.emit([enbip, msg2])
				else:
					msg = 'None'
					msg2 = 'null'
					self.sinOut.emit([enbip, msg])
					self.sinOut2.emit([enbip, msg2])
		command = ['quit']
		SockThread('connectionToCPEPC1', self.socketip[0]).dosendcmd(command, socktask1)
		SockThread('connectionToCPEPC1', self.socketip[0]).dosendcmd(command, socktask2)


class MyDodlultestThread(QThread):
	sinOut = pyqtSignal(list)
	sinOut2 = pyqtSignal(list)
	
	def __init__(self, parent=None):
		super(MyDodlultestThread, self).__init__(parent)
	
	def getSendingmsg(self, ueid):
		xmldata = cf.Parsing_XML()
		self.sendlist = []
		for ue in ueid:
			s = xmldata.Operation(ue, 'BOTH')
			self.sendlist.append(s)
		return self.sendlist
	
	def getsocketip(self):
		xmldata = cf.Parsing_XML()
		self.socketip = xmldata.getcontrolpc()
		return self.socketip
	
	def cpeipToEnbip(self, cpeip):
		xmldata = cf.Parsing_XML()
		uedata = xmldata.get_ue_data(xmlname)
		enbdata = xmldata.get_enb_data(xmlname)
		for k in uedata.keys():
			if uedata[k]['cpeip'] == cpeip:
				return enbdata[k]['enbip']
	
	def run(self):
		print self.sendlist
		socktask1 = SockThread('connectionToCPEPC', self.socketip[0])
		socktask1.setDaemon(True)
		socktask1.start()
		socktask2 = SockThread('connectionToCPEPC', self.socketip[1])
		socktask2.setDaemon(True)
		socktask2.start()
		for command in self.sendlist:
			if command[-1] == self.socketip[0]:
				SockThread('connectionToCPEPC1', self.socketip[0]).dosendcmd(command[:-1], socktask1)
				time.sleep(3)
				result = SockThread('connectionToCPEPC1').getresult(socktask1)
				print 'result1:', result
				cpeip = result[0]
				enbip = self.cpeipToEnbip(cpeip)
				check = str(result[2][0])
				if check == 'True':
					msg = '%s, %s, %s' % (result[2][1][0][0], result[2][1][0][1], result[2][1][0][2])
					msg2 = '%s, %s, %s' % (result[2][1][1][0], result[2][1][1][1], result[2][1][1][2])
					self.sinOut.emit([enbip, msg])
					self.sinOut2.emit([enbip, msg2])
				else:
					msg = 'None'
					msg2 = 'None'
					self.sinOut.emit([enbip, msg])
					self.sinOut2.emit([enbip, msg2])
			if command[-1] == self.socketip[1]:
				SockThread('connectionToCPEPC2').dosendcmd(command[:-1], socktask2)
				time.sleep(3)
				result = SockThread('connectionToCPEPC1').getresult(socktask2)
				print 'result2:', result
				cpeip = result[0]
				enbip = self.cpeipToEnbip(cpeip)
				check = str(result[2][0])
				if check == 'True':
					msg = '%s, %s, %s' % (result[2][1][0][0], result[2][1][0][1], result[2][1][0][2])
					msg2 = '%s, %s, %s' % (result[2][1][1][0], result[2][1][1][1], result[2][1][1][2])
					self.sinOut.emit([enbip, msg])
					self.sinOut2.emit([enbip, msg2])
				else:
					msg = 'None'
					msg2 = 'None'
					self.sinOut.emit([enbip, msg])
					self.sinOut2.emit([enbip, msg2])
		command = ['quit']
		SockThread('connectionToCPEPC1', self.socketip[0]).dosendcmd(command, socktask1)
		SockThread('connectionToCPEPC1', self.socketip[0]).dosendcmd(command, socktask2)

class MyBothtestThread(QThread):
	sinOut = pyqtSignal(list)
	sinOut2 = pyqtSignal(list)
	
	def __init__(self, parent=None):
		super(MyBothtestThread, self).__init__(parent)
	
	def getSendingmsg(self, ueid):
		xmldata = cf.Parsing_XML()
		self.sendlist = []
		for ue in ueid:
			s = xmldata.Operation(ue, 'BOTH')
			self.sendlist.append(s)
		return self.sendlist
	
	def cpeipToEnbip(self, cpeip):
		xmldata = cf.Parsing_XML()
		uedata = xmldata.get_ue_data(xmlname)
		enbdata = xmldata.get_enb_data(xmlname)
		for k in uedata.keys():
			if uedata[k]['cpeip'] == cpeip:
				return enbdata[k]['enbip']
	
	def getsocketip(self):
		xmldata = cf.Parsing_XML()
		self.socketip = xmldata.getcontrolpc()
		return self.socketip
	
	def run(self):
		socktask1 = SockThread('connectionToCPEPC', self.socketip[0])
		socktask1.setDaemon(True)
		socktask1.start()
		socktask2 = SockThread('connectionToCPEPC', self.socketip[1])
		socktask2.setDaemon(True)
		socktask2.start()
		for command in self.sendlist:
			if command[-1] == self.socketip[0]:
				SockThread('connectionToCPEPC1', self.socketip[0]).dosendcmd(command[:-1], socktask1)
				time.sleep(3)
			if command[-1] == self.socketip[1]:
				SockThread('connectionToCPEPC2').dosendcmd(command[:-1], socktask2)
				time.sleep(3)
		for command in self.sendlist:
			if command[-1] == self.socketip[0]:
				result = SockThread('connectionToCPEPC1').getresult(socktask1)
			if command[-1] == self.socketip[1]:
				result = SockThread('connectionToCPEPC2').getresult(socktask2)
			print result
			cpeip = result[0]
			enbip = self.cpeipToEnbip(cpeip)
			check = str(result[2][0])
			if check == 'True':
				msg = '%s, %s, %s' % (result[2][1][0][0], result[2][1][0][1], result[2][1][0][2])
				msg2 = '%s, %s, %s' % (result[2][1][1][0], result[2][1][1][1], result[2][1][1][2])
				self.sinOut.emit([enbip, msg])
				self.sinOut2.emit([enbip, msg2])
			else:
				msg = 'None'
				msg2 = 'None'
				self.sinOut.emit([enbip, msg])
				self.sinOut2.emit([enbip, msg2])
		command = ['quit']
		SockThread('connectionToCPEPC1', self.socketip[0]).dosendcmd(command, socktask1)
		SockThread('connectionToCPEPC1', self.socketip[0]).dosendcmd(command, socktask2)


def accessible(enbip, count=5):
	pingcmd = 'ping %s -n %d' % (enbip, int(count))
	p = subprocess.Popen(pingcmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	out = p.stdout.read()
	data = unicode(eval(repr(out)), "gbk")
	result = re.findall(r'Ping(.*)Ping', data, re.M | re.S)
	if not result: return False
	lines = result[0].split('\r\n')
	if len(lines) <= 3: return False
	lines = lines[1:-2]
	ttls = re.findall(r'TTL=', result[0])
	if float(len(ttls)) / float(len(lines)) < 0.5:
		return False
	try:
		localssh = paramiko.SSHClient()
		localssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		localssh.connect(enbip, 27149, 'admin', 'admin')
		time.sleep(1)
		localssh.close()
	except Exception, e:
		return False
	return True

if __name__ == "__main__":
	multiprocessing.freeze_support()
	app = QtGui.QApplication(sys.argv)
	myobj = openWnd()
	myobj.show()
	sys.exit(app.exec_())