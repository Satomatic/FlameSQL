from tkinter import *
import tkinter.ttk as tkinter2
from tkinter import messagebox
from tkinter import filedialog
from Lib.Saphire import *
import linecache
import MySQLdb
import time
import sys
import os

def Exit():
	if messagebox.askyesno("Exit", "Are you sure you would\nlike to exit?"):
		sys.exit(1)
	else:
		pass

def Logout(window):
	window.destroy()
	Login()

def MainProgram(hostname, username, password):
	window = Tk()
	
	window.title("FlameSQL :: " + hostname)
	window.geometry("1280x720")
	window.iconbitmap("Resources/icon.ico")
	window.protocol('WM_DELETE_WINDOW', Exit)

	def ServerInfo():
		serverinfo = Tk()

		serverinfo.title("FlameSQL Server Info")
		serverinfo.geometry("500x500")
		serverinfo.resizable(0,0)
		serverinfo.iconbitmap("Resources/icon.ico")
		centerwindow(serverinfo)

		def ServerInfoFuntion():
			for widget in serverinfo.winfo_children():
				widget.destroy()

			def ServerShutdown():
				if messagebox.askyesno("Shutdown", "Are you sure you would like\nto shut down the server?"):
					try:
						conn = MySQLdb.connect(hostname, username, password)
						conn.shutdown()
						conn.close()
					except (MySQLdb.Error, MySQLdb.Warning) as e:
						error = str(e).strip("(").strip(")")
						datasplit = error.split(", ")
						messagebox.showerror("Error", datasplit[0] + "\n" + datasplit[1])
					serverinfo.destroy()
					Logout(window)
				else:
					pass

			# Get server stats
			conn = MySQLdb.connect(hostname, username, password)
			statRaw = conn.stat()
			conn.close()

			statArray = statRaw.split("  ")
			print(statArray)

			headerPanel = PanedWindow(serverinfo, bd=2, relief=RIDGE)
			headerPanel.pack(fill=X)
			Label(headerPanel, text=" Server manager", font=("", 10), height=2).pack(side=LEFT)
			Button(headerPanel, text="refresh", font=("", 10), bd=0, command=ServerInfoFuntion).pack(side=RIGHT)
			Button(headerPanel, text="shutdown", font=("", 10), bd=0, command=ServerShutdown).pack(side=RIGHT)

			infoPanel = PanedWindow(serverinfo, bd=2, relief=RIDGE)
			infoPanel.pack(fill=BOTH, expand=1)

			Label(infoPanel, text="Hostname\n\nUptime\nThreads\nQuestions\nSlow queries\nOpens\nFlush tables\nOpen tables\nQueries per second avg",
				  font=("", 10), anchor=W, justify=LEFT).place(x=10, y=10)

			infoText = hostname + "\n\n"
			for item in statArray:
				itemsplit = item.split(": ")
				if itemsplit[0] == "Uptime":
					time_convert = time.strftime('%H:%M:%S', time.localtime(int(itemsplit[1])))
					infoText = infoText + itemsplit[1] + " (" + time_convert + ")" + "\n"
				else:
					infoText = infoText + itemsplit[1] + "\n"

			Label(infoPanel, text=infoText, font=("", 10), anchor=W, justify=LEFT).place(x=180, y=10)

			Label(infoPanel, )

			serverinfo.mainloop()

		ServerInfoFuntion()

	def ExportServerStats():
		exportlocation = filedialog.asksaveasfilename(title="Export stats", filetypes = (("all files", "*.*"), ("text file", "*.txt")))

		if exportlocation:
			conn = MySQLdb.connect(hostname, username, password)
			cursor = conn.cursor()
			rawStats = conn.stat()

			datasplit = rawStats.split("  ")

			exportFile = open(exportlocation, "w")
			for item in datasplit:
				exportFile.write(item + "\n")

			exportFile.close()

			messagebox.showinfo("Done", "Server stats have been exported to\n" + exportlocation)

		else:
			pass

	def GetDatabases():
		conn = MySQLdb.connect(hostname, username, password)
		cursor = conn.cursor()
		cursor.execute("show databases")
		server_return = cursor.fetchall()
		
		DatabaseListbox.delete(0, END)
		
		if server_return:
			for row in server_return:
				DatabaseListbox.insert(END, row)
		else:
			DatabaseListbox.insert(END, "No databases")
			
		cursor.close()
		conn.close()

	def DatabaseLoad(event):
		select = DatabaseListbox.get(DatabaseListbox.curselection())
		selected = str(select[0])
		
		DropDatabaseButton.config(state='normal')
		
		global database
		database = selected

		conn = MySQLdb.connect(hostname, username, password, selected)
		cursor = conn.cursor()
		cursor.execute("show tables")
		server_return = cursor.fetchall()
		
		TableListbox.delete(0, END)
		
		if server_return:
			for row in server_return:
				TableListbox.insert(END, str(''.join(row)))
		else:
			TableListbox.insert(END, "No tables found")
		
	def TableLoad(event):
		DropTableButton.config(state='normal')

		def InsertRow():
			insertwindow = Tk()

			insertwindow.title("Insert Row")
			insertwindow.geometry("400x430")
			insertwindow.resizable(0,0)
			insertwindow.iconbitmap("Resources/icon.ico")

			def RowSubmit():
				item_array = []
				count = 0
				for item in MainContainer.winfo_children():
					item_name = str(item)
					if "label" in item_name:
						pass
					else:
						column_data = row_array[count]
						print(column_data)

						dataSplit = column_data.split("::")
						data_type = dataSplit[1]

						print(data_type)

						item_data = item.get()
						if data_type == "text":
							item_array.insert(len(item_array), "'" + item_data + "'")
						else:
							item_array.insert(len(item_array), item_data)

						count = count + 1

				sql_command = "insert into " + tablename + " ("
				count = 0
				for item in row_array:
					itemSplit = item.split("::")
					itemSplitName = itemSplit[0]

					sql_command = sql_command + itemSplitName
					count = count + 1
					if count == len(row_array):
						sql_command = sql_command + ") values ("
					else:
						sql_command = sql_command + ", "

				print(sql_command)

				count = 0
				for item in item_array:
					sql_command = sql_command + item
					count = count + 1
					if count == len(item_array):
						sql_command = sql_command + ")"
					else:
						sql_command = sql_command + ","
				print(sql_command)

				try:
					conn = MySQLdb.connect(hostname, username, password, database)
					cursor = conn.cursor()
					cursor.execute(sql_command)
					conn.commit()
					conn.close()
				except (MySQLdb.Error,MySQLdb.Warning) as e:
					error = str(e).strip("(").strip(")")
					datasplit = error.split(", ")
					messagebox.showerror("Error", datasplit[0] + "\n" + datasplit[1])

				TableLoad("oof")
				insertwindow.destroy()

			Label(insertwindow, text="\nInsert row\n", font=("", 11)).pack(fill=X)
			MainContainer = Frame(insertwindow, bd=2, relief=RIDGE)
			MainContainer.pack(fill=BOTH, expand=1)

			# Get column information
			global database

			conn = MySQLdb.connect(hostname, username, password, database)
			cursor = conn.cursor()
			cursor.execute("show columns from " + tablename)
			server_return = cursor.fetchall()
			print(server_return)

			row_array = []

			for row in server_return:
				column_name = row[0]
				column_type = row[1]

				row_array.insert(len(row_array), column_name + "::" + column_type)

			cursor.close()
			conn.close()

			# Draw stuff
			init_pos_y = 10
			add_value = 30

			for item in row_array:
				init_pos_y = init_pos_y + add_value
				Label(MainContainer, text=item, font=("", 11)).place(x=10, y=init_pos_y)

				data_entry = Entry(MainContainer, font=("", 10), bd=2, relief=RIDGE, width=30)
				data_entry.place(x=90, y=init_pos_y)

			for widget in MainContainer.winfo_children():
				print(str(widget))

			FooterPanel = Frame(insertwindow, height=30)
			FooterPanel.pack(fill=X)

			Button(FooterPanel, text="Submit", bd=2, relief=RIDGE, width=10, command=RowSubmit).place(x=1, y=1)
			Button(FooterPanel, text="close", bd=2, relief=RIDGE, width=10, command=insertwindow.destroy).place(x=90, y=1)

			insertwindow.mainloop()

		def DrawTable(table):
			def DeleteRow(selection_array):
				if messagebox.askyesno("Sure", "Are you sure you would like to delete this data?"):
					# Get columns
					conn = MySQLdb.connect(hostname, username, password, database)
					cursor = conn.cursor()
					cursor.execute("show columns from " + table)
					server_return = cursor.fetchall()

					column_array = []
					for item in server_return:
						column_array.insert(len(column_array), item[0] + "::" + item[1])

					sql = "delete from " + table + " where "

					count = 0
					for item in selection_array:
						value = item
						column = column_array[count]

						print(value)
						print(column)

						datasplit = column.split("::")

						print(datasplit)

						if "text" in datasplit[1]:
							char = "'"
						else:
							char = ""

						sql = sql + datasplit[0] + "=" + char + value + char + ""

						if count == len(selection_array) - 1:
							sql = sql + " limit 1" # sets limit to 1 to stop from deleting duplicate rows
						else:
							sql = sql + " and "

						count = count + 1

					try:
						print(sql)
						cursor.execute(sql)
						conn.commit()
						TableLoad("oof")
					except (MySQLdb.Error,MySQLdb.Warning) as e:
						error = str(e).strip("(").strip(")")
						datasplit = error.split(", ")
						messagebox.showerror("Error",datasplit[0] + "\n" +datasplit[1])

					cursor.close()
					conn.close()
				else:
					pass

			def GetSelectedRow(event):
				try:
					selected = treeview.item(treeview.selection())
					print(type(selected))
					print(selected)
					item = treeview.selection()[0]
					values = treeview.item(item)['values']
					selection_array = []
					for item in values:
						item = str(item)
						selection_array.insert(len(selection_array), item)

					DeleteRowButton.config(state='normal', command=lambda: DeleteRow(selection_array))
				except:
					pass

			column_array = []
			
			conn = MySQLdb.connect(hostname, username, password, database)
			cursor = conn.cursor()

			# Get column names #
			cursor.execute("show columns from " + table)
			column_raw = cursor.fetchall()
			for item in column_raw:
				column_name = item[0]
				column_array.insert(len(column_array), column_name)
			
			# Get table data #
			cursor.execute("select * from " + table)
			table_raw = cursor.fetchall()
			
			# Draw table widget #
			tv = tkinter2.Treeview(MainWorkspace)
			tv['columns'] = column_array
			tv.heading("#0", text='', anchor="w")
			tv.column("#0", anchor="w", width=1)
			
			for item in column_array:
				tv.heading(item, text=item, anchor="w")
				tv.column(item, anchor="w", width=10)
	
			treeview = tv
			treeview.pack(fill=BOTH, expand=1)
			
			# Insert data to table #
			for row in table_raw:
				treeview.insert('', 'end', values=row)

			treeview.bind("<ButtonRelease-1>", GetSelectedRow)
	
		ClearPanel(MainWorkspace)
		if "load_table::" in str(event):
			tablename = event.strip("load_table::")
		else:
			tablename = TableListbox.get(TableListbox.curselection())

		
		# Top Panel #
		TopPanel = Frame(MainWorkspace, height=25, bd=2, relief=GROOVE)
		TopPanel.pack(fill=X)
		Label(TopPanel, text="Table name: " + tablename, font=("", 10)).pack(side=LEFT)
		
		# Control Panel #
		ControlPanel = PanedWindow(MainWorkspace, height=25, bd=2, relief=GROOVE)
		ControlPanel.pack(fill=X)
		
		Button(ControlPanel, text="Insert row", width=10, bd=0, command=InsertRow).pack(side=LEFT)
		DeleteRowButton = Button(ControlPanel, text="Delete row", width=10, bd=0, state='disabled')
		DeleteRowButton.pack(side=LEFT)

		Button(ControlPanel, text="Refresh", width=10, bd=0, command=lambda: TableLoad("oof")).pack(side=RIGHT)

		#Label(TopPanel, text="Order by", font=("", 10)).place(x=250, y=0)
		
		DrawTable(tablename)
		
	def NewDatabase():
		newwindow = Tk()
		
		newwindow.title("FlameSQL New Database")
		newwindow.geometry("300x100")
		newwindow.resizable(0,0)
		newwindow.iconbitmap("Resources/icon.ico")
		newwindow.attributes("-topmost", True)
		centerwindow(newwindow)
		
		def DatabaseCreate():
			databasename = DatabaseE.get()
		
			conn = MySQLdb.connect(hostname, username, password)
			cursor = conn.cursor()
			
			try:
				cursor.execute("create database " + databasename)
				conn.commit()
				newwindow.destroy()
				messagebox.showinfo("Done", "Created database '" + databasename + "'")
			except (MySQLdb.Error, MySQLdb.Warning) as e:
				error = str(e).strip("(").strip(")")
				datasplit = error.split(", ")
				newwindow.destroy()
				messagebox.showerror("Error", datasplit[0] + "\n" + datasplit[1])
				
			cursor.close()
			conn.close()
			
			GetDatabases()

		Label(newwindow, text="New database", font=("", 10)).place(x=10, y=10)
		DatabaseE = Entry(newwindow, width=30, bd=2, relief=RIDGE)
		DatabaseE.place(x=10, y=40)
		
		Button(newwindow, text="Create", bd=2, relief=RIDGE, width=10, command=DatabaseCreate).place(x=10, y=70)
		
		add_placeholder_to(DatabaseE, "Database name", "")
		
		newwindow.mainloop()
		
	def NewTable():
		try:
			database = DatabaseListbox.get(DatabaseListbox.curselection())
			database_select = True
		except:
			messagebox.showerror("Error", "Please select a database")
			database_select = False
		
		if database_select == True:
			newwindow = Tk()
			
			newwindow.title("FlameSQL New Table")
			newwindow.geometry("400x430")
			newwindow.resizable(0,0)
			newwindow.iconbitmap("Resources/icon.ico")
			#newwindow.attributes("-topmost", True)
			centerwindow(newwindow)
			
			def CreateTable():
				table_name = TableNameE.get()
				field_count = 0
				field_string = ""
				
				for item in field_array:
					field_count = field_count + 1
				
				if table_name == "Table name" or table_name == " ":
					messagebox.showerror("Error", "Please enter table name")
				elif field_count == 0:
					messagebox.showerror("Error", "Table must have at least 1 field")
				else:
					count = 0
					for item in field_array:
						count = count + 1
						if count == field_count:
							field_string = field_string + item
						else:
							field_string = field_string + item + ","
						
					sql_string = "create table " + table_name + " (" + field_string + ")"
					print(sql_string)
					try:
						conn = MySQLdb.connect(hostname, username, password, str(database[0]))
						cursor = conn.cursor()
						
						cursor.execute(sql_string)
						conn.commit()
						
						cursor.close()
						conn.close()
						
						newwindow.destroy()
						DatabaseLoad("New table took far too long - Satomatic")

						messagebox.showinfo("Done", "Table '" + table_name + "' has been created")
					except (MySQLdb.Error, MySQLdb.Warning) as e:
						error = str(e).strip("(").strip(")")
						datasplit = error.split(", ")
						messagebox.showerror("Error", datasplit[0] + "\n" + datasplit[1])
						newwindow.attributes("-topmost", 1) # Brings window back to front
						newwindow.attributes("-topmost", 0)
			
			def InsertField():
				fieldname = FieldNameE.get()
				fieldtype = FieldTypeE.get()
				
				if fieldname == "Field name" or fieldname == " ":
					messagebox.showerror("Error", "Please fill in field boxes")
				elif fieldtype == "Field type" or fieldtype == " ":
					messagebox.showerror("Error", "Please fill in field boxes")
				else:
					treeview.insert('', 'end', values=((fieldname, fieldtype)))
					
					field_array.insert(len(field_array), fieldname + " " + fieldtype)

				print(field_array)

			# Load data types #
			field_type_array = []
			data_type_raw = linecache.getline("Data/SQLData.dat", 2).strip("\n")
			datasplit = data_type_raw.split(", ")
			for item in datasplit:
				field_type_array.insert(0, item)
			
			field_array = []
			
			InfoPanel = Frame(newwindow, height=170, bd=2, relief=RIDGE)
			InfoPanel.pack(fill=X)
			
			Label(InfoPanel, text="Create table", font=("", 10)).place(x=10, y=10)
			
			TableNameE = Entry(InfoPanel, width=30, bd=2, relief=RIDGE)
			TableNameE.place(x=10, y=40)
			
			Label(InfoPanel, text="Field name", font=("", 10)).place(x=10, y=100)
			FieldNameE = Entry(InfoPanel, width=20, bd=2, relief=RIDGE)
			FieldNameE.place(x=10, y=120)
			Label(InfoPanel, text="Field type", font=("", 10)).place(x=160, y=100)
			
			FieldTypeE = tkinter2.Combobox(InfoPanel, values=field_type_array)
			FieldTypeE.current(0)
			FieldTypeE.place(x=160, y=120)
			
			Button(InfoPanel, text="Insert", bd=2, relief=RIDGE, width=10, command=InsertField).place(x=305, y=117)
			
			add_placeholder_to(TableNameE, "Table name", "")
			add_placeholder_to(FieldNameE, "Field name", "")
			
			tv = tkinter2.Treeview(newwindow)
			tv['columns'] = ('Field name', 'Field type')
			tv.heading("#0", text='', anchor='w')
			tv.column("#0", anchor="w", width=1)
			tv.heading('Field name', text='Field name', anchor='w')
			tv.column('Field name', anchor='w', width=10)
			tv.heading('Field type', text='Field type', anchor='w')
			tv.column('Field type', anchor='w', width=10)
			treeview = tv
			treeview.pack(fill=BOTH, expand=1)
			
			BottomPanel = Frame(newwindow, height=30)
			BottomPanel.pack(fill=X, expand=1)
			
			Button(BottomPanel, text="ok", bd=2, relief=RIDGE, width=10, command=CreateTable).place(x=1, y=1)
			Button(BottomPanel, text="close", bd=2, relief=RIDGE, width=10, command=newwindow.destroy).place(x=90, y=1)
			
			newwindow.mainloop()
	
	def DropDatabase():
		selected = DatabaseListbox.get(DatabaseListbox.curselection())
		databasename = str(selected[0])
		
		if messagebox.askyesno("Sure", "Are you sure you would like to\ndrop database '" + databasename + "'"):
			try:
				conn = MySQLdb.connect(hostname, username, password)
				cursor = conn.cursor()
				cursor.execute("drop database " + databasename)
				conn.commit()
				cursor.close()
				conn.close()
				
				GetDatabases()
				messagebox.showinfo("Done", "Database '" + databasename + "' has been dropped")
			except (MySQLdb.Error, MySQLdb.Warning) as e:
				error = str(e).strip("(").strip(")")
				datasplit = error.split(", ")
				messagebox.showerror("Error", datasplit[0] + "\n" + datasplit[1])
		else:
			pass
			
		DropDatabaseButton.config(state='disabled')
	
	def DropTable():
		tablename = TableListbox.get(TableListbox.curselection())
	
		if messagebox.askyesno("Sure", "Are you sure you would like to\ndrop database '" + tablename + "'"):
			try:
				conn = MySQLdb.connect(hostname, username, password, database)
				cursor = conn.cursor()
				cursor.execute("drop table " + tablename)
				conn.commit()
				cursor.close()
				conn.close()
				
				DatabaseLoad("At this point its just not except because except has a c")
				messagebox.showinfo("Done", "Table '" + tablename + "' has been dropped")
			except (MySQLdb.Error, MySQLdb.Warning) as e:
				error = str(e).strip("(").strip(")")
				datasplit = error.split(", ")
				messagebox.showerror("Error", datasplit[0] + "\n" + datasplit[1])
		else:
			pass
			
		DropTableButton.config(state='disabled')

	def UserPanel():
		userwin = Tk()

		userwin.title("FlameSQL User panel")
		userwin.geometry("700x500")
		userwin.resizable(0,0)
		userwin.iconbitmap("Resources/icon.ico")
		#userwin.attributes("-topmost", True)
		centerwindow(userwin)

		def MainPanel():
			ClearPanel(userwin)
			def LoadUser(event):
				def DeleteUser(user):
					if messagebox.askyesno("Sure", "Are you sure you would like to\ndelete the user " + user):
						pushWindow(userwin)
						try:
							userSplit = user.split("@")
							userName = userSplit[0]
							userHost = userSplit[1]
							conn = MySQLdb.connect(hostname, username, password)
							cursor = conn.cursor()
							cursor.execute("DROP USER '" + userName + "'@'" + userHost + "'")
							conn.commit()
							cursor.close()
							conn.close()

							MainPanel()
						except (MySQLdb.Error, MySQLdb.Warning) as e:
							error = str(e).strip("(").strip(")")
							datasplit = error.split(", ")
							messagebox.showerror("Error", datasplit[0] + "\n" + datasplit[1])
					else:
						pass

				selected = UserList.get(UserList.curselection())

				DeleteUserButton.config(state='normal', command=lambda: DeleteUser(selected))

			def NewUser():
				ClearPanel(ContentFrame)

				def KeyPress(event):
					color = "#ffffff"
					password = PasswordE.get()
					password_strength = CheckPasswordStrength(password)

					if password_strength == "weak":
						color = "#d00000"
					elif password_strength == "good":
						color = "#ff7e00"
					elif password_strength == "strong":
						color = "#00b32e"

					StrengthLabel.config(text=password_strength,fg=color)

				def CreateUser():
					newHostname = HostnameE.get()
					newUsername = UsernameE.get()
					newPassword = PasswordE.get()
					newRetype = RetypeE.get()

					if (newHostname == "" or newHostname == "Hostname"):
						messagebox.showerror("Error", "You must include a\nHostname\nUsername\nand Password")
						pushWindow(userwin)
					elif (newUsername == "" or newUsername == "Username"):
						messagebox.showerror("Error", "You must include a\nHostname\nUsername\nand Password")
						pushWindow(userwin)
					elif (newPassword == "" or newPassword == "Password"):
						messagebox.showerror("Error", "You must include a\nHostname\nUsername\nand Password")
						pushWindow(userwin)
					elif (newRetype == "" or newRetype == "Confirm password"):
						messagebox.showerror("Error", "Please confirm the password before\ncontinuing")
						pushWindow(userwin)
					else:
						if(newPassword == newRetype):
							try:
								count = 0

								conn = MySQLdb.connect(hostname, username, password)
								cursor = conn.cursor()
								sql = "create user '" + newUsername + "'@'" + newHostname + "' identified by '" + newPassword + "'"

								cursor.execute(sql)
								conn.commit()

								if len(checkArray) == 0:
									pass
								else:
									sql = "grant"
									for item in checkArray:
										if count == 0:
											sql = sql + " " + item
											count = count + 1
										else:
											sql = sql + "," + item
											count = count + 1

									sql = sql + " on *.* to '" + newUsername + "'@'" + newHostname + "'"
									cursor.execute(sql)

								QueryLimit = mxQueryLimitE.get()
								UpdateLimit = mxUpdateLimitE.get()
								ConnectionLimit = mxConnectionLimitE.get()

								if(QueryLimit == "" or "Max query limit"):
									pass
								else:
									try:
										intv = int(QueryLimit)
										sql = "ALTER USER '" + newUsername + "'@'" + newHostname + "' WITH MAX_QUERIES_PER_HOUR " + str(QueryLimit)
										print(sql)
									except:
										messagebox.showerror("Error", "Max query limit was ignored\nbecause it is not an integer")
										pushWindow(userwin)

								if (UpdateLimit == "" or "Max update limit"):
									pass
								else:
									try:
										inv = int(UpdateLimit)
										sql = "ALTER USER '" + newUsername + "'@'" + newHostname + "' WITH MAX_UPDATES_PER_HOUR " + str(UpdateLimit)
										print(sql)
									except:
										messagebox.showerror("Error", "Max update limit was ignored\nbecause it is not an integer")
										pushWindow(userwin)

								if (ConnectionLimit == "" or "Max connection limit"):
									pass
								else:
									try:
										intv = int(ConnectionLimit)
										sql = "ALTER USER '" + newUsername + "'@'" + newHostname + "' WITH MAX_CONNECTIONS_PER_HOUR " + str(ConnectionLimit)
										print(sql)
									except:
										messagebox.showerror("Error", "Max connection limit was ignored\nbecause it is not an integer")
										pushWindow(userwin)

								messagebox.showinfo("Done", "User created '" + newUsername + "'@'" + newHostname + "'")

								conn.commit()
							except:
								messagebox.showerror("Error", "There was an error creating the user\n'" + newUsername + "'@'" + newPassword + "'")

							userwin.destroy()
						else:
							messagebox.showerror("Error", "Passwords do not match")
							pushWindow(userwin)

				# Login settings #
				Label(ContentFrame, text="Create new user", font=("", 10)).place(x=10, y=10)

				HostnameE = Entry(ContentFrame, width=40, bd=2, relief=RIDGE, font=("", 10))
				HostnameE.place(x=10, y=50)

				UsernameE = Entry(ContentFrame, width=40, bd=2, relief=RIDGE, font=("", 10))
				UsernameE.place(x=10, y=80)

				PasswordE = Entry(ContentFrame, width=40, bd=2, relief=RIDGE, font=("", 10))
				PasswordE.place(x=10, y=110)
				PasswordE.bind("<Key>", KeyPress)

				StrengthLabel = Label(ContentFrame, font=( "", 10))
				StrengthLabel.place(x=300, y=140)

				RetypeE = Entry(ContentFrame, width=40, bd=2, relief=RIDGE, font=("", 10))
				RetypeE.place(x=10, y=140)

				# Limit settings #
				Label(ContentFrame, text="Set account limits *optional", font=("", 10)).place(x=10, y=180)
				mxQueryLimitE = Entry(ContentFrame, width=30, bd=2, relief=RIDGE, font=("", 10))
				mxQueryLimitE.place(x=10, y=210)

				mxUpdateLimitE = Entry(ContentFrame, width=30, bd=2, relief=RIDGE, font=("", 10))
				mxUpdateLimitE.place(x=10, y=240)

				mxConnectionLimitE = Entry(ContentFrame, width=30, bd=2, relief=RIDGE, font=("", 10))
				mxConnectionLimitE.place(x=10, y=270)

				# Create account buttons #
				tkinter2.Button(ContentFrame, text="Create account", width=14, command=CreateUser).place(x=10, y=300)

				add_placeholder_to(HostnameE, "Hostname", "")
				add_placeholder_to(UsernameE, "Username", "")
				add_placeholder_to(PasswordE, "Password", "*")
				add_placeholder_to(RetypeE, "Confirm password", "*")

				add_placeholder_to(mxQueryLimitE, "Max query limit", "")
				add_placeholder_to(mxUpdateLimitE, "Max update limit", "")
				add_placeholder_to(mxConnectionLimitE, "Max connection limit", "")

				# Draw permissions #
				permsFrame = LabelFrame(ContentFrame, text="User permissions", width=150, height=430, font=("", 10), labelanchor=N)
				permsFrame.place(x=350, y=45)

				# Draw check boxes #
				permsCheckLine = linecache.getline("Data/SQLData.dat", 3).strip("\n")

				checkArray = []
				def CheckValue(value):
					if value in checkArray:
						checkArray.remove(value)
					else:
						checkArray.insert(0, value)

				dataSplit = permsCheckLine.split(", ")
				position = 0
				for item in dataSplit:
					print("Drawing " + item)
					cb = Checkbutton(permsFrame, text=item, command=lambda x=item: CheckValue(x))
					cb.place(x=10, y=position)
					position = position + 20

			# Side controls #
			SideContainer = Frame(userwin, bd=0, relief=RIDGE)
			SideContainer.pack(side=LEFT, fill=Y)
			UserList = Listbox(SideContainer, width=29, bd=2, relief=RIDGE)
			UserList.pack(fill=Y, expand=1)
			UserList.bind("<<ListboxSelect>>", LoadUser)

			# Main content frame #
			ContentFrame = Frame(userwin, bd=2, relief=RIDGE)
			ContentFrame.pack(fill=BOTH, expand=1)

			# Load users #
			conn = MySQLdb.connect(hostname, username, password)
			cursor = conn.cursor()
			cursor.execute("select * from mysql.user")
			server_return = cursor.fetchall()

			if server_return:
				for row in server_return:
					host = row[0]
					user = row[1]
					UserList.insert(END, user + "@" + host)

			cursor.close()
			conn.close()

			Footer = Frame(SideContainer, bd=2, relief=RIDGE, height=25)
			Footer.pack(fill=X)

			# Footer controls #
			tkinter2.Button(Footer, text="New user", width=13, command=NewUser).pack(side=LEFT)
			DeleteUserButton = tkinter2.Button(Footer, text="Delete", width=13, state='disabled')
			DeleteUserButton.pack(side=LEFT)

		MainPanel()

		userwin.mainloop()

	# Menu bar #
	menubar = Menu(window)
	menubar.add_command(label="Users", command=UserPanel)

	servermenu = Menu(menubar, tearoff=0)
	servermenu.add_command(label="Server manager", command=ServerInfo)
	servermenu.add_command(label="Export stats", command=ExportServerStats)
	menubar.add_cascade(label="Server", menu=servermenu)

	optionmenu = Menu(menubar, tearoff=0)
	menubar.add_cascade(label="Options", menu=optionmenu)

	menubar.add_command(label="Logout", command=lambda: Logout(window))
	menubar.add_command(label="Exit", command=Exit)
	window.configure(menu=menubar)
	
	SidePanel = Frame(window, width=150, bd=2, relief=RIDGE)
	SidePanel.pack(side=LEFT, fill=Y)
	
	TitlePanel = Frame(SidePanel, height=25, width=150)
	TitlePanel.pack(fill=X)
	DBContainer = Frame(SidePanel, height=25, width=150)
	DBContainer.pack(fill=BOTH, expand=1)
	TitlePanel2 = Frame(SidePanel, height=25, width=150)
	TitlePanel2.pack(fill=X)
	TBContainer = Frame(SidePanel, height=25, width=150)
	TBContainer.pack(fill=BOTH, expand=1)
	
	# Database list #
	DropDatabaseButton = Button(TitlePanel, text="-", font=("", 11), width=5, height=1, bd=0, state='disabled', command=DropDatabase)
	DropDatabaseButton.pack(side=LEFT, fill=X)
	Label(TitlePanel, text="Databases", font=("", 10), width=25).pack(side=LEFT, fill=X)
	Button(TitlePanel, text="+", font=("", 11), width=5, height=1, bd=0, command=NewDatabase).pack(side=LEFT, fill=X)
	DatabaseListbox = Listbox(DBContainer, exportselection=False)
	DatabaseListbox.pack(fill=BOTH, expand=1, side=LEFT)
	DatabaseListbox.bind('<<ListboxSelect>>', DatabaseLoad)
	
	DVScrollbar = Scrollbar(DatabaseListbox)
	DVScrollbar.pack(side=RIGHT, fill=Y)
	DVScrollbar.config(command=DatabaseListbox.yview)
	DatabaseListbox.config(yscrollcommand=DVScrollbar.set)
	
	# Table list #
	DropTableButton = Button(TitlePanel2, text="-", font=("", 11), width=5, height=1, bd=0, state='disabled', command=DropTable)
	DropTableButton.pack(side=LEFT, fill=X)
	Label(TitlePanel2, text="Tables", font=("", 10), width=25).pack(side=LEFT, fill=X)
	Button(TitlePanel2, text="+", font=("", 11), width=5, height=1, bd=0, command=NewTable).pack(side=LEFT, fill=X)
	TableListbox = Listbox(TBContainer, exportselection=False)
	TableListbox.pack(fill=BOTH, expand=1, side=LEFT)
	TableListbox.bind('<<ListboxSelect>>', TableLoad)
	
	TVScrollbar = Scrollbar(TableListbox)
	TVScrollbar.pack(side=RIGHT, fill=Y)
	TVScrollbar.config(command=TableListbox.yview)
	TableListbox.config(yscrollcommand=TVScrollbar.set)
	
	# Main workspace #
	MainWorkspace = Frame(window, bd=2, relief=RIDGE)
	MainWorkspace.pack(fill=BOTH, expand=1)

	# Bottom panel
	BottomPanel = Frame(window, height=40, bd=2, relief=RIDGE)
	BottomPanel.pack(fill=X)
	
	# Run on GUI load #
	GetDatabases()
	
	window.mainloop()
		
def Login():
	window = Tk()
	
	window.title("FlameSQL Login")
	window.geometry("600x500")
	window.iconbitmap("Resources/icon.ico")
	window.resizable(0,0)
	window.protocol('WM_DELETE_WINDOW', Exit)
	centerwindow(window)

	def LoadSaved():
		SavedListbox.delete(0, END)
	
		if os.path.isfile("Data/Saved.dat"):
			SaveFile = open("Data/Saved.dat")
			
			for line in SaveFile:
				DataSplit = line.split("::")
				Hostname = DataSplit[0]
				Username = DataSplit[1]
				Password = DataSplit[2]
				
				SavedListbox.insert(END, Username + "@" + Hostname)

			SaveFile.close()
		else:
			SaveFile = open("Data/Saved.dat", "w")
			SaveFile.close()
	
	def LoadNewGui():
		def CheckInfo():
			hostname = HostnameE.get()
			username = UsernameE.get()
			password = PasswordE.get()
			
			if hostname == "Hostname" or hostname == " ":
				info = False
			elif username == "Username" or username == " ":
				info = False
			elif password == "Password" or password == " ":
				info = False
				
			if info == False:
				returnstring = "no"
			else:
				returnstring = "yes"
				
			return returnstring
	
		def Connect(event):
			hostname = HostnameE.get()
			username = UsernameE.get()
			password = PasswordE.get()
			
			try:
				connection = MySQLdb.connect(hostname, username, password)
				cursor = connection.cursor()
				cursor.close()
				connection.close()
				
				window.destroy()
				
				MainProgram(hostname, username, password)
			except (MySQLdb.Error, MySQLdb.Warning) as e:
				error = str(e).strip("(").strip(")")
				datasplit = error.split(", ")
				messagebox.showerror("Error", datasplit[0] + "\n" + datasplit[1])
		
		def TestConnection():
			hostname = HostnameE.get()
			username = UsernameE.get()
			password = PasswordE.get()
			
			try:
				connection = MySQLdb.connect(hostname, username, password)
				cursor = connection.cursor()
				cursor.close()
				connection.close()
				messagebox.showinfo("Done", "Succesfully connected to '" + hostname + "'")
			except (MySQLdb.Error, MySQLdb.Warning) as e:
				error = str(e).strip("(").strip(")")
				datasplit = error.split(", ")
				messagebox.showerror("Error", datasplit[0] + "\n" + datasplit[1])
				
		def Save():
			infocheck = CheckInfo
			
			if infocheck == "no":
				pass
			else:
				hostname = HostnameE.get()
				username = UsernameE.get()
				password = PasswordE.get()
				
				SaveFile = open("Data/Saved.dat", "a")
				SaveFile.write(hostname + "::" + username + "::" + password + "\n")
				SaveFile.close()
				
				LoadSaved()
	
		def OpenSave(event):
			selected = SavedListbox.get(SavedListbox.curselection())
			
			datasplit = selected.split("@")
			hostname = datasplit[1]
			username = datasplit[0]
			
			SaveFile = open("Data/Saved.dat")
			for line in SaveFile:
				if hostname + "::" + username + "::" in line:
					datasplit = line.split("::")
					hostname = datasplit[0].strip("\n")
					username = datasplit[1].strip("\n")
					password = datasplit[2].strip("\n")
					
					try:
						connection = MySQLdb.connect(hostname, username, password)
						cursor = connection.cursor()
						cursor.close()
						connection.close()
						
						window.destroy()
						
						MainProgram(hostname, username, password)
					except (MySQLdb.Error, MySQLdb.Warning) as e:
						error = str(e).strip("(").strip(")")
						datasplit = error.split(", ")
						messagebox.showerror("Error", datasplit[0] + "\n" + datasplit[1])
			SaveFile.close()
	
		Label(ConnInfoFrame, text="Hostname", font=("", 11)).place(x=10, y=10)
		HostnameE = Entry(ConnInfoFrame, width=40, bd=2, relief=RIDGE, font=("", 10))
		HostnameE.place(x=100, y=10)
		
		Label(ConnInfoFrame, text="Username", font=("", 11)).place(x=10, y=60)
		UsernameE = Entry(ConnInfoFrame, width=40, bd=2, relief=RIDGE, font=("", 10))
		UsernameE.place(x=100, y=60)
		
		Label(ConnInfoFrame, text="Password", font=("", 11)).place(x=10, y=110)
		PasswordE = Entry(ConnInfoFrame, width=40, bd=2, relief=RIDGE, font=("", 10))
		PasswordE.place(x=100, y=110)
	
		add_placeholder_to(HostnameE, "Hostname", "")
		add_placeholder_to(UsernameE, "Username", "")
		add_placeholder_to(PasswordE, "Password", "*")

		HostnameE.bind("<Return>", Connect)
		UsernameE.bind("<Return>", Connect)
		PasswordE.bind("<Return>", Connect)
		SavedListbox.bind('<<ListboxSelect>>', OpenSave)
		
		tkinter2.Button(ConnInfoFrame, text="Connect", width=12, command=lambda: Connect("Reeeeee XD")).place(x=10, y=200)
		tkinter2.Button(ConnInfoFrame, text="Test", width=12, command=TestConnection).place(x=100, y=200)
		tkinter2.Button(ConnInfoFrame, text="Save", width=12, command=Save).place(x=190, y=200)
	
	TopPanel = PanedWindow(window, height=30, bd=2, relief=RIDGE)
	TopPanel.pack(fill=X)
	
	Label(TopPanel, text="Saved", font=("", 11)).place(x=10, y=2)
	Label(TopPanel, text="Connection info", font=("", 11)).place(x=195, y=2)
	
	SavedListbox = Listbox(window, width=25, bd=2, relief=RIDGE, font=("", 10))
	SavedListbox.pack(side=LEFT, fill=Y)
	
	ConnInfoFrame = Frame(window, bd=2, relief=RIDGE)
	ConnInfoFrame.pack(fill=BOTH, expand=1)
	
	LoadSaved()
	LoadNewGui()
	
	window.mainloop()

Login()
