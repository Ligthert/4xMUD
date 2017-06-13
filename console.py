#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cmd
import pymysql.cursors
import os
from getpass import getpass
import prettytable
import configparser
from jinja2 import Template

# Load out the config
config = configparser.ConfigParser()
config.read('config.ini')

# Connect to the MySQL Server using the data in the configfile
db = pymysql.connect(host=config['database']['hostname'],
  user=config['database']['username'],
  password=config['database']['password'],
  db=config['database']['database'],
  cursorclass=pymysql.cursors.DictCursor)
  # Because 2 spaces are better than one tab

cursor = db.cursor()

# Have some preset queries that should make our life easier
sql_auth_search = "SELECT count(*) as count FROM users WHERE username=%s"
sql_auth_check = "SELECT id FROM users WHERE username=%s AND password=%s"
sql_auth_create = "INSERT INTO users (username,password) VALUES (%s,%s)"
sql_player_info = "SELECT * FROM users WHERE id=%s"
sql_player_update_password = "UPDATE users SET password=%s WHERE id=%s"
sql_player_update_description = "UPDATE users SET description=%s WHERE id=%s"
sql_player_update_email = "UPDATE users set email=%s WHERE id=%s"
sql_player_update_capital = "UPDATE users SET capital=%s WHERE id=%s"
sql_colony_get = "SELECT * FROM colonies WHERE id=%s AND user=%s"
sql_colony_list = "SELECT * FROM colonies WHERE user=%s"
sql_colony_set_taxrate = "UPDATE colonies SET taxrate=%s WHERE id=%s"

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
        # ret = auth_search(username)
        ret = cursor.execute(sql_auth_search,username)
        retval = cursor.fetchone()
        if retval['count']==1:
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
          cursor.execute(sql_auth_create, (username,passwd1) )
          db.commit()
          print("Password accepted. Please login.")
          password_same = 1

    # If a normal username is given, try and login the user
    else:
      password = getpass("Password: ")
      ##ret = auth_check(username,password)
      ret = cursor.execute(sql_auth_check, (username,password))
      retval = cursor.fetchone()
      if retval != None:
        user_id = retval['id']
      else:
        print("ERROR: username/password combination not found")

  return user_id

def colony_show(pid=0,colony=0):
  if pid != 0:
    print ("Do stuff")
    # Check if colony is not 0
    # Check if colony is owned by a player
    # check if player capital is not 0
  else:
    print ("Syntax Error: No PID provided")

# Do the CLI main loop
class x4mud(cmd.Cmd):
  prompt="4xMUD HQ> "

  def do_player(self,line):
    params = line.split(" ")
    length = len(params)

    if params[0] == "set" and length == 3:
      if params[1] == "capital":
        capital = params[2]
        # TODO: Extentensive checking if...
        # - Colony is owned by player
        # - Didn't do it recently
        cursor.execute(sql_player_update_capital, (capital,pid))
        db.commit()

      elif params[1] == "password" or params[1] == "passwd":
        password_same = 0
        while password_same == 0:
          print("Type your desired password")
          passwd1 = input("Password (1): ")
          passwd2 = input("Password (2): ")
          if passwd1 != passwd2:
            print("ERROR: These passwords don't match. PLease try again.")
          else:
            # auth_create(username,passwd1)
            cursor.execute(sql_player_update_password, (passwd1,pid) )
            db.commit()
            print("Password accepted.")
            password_same = 1
        password_same = 0

      elif params[1] == "email" and params[2] != "":
        email = params[2]
        cursor.execute(sql_player_update_email, (email,pid) )
        db.commit()

    # Show other player's info
    elif params[0] == "info" and length == 2:
      ret = cursor.execute(sql_player_info, (params[1]) )
      if ret != 0:
        player = cursor.fetchone()
        f = open("templates/player_info.tmpl")
        template = Template(f.read())
        print( template.render(name=player['username'],id=pid,score=player['score'],description=player['description'])  )
        f.close()
      else:
        print("Player does not exist.")

    # Print user info
    elif params[0] == "info":
      cursor.execute(sql_player_info, (pid) )
      player = cursor.fetchone()
      f = open("templates/player_self.tmpl")
      template = Template(f.read())
      print( template.render(name=player['username'],id=pid,score=player['score'])  )
      f.close()


    # Set custom description
    elif params[0] == "set" and params[1] == "description":
      description = input("Description: ")
      cursor.execute(sql_player_update_description, (description,pid) )
      db.commit()

    # Anything else is syntax error
    else:
      print("Syntax Error")


  def help_player(self):
    print("The player command is to look up your own or other player's statistics and to set your own preferences.")
    x = prettytable.PrettyTable(["Command", "Description"])
    x.align["Command"] = "l"
    x.align["Description"] = "l"
    x.add_row(["player","print your statistics and score"])
    x.add_row(["player set description","set your description"])
    x.add_row(["player set email user@domain.tld","set your email address"])
    x.add_row(["player set password","set a new password"])
    x.add_row(["player set capital <id>","set a capital city (colony id)"])
    x.add_row(["player info <playername>","print player statistics and score"])
    print(x)

  def do_colony(self, line):
    params = line.split(" ")
    length = len(params)
    # print(length)
    # print(params)
    if length == 1 and params[0] == "":

      x = prettytable.PrettyTable(["ID","Name","Population"])
      x.align["ID"] = "l"
      x.align["Name"] = "l"
      x.align["Population"] = "l"
      ret = cursor.execute(sql_colony_list,(pid))
      if ret != 0:
        retval = cursor.fetchall()
        for colony in retval:
          x.add_row([colony['id'],colony['name'],colony['population']])
        print(x)
      else:
        print("No colonies")

    elif length == 1 and params[0] != "":
      # TODO Check of colony is owned by player
      colony = params[0]
      if colony.isnumeric():
        # Check to see of the colony is yours
        ret = cursor.execute(sql_colony_get,(colony,pid))
        if ret != 0:
            retval = cursor.fetchall()
            retval = retval[0]
            print(retval)
            x=prettytable.PrettyTable(["Key","Value"])
            x.align["Key"] = "l"
            x.align["Value"] = "l"
            x.add_row(["ID",retval['id']])
            x.add_row(["Name",retval['name']])
            x.add_row(["Population",retval['population']])
            x.add_row(["Sick",retval['sick']])
            x.add_row(["Employed",retval['employed']])
            x.add_row(["Tax-Rate",retval['taxrate']])
            print(x)
        else:
          print("Error: Requested colony is not yours (yet)")

      else:
        print("Error: Colony ID isn't a numeric")

    # Enter the set-cycle
    elif params[1] == "set":
      # set taxrate
      if params[2] == "taxrate":
        colony = params[0]
        taxrate = int(params[3])
        if taxrate >= 0 and taxrate <=100:
          cursor.execute(sql_colony_set_taxrate,(taxrate,colony))
          db.commit()
          print("Set taxrate (%) to: "+str(taxrate))
        else:
          print("Error: taxrate is not in 0-100")

  def help_colony(this):
    print("The colony command is to administrate most aspects of the colonies.")
    x = prettytable.PrettyTable(["Command","Description"])
    x.align["Command"] = "l"
    x.align["Description"] = "l"
    x.add_row(["colony","Returns a list of all player held colonies"])
    x.add_row(["colony #","Show details of a single colony"])
    x.add_row(["colony # set taxrate #","Set the taxrate of a colony"])
    print(x)

  def do_blueprints(this,line):
    params = line.split(" ")
    length = len(params)

    if params[0] == "":
      print("List stuff")

    if params[0] == "class" and params[1].isnumeric():
      if params[2] == "type" and params[3].isnumeric():
        print("type stuff")
    else:
        print("class stuff")

    if params[0] == "view" and params[1].isnumeric():
      print("Do view stuff")

    if params[0] == "delete" and params[1].isnumeric():
      print("Delete stuff")

  def help_blueprints(this):
    print("The blueprints command allows the administration of blueprints from viewing, searching and deleting.")
    x = prettytable.PrettyTable(["Command","Description"])
    x.align["Command"] = "l"
    x.align["Description"] = "l"
    x.add_row(["blueprints","Returns a list of all blueprints owned by the player."])
    x.add_row(["blueprints class #","Searches for all instances of class of blueprints. These can be: buildings"])
    x.add_row(["blueprints class # type #","Searches for all instances of a class and type of blueprints."])
    x.add_row(["blueprints view #","Review specs of a blueprint"])
    x.add_row(["blueprints delete #","Deletes a blueprint"])
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
  db.close()
