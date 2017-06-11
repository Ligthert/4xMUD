#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb
import cmd
import pprint
from getpass import getpass
import os
import prettytable

# This spice must flow!
con = mdb.connect('localhost', 'ts', 'ts', 'ts')
cur = con.cursor()

user_id = 0

def login():
	login_id = 0
	uniq = 0

	os.system("cat motd")

	print "Login with your username and password. If you are new and wish to create a new account. Login with user 'create'";
	while login_id == 0:
		username = raw_input("Username:")
		
		if username == "create":
			# Helpful account creation stuff happens here.
			# Magical MySQL stuff is going to happen here.

			print "Before you can login, we need a unique username. This is the name other players will see."
			username = raw_input("Username:")
			username = con.escape_string(username)
			sql = "SELECT username FROM users WHERE username=%s"
			cur.execute(sql,(username))
			if ( cur.rowcount == 1):
				uniq = 0
			else:
				uniq = 1

			while uniq == 0:
				print "It appears this name is already in use. :-( Please choose another username."
				username = raw_input("Username:")
				username = con.escape_string(username)
				sql = "SELECT username FROM users WHERE username=%s"
				cur.execute(sql,(username))
				if ( cur.rowcount == 1):
					uniq = 0
				else:
					uniq = 1

			print "Now we need a strong password. You will see on screen what is entered."
			password = raw_input("Password:")
			print "This is a pretty weak password, but strong enough... For now."
		
			password = con.escape_string(password)
			
			sql = "INSERT INTO users SET username=%s,password=%s"
			cur.execute(sql,(username,password))
			
			login_id = con.insert_id()			

			# outcast@overseer:~$ set | grep 79.130.85.30
			# SSH_CLIENT='79.130.85.30 11790 65535'
			# SSH_CONNECTION='79.130.85.30 11790 81.171.33.99 65535'

		else:
			password = getpass("Password:")
			username = con.escape_string(username)
			password = con.escape_string(password)
			sql = "SELECT id FROM users WHERE username=%s and password=%s"
			cur.execute(sql, (username, password))
			if ( cur.rowcount == 1 ):
				res = cur.fetchone()
				login_id = res[0]
			else:
				print "Wrong user/pass combination. Try again."
			
	
	return login_id


class cli_interface(cmd.Cmd):
 """ The main program """
 # colony fleet player planet research blueprints design
 prompt="HQ>"

# def do_colony():

# def help_colony():

# def complete_colony():

# def do_fleet():

# def do_show():

 def do_player(self,line):
	params = line.split(" ")
	length = len(params)
	
	if params[0] == "set" and length == 3:
	 if params[1] == "capital":
	  print "do capital stuff"
	 elif params[1] == "password" or params[1] == "passwd":
	  print "do passwd stuff"
	 elif params[1] == "email":
	  print "do email stuff"
	 else:
	  print "Syntax Error"

	elif params[0] == "info" and length == 2:
	 print "params1 stuff + mysql magic"
	elif params[0] == "":
	 print "In Soviet Russia Info Looks up You!!!"
	elif params[0] == "set" and params[1] == "description":
		print "params 2 and beyond!"
	else:
	 print "Syntax Error"	

 def help_player(self):
	print "\nThe player command is to look up your own or other player's statistics and to set your own preferences.\n"
	x = prettytable.PrettyTable(["Command", "Description"])
	x.align["Command"] = "l"
	x.align["Description"] = "l"
	x.add_row(["player","print your statistics and score"])
        x.add_row(["player set description \"Things about yourself\"","set your description"])
        x.add_row(["player set email user@domain.tld","set your email address"])
        x.add_row(["player set password PASSWORD","set a new password"])
	x.add_row(["player set capital <id>","set a capital city (colony id)"])
        x.add_row(["player info <playername>","print player statistics and score"])
	print x

# def do_planet():

# def do_research():

# def do_blueprints():

# def do_design():

 def do_EOF(self, line):
  print "Thank you for playing! :-)"
  return True

 def help_EOF(this):
  print "Also known as CTRL+D, this will end your current session."

 def emptyline(self):
  pass


if __name__ == '__main__':
#	user_id = login()
	user_id = 1
	cli_interface().cmdloop()
