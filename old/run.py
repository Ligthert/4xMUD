#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cmd
import postgresql
import os
from getpass import getpass
import prettytable
import configparser
from jinja2 import Template

# Load out the config
config = configparser.ConfigParser()
config.read('config.ini')

# Compulsary Database stuff
db = postgresql.open("pq://"+config['database']['username']+":"+config['database']['password']+"@"+config['database']['hostname']+"/"+config['database']['database'])

auth_search = db.prepare("SELECT count(*) FROM players WHERE name=$1")
auth_check = db.prepare("SELECT id FROM players WHERE name=$1 and pass=$2")
auth_create = db.prepare("INSERT INTO players (name,pass) VALUES ($1,$2)")
player_info = db.prepare("SELECT * FROM players WHERE id=$1")

# Global stuff. Ugly, should work.
pid = int()

# Do login prompt stuff
def login():
  user_id = 0
  print("Login with your username and password.\nIf you are new and wish to create a new account, login with user 'create'")
  while user_id == 0:
    username = input("Username: ")

    # The new user dialog
    if username == "create":
      username_uniq = 0
      password_same = 0
      while username_uniq == 0:
        print("Please enter your desired username: ")
        username = input("Username: ")
        ret = auth_search(username)
        if ret[0][0]==1:
          print("ERROR: Username already exists, please try again.")
        else:
          print("Username accepted, please choose a password.")
          username_uniq=1
      while password_same == 0:
        print("Type your desired password")
        passwd1 = input("Password (1): ")
        passwd2 = input("Password (2): ")
        if passwd1 != passwd2:
          print("ERROR: These passwords don't match. PLease try again.")
        else:
          auth_create(username,passwd1)
          print("Password accepted. Please login.")
          password_same = 1

    # If a normal username is given, try and login the user
    else:
      password = getpass("Password: ")
      ret = auth_check(username,password)
      if len(ret) != 0:
        user_id = ret[0][0]
      else:
        print("ERROR: username/password combination not found")

  return user_id


# Do the CLI main loop
class x4mud(cmd.Cmd):
  prompt="4xMUD HQ> "

  def do_player(self,line):
    params = line.split(" ")
    length = len(params)

    if params[0] == "set" and length == 3:
      if params[1] == "capital":
        print("do capital stuff")
      elif params[1] == "password" or params[1] == "passwd":
        print( "do passwd stuff")
      elif params[1] == "email":
        print("do email stuff")
      else:
        print("Syntax Error")

    # Show other player's info
    elif params[0] == "info" and length == 2:
      print("params1 stuff + mysql magic")

    # Print user info
    elif params[0] == "":
      qres = player_info(pid)
      player = qres[0]
      f = open("templates/player_self.tmpl")
      template = Template(f.read())
      print( template.render(name=player['name'],id=pid,score=player['score'])  )


    # Set custom description
    elif params[0] == "set" and params[1] == "description":
      print("params 2 and beyond!")

    # Anything else is syntax error
    else:
      print("Syntax Error")


  def help_player(self):
    print("The player command is to look up your own or other player's statistics and to set your own preferences.")
    x = prettytable.PrettyTable(["Command", "Description"])
    x.align["Command"] = "l"
    x.align["Description"] = "l"
    x.add_row(["player","print your statistics and score"])
    x.add_row(["player set description \"Things about yourself\"","set your description"])
    x.add_row(["player set email user@domain.tld","set your email address"])
    x.add_row(["player set password PASSWORD","set a new password"])
    x.add_row(["player set capital <id>","set a capital city (colony id)"])
    x.add_row(["player info <playername>","print player statistics and score"])
    print(x)

  def do_EOF(self, line):
    f = open("motd_end")
    print(f.read())
    return True

  def help_EOF(this):
    print("Also known as CTRL+D, this will end your current session.")

  def emptyline(self):
    pass

# __main__
if __name__ == '__main__':
  f = open("motd")
  print(f.read())
  pid = login()
  if pid!=0:
    x4mud().cmdloop()
