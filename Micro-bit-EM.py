from microbit import *
import radio


# On initialise la communication Radio
radio.on()
radio.config(length=251)
radio.config(channel=45)
radio.config(address=0x86245977)

# On initialise la communication UART
uart.init(baudrate=115200, bits=2048)

def request_connection(request): 
    uart_Rx_buffer = [request]
    display.set_pixel(2, 2, 5)
    uart.write(bytes(uart_Rx_buffer[0]))
    return

while True: 
    # On attend un message de la microbit 
    RFmessage = radio.receive()

    try:
        request = eval(RFmessage)
    except:
        continue

    request_connection(request)
