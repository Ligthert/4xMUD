#!/usr/bin/python
# -*- coding: utf-8 -*-

import MySQLdb as mdb

con = mdb.connect('localhost', 'ts', 'ts', 'ts');

cur = con.cursor()
cur.execute("SELECT VERSION()")
print cur.fetchone()
