__author__ = 'daniel.dejager'

import zmq,smtplib

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("ipc:///tmp/ln-email")

socket.setsockopt(zmq.SUBSCRIBE,"")
username = 'danielmiester@gmail.com'
password = 'Bogus'


server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login(username,password)

while True:
    msg =  socket.recv()
    msg = msg.split(",",1)
    message = msg[0]
    emails = msg[1].split(",")
    if len(emails)>0:
        try:
            print "sending ",message, "to",emails
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.starttls()
            server.login(username, password)
            server.sendmail("danielmiester+alerts@gmail.com", emails, message)
            server.quit()
        except Exception as e:
            print e
