from tkinter import messagebox
from tkinter import filedialog
from Lib.Widgets import *
import MySQLdb
import os

def UploadSQL(hostname, username, password):
    filelocation = filedialog.askopenfilename()

    if os.path.isfile(filelocation):
        sqlfile = open(filelocation)
        sqldata = sqlfile.read()
        sqlfile.close()

        sqldata = sqldata.replace("\n", "")
        sqldatasplit = sqldata.split(";")

        try:
            conn = MySQLdb.connect(host=hostname, user=username, passwd=password, port=int(port))
            cursor = conn.cursor()

            for item in sqldatasplit:
                if len(item) > 0:
                    cursor.execute(item + ";")

            conn.commit()
            conn.close()

        except (MySQLdb.Error, MySQLdb.Warning) as e:
            error = str(e).strip("(").strip(")")
            datasplit = error.split(", ")
            messagebox.showerror("Error", datasplit[0] + "\n" + datasplit[1])

    else:
        pass

def ExecuteSQL(hostname, username, password):
    filelocation = filedialog.askopenfilename()

    if filelocation == "":
        return 0

    if os.path.isfile(filelocation):
        errors = []

        sqlfile = open(filelocation)
        sqldata = sqlfile.read()
        sqlfile.close()

        sqldata = sqldata.replace("\n", "")
        sqldatasplit = sqldata.split(";")

        connection = MySQLdb.connect(host=hostname, user=username, passwd=password, port=int(port))
        cursor = connection.cursor()

        for item in sqldatasplit:
            try:
                if len(item) > 0:
                    cursor.execute(item + ";")

            except Exception as e:
                errors.insert(len(errors), str(e))

        connection.commit()
        connection.close()

        if len(errors) > 0:
            if messagebox.askyesno("Error", "The file executed with " + str(len(errors)) + " errors\nWould you like to dump to file?"):
                savelocation = filedialog.asksaveasfilename(defaultextension=".log")

                if savelocation == "":
                    return 0

                if os.path.isfile(savelocation):
                    savefile = open(savelocation, "w")

                    for item in errors:
                        savefile.write(item + "\n")

                    savefile.close()
                else:
                    messagebox.showerror("Error", "File path does not exist\n" + savelocation)

    else:
        messagebox.showerror("Error", "File path does not exist\n" + filelocation)