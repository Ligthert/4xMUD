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
db.autocommit(True)

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
sql_player_credits_add = "UPDATE users SET credits = credits + %s WHERE id=%s"
sql_player_credits_rem = "UPDATE users SET credits = credits - %s WHERE id=%s"

sql_colony_get = "SELECT * FROM colonies WHERE id=%s AND user=%s"
sql_colony_list = "SELECT * FROM colonies WHERE user=%s"
sql_colony_set_taxrate = "UPDATE colonies SET taxrate=%s WHERE id=%s"
sql_colony_build_buildings_check = "SELECT * FROM buildings WHERE colony=%s and blueprint=%s"
sql_colony_build_buildings_insert = "INSERT INTO buildings (colony,blueprint,amount) VALUES (%s,%s,%s)"
sql_colony_build_buildings_add = "UPDATE buildings SET amount = amount + %s WHERE colony=%s and blueprint=%s"
sql_colony_build_buildings_rem = "UPDATE buildings SET amount = amount - %s WHERE colony=%s and blueprint=%s"
sql_colony_build_buildings_del = "DELETE FROM buildings WHERE colony=%s and blueprint=%s"
sql_colony_build_ships = ""
sql_colony_metal_add = "UPDATE colonies SET metal = metal + %s WHERE id=%s"
sql_colony_metal_rem = "UPDATE colonies SET metal = metal - %s WHERE id=%s"
sql_colony_water_add = "UPDATE colonies SET water = water + %s WHERE id=%s"
sql_colony_water_rem = "UPDATE colonies SET water = water - %s WHERE id=%s"
sql_colony_employment_rem = "UPDATE colonies set employed = employed - %s WHERE id=%s"
sql_colony_employment_add = "UPDATE colonies set employed = employed + %s WHERE id=%s"

sql_blueprints_list = "SELECT bp.* FROM blueprints_owned as bpo LEFT JOIN blueprints as bp ON bp.id=bpo.blueprint WHERE bpo.user=%s"
sql_blueprints_view = "SELECT bp.* FROM blueprints_owned as bpo LEFT JOIN blueprints as bp ON bp.id=bpo.blueprint WHERE bpo.user=%s and bp.id=%s"
sql_blueprints_delete = "DELETE FROM blueprints_owned WHERE user=%s AND blueprint=%s"
sql_blueprints_class = "SELECT bp.* FROM blueprints_owned as bpo LEFT JOIN blueprints as bp ON bp.id=bpo.blueprint WHERE bpo.user=%s and bp.class=%s"
sql_blueprints_type = "SELECT bp.* FROM blueprints_owned as bpo LEFT JOIN blueprints as bp ON bp.id=bpo.blueprint WHERE bpo.user=%s and bp.type=%s"

# Variables we might need
CLASSES = ["building"]
TYPES = ["lab","well","mine","hospital","farm"]

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

    elif params[0].isnumeric() and params[1] == "buildings" and params[2].isnumeric() and params[3].isnumeric():
      colony_id = params[0]
      buildings = params[2]
      amount = params[3]
      blueprint = {}
      colony = {}

      colony_owned = 0
      colony_blueprint = 0
      colony_resources = 0
      colony_credits = 0
      colony_workers = 0
      # Check if the colony exists and owned by the player
      ret = cursor.execute(sql_colony_get, (colony_id,pid) )
      if ret != 0:
        colony_owned = ret
        colony = cursor.fetchall()
        colony = colony[0]
      else:
        print("Colony does not exist of belong to you.")
      # Check if the blueprint exits and owned by the player
      ret = cursor.execute(sql_blueprints_view, (pid, buildings))
      if colony_owned != 0 and ret != 0:
        colony_blueprint = ret
        blueprint = cursor.fetchall()
        blueprint = blueprint[0]
      else:
        print("Blueprint not found")

      # Check if there is enough money to build the buildings
      ret = cursor.execute(sql_player_info, (pid))
      player = cursor.fetchall()
      player = player[0]
      # print(player)
      # print(blueprint)
      # print(colony)
      if int(blueprint['price'] * int(amount)) <= player['credits']:
        colony_credits = int(blueprint['price']) * int(amount) # Store this for later
      else:
        print("There isn't enough budget to complete this project.")

      # Check if there are enough resources to build the buildings
      if ( (blueprint['metal'] * int(amount)) <= colony['metal']) and ( (blueprint['water'] * int(amount)) <= colony['water'] ):
        colony_resources = 1;
      else:
        print("There are insufficient resources available at the colony to complete this project.")

      # Check if there are enough unemployed and healthy people for the buildings
      if int(blueprint['power'] * amount) <= (colony['population'] - colony['employed'] - colony['sick']):
        colony_workers = blueprint['power'] * int(amount)


      if colony_owned != 0 and colony_blueprint != 0 and colony_resources != 0 and colony_credits != 0 and colony_workers != 0:
        # Reduce player credits
        ret = cursor.execute(sql_player_credits_rem, (colony_credits,pid) )
        # Reduce colony resources
        ret = cursor.execute(sql_colony_metal_rem, (blueprint['metal'] * int(amount),colony_id) )
        ret = cursor.execute(sql_colony_water_rem, (blueprint['water'] * int(amount),colony_id) )
        # Increase colony employed
        ret = cursor.execute(sql_colony_employment_rem, (int(blueprint['power'] * amount), colony_id) )

        print("Building "+amount+" x "+blueprint['name']+" in colony "+colony['name'])
        ret = cursor.execute(sql_colony_build_buildings_check, (colony_id,blueprint['id']))
        if ret != 0:
          cursor.execute( sql_colony_build_buildings_add, ( int(amount), colony_id, blueprint['id'] ) )
        else:
          cursor.execute(sql_colony_build_buildings_insert, (colony_id,blueprint['id'],int(amount)))

    elif params[0].isnumeric() and params[1] == "demolish" and params[2].isnumeric() and params[3].isnumeric():
      colony_id = params[0]
      buildings = params[2]
      amount = int(params[3])
      colony = {}
      colony_owned = 0

      # Check if colony is owned by player
      # Check if colony has buildings of type
      # if colony > buildings:
      #   UPDATE
      # elif buildings >= colony:
      #   DELETE
      ret = cursor.execute(sql_colony_get, (colony_id,pid) )
      if ret != 0:
        colony_owned = ret
        colony = cursor.fetchall()
        colony = colony[0]
      else:
        print("Colony does not exist of belong to you.")

      ret = cursor.execute(sql_colony_build_buildings_check, (colony_id,buildings))
      if ret!=0:
        retval = cursor.fetchall()
        structures = retval[0]
        if structures['amount'] > amount:
          cursor.execute( sql_colony_build_buildings_rem, ( amount, colony_id, buildings ) )
          print(str(amount) + " buildings of the type "+str(buildings)+" have been demolished.")
        else:
          cursor.execute( sql_colony_build_buildings_del, ( colony_id, buildings ) )
          print(str(structures['amount']) + " buildings of the type "+str(buildings)+" have been demolished.")

      else:
        print("No such buldings exist in this colony.")



  def help_colony(this):
    print("The colony command is to administrate most aspects of the colonies.")
    x = prettytable.PrettyTable(["Command","Description"])
    x.align["Command"] = "l"
    x.align["Description"] = "l"
    x.add_row(["colony","Returns a list of all player held colonies"])
    x.add_row(["colony #","Show details of a single colony"])
    x.add_row(["colony # set taxrate #","Set the taxrate of a colony"])
    x.add_row(["colony # buildings X Y","Build Y amount of X building at colony."])
    x.add_row(["colony # demolish X Y","Demolish Y amount of X buildings at colony."])
    x.add_row(["colony # ships X Y","Build Y amount of X ships"])
    print(x)

  def do_blueprints(this,line):
    params = line.split(" ")
    length = len(params)

    # print(params)
    # print(length)

    if params[0] == "":
      ret = cursor.execute(sql_blueprints_list,(pid))
      blueprints = cursor.fetchall()
      x = prettytable.PrettyTable(["ID","Inventor","Name","Price (credits)"])
      x.align["ID"] = "l"
      x.align["Inventor"] = "l"
      x.align["Name"] = "l"
      x.align["Price (credits)"] = "l"
      for blueprint in blueprints:
        x.add_row([blueprint['id'],blueprint['inventor'],blueprint['name'],blueprint['price']])
      print(x)

    if params[0] == "class" and params[1] != "":
      search_class = params[1]
      if search_class in CLASSES:
        ret = cursor.execute(sql_blueprints_class, (pid,search_class) )
        if ret != 0:
          bp = cursor.fetchall()
          print(bp)
        else:
          print("No blueprints found of this class.")
      else:
        print("Invalid class: "+search_class)

    if params[0] == "type" and params[1] != "":
      search_type = params[1]
      if search_type in TYPES:
        ret = cursor.execute(sql_blueprints_type, (pid,search_type) )
        if ret != 0:
          bp = cursor.fetchall()
          print(bp)
        else:
          print("No blueprints found of this class.")
      else:
        print("Invalid class: "+type_class)

    if params[0] == "view" and params[1].isnumeric():
      bp = params[1]
      ret = cursor.execute( sql_blueprints_view,(pid,bp) )
      if ret!=0:
        bp = cursor.fetchall()
        print(bp)
      else:
        print("No blueprints found with this ID")

    if params[0] == "delete" and params[1].isnumeric():
      print("Delete stuff")
      bp = params [1]
      ret = cursor.execute( sql_blueprints_delete, (pid,bp) )
      if ret == 1:
        db.commit()
        print("Blueprint ("+bp+") deleted.")
      else:
        print("Blueprint not deleted.")

  def help_blueprints(this):
    print("The blueprints command allows the administration of blueprints from viewing, searching and deleting.")
    x = prettytable.PrettyTable(["Command","Description"])
    x.align["Command"] = "l"
    x.align["Description"] = "l"
    x.add_row(["blueprints","Returns a list of all blueprints owned by the player."])
    x.add_row(["blueprints class #","Searches for all instances of class of blueprints. These can be: buildings"])
    x.add_row(["blueprints type #","Searches for all instances of a class and type of blueprints."])
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
