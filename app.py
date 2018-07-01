# -*- coding: utf-8 -*-
#!/usr/bin/env python
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
from flask import Flask
from flask import render_template, request, send_file, make_response, session
import sqlite3
import sys
import time
# import navio.pwm
# import navio.util
import navio.ublox
import thread
reload(sys)
sys.setdefaultencoding('utf8')
from threading import Lock
from flask_socketio import SocketIO, emit, disconnect
# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

mon=20
mof=0.5
# navio.util.check_apm()
# def setPWM(l,r,rev) :
# 	pwmL = 0
# 	pwmR = 2
# 	pwmRev = 1
# 	with navio.pwm.PWM(pwmL) as pwml,navio.pwm.PWM(pwmR) as pwmr,navio.pwm.PWM(pwmRev) as pwmrev:
# 		pwml.set_period(50)
# 		pwml.enable()
# 		pwmr.set_period(50)
# 		pwmr.enable()
# 		pwmrev.set_period(50)
# 		pwmrev.enable()
# 		for x in range(0,500):
# 			pwml.set_duty_cycle(l)
# 			pwmr.set_duty_cycle(r)
# 			pwmrev.set_duty_cycle(rev)

data1="STOP"

def background_thread():
	conn1=sqlite3.connect('sensorsData.db', check_same_thread=False)
	curs1=conn.cursor()
	while True:
		for row in curs1.execute("SELECT * FROM GPS_data ORDER BY id DESC LIMIT 1"):
			lon = row[1]
			lat = row[2]
			fix = row[3] #	    print(lat +lon+fix)
		socketio.emit('my_response',{'lat': lat,'lon':lon,'fix': fix},namespace='/test')
		socketio.sleep(10)

# if data1=="STOP":
#	setPWM(mof,mof,mof)
# elif data1=="FORWARD":
# 	setPWM(mon,mon,mof)
# elif data1=="RIGHT":
# 	setPWM(mon,mof,mon)
# elif data1=="LEFT":
# 	setPWM(mof,mon,mon)
# elif data1=="BACK":
# 	setPWM(mof,mof,mon)

#thread.start_new_thread(background_thread1,(data1))

conn=sqlite3.connect('sensorsData.db', check_same_thread=False)
curs=conn.cursor()

@socketio.on('my_event', namespace='/test')
def test_message(message):
	for row in curs.execute("SELECT * FROM GPS_data ORDER BY id DESC LIMIT 1"):
		lon = row[1]
		lat = row[2]
		fix = row[3]
	print('Client myevent')
	socketio.emit('my_response',{'lat': lat,'lon':lon,'fix': fix},namespace='/test')

@socketio.on('connect', namespace='/test')
def test_connect():
	for row in curs.execute("SELECT * FROM GPS_data ORDER BY id DESC LIMIT 1"):
		fix = row[3]
		lat = row[2]
		lon = row[1]
	print('Client connected')
	socketio.emit('my_response',{'lat': lat,'lon':lon,'fix': fix},namespace='/test')
	global thread
	with thread_lock:
		if thread is None:
			thread = socketio.start_background_task(target=background_thread)
#            thread1 = socketio.start_background_task(target=background_thread1)
	print('Thread started')

@socketio.on('disconnect', namespace='/test')
def test_disconnect():
	print('Client disconnected', request.sid)

def getHistData (numSamples):
	curs.execute("SELECT * FROM Sensor_data ORDER BY timestamp DESC LIMIT "+str(numSamples))
	data = curs.fetchall()
	dates = []
	temps = []
	hums = []
	for row in reversed(data):
		dates.append(row[0])
		temps.append(row[1])
		hums.append(row[2])
	return dates,temps,hums

def getData():
	for row in curs.execute("SELECT * FROM Sensor_data ORDER BY timestamp DESC LIMIT 1"):
		time = str(row[0])
		temp = row[1]
		hum = row[2]
	return time, temp, hum

def maxRowsTable():
	for row in curs.execute("select COUNT(temp) from  Sensor_data"):
		maxNumberRows=row[0]
	return maxNumberRows

# define and initialize global variables
global numSamples
numSamples = maxRowsTable()
if (numSamples > 101):
	numSamples = 100

@app.route("/")
def index():
	return render_template('home.html',async_mode=socketio.async_mode)

@app.route("/award.html")
def award():
	return render_template('award.html')

@app.route("/remote.html")
def remote():
	return render_template('remote.html', async_mode=socketio.async_mode )

@app.route("/home.html")
def home():
	return render_template('home.html')

@app.route("/video.html")
def video():
	return render_template('video.html')

@app.route("/sensor.html")
def sensor():
	time, temp, hum = getData()
	templateData = {
		'time': time,
		'temp': temp,
		'ph': hum
		}
	return render_template('sensorPlot.html',**templateData)

@app.route("/sensorPlot.html")
def sensorPlot():
	time, temp, hum= getData()
	templateData = {
		'time': time,
		'temp': temp,
		'ph': hum
		}
	return render_template('sensorPlot.html',**templateData)

@app.route("/historicPlot.html")
def historicPlot():
	templateData = {
	'numSamples'	: numSamples
	    }
	return render_template('historicPlot.html',**templateData)

@app.route("/map.html")
def map():
	return render_template('map.html', async_mode=socketio.async_mode)

@app.route('/historicPlot.html', methods=['POST'])
def change():
	global numSamples
	# Getting the value from the webpage
	numSamples = int(request.form['numSamples'])
	numMaxSamples = maxRowsTable()
	if (numSamples > numMaxSamples):
	    numSamples = (numMaxSamples-1)
	templateData = {
	'numSamples'	: numSamples
	}
	return render_template('historicPlot.html',**templateData)

@app.route('/left_side')
def left_side():
# 	setPWM(mof,mon,mon)
	data1="LEFT"
	print(data1)
	return 'true'

@app.route('/right_side')
def right_side():
# 	setPWM(mon,mof,mon)
	data1="RIGHT"
	print(data1)
	return 'true'

@app.route('/up_side')
def up_side():
# 	setPWM(mon,mon,mof)
	data1="FORWARD"
	print(data1)
	return 'true'

@app.route('/down_side')
def down_side():
# 	setPWM(mof,mof,mon)
	data1="BACK"
	print(data1)
	return 'true'

@app.route('/stop')
def stop():
# 	setPWM(mof,mof,mof)
	data1="STOP"
	print(data1)
	return  'true'

@app.route('/plot/temp')
def plot_temp():
	times, temps, hums  = getHistData(numSamples)
	ys = temps
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title("Temperature Sensor")
	axis.set_xlabel("Samples")
	axis.set_ylabel("Temperature [°C]")
	axis.grid(True)
	xs = range(numSamples)
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response

@app.route('/plot/ph')
def plot_ph():
	times, temps, hums = getHistData(numSamples)
	ys = hums
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title("Humidity Sensor")
	axis.set_xlabel("Samples")
	axis.set_ylabel("Percentage Humidity")
	axis.grid(True)
	xs = range(numSamples)
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response

if __name__ == "__main__":
	#app.debug = True
	print("Start")
	socketio.run(app, debug=True,host='0.0.0.0',port=5010)

# sudo modprobe bcm2835-v4l2