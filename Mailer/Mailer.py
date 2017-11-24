import smtplib
from email.message import EmailMessage

#Verander om e-mail te veranderen.
inlogname = "SETeam10@gmail.com"
fromaddr = "SETeam10@gmail.com"
password = "GPUSchedule1"


#Doesn't work on home PC, but fairly certain it should work on leiden PCs, need to test
#Gets blocked by provider, see http://issc.leidenuniv.nl/ict-voor-studenten/handleidingen/umail.html bij 'opmerking'
#inlogname = "s1530186"
#fromaddr = "s1530186@umail.leidenuniv.nl" # - this format should be correct.
#password = not giving you my password




#Als iets in de standaardmail file iets in tobereplaced is, dan
#wordt het vervangen door diezelfde positie in replacementss.
#Dus tobereplaced[0] wordt replacements[0]
#Als je meer replacements wil, 4 stappen:
#1: doe een extra waarde bij tobereplaced. Bijvoorbeeld '[EXAMPLE]'
#2: doe een extra waarde bij replacements. Maakt niet uit, wordt overschreven.
#3: doe een extra functie argument bij sendamail. Nu, sendamail(mailno, username, servernumber, example)
#4: extra assignment in sendamail. replacements[2] (of 3, of 4...)  = example.
#Done!
tobereplaced = ['[USERNAME]', '[SERVERNUM]']
replacements = ['', '']


#Stuurt mail met de gmail 'fromaddr' met wachtwoord 'password'.
#Die zijn global voor makkelijke aanpassing.
#naar toaddr, met als subject mailsubject, en als content mailbody.
def sendmails(toaddr, mailsubject, mailbody):
	
	msg = EmailMessage()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = mailsubject
	
	text = msg.as_string()
	text += mailbody
	
	#Verander naar de leidenuniv smtp zodra we een officiele account hebben.
	#with smtplib.SMTP('smtp.leidenuniv.nl', 25) as server:
	with smtplib.SMTP('smtp.gmail.com', 587) as server:
		server.starttls()
		server.login(inlogname, password)
		server.sendmail(fromaddr, toaddr, text)


#Vervangt de username met de custom mail in de custommails file
#Als die username er in staat.
#Anders, doet @umail.leidenuniv.nl er bij en stuurt dat.
def processusername(username):
	try:
		with open('custommails', 'r') as m:
			for line in m:
				helptext = line.split()
				if(len(helptext) < 2):
					break
				if username == helptext[0]:
					return helptext[1]
	except IOError as e:
		print(e)
		print('custommails does not exist. Creating empty custommails file.')
		f = open('custommails', 'w+')
		f.close();
	username += '@umail.leidenuniv.nl'
	return username


#De functie die je aan wil roepen.
#Mailno selecteerd de standaardmail te gebruiken.
def sendamail(mailno, username, servernumber):
	replacements[0] = username
	replacements[1] = servernumber
	
	try: #Necessary even with 'with open', if the standard mail does not exist.
		with open('standaardmail' + str(mailno), 'r') as f:
			toaddr = processusername(username)
			t = f.readline()
			mailsubject = t
			mailbody = ''
			for line in f:
				mailbody += line
				mailbody += '\n'
			i = 0
			for things in tobereplaced:
				mailsubject = mailsubject.replace(things, str(replacements[i]))
				mailbody = mailbody.replace(things, str(replacements[i]))
				i += 1
			sendmails(toaddr, mailsubject, mailbody)
	except IOError as e:
		print(e)

	
sendamail(2, 's1530186', 3)


