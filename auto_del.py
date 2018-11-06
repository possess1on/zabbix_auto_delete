#!/usr/bin/python
# -*- coding: utf-8 -*-

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
  Time_Check_Days=30
  
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
	f = open('/home/sd/del_host_log/del_log_'+ now2.strftime("%d-%m-%Y")+'.txt', 'w')
	for trigger in z.trigger.get({"output": [ "triggerid", "description", "priority" ], "filter": { "value": 1 }, "sortfield": "priority", "sortorder": "DESC"}):
		if trigger["description"] == u'{HOST.NAME} нет связи':
			trigmsg = z.trigger.get({"triggerids": trigger["triggerid"], "selectHosts": "extend"}) #json with []
			for tm in trigmsg: #json withOut []
				for l in tm['hosts']:
					problem = z.problem.get({"hostids": l['hostid'], "recent": "true", "sortfield": "eventid"})
			for pr in problem:
				if int(pr['clock']) < Timestamp_Time_Check_Days:
					hostinterface = z.hostinterface.get({"hostids": l['hostid'], "output": "extend"})
					for hi in hostinterface:
						r = now2.strftime("%d-%m-%Y %H:%M")+ " " + hi["hostid"] + " " + pr["name"] + " " + hi["ip"] + " " + hi["dns"]
						#print r
						f.write(r + '\n')
						z.host.delete( [int(hi['hostid'])] )
	f.close()
	sendmail(hi["hostid"], pr["name"], hi["ip"], hi["dns"])

def sendmail(hostid, name, ip, dns):
	print "in sendmail function"
	import smtplib 
	import email.utils 
	from email.mime.multipart import MIMEMultipart 
	from email.mime.base import MIMEBase 
	from email.mime.text import MIMEText 
	from email import Encoders
	from datetime import datetime
	
	#Mail settings
	SMTPServer = "exsrv.example.com"
	FromAddr = "example@example.com"
	ToAddr = "example2@example2.com"
	
	#email
	now2 = datetime.now()
	msg = MIMEMultipart('ZDel') 
	msg['To'] = email.utils.formataddr(('ZDel', ToAddr)) 
	msg['From'] = email.utils.formataddr(('ZDel', FromAddr)) 
	msg['Subject'] = 'Zabbix deleted host more than 30d inactive' 

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
