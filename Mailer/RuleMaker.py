import sys

OwnPath = sys.path[0] + '/' #This doesn't need to be changed
                            #The rulemaker is an independent utility.
def is_int(s):
	try:
		int(s)
		return True
	except ValueError:
		return False
	return False
                            
def DisplayThings():
	print('Would you like to see the current')
	print('(R)ules, (G)roups or (E)xceptions?')
	arg = input('--> ')
	arg = arg.upper()
	if(arg == 'R'):
		with open(OwnPath + 'Rules', 'r') as Rulesfile:
			i = 1
			for line in Rulesfile:
				print('{0}: {1}'.format(i, line.rstrip()))
				i = i+1
	elif(arg == 'G'):
		with open(OwnPath + 'Groups', 'r') as Groupfile:
			for line in Groupfile:
				print(line.rstrip())
	elif(arg == 'E'):
		with open(OwnPath + 'exceptions', 'r') as Exceptionsfile:
			for line in Exceptionsfile:
				print(line.rstrip())
	else:
		print('This is not a valid argument!')
	print()
		
def CreateThings():
	print('Would you like to add a')
	print('(R)ule, (G)roup or (E)xception?')
	arg = input('--> ')
	arg = arg.upper()
	if(arg == 'R'):
		with open(OwnPath + 'Rules', 'a') as Rulesfile:
			print('Please enter a rule in the format')
			print('[EXCEPT/INCLUDE] [GROUP] [TIME] [NUMBER] [INTERVAL] [CUSTOM] [ISSUENO]')
			arg = input('--> ')
			helptext = arg.split()
			if(is_int(helptext[2]) and is_int(helptext[3]) and is_int(helptext[4]) and is_int(helptext[6])):
				Rulesfile.write(arg)
			else:
				print('This is not a valid rule. Rule was not added')
	elif(arg == 'G'):
		with open(OwnPath + 'Groups', 'a') as Groupfile:
			print('Please enter a group in the format')
			print('[GROUPNAME] [USERNAME1] [USERNAME2] [USERNAME3] [USERNAME4]...')
			arg = input('--> ')
			Groupfile.write(arg)
	elif(arg == 'E'):
		with open(OwnPath + 'exceptions', 'a') as Exceptionsfile:
			print('Please enter an username')
			arg = input('--> ')
			Exceptionsfile.write(arg)
	else:
		print('This is not a valid argument!')
	print()
	

def RemoveThings():
	print('Would you like to remove a')
	print('(R)ule, (G)roup or (E)xception?')
	arg = input('--> ')
	arg = arg.upper()
	if(arg == 'R'):
		print('Please enter the line number of the rule you wish to remove.')
		print('As given by the Display function')
		arg = input('--> ')
		if(is_int(arg)):
			with open(OwnPath + 'Rules', 'r+') as Rulesfile:
				i = 1
				d = Rulesfile.readlines()
				Rulesfile.seek(0)
				for line in d:
					if(i != int(arg)):
						Rulesfile.write(line)
					i = i+1
				Rulesfile.truncate()
		else:
			print('This is not a valid argument!')
	elif(arg == 'G'):
		print('Please enter the name of the group you wish to remove.')
		arg = input('--> ')
		with open(OwnPath + 'Groups', 'r+') as Groupfile:
			d = Groupfile.readlines()
			Groupfile.seek(0)
			for line in d:
				helptext = line.split()
				if(helptext[0] != arg):
					Groupfile.write(line)
			Groupfile.truncate()
	elif(arg == 'E'):
		print('Please enter the username you wish to remove.')
		arg = input('--> ')
		with open(OwnPath + 'exceptions', 'r+') as Exceptionsfile:
			d = Exceptionsfile.readlines()
			Exceptionsfile.seek(0)
			for line in d:
				helptext = line.split()
				if(helptext[0] != arg):
					Exceptionsfile.write(line)
			Exceptionsfile.truncate()
	else:
		print('This is not a valid argument!')
	print()



cont = True
print('Welcome to the RuleMaker utility for the GPU monitor and alerting system.')
print('This utility allows you create rules, groups those rules apply to, and overall exceptions.')
print('For the mailer system of the GPU monitor and alerting system.')
while(cont):
	print('What would you like to do?')
	print('Display the current rules, groups or overall exceptions (D)')
	print('Add a new rule, group or overall exception (A)')
	print('Remove a rule, group or overall exception (R)')
	print('Or end the program (E)?')
	print('Please enter the associated letter. Not case sensitive.')
	arg = input('--> ')
	arg = arg.upper()
	if(arg == 'D'):
		DisplayThings()
	elif(arg == 'A'):
		CreateThings()
	elif(arg == 'R'):
		RemoveThings()
	elif(arg == 'E'):
		cont = False
	else:
		print('This is not a valid argument!')
	
	
	
	
	
	
	
	
	
	
	
	
	
	
