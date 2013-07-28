import random
from time import sleep
import zmq

__author__ = 'daniel.dejager'




context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("ipc:///tmp/ln-states")


while True:
    machine = ["Dryer","Washer"][random.randint(0,1)]
    option = ["Power","Buzz"][random.randint(0,1)] if machine != "Washer" else "Power"
    state = ["On","Off"][random.randint(0,1)]
    msg = "Update State,{} {} {}".format(machine,option,state)
    print msg
    socket.send(msg)
    sleep(2)


