import radio
import microbit
from microbit import sleep
from microbit import uart
from microbit import display

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
    #Inversion de l'ordre des caractères
    msg = str(msg)
    translated = ''
    while i >= 0:
        translated = translated + msg[i]
        i = i - 1
    return translated

def cipher_key(msg, key):
    result = ""
    key_tmp = key
    bin_msg = map(bin,bytearray(msg))

    z = 0
    for bit_msg in (list(bin_msg)):
        z += 1

    while len(key_tmp) <= z:
        key_tmp += key
    key_tmp += key
    #print("len_key ", len(key_tmp))
    bin_key = map(bin,bytearray(key_tmp))
    bin_key = list(bin_key)

    #print("key",key_tmp)
    bin_msg = map(bin,bytearray(msg))

    i = 0
    for bit_msg in list(bin_msg):
        #print("bit")
        bit_msg = int(bit_msg)
        bit_key = int(bin_key[i])
        tmp = bit_msg ^ bit_key

        result += chr(tmp)
        i += 1
    return result

def encrypt(msg):
    msg = str(msg)
    i =  len(msg) - 1
    msg = reverse(msg, i)
    msg = cipher_key(msg, key)
    return msg

def decrypt(msg):
    msg = str(msg)
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
    elif receivedMsg:
        p_msg = parse(receivedMsg)
        
        #réception de la clée et envoie d'un acquitement
        if p_msg.type == "key":
            key = p_msg.msg
            radio.send("keyOK")
        
        #réception du channel chiffré et envoi d'un acquitement chiffré
        if p_msg.type == "ch1":
            r_msg = decrypt(p_msg.msg)

            send_txt = encrypt("OK")
            #radio.send(send_txt)
            send_msg="ch1"+send_txt
            radio.send(send_msg)
            str_msg = str(r_msg)
            int_msg = int(str_msg, 10)
            
            radio.config(channel=10)
            #radio.config(channel=int_msg)
            microbit.display.scroll("channel Ok", wait=False, loop=False)
        
        #réception de l'acquitement chiffré de la connexion établie
        if p_msg.type == "ch2":
            microbit.display.scroll("ch2", wait=False, loop=False)
            msg_r = decrypt(p_msg.msg)
            if msg_r == "established":
                connect = True
                microbit.display.scroll(msg_r, wait=False, loop=False)
        
        #Si connexion établie, envoie des messages par UART
        if p_msg.type == "msg" and connect == True:
            microbit.display.scroll("UART Recieve", wait=False, loop=False)
            msg_r = decrypt(p_msg.msg)
            uart_write_request(msg_r)
            #uart_write_request(p_msg.msg)
            microbit.display.scroll("UART Send", wait=False, loop=False)


    
