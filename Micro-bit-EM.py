import radio
import microbit
from microbit import sleep

radio.on()

connect = False
#key = "IY546G6ZAubNFiua4zhef78p4afeaZRG"
key = ""
uart.init(baudrate=115200, bits=8,parity=None, stop=1)

def uart_write_request(request): 
    display.set_pixel(2, 2, 5)
    uart.write(request)
    return True

class Msg:
    def __init__(self):
        self.msg = ""
        self.type = ""

def parse(msg):
    l = len(msg) - 1
    print("length: ", l)
    i = 0
    parse_msg = Msg()
    while i <= l:
        print("i", i)
        if i < 3:
            parse_msg.type += msg[i]
        if i  >= 3:
            parse_msg.msg += msg[i]
        i += 1
    return parse_msg

def reverse(msg, i):
    translated = ''
    while i >= 0:
        translated = translated + msg[i]
        i = i - 1
    return translated

def cipher_key(msg, key):
    result = ""
    key_tmp = str(key)
    while len(key) < len(msg):
        key_tmp = str(key_tmp) + str(key)

    key2 = ''
    for i in range(len(msg)):
        key2 += key_tmp[i]

    bin_msg = map(bin,bytearray(msg))
    bin_key = map(bin,bytearray(key2))
    #bin_msg = map(bin,bytearray(bytearray(b'10')))
    #bin_msg = map(bin,bytearray(msg))
    #bin_key = map(bin,bytearray(key2))

    bin_key = list(bin_key)
    i = 0
    for bit_msg in list(bin_msg):
        #bit_msg = int(bit_msg, base=2)
        #bit_key = int(bin_key[i], base=2)
        bit_msg = int(bit_msg)
        bit_key = int(bin_key[i])
        tmp = bit_msg ^ bit_key
        result += chr(tmp)
        i += 1
    return result

def encrypt(msg):
    i =  len(msg) - 1
    msg = reverse(msg, i)
    msg = cipher_key(msg, key)
    return msg

def decrypt(msg):
    i =  len(msg) - 1
    msg = cipher_key(msg, key)
    msg = reverse(msg, i)
    return msg
    
def send(msg):
    radio.send_bytes(msg)
    
def send_key(key):
    radio.send_value("key")
    
while True:
    receivedMsg = radio.receive()
    if receivedMsg is None:
        continue
    if receivedMsg:
        p_msg = parse(receivedMsg)
        
        if p_msg.type == "key":
            key = p_msg.msg
            radio.send("keyOK")
        
        if p_msg.type == "ch1":
            r_msg = decrypt(p_msg.msg)

            send_txt = encrypt("OK")
            #radio.send(send_txt)
            send_msg="ch1"+send_txt
            radio.send(send_msg)

            microbit.display.scroll(r_msg, wait=False, loop=False)
            #radio.config(channel=10)
            #tmp_msg = int(r_msg) - 1
            #r_msg = tmp_msg + 1
            str_msg = str(r_msg)
            int_msg = int(str_msg, 10)
            
            radio.config(channel=int_msg)
        
        if p_msg.type == "ch2":
            #microbit.display.scroll("Ch2", wait=False, loop=False)
            msg_r = decrypt(p_msg.msg)
            if msg_r == "established":
                connect = True
                microbit.display.scroll(msg_r, wait=False, loop=False)
        
        if p_msg.type == "msg" and connect == True:
            msg_r = decrypt(p_msg.msg)
            uart_write_request(msg_r)

    
