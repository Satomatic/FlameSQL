from tkinter import messagebox
from tkinter import filedialog
import tkinter.ttk as ttk
from tkinter import *
import MySQLdb
import sqlite3
import os

def ExportDatabase(hostname, username, password, databasename, location):
	try:
		connection = MySQLdb.connect(host=hostname, user=username, passwd=password, port=int(port), db=databasename)
		cursor = connection.cursor()

		# create database file #
		database = sqlite3.connect(location)
		dbcursor = database.cursor()

		# get tables from database #
		cursor.execute("show tables;")
		tablelist = cursor.fetchall()

		# create tables #
		for item in tablelist:
			fields = []
			types = []
			tablename = item[0]

			# get columns #
			cursor.execute("DESCRIBE " + tablename)
			tablefields = cursor.fetchall()

			for item in tablefields:
				fields.insert(len(fields), item[0])
				types.insert(len(types), item[1])

			# create table #
			sql = "create table " + tablename + "("
			count = 0
			for item in fields:
				sql += fields[count] + " " + types[count] + ","

				count += 1

			sql = sql[:-1]
			sql += ");"

			dbcursor.execute(sql)

			# insert table data #
			cursor.execute("select * from " + tablename)
			tabledata = cursor.fetchall()

			for row in tabledata:
				sql2 = "insert into " + tablename + " values ("

				for col in row:
					if isinstance(col, int):
						sql2 += str(col)
					else:
						sql2 += "'" + str(col) + "'"

					sql2 += ", "

				sql2 = sql2[:-2]
				sql2 += ");"

				dbcursor.execute(sql2)

		connection.close()
		database.commit()
		database.close()

		messagebox.showinfo("Done", "Database has been exported\n" + location)
	except Exception as e:
		messagebox.showerror("Error", "There was an error exporting database\n" + str(e))
