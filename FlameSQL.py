import tkinter.ttk as tkinter2
from tkinter import messagebox
from tkinter import filedialog
from Lib.Sapphire import *
from tkinter import *
import linecache
import sqlite3
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
				for item in itemFrame.winfo_children():
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

			row_array = []

			for row in server_return:
				column_name = row[0]
				column_type = row[1]

				row_array.insert(len(row_array), column_name + "::" + column_type)

			cursor.close()
			conn.close()

			# I hate scrolling frames in tkinter :/ #
			scrollArea = Canvas(MainContainer, highlightthickness=0)
			scrollArea.grid(column=0, row=0, sticky=N+S+E+W)

			scrollBar = Scrollbar(MainContainer)
			scrollBar.grid(column=1, row=0, sticky=N+S)

			scrollArea.config(yscrollcommand=scrollBar.set)
			scrollBar.config(command=scrollArea.yview)

			itemFrame = Frame(scrollArea, bd=0)

			# Draw stuff
			init_pos_y = 0
			add_value = 1

			for item in row_array:
				init_pos_y = init_pos_y + add_value
				Label(itemFrame, text=item, font=("", 11), justify=LEFT).grid(row=init_pos_y, column=0, sticky=W)

				data_entry = Entry(itemFrame, font=("", 10), bd=2, relief=RIDGE, width=30)
				data_entry.grid(row=init_pos_y, column=1)

			scrollArea.create_window((0,0), anchor=NW, window=itemFrame)
			itemFrame.update_idletasks()
			scrollArea.config(scrollregion= itemFrame.bbox("all"))

			FooterPanel = Frame(insertwindow, height=30)
			FooterPanel.pack(fill=X)

			tkinter2.Button(FooterPanel, text="Submit", width=10, command=RowSubmit).place(x=2, y=2)
			tkinter2.Button(FooterPanel, text="Close", width=10, command=insertwindow.destroy).place(x=80, y=2)

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

			def EditRow(selection_array):
				editwin = Tk()

				editwin.title("FlameSQL Edit row")
				editwin.geometry("400x430")
				editwin.resizable(0,0)
				editwin.iconbitmap("Resources/icon.ico")

				def editCommand():
					sql = "UPDATE " + tablename + " SET "

					item_data_array = []
					for item in objectArea.winfo_children():
						item_name = str(item)

						if "label" in item_name:
							pass
						else:
							item_input = item.get()
							
							item_data_array.insert(len(item_data_array), item_input)

					count = 0
					for item in selection_array:
						if "text" in col_type_array[count]:
							syn = "'"
						else:
							syn = ""

						sql = sql + col_name_array[count] + "=" + syn + item_data_array[count] + syn + ","

						count = count + 1

					sql = sql[:-1] + " WHERE "

					count = 0
					for item in selection_array:
						col = col_name_array[count]
						val = col_data_array[count]
						fom = col_type_array[count]

						if "text" in fom:
							syn = "'"
						else:
							syn = ""

						sql = sql + col + "=" + syn + val + syn + " AND "

						count = count + 1

					sql = sql[:-5]

					print(sql)

					try:
						conn = MySQLdb.connect(hostname, username, password, database)
						cursor = conn.cursor()
						cursor.execute(sql)
						cursor.close()
						conn.commit()
						conn.close()

						messagebox.showinfo("Done", "Data has been updated")

						TableLoad("Oof")

						editwin.destroy()

					except Exception as e:
						messagebox.showerror("Error", str(e))
						
						raiseFrame(editwin)

				def cancel():
					editwin.destroy()

				headerPanel = Frame(editwin, height=50, bd=2, relief=RIDGE)
				headerPanel.pack(fill=X)
				Label(headerPanel, text="\nEdit data\n", font=("", 11)).pack(fill=X)

				mainContainer = Frame(editwin, bd=2, relief=RIDGE)
				mainContainer.pack(fill=BOTH, expand=1)

				scrollArea = Canvas(mainContainer, highlightthickness=0)
				scrollArea.grid(column=0, row=0, sticky=N+S+E+W)

				scrollBar = Scrollbar(mainContainer)
				scrollBar.grid(column=1, row=0, sticky=N+S)
				scrollArea.config(yscrollcommand=scrollBar.set)
				scrollBar.config(command=scrollArea.yview)

				objectArea = Frame(scrollArea)
				
				# I still hate scrolling frames in tkinter :/ #
				conn = MySQLdb.connect(hostname, username, password, database)
				cursor = conn.cursor()
				cursor.execute("show columns from " + tablename)
				serverreturn = cursor.fetchall()
				cursor.close()
				conn.close()

				print(serverreturn)

				count = 0
				pos_y = 0
				col_type_array = []
				col_name_array = []
				col_data_array = []
				for item in serverreturn:
					col_name = item[0]
					col_type = item[1]
					col_data = selection_array[count]


					col_type_array.insert(len(col_type_array), col_type)
					col_name_array.insert(len(col_name_array), col_name)
					col_data_array.insert(len(col_data_array), col_data)

					pos_y = pos_y + 1

					if len(col_name) > 10:
						labelText = limitText(10, col_name)
					else:
						labelText = extendText(20, col_name)

					Label(objectArea, text=labelText, font=("", 11), justify=LEFT).grid(row=pos_y, column=0, sticky=W)

					data_entry = Entry(objectArea, font=("", 10), bd=2, relief=RIDGE, width=30)
					data_entry.grid(row=pos_y, column=1)

					add_placeholder_to(data_entry, col_data, "")

					count = count + 1

				scrollArea.create_window((0,0), anchor=NW, window=objectArea)
				objectArea.update_idletasks()
				scrollArea.config(scrollregion=objectArea.bbox("all"))

				FooterPanel = Frame(editwin, height=40, bd=2, relief=RIDGE)
				FooterPanel.pack(fill=X)

				tkinter2.Button(FooterPanel, text="Save", width=14, command=editCommand).pack(side=LEFT)
				tkinter2.Button(FooterPanel, text="Cancel", width=14, command=cancel).pack(side=LEFT)

				editwin.mainloop()


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
					EditRowButton.config(state='normal', command=lambda: EditRow(selection_array))
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

		EditRowButton = Button(ControlPanel, text="Edit row", width=10, bd=0, state='disabled')
		EditRowButton.pack(side=LEFT)

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
		
		tkinter2.Button(newwindow, text="Create", width=10, command=DatabaseCreate).place(x=10, y=70)
		
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
					raiseFrame(newwindow)
				elif field_count == 0:
					messagebox.showerror("Error", "Table must have at least 1 field")
					raiseFrame(newwindow)
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
						
						raiseFrame(newwindow)
			
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
			
			TableNameE = Entry(InfoPanel, width=30, bd=2, relief=GROOVE)
			TableNameE.place(x=10, y=40)
			
			Label(InfoPanel, text="Field name", font=("", 10)).place(x=10, y=100)
			FieldNameE = Entry(InfoPanel, width=20, bd=2, relief=GROOVE)
			FieldNameE.place(x=10, y=120)
			Label(InfoPanel, text="Field type", font=("", 10)).place(x=160, y=100)
			
			FieldTypeE = tkinter2.Combobox(InfoPanel, values=field_type_array)
			FieldTypeE.current(0)
			FieldTypeE.place(x=160, y=120)
			
			Button(InfoPanel, text="Insert", width=10, height=1, bd=2, relief=GROOVE, font=("", 8), command=InsertField).place(x=308, y=118)
			
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
			
			Button(BottomPanel, text="ok", bd=2, relief=GROOVE, width=10, command=CreateTable).place(x=5, y=3)
			Button(BottomPanel, text="close", bd=2, relief=GROOVE, width=10, command=newwindow.destroy).place(x=94, y=3)
			
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
		centerwindow(userwin)

		def MainPanel():
			ClearPanel(userwin)
			def LoadUser(event):
				def DeleteUser(user):
					if messagebox.askyesno("Sure", "Are you sure you would like to\ndelete the user " + user):
						raiseFrame(userwin)
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
						raiseFrame(userwin)
					elif (newUsername == "" or newUsername == "Username"):
						messagebox.showerror("Error", "You must include a\nHostname\nUsername\nand Password")
						raiseFrame(userwin)
					elif (newPassword == "" or newPassword == "Password"):
						messagebox.showerror("Error", "You must include a\nHostname\nUsername\nand Password")
						raiseFrame(userwin)
					elif (newRetype == "" or newRetype == "Confirm password"):
						messagebox.showerror("Error", "Please confirm the password before\ncontinuing")
						raiseFrame(userwin)
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
										raiseFrame(userwin)

								if (UpdateLimit == "" or "Max update limit"):
									pass
								else:
									try:
										inv = int(UpdateLimit)
										sql = "ALTER USER '" + newUsername + "'@'" + newHostname + "' WITH MAX_UPDATES_PER_HOUR " + str(UpdateLimit)
										print(sql)
									except:
										messagebox.showerror("Error", "Max update limit was ignored\nbecause it is not an integer")
										raiseFrame(userwin)

								if (ConnectionLimit == "" or "Max connection limit"):
									pass
								else:
									try:
										intv = int(ConnectionLimit)
										sql = "ALTER USER '" + newUsername + "'@'" + newHostname + "' WITH MAX_CONNECTIONS_PER_HOUR " + str(ConnectionLimit)
										print(sql)
									except:
										messagebox.showerror("Error", "Max connection limit was ignored\nbecause it is not an integer")
										raiseFrame(userwin)

								messagebox.showinfo("Done", "User created '" + newUsername + "'@'" + newHostname + "'")

								conn.commit()
							except:
								messagebox.showerror("Error", "There was an error creating the user\n'" + newUsername + "'@'" + newPassword + "'")

							userwin.destroy()
						else:
							messagebox.showerror("Error", "Passwords do not match")
							raiseFrame(userwin)

				# Login settings #
				Label(ContentFrame, text="Create new user", font=("", 10)).place(x=10, y=10)

				HostnameE = Entry(ContentFrame, width=40, bd=2, relief=GROOVE, font=("", 10))
				HostnameE.place(x=10, y=50)

				UsernameE = Entry(ContentFrame, width=40, bd=2, relief=GROOVE, font=("", 10))
				UsernameE.place(x=10, y=80)

				PasswordE = Entry(ContentFrame, width=40, bd=2, relief=GROOVE, font=("", 10))
				PasswordE.place(x=10, y=110)
				PasswordE.bind("<Key>", KeyPress)

				StrengthLabel = Label(ContentFrame, font=( "", 10))
				StrengthLabel.place(x=300, y=140)

				RetypeE = Entry(ContentFrame, width=40, bd=2, relief=GROOVE, font=("", 10))
				RetypeE.place(x=10, y=140)

				# Limit settings #
				Label(ContentFrame, text="Set account limits *optional", font=("", 10)).place(x=10, y=180)
				mxQueryLimitE = Entry(ContentFrame, width=30, bd=2, relief=GROOVE, font=("", 10))
				mxQueryLimitE.place(x=10, y=210)

				mxUpdateLimitE = Entry(ContentFrame, width=30, bd=2, relief=GROOVE, font=("", 10))
				mxUpdateLimitE.place(x=10, y=240)

				mxConnectionLimitE = Entry(ContentFrame, width=30, bd=2, relief=GROOVE, font=("", 10))
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

	def ExportDatabase():
		exportwin = Tk()

		exportwin.title("FlameSQL Export database")
		exportwin.geometry("400x430")
		exportwin.iconbitmap("Resources/icon.ico")
		exportwin.resizable(0,0)

		selectedDatabase = ""

		def ExportClose():
			exportwin.destroy()

		def ExportCommand():
			global selectedDatabase
			
			exportLocation = filedialog.asksaveasfilename(filetypes=(("database file","*.db"),("all files","*.*")), title="Export database")

			import Lib.Export as exportlib
			exportlib.ExportDatabase(hostname, username, password, selectedDatabase[0], exportLocation, exportwin)

		def DatabaseSelect(event):
			global selectedDatabase

			try:
				selectedDatabase = databaseSelect.get(databaseSelect.curselection())
			except:
				pass

			if selectedDatabase:
				databaseLabel.config(text="Database: " + str(selectedDatabase[0]))
			else:
				messagebox.showerror("Error", "Please select a database")

		def GetDatabases():
			conn = MySQLdb.connect(hostname, username, password)
			cursor = conn.cursor()
			cursor.execute("show databases")
			serverreturn = cursor.fetchall()
			cursor.close()
			conn.close()

			for item in serverreturn:
				databaseSelect.insert(END, item)

		HeaderPanel = Frame(exportwin, height=80, bd=2, relief=RIDGE)
		HeaderPanel.pack(fill=X)
		Label(exportwin, text="Export database", font=("", 10)).place(x=10, y=10)

		databaseLabel = Label(HeaderPanel, text="Database: no database selected", font=("", 10))
		databaseLabel.place(x=10, y=50)

		databaseSelect = Listbox(exportwin)
		databaseSelect.pack(fill=BOTH, expand=1)
		databaseSelect.bind("<<ListboxSelect>>", DatabaseSelect)

		BottomPanel = Frame(exportwin, height=20, bd=2, relief=RIDGE)
		BottomPanel.pack(fill=X)

		tkinter2.Button(BottomPanel, text="export", width=15, command=ExportCommand).pack(side=LEFT)
		tkinter2.Button(BottomPanel, text="cancel", width=15, command=ExportClose).pack(side=LEFT)

		GetDatabases()

		exportwin.mainloop()

	# Menu bar #
	menubar = Menu(window)
	menubar.add_command(label="Users", command=UserPanel)

	servermenu = Menu(menubar, tearoff=0)
	servermenu.add_command(label="Server manager", command=ServerInfo)
	servermenu.add_command(label="Export stats", command=ExportServerStats)
	servermenu.add_separator()
	servermenu.add_command(label="Export database", command=ExportDatabase)
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
	
		database = sqlite3.connect("Data/saved.db")
		cursor = database.cursor()
		cursor.execute("select * from saved")
		dbreturn = cursor.fetchall()
		cursor.close()
		database.close()

		for item in dbreturn:
			Hostname = item[1]
			Username = item[2]
			Password = item[3]

			SavedListbox.insert(END, Username + "@" + Hostname)
	
	def LoadNewGui():
		global HostnameE
		global UsernameE
		global PasswordE

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
	
		def Connect(event, HostnameE, UsernameE, PasswordE):
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
		
		def TestConnection(HostnameE, UsernameE, PasswordE):
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
				
				timestamp = int(time.time())
				database = sqlite3.connect("Data/saved.db")
				cursor = database.cursor()
				cursor.execute("insert into saved(id, hostname, username, password) values (" + str(timestamp) + ", '" + hostname + "', '" + username + "', '" + password + "')")
				cursor.close()
				database.commit()
				database.close()
				
				LoadSaved()
	
		'''def OpenSave(event):
			selected = SavedListbox.get(SavedListbox.curselection())
			
			datasplit = selected.split("@")
			hostname = datasplit[1]
			username = datasplit[0]
			
			database = sqlite3.connect("Data/saved.db")
			cursor = database.cursor()
			cursor.execute("select * from saved")
			dbreturn = cursor.fetchall()
			cursor.close()
			database.close()
			
			for item in dbreturn:
				hostname = item[1]
				username = item[2]
				password = item[3]

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
					messagebox.showerror("Error", datasplit[0] + "\n" + datasplit[1])'''

		def OpenSave(event):
			selected = SavedListbox.get(SavedListbox.curselection())

			ClearPanel(ConnInfoFrame)

			def UpdateSave():
				hostname = HostnameE.get()
				username = UsernameE.get()
				password = PasswordE.get()

				timestamp = int(time.time())

				try:
					sql = "delete from saved where hostname='" + hostname + "' and username='" + username + "'"
					print(sql)
					sql2 = "insert into saved(id, hostname, username, password) values (" + str(timestamp) + ", '" + hostname + "', '" + username + "', '" + password + "')"
					database = sqlite3.connect("Data/saved.db")
					cursor = database.cursor()
					cursor.execute(sql)
					database.commit()
					cursor.execute(sql2)
					database.commit()
					cursor.close()
					database.close()
					
					messagebox.showinfo("Done", "Server information has been updated.")
					LoadSaved()
				except Exception as e:
					messagebox.showerror("Error", str(e))

			def DeleteSave():
				hostname = HostnameE.get()
				username = UsernameE.get()
				password = PasswordE.get()

				try:
					sql = "delete from saved where hostname='" + hostname + "' and username='" + username + "' and password='" + password + "'"
					database = sqlite3.connect("Data/saved.db")
					cursor = database.cursor()
					cursor.execute(sql)
					cursor.close()
					database.commit()
					database.close()

					LoadSaved()
				except Exception as e:
					messagebox.showerror("Error", str(e))

			datasplit = selected.split("@")
			username = datasplit[0]
			serverip = datasplit[1]

			database = sqlite3.connect("Data/saved.db")
			cursor = database.cursor()
			cursor.execute("select * from saved where hostname='" + serverip + "' and username='" + username + "'")
			dbreturn = cursor.fetchall()
			cursor.close()
			database.close()

			for item in dbreturn:
				password = item[3]

			Label(ConnInfoFrame, text="Hostname", font=("", 11)).place(x=10, y=10)
			HostnameE = Entry(ConnInfoFrame, width=40, bd=2, relief=RIDGE, font=("", 10))
			HostnameE.place(x=100, y=10)
			
			Label(ConnInfoFrame, text="Username", font=("", 11)).place(x=10, y=60)
			UsernameE = Entry(ConnInfoFrame, width=40, bd=2, relief=RIDGE, font=("", 10))
			UsernameE.place(x=100, y=60)
			
			Label(ConnInfoFrame, text="Password", font=("", 11)).place(x=10, y=110)
			PasswordE = Entry(ConnInfoFrame, width=40, bd=2, relief=RIDGE, font=("", 10), show="*")
			PasswordE.place(x=100, y=110)

			HostnameE.insert(END, serverip)
			UsernameE.insert(END, username)
			PasswordE.insert(END, password)

			tkinter2.Button(ConnInfoFrame, text="Connect", width=12, command=lambda: Connect("Reeeeee XD", HostnameE, UsernameE, PasswordE)).place(x=10, y=200)
			tkinter2.Button(ConnInfoFrame, text="Test", width=12, command=lambda: TestConnection(HostnameE, UsernameE, PasswordE)).place(x=100, y=200)
			tkinter2.Button(ConnInfoFrame, text="Update", width=12, command=UpdateSave).place(x=190, y=200)
			tkinter2.Button(ConnInfoFrame, text="Delete", width=12, command=DeleteSave).place(x=280, y=200)

		global HostnameE
		global UsernameE
		global PasswordE

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
		
		tkinter2.Button(ConnInfoFrame, text="Connect", width=12, command=lambda: Connect("Reeeeee XD", HostnameE, UsernameE, PasswordE)).place(x=10, y=200)
		tkinter2.Button(ConnInfoFrame, text="Test", width=12, command=lambda: TestConnection(HostnameE, UsernameE, PasswordE)).place(x=100, y=200)
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

if os.path.isfile("Data/saved.db"):
	pass
else:
	database = sqlite3.connect("Data/saved.db")
	cursor = database.cursor()
	cursor.execute("create table saved(id INTEGER, hostname TEXT, username TEXT, password TEXT)")
	cursor.close()
	database.commit()

Login()
