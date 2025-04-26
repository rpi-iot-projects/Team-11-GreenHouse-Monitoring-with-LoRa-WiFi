'''
This code is for Raspberry pi gateway. (model 3 b)
It receives decrypted sensor data from RP2040 receiver module using UART
Then, it uploads the respective data in the thingsboard cloud using mqtt
'''

# import required libraries  
import paho.mqtt.client as mqtt
import json
import time
import random
import serial


# ThingsBoard server address
THINGSBOARD_HOST = 'thingsboard.cloud'  # or your server address

# Access tokens for your ThingsBoard devices (unique to each device)
ACCESS_TOKEN_GH1 = 'EoafM9JRXJaSYR2J9MyW' # token for greenhouse 1 (transmitter 1)
ACCESS_TOKEN_GH2 = 'p75S31VBocPbAGaaza0A' # token for greenhouse 2 (transmitter 2)

# MQTT topic for telemetry data
TELEMETRY_TOPIC = 'v1/devices/me/telemetry' # this is the default topic in thingsboard cloud, as each devices are unique

## this function uploads the sensor data (telemetry) to server. requires token (to destinguish which greenhouse to update)
def send_telemetry(token, telemetry):
    """Create an MQTT client, connect and publish telemetry data."""
    client = mqtt.Client()
    # Set the device access token as the MQTT username
    client.username_pw_set(token)
    
    try:
        # Connect to ThingsBoard Cloud, default unsecured port is 1883
        client.connect(THINGSBOARD_HOST, 1883, 60)
        client.loop_start()
        # Publish telemetry data (converted to JSON)
        client.publish(TELEMETRY_TOPIC, json.dumps(telemetry), qos=1)
        # Give some time for the message to be sent
        time.sleep(1)
    except Exception as e:
        print("Error sending telemetry:", e)
    finally:
        client.loop_stop()
        client.disconnect()

        
def data_from_rfm95(data):
	packet = data

	source = packet['S']
	# print('source: ', source)


	# Check the source index from the transmitted text. transmitter 1 has tag of 1, transmitter 2 has tag of 2
	if source == 1:
		rand_token = ACCESS_TOKEN_GH1
	else:
		rand_token = ACCESS_TOKEN_GH2
		
	return rand_token, data
	

if __name__ == '__main__':
	
	#Initialize UART communication
	ser = serial.Serial("/dev/ttyS0", 9600, timeout =1)
	try:
		while True:

			# Read/Simulate sensor data for each greenhouse from UART
			data = (ser.read(100))

			#check the length of data
			if len(data)>0:
				print('received a packet')

				try:
					
					data = data.decode('utf-8')
					print('data' , data)
					print ('data type: ', type(data))
				
					data = json.loads(data)

					# assign the access token
					rand_token, telemetry = data_from_rfm95(data)

					# Send telemetry data to ThingsBoard for each device
					send_telemetry(rand_token, telemetry)

					# Pause before sending the next set of data
					time.sleep(2)  # Send data every 2 seconds; adjust as needed
				except:
					print('error in data')
					pass

			time.sleep(0.1)

	except KeyboardInterrupt:
		print("Terminated by user")

