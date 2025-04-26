"""
CircuitPython Feather RP2040 RFM95 Packet Transmit Module

This code transmits the data to gateway receiver RP2040 using LoRa
'{
  'S':int
  'T':int
  'temperature':float
  'humidity':float
  'soil moisture':float
  }'
S: sender (has an int value)
T: target (has an int value)
temp: float data from sensor 1
humidity: float data from sensor 2
soil moisture: float data from sensor 3
"""

#import the libraries
import os
import json
import time
import board
import digitalio
import adafruit_rfm9x
import aesio
import random
import adafruit_dht
from analogio import AnalogIn

# Pre-shared 16-byte key for AES encryption.
key = b"thisistestkey123"

#pre-defined receiver value
rx = 0

#pre-defined this model's number (for other transmitter it is 1)
tx = 2

def pad_pkcs7(data):
    # Calculate padding length so that padded data is a multiple of 16.
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len] * pad_len)

def xor_bytes(b1, b2):
    # XOR two byte sequences (both must be 16 bytes).
    return bytes(a ^ b for a, b in zip(b1, b2))

def aes_ecb_encrypt_block(key, block):
    # Encrypts a 16-byte block using AES in ECB mode.
    cipher = aesio.AES(key)
    out_block = bytearray(16)
    # encrypt_into expects the input block to be 16 bytes.
    cipher.encrypt_into(block, out_block)
    return bytes(out_block)

def cbc_encrypt(key, iv, padded_plaintext):
    ciphertext = bytearray()
    previous = iv
    # Process the plaintext in 16-byte blocks.
    for i in range(0, len(padded_plaintext), 16):
        block = padded_plaintext[i:i+16]
        # XOR the plaintext block with the previous ciphertext (or IV for first block).
        xored = xor_bytes(block, previous)
        # Encrypt the xored block.
        enc_block = aes_ecb_encrypt_block(key, xored)
        ciphertext.extend(enc_block)
        # The ciphertext block now becomes the "previous" value.
        previous = enc_block
    return bytes(ciphertext)

# Set up the radio (replace with your actual pin configuration).
RADIO_FREQ_MHZ = 915.0
CS = digitalio.DigitalInOut(board.RFM_CS)
RESET = digitalio.DigitalInOut(board.RFM_RST)
rfm95 = adafruit_rfm9x.RFM9x(board.SPI(), CS, RESET, RADIO_FREQ_MHZ)
#rfm95.spreading_factor = 12

dht = adafruit_dht.DHT11(board.D6)
analog_in = AnalogIn(board.A1)

while True:
    #collect data from sensors
    value1 = dht.temperature
    value2 = dht.humidity
    value3 = analog_in.value

    #convert soil moisture raw ADC to meaningful percentage value
    value3 = 100- ((value3-13500)/(2**16-13500))*100 # 0-100, 100 is WET (short circuit), 0 is DRY

    text = {
            'S': tx,
            'T': rx,
            'temperature': value1,
            'humidity': value2,
            'soil moisture': value3
            }

    # Convert dictionary to JSON and then to bytes.
    plain_data = json.dumps(text).encode('utf-8')

    # Pad the plaintext.
    padded_data = pad_pkcs7(plain_data)

    # Generate a new random IV for this message.
    iv = os.urandom(16)
    # Encrypt using our manual CBC mode.
    encrypted_bytes = cbc_encrypt(key, iv, padded_data)

    # Prepend the IV to the ciphertext. (They are both bytes or bytearray.)
    data_with_iv = iv + encrypted_bytes

    # check if the channel is free (by activating receiving mode. If nothing received, the channel is free)
    try:
        if (rfm95.receive(timeout=2.0)) is None:
            rfm95.send(data_with_iv)
            #wait for 5 seconds after transmission. this is the frequency of data update.
            time.sleep(5)
    except:
        print('channel is BUSY!')
        #wait for random time between 1 to 3 seconds
        wait_time = random.randint(1,3)
        time.sleep(wait_time)
