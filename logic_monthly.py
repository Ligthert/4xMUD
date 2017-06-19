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
