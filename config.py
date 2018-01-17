#!/usr/bin/env python
#coding=utf-8
from xml.dom import minidom

class Parsing_XML():
	def __init__(self):
		pass
	
	'''Parsing XML-formatted files for Lart_i'''
	
	def get_attrvalue(self, node, attrname):
		return node.getAttribute(attrname) if node else ''
	
	def get_nodevalue(self, node, index=0):
		return node.childNodes[index].nodeValue if node else ''
	
	def get_xmlnode(self, node, name):
		return node.getElementsByTagName(name) if node else []
	
	def xml_to_string(self, filename):
		doc = minidom.parse(filename)
		return doc.toxml('UTF-8')
	
	def get_ue_data(self, filename):
		doc = minidom.parse(filename)
		root = doc.documentElement
		ue_nodes = self.get_xmlnode(root, 'ue')
		ue_list = {}
		for node in ue_nodes:
			ue_id = self.get_attrvalue(node, 'id')
			node_controlpcIp = self.get_xmlnode(node, 'controlpc')
			node_cpeip = self.get_xmlnode(node, 'cpeip')
			node_model = self.get_xmlnode(node, 'model')
			node_serverip = self.get_xmlnode(node, 'serverip')
			ue_controlpcIp = self.get_nodevalue(node_controlpcIp[0])
			ue_cpeip = self.get_nodevalue(node_cpeip[0])
			ue_model = self.get_nodevalue(node_model[0])
			ue_serverip = self.get_nodevalue(node_serverip[0])
			if ue_controlpcIp == '1':
				ue_controlpcIp = self.getcontrolpc()[0]
			elif ue_controlpcIp == '2':
				ue_controlpcIp = self.getcontrolpc()[1]
			else:
				ue_controlpcIp = ''
			ue = {}
			ue['controlpc'], ue['cpeip'], ue['model'], ue['serverip'] = (
				ue_controlpcIp, ue_cpeip, ue_model, ue_serverip)
			ue_list[ue_id] = ue
		return ue_list
	
	def get_enb_data(self, filename):
		doc = minidom.parse(filename)
		root = doc.documentElement
		enb_nodes = self.get_xmlnode(root, 'enb')
		enb_list = {}
		for node in enb_nodes:
			enb_id = self.get_attrvalue(node, 'id')
			node_enbip = self.get_xmlnode(node, 'enbip')
			node_earfcn = self.get_xmlnode(node, 'earfcn')
			node_pci = self.get_xmlnode(node, 'pci')
			node_mme = self.get_xmlnode(node, 'mme')
			node_plmn = self.get_xmlnode(node, 'plmn')
			node_segw = self.get_xmlnode(node, 'segw')
			node_psk = self.get_xmlnode(node, 'psk')
			enb_enbip = self.get_nodevalue(node_enbip[0])
			enb_earfcn = self.get_nodevalue(node_earfcn[0])
			enb_pci = self.get_nodevalue(node_pci[0])
			enb_mme = self.get_nodevalue(node_mme[0])
			enb_plmn = self.get_nodevalue(node_plmn[0])
			enb_segw = self.get_nodevalue(node_segw[0])
			enb_psk = self.get_nodevalue(node_psk[0])
			enb= {}
			enb['enbip'], enb['earfcn'], enb['pci'], enb['mme'], enb['plmn'], enb['segw'], enb['psk'] = (
			enb_enbip, enb_earfcn, enb_pci, enb_mme, enb_plmn, enb_segw, enb_psk)
			enb_list[enb_id] = enb
		return enb_list
	
	def get_ftpdata(self, filename):
		doc = minidom.parse(filename)
		root = doc.documentElement
		ftp_nodes = self.get_xmlnode(root, 'ftpargs')
		ftpargs = []
		for node in ftp_nodes:
			node_serviceTime = self.get_xmlnode(node, 'serviceTime')
			node_ftpUser = self.get_xmlnode(node, 'ftpUser')
			node_ftpPasswd = self.get_xmlnode(node, 'ftpPasswd')
			node_dlThreadCount = self.get_xmlnode(node, 'dlThreadCount')
			node_dwpath = self.get_xmlnode(node, 'dwpath')
			node_localdwpath = self.get_xmlnode(node, 'localdwpath')
			node_dlFilename = self.get_xmlnode(node, 'dlFilename')
			node_ulThreadCount = self.get_xmlnode(node, 'ulThreadCount')
			node_uppath = self.get_xmlnode(node, 'uppath')
			node_localuppath = self.get_xmlnode(node, 'localuppath')
			node_ulFilename = self.get_xmlnode(node, 'ulFilename')
			ftp_serviceTime = self.get_nodevalue(node_serviceTime[0])
			ftp_ftpUser = self.get_nodevalue(node_ftpUser[0])
			ftp_ftpPasswd = self.get_nodevalue(node_ftpPasswd[0])
			ftp_dlThreadCount = self.get_nodevalue(node_dlThreadCount[0])
			ftp_dwpath = self.get_nodevalue(node_dwpath[0])
			ftp_localdwpath = self.get_nodevalue(node_localdwpath[0])
			ftp_dlFilename = self.get_nodevalue(node_dlFilename[0])
			ftp_ulThreadCount = self.get_nodevalue(node_ulThreadCount[0])
			ftp_uppath = self.get_nodevalue(node_uppath[0])
			ftp_localuppath = self.get_nodevalue(node_localuppath[0])
			ftp_ulFilename = self.get_nodevalue(node_ulFilename[0])
			ftpargs = [ftp_serviceTime, ftp_ftpUser, ftp_ftpPasswd, ftp_dlThreadCount, ftp_dwpath, ftp_localdwpath
		                          , ftp_dlFilename, ftp_ulThreadCount, ftp_uppath, ftp_localuppath, ftp_ulFilename]
		return ftpargs
		
	def get_num(self, filename):
		doc = minidom.parse(filename)
		root = doc.documentElement
		num = self.get_xmlnode(root, 'number')
		numvalue = self.get_nodevalue(num[0])
		numlist = numvalue.split(" ")
		return numlist
	
	def getTimeout(self, filename):
		doc = minidom.parse(filename)
		root = doc.documentElement
		node = self.get_xmlnode(root, 'timeout')
		timeout = self.get_nodevalue(node[0])
		return timeout
	
	def getcontrolpc(self, filename='args.xml'):
		doc = minidom.parse(filename)
		root = doc.documentElement
		node = self.get_xmlnode(root, 'controlpc1')
		controlpc1 = self.get_nodevalue(node[0])
		node2 = self.get_xmlnode(root, 'controlpc2')
		controlpc2 = self.get_nodevalue(node2[0])
		return [controlpc1, controlpc2]
	
	def Operation(self, ueid, Operation):
		cpedata = self.get_ue_data('args.xml')[ueid]
		enbdata = self.get_enb_data('args.xml')[ueid]
		ftpargs = self.get_ftpdata('args.xml')
		cpeip = cpedata['cpeip']
		serverip = cpedata['serverip']
		cpetype = cpedata['model']
		earfcn = enbdata['earfcn']
		controlpcip = cpedata['controlpc']
		ftpargs.insert(0, serverip)
		pci = enbdata['pci']
		if Operation == 'ATTACH':
			paramlist = [cpeip, 'ATTACH', [serverip, cpetype, earfcn, pci], controlpcip]
		elif Operation == 'DOWNLOAD':
			paramlist = [cpeip, 'DOWNLOAD', ftpargs, controlpcip]
		elif Operation == 'UPLOAD':
			paramlist = [cpeip, 'UPLOAD', ftpargs, controlpcip]
		elif Operation == 'BOTH':
			paramlist = [cpeip, 'BOTH', ftpargs, controlpcip]
		else:
			paramlist = []
			print 'Operation参数输入错误...'
		return paramlist
		
if __name__ == "__main__":
	print Parsing_XML().Operation('002','ATTACH')