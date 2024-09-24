import serial
from datetime import datetime
import time

DELAY_20S = 20
DELAY_1MIN = 60
DELAY_4MIN = 240

PERIOD_5MIN = 300
PERIOD_1HOUR = 3600
PERIOD_4HOURS = 14400

serialPort = serial.Serial(
    port="COM5", baudrate=9600, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE
)
serial_string = "" 
start_time = time.time()
while 1:
    
    if ((time.time() - start_time) > PERIOD_5MIN + 10):
        break
    """
    
    if ((time.time() - start_time) > PERIOD_1HOUR + 30):
        break
    """
    """
    if ((time.time() - start_time) > PERIOD_4HOURS + 150):
        break
    """
    # Wait until there is data waiting in the serial buffer
    if serialPort.in_waiting > 0:

        # Read data out of the buffer until a carraige return / new line is found
        serial_string = serialPort.readline()

        # Print the contents of the serial data
        try:
            sensors_data = serial_string.decode("Ascii").strip()  
            dt = datetime.now()            
            timestamp = datetime.strftime(dt, "%Y-%m-%d %H:%M:%S")  
            data = sensors_data.split()
            data1 = data[0] + " " + data[1]
            data2 = data[2]
            data3 = data[3]
            data4 = data[4]
            
            with open('sensor1_5min.txt', 'a') as f:                
                f.write(timestamp + " " + data1+"\n")                
                f.close()
            with open('sensor2_5min.txt', 'a') as f:                
                f.write(timestamp + " " + data2+"\n")                
                f.close()
            with open('sensor3_5min.txt', 'a') as f:                
                f.write(timestamp + " " + data3+"\n")                
                f.close()
            with open('sensor4_5min.txt', 'a') as f:                
                f.write(timestamp + " " + data4+"\n")                
                f.close()                                                
            
            """
            with open('sensor1_1hour.txt', 'a') as f:                
                f.write(timestamp + " " + data1+"\n")                
                f.close()
            with open('sensor2_1hour.txt', 'a') as f:                
                f.write(timestamp + " " + data2+"\n")                
                f.close()
            with open('sensor3_1hour.txt', 'a') as f:                
                f.write(timestamp + " " + data3+"\n")                
                f.close()
            with open('sensor4_1hour.txt', 'a') as f:                
                f.write(timestamp + " " + data4+"\n")                
                f.close()
            """
            """
            with open('sensor1_1hour_volatile.txt', 'a') as f:                
                f.write(timestamp + " " + data1+"\n")                
                f.close()
            with open('sensor2_1hour_volatile.txt', 'a') as f:                
                f.write(timestamp + " " + data2+"\n")                
                f.close()
            with open('sensor3_1hour_volatile.txt', 'a') as f:                
                f.write(timestamp + " " + data3+"\n")                
                f.close()
            with open('sensor4_1hour_volatile.txt', 'a') as f:                
                f.write(timestamp + " " + data4+"\n")                
                f.close() 
            """   
            """
            with open('sensor1_4hours.txt', 'a') as f:                
                f.write(timestamp + " " + data1+"\n")                
                f.close()
            with open('sensor2_4hours.txt', 'a') as f:                
                f.write(timestamp + " " + data2+"\n")                
                f.close()
            with open('sensor3_4hours.txt', 'a') as f:                
                f.write(timestamp + " " + data3+"\n")                
                f.close()
            with open('sensor4_4hours.txt', 'a') as f:                
                f.write(timestamp + " " + data4+"\n")                
                f.close()
            """ 
        except:
            pass
        time.sleep(DELAY_20S)