import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="secret"
)

mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE wxwatcher")