'''
Created on Jul 4, 2013

@author: daniel.dejager
'''
from copy import deepcopy
import sys
from threading import Thread
import wx
import zmq
import re

from lnGUI import MainFrame,ContactEditor

class MyContactManager(ContactEditor):
    def __init__(self, parent):
        super(MyContactManager, self).__init__(parent)

    def setItems(self,a):
        self.contactList.SetItems(a)

    def appendHost(self, event):
        buttonName = event.EventObject.Label
        field = self.contactEmail.GetValue()
        field = field.split("@")[0]
        self.contactEmail.SetValue(field)
        if buttonName == "Gmail":
            self.contactEmail.AppendText("@gmail.com")
        elif buttonName == "Verizon":
            self.contactEmail.AppendText("@vtext.com")
        elif buttonName == "Virgin Mobile":
            self.contactEmail.AppendText("@vmobl.com")


    def discardChanges(self, event):
        event.Skip()
        self.EndModal(-1)

    def saveChanges(self, event):
        event.Skip()
        self.EndModal(0)

    def saveItem(self, event):
        pattern = "{} <{}>"
        selection = self.contactList.GetChecked()
        if len(selection) == 0:
            self.contactList.Insert([pattern.format(self.contactName.GetValue(),self.contactEmail.GetValue())])
        else:
            self.contactList.Delete(selection[0])
            self.contactList.Append(pattern.format(self.contactName.GetValue(), self.contactEmail.GetValue()))

    def editItem(self, event):
        self.contactList.SetChecked([event.Selection])
        import re
        r = re.match("(.*) <(.*)>",event.String)
        self.contactName.SetValue(r.group(1))
        self.contactEmail.SetValue(r.group(2))

    def deleteItem(self, event):
        selection = self.contactList.GetChecked()
        if len(selection) > 0:
            self.contactList.Delete(selection[0])

# Thread class that executes processing
class EventProcessor(Thread):
    """Worker Thread Class."""
    def __init__(self,frame):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._want_abort = 0
        self.frame = frame
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):
        """Run Worker Thread."""
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect("ipc:///tmp/ln-states")
        socket.setsockopt(zmq.SUBSCRIBE,"")
        state = {"Dryer":{"Buzz":0,"Power":0},"Washer":{"Power":0}}
        while self._want_abort == 0:
            message = socket.recv()
           # print "Message Recieved:",message
            if message.startswith("Update State,"):
                val = message.split(",")[1]
                r = re.match("(Dryer|Washer) (Buzz|Power) (On|Off)",val)
                machine = r.group(1)
                option = r.group(2)
                p = 1 if r.group(3) == "On" else 0
                state[machine][option]=p
                self.frame.updateUI(state)


    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = 1



class MyFrame(MainFrame):
    def __init__(self, parent):
        self.parent = parent
        super(MyFrame, self).__init__(parent)
        self.thread = EventProcessor(self)


        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("ipc:///tmp/ln-email")
        self.oldValues = {"Dryer":{"Power":0,"Buzz":0},"Washer":{"Power":0}}

    def invokeContactManager(self, event):
        dia = MyContactManager(self.parent)
        dia.setItems(["me <me@you.com>","you <you@me.com>"])
        if dia.ShowModal() == 0:
            items =  dia.contactList.GetItems()
            self.updateLists(items)

    def closeProgram( self, event ):
        event.Skip()
        self.Destroy()
        self.thread.abort()
        sys.exit(0)


    def updateLists(self,a):
        [list.SetItems(a) for list in self.lists]

    def sendNotification(self, message):
        if message == "Dryer Buzz":
            emails = self.dryerBuzzChecks.GetCheckedStrings()
        elif message == "Dryer Done":
            emails = self.dryerDoneChecks.GetCheckedStrings()
        elif message == "Washer Done":
            emails = self.washerDoneChecks.GetCheckedStrings()
        if emails is not None:
            msg = "{},{}".format(message, ",".join(emails))
            print "Sending Message:",msg
            self.socket.send(msg)

    def sendMessage( self, event ):
        message = event.EventObject.Label
        self.sendNotification(message)

    def updateUI(self,values):
        def getColor(state):
            if state == 1:
                return wx.Colour(0,255,0)
            else:
                return wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)

        self.labelDryerBuzz.SetBackgroundColour(getColor(values["Dryer"]["Buzz"]))
        self.labelDryerPower.SetBackgroundColour(getColor(values["Dryer"]["Power"]))
        self.labelWasherPower.SetBackgroundColour(getColor(values["Washer"]["Power"]))

        if values["Dryer"]["Power"] != 1 and self.oldValues["Dryer"]["Power"] == 1:
            self.sendNotification("Dryer Done")
        if values["Dryer"]["Buzz"] == 1 and self.oldValues["Dryer"]["Buzz"] != 1:
            self.sendNotification("Dryer Buzz")
        if values["Washer"]["Power"] != 1 and self.oldValues["Washer"]["Power"] == 1:
            self.sendNotification("Washer Done")

        self.oldValues = deepcopy(values)


class LaundryNotifier(wx.App):
    def OnInit(self):
        self.f = MyFrame(None)
        self.f.lists = [self.f.washerDoneChecks, self.f.dryerBuzzChecks, self.f.dryerDoneChecks]

        self.SetTopWindow(self.f)
        self.f.Show(True)
        self.f.updateLists(["Mom <teaisfine@gmail.com>","Daniel <2062345008@vtext.com>"])


        return True



if __name__ == "__main__":
    app = LaundryNotifier(None)
    app.MainLoop()
    