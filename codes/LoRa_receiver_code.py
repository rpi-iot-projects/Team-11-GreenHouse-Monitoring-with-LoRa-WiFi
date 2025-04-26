"""
CircuitPython Feather RP2040 RFM95 Packet Receive module

This code receives the data from remote RFM module (transmitters), and passes it to gateway RPI using UART
The data structure is as follows:
'{
  'S':int
  'T':int
  'temperature':float
  'humidity':float
  'soil moisture':float
  }'
S: sender (has an int value)
T: target (has an int value)
temp: float data from sensor
humidity: float data from sensor
soil moisture: float data from sensor

"""
#import required libraries
import board
import digitalio
import adafruit_rfm9x
import time
import busio
import json
import aesio

# this is the key for AES decryption
key = b"thisistestkey123"

def unpad_pkcs7(data):
    # Remove PKCS#7 padding.
    padding_len = data[-1]
    return data[:-padding_len]

#XOR two 16-byte data
def xor_bytes(b1, b2):
    return bytes(a ^ b for a, b in zip(b1, b2))

# AES decryption block
def aes_ecb_decrypt_block(key, block):
    cipher = aesio.AES(key)
    out_block = bytearray(16)
    cipher.decrypt_into(block, out_block)
    return bytes(out_block)

# AES decryption wrapper function
def cbc_decrypt(key, iv, ciphertext):
    plaintext = bytearray()
    previous = iv
    # Process the ciphertext in 16-byte blocks.
    for i in range(0, len(ciphertext), 16):
        block = ciphertext[i:i+16]
        # Decrypt the block.
        dec_block = aes_ecb_decrypt_block(key, block)
        # XOR with the previous ciphertext block (or IV for the first block) to recover plaintext.
        plain_block = xor_bytes(dec_block, previous)
        plaintext.extend(plain_block)
        previous = block
    return bytes(plaintext)

# Initialize UART communication mode
uart = busio.UART(board.TX, board.RX, baudrate = 9600)

#Set the ID for this device
rfm_id = 0


# Define radio frequency in MHz.
RADIO_FREQ_MHZ = 915.0 # this is the operating frequency of our RFM95 module

# Define Chip Select and Reset pins for the radio module.
CS = digitalio.DigitalInOut(board.RFM_CS)
RESET = digitalio.DigitalInOut(board.RFM_RST)

# Initialise RFM95 radio
rfm95 = adafruit_rfm9x.RFM9x(board.SPI(), CS, RESET, RADIO_FREQ_MHZ)

# Wait to receive packets.
print("Waiting for packets...")
while True:
    # Look for a new packet - wait up to 5 seconds:
    packet = rfm95.receive(timeout=5.0)
    # If no packet was received during the timeout then None is returned.
    if packet is not None:
        try:

            print("Received a packet!")
            # check the length of packet. If less than 16, then its not worth decoding
            if len(packet) < 16:
                print("Packet too short to contain an IV.")
                continue

            # take out first 16 bytes of packet for IV
            recv_iv = packet[:16]
            ciphertext = packet[16:]
            # Decrypt using our manual CBC decryption.
            padded_plaintext = cbc_decrypt(key, recv_iv, ciphertext)

            #Remove padding if used
            plaintext = unpad_pkcs7(padded_plaintext)

            # Decode the plaintext to confirm if it is the same transmitted text
            plaintext_str = plaintext.decode('utf-8')
            json_data = json.loads(plaintext_str)
            #print("Decrypted JSON:", json_data)

            # check the 'T' value to see if it was intended for this specific user
            # useful in future when we may have multiple receivers
            if json_data['T'] == 0:
                print('Intened for me!')
                #data['temperature'] = 150
                uart.write(bytes(json.dumps(json_data), "UTF-8"))
                print('transmitted to RPi')
                time.sleep(0.5)
            else:
                print('not intended for me')
        except:
            print('Error in packet')

