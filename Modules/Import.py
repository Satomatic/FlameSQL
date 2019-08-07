from tkinter import messagebox
import MySQLdb
import os

def UploadSQL(hostname, username, password, filelocation):
    if os.path.isfile(filelocation):
        sqlfile = open(filelocation)
        sqldata = sqlfile.read()
        sqlfile.close()

        sqldata = sqldata.replace("\n", "")
        sqldatasplit = sqldata.split(";")

        try:
            conn = MySQLdb.connect(hostname, username, password)
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
