import serial
import re
import sqlite3 
import sys
import math
 
dbname='sensorsData.db'

ser = serial.Serial('/dev/ttyUSB0',9600)
temp=0
hum=0


# log sensor data on database
def logData (temp, hum):	
	conn=sqlite3.connect(dbname)
	curs=conn.cursor()
	curs.execute("INSERT INTO Sensor_data values(datetime('now'), (?), (?))", (temp, hum))
	conn.commit()
	conn.close()

# display database data
def displayData():
	conn=sqlite3.connect(dbname)
	curs=conn.cursor()
	print ("\nEntire database contents:\n")
	for row in curs.execute("SELECT * FROM Sensor_data"):
		print (row)
	conn.close()
	
while True:
        read_serial=ser.readline()
        read_list = read_serial.split()
        read_list_num = [float(i) for i in read_list]
        size1=len(read_list_num)
        temp=read_list_num[0]
        hum=read_list_num[1]
	print('logged')
        logData(temp,hum)
#        displayData()
                
        
        
