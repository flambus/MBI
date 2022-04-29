import pyfirmata
import time

port = 'COM7'
board = pyfirmata.Arduino(port)
hold = 5

pin = 4

while True:

    board.digital[pin].write(1)

    time.sleep(hold)

    board.digital[pin].write(0)

    time.sleep(hold)