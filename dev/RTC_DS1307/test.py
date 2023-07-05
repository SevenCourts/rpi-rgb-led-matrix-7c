import smbus
import time
import datetime
import SDL_DS1307
import logging


#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1

print ("RTC with Pi3 USING SDL_DS1307 Library Version 1.0 - From SwitchDoc Labs")
print ("Program started at:\n\t" + time.strftime("%Y-%m-%d %H:%M:%S"))

try:
    ds1307 = SDL_DS1307.SDL_DS1307(1, 0x68)
    ds1307.write_now()

    dt = ds1307._read_date()   #read date from RTC DS1307
    mt=ds1307._read_month()  #read month from RTC DS1307
    yr=ds1307._read_year() #read year from RTC DS1307
    Hr=ds1307._read_hours() #read year from RTC DS1307
    Mn=ds1307._read_minutes() #read year from RTC DS1307
    Sc=ds1307._read_seconds() #read year from RTC DS1307
    
    #Convert float in Int
    date=int(dt) 
    months=int(mt)
    year=int(yr)
    Hours=int(Hr)
    Minutes=int(Mn)
    Seconds=int(Sc)

    time.sleep(2)

    currenttime = datetime.datetime.utcnow()

    print ("Current time:\n\t" + str(currenttime))
    print ("Raspberry Pi:\n\t" + time.strftime("%Y-%m-%d %H:%M:%S"))
    print ("DS1307 RTC:\n\t%d-%d-%d-%d %d:%d" % (ds1307._read_year(),ds1307._read_month(),ds1307._read_date(),ds1307._read_hours(),ds1307._read_minutes(),ds1307._read_seconds()))

    Timestamp =str (year) +"-"+ str(months)+"-"+str(date) +""+ str (Hours) +":"+ str(Minutes) +":"+ str(Seconds)
    print ("TimeStamp:\n\t",Timestamp)
except OSError as e:
    log(e, 'Cannot access RTC DS1307')
