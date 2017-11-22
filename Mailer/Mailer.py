import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

#Verander om e-mail te veranderen.
#Noot: Kan alleen met gmail.
fromaddr = "SETeam10@gmail.com"
password = "GPUSchedule1"

#Als iets in de standaardmail file iets in replacements is, dan
#wordt het vervangen door diezelfde positie in helpthings.
#Dus replacements[0] wordt helpthings[0]
#Als je meer replacements wil, 4 stappen:
#1: doe een extra waarde bij replacements. Bijvoorbeeld '[EXAMPLE]'
#2: doe een extra waarde bij helpthings. Maakt niet uit, wordt overschreven.
#3: doe een extra functie argument bij sendamail. Nu, sendamail(username, servernumber, example)
#4: extra assignment in sendamail. helpthings[2] (of 3, of 4...)  = example.
#Done!
replacements = ['[USERNAME]', '[SERVERNUM]']
helpthings = ['', '']


#Stuurt mail met de gmail 'fromaddr' met wachtwoord 'password'.
#Die zijn global voor makkelijke aanpassing.
#naar toaddr, met als subject mailsubject, en als content mailbody.
def sendmails(toaddr, mailsubject, mailbody):
	
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['to'] = toaddr
	msg['Subject'] = mailsubject

	msg.attach(MIMEText(mailbody, 'plain'))

	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr, password)
	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.quit


#Gaat door de standaardmail en vervangt de replacements met de helpthings.
def processstandardmail(text):
	helptext = ''
	helpbool = True
	for word in text.split():
		helpbool = True
		i = 0
		for things in replacements:
			if word == things:
				helptext += str(helpthings[i])
				helpbool = False
			i += 1
	
		if(helpbool):
			helptext += word
		helptext += ' '
	return helptext


#Vervangt de username met de custom mail in de custommails file
#Als die username er in staat.
#Anders, doet @umail.leidenuniv.nl er bij en stuurt dat.
def processusername(username):
	try:
		with open('custommails', 'rb') as m:
			for line in m:
				helptext = line.split()
				if(len(helptext) < 2):
					break
				if username == helptext[0]:
					return helptext[1]
	except IOError:
		print 'custommails does not exist. Creating empty custommails file.'
		f = open('custommails', 'w+')
		f.close();
	username += '@umail.leidenuniv.nl'
	return username


#De functie die je aan wil roepen.
#Mailno selecteerd de standaardmail te gebruiken.
def sendamail(mailno, username, servernumber):
	helpthings[0] = username
	helpthings[1] = servernumber
	
	try:
		with open('standaardmail' + str(mailno), 'rb') as f:
			toaddr = processusername(username)
			t = f.readline()
			mailsubject = processstandardmail(t)
			mailbody = ''
			for line in f:
				mailbody += processstandardmail(line)
				mailbody += '\n'
			sendmails(toaddr, mailsubject, mailbody)
	except IOError:
		print 'Requested standard mail does not exist.'


