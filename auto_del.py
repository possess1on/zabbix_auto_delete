#!/usr/bin/python
# -*- coding: utf-8 -*-
#https://github.com/possess1on/zabbix_auto_delete/

def removehost():
	print "in removehost function"
	import re, requests, sys, json, time
	from zabbix_api import ZabbixAPI, Already_Exists
	from datetime import datetime
	reload(sys)
	sys.setdefaultencoding('utf8')

	#Zabbix credentials
	Server = "https://ip_addr/zabbix"
	Login = "Admin"
	Password = "zabbix"
	Time_Check_Days = 60
	Trigger_description = u'нет связи'
	Trigger_description2 = u'Нет связи более 20 минут'
	#Trigger_description2 = u'{HOST.NAME} нет связи'
  
	#Parser settings
	now2 = datetime.now()
	z = ZabbixAPI(server=Server)
	z.login(Login, Password)
	#timestamp
	Timestamp_Time_Now = int(time.mktime(datetime.now().timetuple()))
	Timestamp_Time_Now_value = datetime.fromtimestamp(Timestamp_Time_Now)
	#
	Timestamp_Time_Check_Days = Timestamp_Time_Now - (3600 * 24 * Time_Check_Days)
	Timestamp_Time_Check_Days_value = datetime.fromtimestamp(Timestamp_Time_Check_Days)
	#parser
	
	for trigger in z.trigger.get({"output": [ "triggerid", "description", "priority" ], "filter": { "value": 1 }, "sortfield": "priority", "sortorder": "DESC"}):
		#if trigger["description"] == Trigger_description:
		if Trigger_description in (trigger["description"].lower()):
			if Trigger_description2 not in trigger["description"]:
				trigmsg = z.trigger.get({"triggerids": trigger["triggerid"], "selectHosts": "extend"}) #json with []
				for tm in trigmsg: #json withOut []
					for l in tm['hosts']:
						problem = z.problem.get({"objectids": trigger["triggerid"], "recent": "true", "sortfield": "eventid"})
				for pr in problem:
					if int(pr['clock']) < Timestamp_Time_Check_Days:
						hostinterface = z.hostinterface.get({"hostids": l['hostid'], "output": "extend"})
						for hi in hostinterface:
							r = now2.strftime("%d-%m-%Y %H:%M")+ " " + hi["hostid"]+"/"+trigger["triggerid"] + " " + pr["name"] + " " + hi["ip"] + " " + hi["dns"]
							print r
							f = open('/home/sd/del_host_log/del_log_'+ now2.strftime("%d-%m-%Y")+'.txt', 'a+')
							f.write(r + '\n')
							f.close()
							z.host.delete( [int(hi['hostid'])] )
	try:
		sendmail()
	except Exception:
		print "No host for delete"

def sendmail():
	print "in sendmail function"
	import smtplib 
	import email.utils 
	from email.mime.multipart import MIMEMultipart 
	from email.mime.base import MIMEBase 
	from email.mime.text import MIMEText 
	#from email import Encoders
	from datetime import datetime
	
	#Mail settings
	SMTPServer = "exsrv.example.com"
	FromAddr = "example@example.com"
	ToAddr = "example@example.com"
	
	#email
	now2 = datetime.now()
	msg = MIMEMultipart('ZDel') 
	msg['To'] = email.utils.formataddr(('ZDel', ToAddr)) 
	msg['From'] = email.utils.formataddr(('ZDel', FromAddr)) 
	msg['Subject'] = 'Zabbix deleted host more than 60d inactive' 

	# Attach a file 

	#mail_file = file('/home/sd/del_host_log/del_log_'+ now2.strftime("%d-%m-%Y")+'.txt').read() 
	
	mail_file = MIMEBase('application', 'octet-stream') 
	mail_file.set_payload(open('/home/sd/del_host_log/del_log_'+ now2.strftime("%d-%m-%Y")+'.txt', 'rb').read()) 
	mail_file.add_header('Content-Disposition', 'attachment', filename='del_log_'+ now2.strftime("%d-%m-%Y")+'.txt') 
	#Encoders.encode_base64(mail_file) 
	msg.attach(mail_file) 
	
	# Define SMTP server 

	server = smtplib.SMTP(SMTPServer) 
	server.set_debuglevel(False) # show communication with the server 

	# Send the mail 

	try: 
		server.sendmail(FromAddr, [ToAddr], msg.as_string()) 
	finally: 
		server.quit()

if __name__ == "__main__":
	removehost()
