import navio.util
import navio.ublox
import sqlite3
import sys

def updateData(lat1,lon1,fix1):
    conn=sqlite3.connect('../sensorsData.db')
    curs=conn.cursor()
    curs.execute("""UPDATE GPS_data SET id=1, lon=?, lat=?,fix=? WHERE id=1""",(lon1,lat1,fix1))
    conn.commit()
    conn.close()

def display():
    for row in curs.execute("SELECT * FROM GPS_data"):
	print(row)

if __name__ == "__main__":
    ubl = navio.ublox.UBlox("spi:0.0", baudrate=5000000, timeout=2)
    ubl.configure_poll_port()
    ubl.configure_poll(navio.ublox.CLASS_CFG, navio.ublox.MSG_CFG_USB)
    #ubl.configure_poll(navio.ublox.CLASS_MON, navio.ublox.MSG_MON_HW)
    ubl.configure_port(port=navio.ublox.PORT_SERIAL1, inMask=1, outMask=0)
    ubl.configure_port(port=navio.ublox.PORT_USB, inMask=1, outMask=1)
    ubl.configure_port(port=navio.ublox.PORT_SERIAL2, inMask=1, outMask=0)
    ubl.configure_poll_port()
    ubl.configure_poll_port(navio.ublox.PORT_SERIAL1)
    ubl.configure_poll_port(navio.ublox.PORT_SERIAL2)
    ubl.configure_poll_port(navio.ublox.PORT_USB)
    ubl.configure_solution_rate(rate_ms=1000)

    ubl.set_preferred_dynamic_model(None)
    ubl.set_preferred_usePPP(None)

    ubl.configure_message_rate(navio.ublox.CLASS_NAV, navio.ublox.MSG_NAV_POSLLH, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_NAV, navio.ublox.MSG_NAV_PVT, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_NAV, navio.ublox.MSG_NAV_STATUS, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_NAV, navio.ublox.MSG_NAV_SOL, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_NAV, navio.ublox.MSG_NAV_VELNED, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_NAV, navio.ublox.MSG_NAV_SVINFO, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_NAV, navio.ublox.MSG_NAV_VELECEF, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_NAV, navio.ublox.MSG_NAV_POSECEF, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_RXM, navio.ublox.MSG_RXM_RAW, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_RXM, navio.ublox.MSG_RXM_SFRB, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_RXM, navio.ublox.MSG_RXM_SVSI, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_RXM, navio.ublox.MSG_RXM_ALM, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_RXM, navio.ublox.MSG_RXM_EPH, 1)
    ubl.configure_message_rate(navio.ublox.CLASS_NAV, navio.ublox.MSG_NAV_TIMEGPS, 5)
    ubl.configure_message_rate(navio.ublox.CLASS_NAV, navio.ublox.MSG_NAV_CLOCK, 5)
    #ubl.configure_message_rate(navio.ublox.CLASS_NAV, navio.ublox.MSG_NAV_DGPS, 5)
    lat1=19
    lon1=72
    fix1=2
    while True:
        msg = ubl.receive_message()
	if msg is None:
            if opts.reopen:
                ubl.close()
                ubl = navio.ublox.UBlox("spi:0.0", baudrate=5000000, timeout=2)
                continue
            print(empty)
            break
        #print(msg.name())
	while msg.name() != "NAV_POSLLH" :
            msg = ubl.receive_message()
        if msg.name() == "NAV_POSLLH":
            outstr = str(msg).split(",")[1:]
            lon1 = float(outstr[0].split('=')[1])/10000000
	    lat1 = float(outstr[1].split('=')[1])/10000000
#	    lon1=73.757779
#	    lat1=18.425613
	while msg.name() != "NAV_STATUS" :
            msg = ubl.receive_message()
        if msg.name() == "NAV_STATUS":
            outstr1 = str(msg).split(",")[1:2]
            fix_str = str(outstr1).split("=")[1]
#	    fix1=3
	    fix1 = float(str(fix_str).split("'")[0])
	updateData(lat1,lon1,fix1)
	print('updated' + ' lat '+str(lat1)+' lon '+str(lon1)+' fix '+ str(fix1))
