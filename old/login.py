#!/usr/bin/python

from getpass import getpass

user_id = 0

print "Login with your username and password. If you are new and wish to create a new account. Login with user 'create'";
while user_id == 0:
	username = raw_input("Username:")

	if username == "create":
		print "Fun!\n"
		user_id = 1
		password = "*****"
	else:
		#password = raw_input("Password:")
		password = getpass("Password:")
		user_id = 2

print username,"/",password,"\n"

# print "Hello", name
# raw_input("Press any key to exit.") 
