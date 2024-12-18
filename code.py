"""CircuitPython Essentials Storage logging example"""
import time
import board
import busio
from adafruit_circuitplayground import cp

# Set up UART communication with the Sprint-IR etCO2 sensor
uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout = 0.05)

try:

    # set the mode of the CO2 sensor to polling mode: the sensor will send data when asked
    uart.write("K 2\r\n")

    time.sleep(0.5)

    data_received = uart.read(8)  # Adjust byte size as per Sprint-IR sensor documentation
    if data_received:
        print(f"Mode: {data_received}")  # Display reading

    uart.write(".\r\n")

    time.sleep(0.5)

    data_received2 = uart.read(10)  # Adjust byte size as per Sprint-IR sensor documentation
    if data_received2:
        print(f"multiplier: {data_received2}")  # Display reading

    decoded_data = data_received2.decode('ascii')  # Convert bytes to string
    clean_data = decoded_data.strip()  # Remove leading and trailing whitespace
    numeric_part = ''.join(filter(str.isdigit, clean_data))  # Keep only digits
    mult = int(numeric_part)  # Convert to integer

    # enter loop: this runs continuously during data collection


    with open("/acceleration.txt", "w") as fp: # create blank/overwrite existing acceleration.txt file
        while True:
            start_time = time.monotonic()  # Record loop start time

            uart.write(b"z\r\n")  # Request raw CO2 reading from Sprint-IR sensro
            time.sleep(0.01)  # Allow sensor time to respond (10 ms is typical)

            val = uart.read(10)  # Read the response
            decoded_data = val.decode('ascii') # convert to ASCII

            # Convert bytes to string
            clean_data = decoded_data.strip()  # Remove leading and trailing whitespace
            numeric_part = ''.join(filter(str.isdigit, clean_data))  # Keep only digits
            trueval = mult*int(numeric_part)  # Convert to integer

            print(trueval) # check decoded value from sensor

            # Maintain 20 Hz data collection based on variance in loop exection elapsed time
            elapsed = time.monotonic() - start_time
            if elapsed < 0.05:  # 20 Hz = 1/20 = 0.05 seconds
                time.sleep(0.05 - elapsed)

            x, y, z = cp.acceleration # get acceleration data

            # format three accerlation values and CO2 data, store data in a buffer
            data_line = '{0:f}, {1:f}, {2:f} {3:d}\n'.format(x, y, z, trueval)
            print(data_line)  # Print to Serial to check data
            fp.write(data_line)
            
            if button == 1: # if either button is pressed, exit the while loop to cease data collection
                break
    fp.flush() # write data from buffer to .txt file

# overall debugging for the low-level OS of the Adafruit Circuit Playground Express
except OSError as e:  # Typically when the filesystem isn't writeable...
    delay = 0.5  # ...blink the LED every half second.
    if e.args[0] == 28:  # If the file system is full...
        delay = 0.25  # ...blink the LED faster!
    while True:
        time.sleep(delay)
