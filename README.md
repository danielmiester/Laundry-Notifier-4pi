# Laundry Notifier for raspberryPi

###Motivation        

I live in a large houshold and it seems that there's always a load in the washer or dryer. I 've had the rpi floating around for a while so I've finally decided on a useful project for it. Combine it with a userfriendly interface to inform users via text message  when their load is done.
 
###Execution
I created this using Python,wxPython, and ØMQ--more on that later

I used the handy wxFormBuilder app to generate the UI's  layout code, as I hate coding UIs by hand. I'm ok with wiring them up by hand, but there's nothing like a WYSIWYGenvironment fory laying out a UI.
I wanted to decouple the UI from the emailer and from the hardware, so I used 0mq to provide a message passing archetecture between them. Over engineered? Yes. Really easy to implement, definately. Because I impemented the message bus, getting the various components to work together was rediculously easy.
I created a simple standin message server that emulated the washer and dryer, and left that running while I got the ui to respond as I had envisioned.
after I got the UI working, and generating messages for the emailer, it was chileds play to get the emailer working, as I only ever had to restart the emailer.

###DISCLAIMER:
I have not yet run this code on the rPi, or implemented the hardware side of this. Before this could work with your system, you will have to create a 0mq publisher that outputs to `ipc:///tmp/ln-states` and reads the states of your hardware.
The UI expects events to match the following REGEX pattern
`^Update State,(Washer|Dryer) (Buzz|Power) (On|Off)$`
Be aware that in this version, the functionality if you try to inform it about the washer's buzzer is unknown.

You will also have to update messageender.py to point to your email server, and include your username and pasword.

