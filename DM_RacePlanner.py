import sys
import ac
import acsys 
import csv
import os
import datetime
import time
import platform

if platform.architecture()[0] == "64bit":
  sysdir = "stdlib64"
else:
  sysdir = "stdlib"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "dmrp", sysdir))
os.environ['PATH'] = os.environ['PATH'] + ";."

from dmrp import dmrp

# compound
compound = 'NA'

# lap valid
lap_valid = 1
  
# is car in the pit lane
current_inpit = 0

# was car in the pit lane on the current lap
current_lap_inpit = 0

# current lap number
lapnumber = ac.getCarState(0, acsys.CS.LapCount)

# last lap time
last_lap = 0

# current date and file name
now = datetime.date.today()
driver_name = ac.getDriverName(0)
track_name = ac.getTrackName(0)
car = ac.getCarName(0)

# file name
file_name = time.strftime('%Y%m%d%H%M%S', time.localtime()) + "_" + driver_name + "_" + track_name + ".csv"

# get lap time on this lap
get_laptime = 0

# initiate empty lists
time_list = []
lap_list = []
pit_list = []
laptime_list = []
compound_list = []
valid_list = []

def acMain(ac_version):
	
	return "DM Race Planner"
	
def acUpdate(deltaT):
	global current_inpit, lapnumber, current_lap_inpit, compound, lap_valid, time_list, lap_list, pit_list, laptime_list, compound_list, valid_list, last_lap, get_laptime
	
	# invalidate lap when more than 2 tyres off the track
	if dmrp.info.physics.numberOfTyresOut > 2:
		lap_valid_tmp = 0
		if lap_valid_tmp != lap_valid:
			lap_valid = lap_valid_tmp
	
	pit = ac.isCarInPitline(0)
	if pit != current_inpit:
	
		# get compound after car left the pitlane
		if pit == 0:
			compound = dmrp.info.graphics.tyreCompound
			
		current_inpit = pit        	        	
		if current_inpit == 1:
			current_lap_inpit = current_inpit

	lap = ac.getCarState(0, acsys.CS.LapCount)
	
	# new lap
	if lap != lapnumber:
		dt = time.strftime('%Y%m%d%H%M%S', time.localtime())
		lapnumber = lap

		get_laptime = 1
		
		# update lists
		time_list.append(dt)
		lap_list.append(lapnumber)
		pit_list.append(current_lap_inpit)
		compound_list.append(compound)
		valid_list.append(lap_valid)
				
		current_lap_inpit = 0
		current_inpit = 0
		lap_valid = 1

	# get last lap time after 1 second
	curent_laptime = ac.getCarState(0, acsys.CS.LapTime)
	if curent_laptime > 1000 and get_laptime == 1:
		last_lap = ac.getCarState(0, acsys.CS.LastLap)

		# update laptime list
		laptime_list.append(last_lap)

		get_laptime = 0

def acShutdown():
	global track_name, driver_name, car, file_name, time_list, lap_list, pit_list, laptime_list, compound_list, valid_list

	insert_rows = len(lap_list) 

	try:
		# set up mySQL connection
		con = dmrp.pymysql.connect('22707.v.tld.pl', 'admin22707_raceplanner', '9AeG6fZ6l9', 'baza22707_raceplanner')
		cur = con.cursor()

		# upload lap to the database
		for i in range(insert_rows):
		
			sql = "INSERT INTO `SessionData` (`lap`, `track`, `driver`, `car`, `time`, `pit`, `laptime`, `compound`, `valid`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
			cur.execute(sql, (lap_list[i], track_name, driver_name, car, time_list[i], pit_list[i], laptime_list[i], compound_list[i], valid_list[i]))
			con.commit()
		con.close()
	
	except:
		# export csv locally if error occurs
		with open(file_name, 'w', newline = '') as csvfile:
			writer = csv.DictWriter(csvfile, fieldnames = ['lap', 'track', 'driver', 'car', 'time', 'pit', 'laptime', 'compound', 'valid'], delimiter = ';')
			writer.writeheader()
			for row in range(insert_rows):
				writer.writerow({'lap': lap_list[row], 'track': track_name, 'driver': driver_name, 'car': car, 'time': time_list[row], 
				'pit': pit_list[row], 'laptime': laptime_list[row], 'compound': compound_list[row], 'valid': valid_list[row]})
