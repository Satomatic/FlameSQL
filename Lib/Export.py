from tkinter import messagebox
from tkinter import filedialog
import tkinter.ttk as ttk
from tkinter import *
import MySQLdb
import sqlite3
import os

def ExportDatabase(hostname, username, password, databasename, location, window):
	try:
		# create database file #
		database = sqlite3.connect(location)
		dbcursor = database.cursor()

		conn = MySQLdb.connect(hostname, username, password, databasename)
		cursor = conn.cursor()
		cursor.execute("show tables")
		serverTables = cursor.fetchall()

		for item in serverTables:
			item = item[0]

			# create table #
			sql = "create table " + item + "("
			sql2 = "insert into " + item + "("

			cursor.execute("DESCRIBE " + item)
			tableColumns = cursor.fetchall()

			objectArray = []

			count = 0
			for column in tableColumns:
				count = count + 1

				objectArray.insert(len(objectArray), column[1])

				if count == len(tableColumns):
					sql = sql + column[0] + " " + column[1]
					sql2 = sql2 + column[0]
				else:
					sql = sql + column[0] + " " + column[1] + ", "
					sql2 = sql2 + column[0] + ", "

			sql += ")"
			sql2 += ") values ("

			dbcursor.execute(sql)

			# transfer data #
			cursor.execute("select * from " + item)
			datareturn = cursor.fetchall()

			print(datareturn)

			for row in datareturn:
				count = 0
				for data in row:
					print(data)
					print(objectArray[count])

					if "text" in objectArray[count]:
						sql2 = sql2 + "'" + data + "', "
					else:
						sql2 = sql2 + str(data) + ", "

					count = count + 1

				sql2 = sql2[:-2] + ")"
				print(sql2)

				dbcursor.execute(sql2)

		cursor.close()
		conn.close()

		dbcursor.close()
		database.commit()
		database.close()

		messagebox.showinfo("Done", "Database has been exported\n" + location)
	except Exception as e:
		messagebox.showerror("Error", "There was an error exporting database\n" + str(e))

	window.destroy()
