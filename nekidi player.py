#this code require a virtual keyboard (piano) to work
#You can use 'loopMidi' and create a port name of your choose

import mido
import mido.backends.rtmidi

import json
import os
import math
import time
import threading

import tkinter as tk
from tkinter import ttk

from tkinter import filedialog

class myApp():

    def __init__(self):
        self.portOutputList = mido.get_output_names()

        self.window = tk.Tk()
        self.window.title("Nekidi Player v1.0")
        self.window.geometry("555x400")
        self.window.resizable(False,False)
        self.window.iconbitmap("icon.ico")



        self.select_file_text = tk.StringVar()
        self.select_file_text.set("waiting for..")

        self.song_timestamp = tk.StringVar()
        self.song_timestamp.set("Timestamp: 00:00/00:00") 
        
        self.progressVar = tk.StringVar()
        self.progressVar.set(0) 
          
        
        self.stopThread = False
        self.songTime = "00:00"
        self.songLength = "00:00"
        self.startTime = time.time()
        self.playingMidi = False


        #Frame A
        self.frameA = tk.Frame(self.window,padx=2,pady=2)
        self.frameA.grid(column=0,row=0, sticky=tk.W)

        tk.Label(self.frameA, text="File").grid(row=0, column=0, padx=2, sticky=tk.W)
        
        self.fillEntry = tk.Entry(self.frameA,width=38,state="readonly", textvariable=self.select_file_text)
        self.fillEntry.grid(row=0, column=1,sticky=tk.W)
        
        tk.Button(self.frameA, text="...",width=3, command=self.askMidFile).grid(row=0, column=2,sticky=tk.W)


        #Frame B
        self.frameB = tk.Frame(self.window,padx=8,pady=2)
        self.frameB.grid(column=1,row=0,sticky=tk.E)
        
        tk.Label(self.frameB, text="MIDI Out").grid(row=0, column=0, padx=2,sticky=tk.W)


        self.lastPortList = self.portOutputList
        self.selectedPort = tk.StringVar()
        self.selectedPort.set(self.portOutputList[0])
        self.portList = ttk.Combobox(self.frameB, textvariable=self.selectedPort, width=28)
        self.portList.configure(state="readonly",values=self.portOutputList)
        self.portList.grid(column=1,row=0,sticky=tk.W)

        self.sendToPort = mido.open_output(self.selectedPort.get())
        self.portList.bind('<<ComboboxSelected>>', self.setNewPort)

 
        #Frame C
        self.frameC = tk.Frame(self.window,padx=2,pady=25)
        self.frameC.grid(column=1,row=1,sticky=tk.N)

        self.timestampLabel = tk.Label(self.frameC, textvariable=self.song_timestamp).grid(row=0, column=0, padx=2, sticky=tk.W)

        self.timeProgress = ttk.Progressbar(self.frameC,orient='horizontal',mode='determinate', value=0,variable=self.progressVar, maximum=100,length=250)
        self.timeProgress.grid(row=1,column=0)

        self.play = tk.Button(self.frameC, text="Send midi", command=self.playThreadMidi)
        self.play.grid(row=2,column=0)
        self.play.configure(width=10,state=tk.DISABLED)

        self.stop = tk.Button(self.frameC, text="Stop midi", command=self.stopMidi)
        self.stop.grid(row=3,column=0)
        self.stop.configure(width=10,state=tk.DISABLED)


        #Frame D
        self.frameD = tk.Frame(self.window,padx=2,pady=2,width=15)
        self.frameD.grid(row=1,column=0,sticky=tk.W)

        tk.Label(self.frameD, text="Instrument list").grid(row=0, column=0, padx=2, sticky=tk.W)

        self.instrumentList = ttk.Treeview(self.frameD, column=("c1", "c2"), show='headings', height=16)
        self.instrumentList.column("# 1", anchor=tk.CENTER, width=80)
        self.instrumentList.heading("# 1", text="Channels")
        self.instrumentList.column("# 2", anchor=tk.CENTER, width=210)
        self.instrumentList.heading("# 2", text="Instruments")
        self.instrumentList.grid(row=1, column=0)


        self.updateInfo()
        self.window.protocol("WM_DELETE_WINDOW",self.closeWindow)

        self.window.mainloop()


    def stopMidi(self):
        if hasattr(self, 'playThread') and self.playThread.is_alive():
            self.stopThread = True

    def closeWindow(self):
        self.stopMidi()
        self.window.quit()

    def playThreadMidi(self):
        if hasattr(self, 'playThread') and self.playThread.is_alive():
            self.stopMidi()
        else:
            self.playThread = threading.Thread(target=self.playMidi)
            self.playThread.start()


    def secToReadableTime(self,time):
        minutes = math.floor(time / 60)
        seconds = math.floor(time) % 60
        return "{:02}".format(minutes) + ":" + "{:02}".format(seconds)


    def readInformation(self):
        self.songLength = self.secToReadableTime(self.newMid.length)
        self.songTime = self.secToReadableTime(0)
        
        self.timeProgress.configure(value=0,maximum=self.newMid.length)


        for i in self.instrumentList.get_children():
            self.instrumentList.delete(i)
            
        everyInstrument = []
        for track in self.newMid.tracks:
            for msg in track:
                if msg.type == "program_change":
                    #print("Channel:", msg.channel+1, "Instrument:", instrument_list[msg.program])

                    forceInstrument = instrument_list[msg.program]
                    if msg.channel+1 == 10:
                        forceInstrument = "Drums"

                    if not self.instrumentList.exists(msg.channel+1):
                        self.instrumentList.insert(parent='', index=msg.channel+1, iid=msg.channel+1, text=forceInstrument, values=(msg.channel+1, forceInstrument))

                        self.window.update()


    def playMidi(self):
        self.startTime = time.time()
        self.play.configure(state=tk.DISABLED)
        self.stop.configure(state=tk.NORMAL)
        self.playingMidi = True

        for msg in self.newMid.play():
            if self.stopThread:
                break

            self.sendToPort.send(msg)


        self.stopThread = False
        self.playingMidi = False
        self.play.configure(state=tk.NORMAL)
        self.stop.configure(state=tk.DISABLED)



    def askMidFile(self):
        self.file_path = filedialog.askopenfilename(initialdir="midi/",filetypes=[("MIDI Files", "*.mid")])

        if self.file_path:
            self.stopMidi()

            self.play.configure(state=tk.DISABLED)
            self.newMid = mido.MidiFile(self.file_path)

            self.croppedPath = self.file_path.split("/")[-2] + "/" + self.file_path.split("/")[-1]
            self.select_file_text.set(self.croppedPath)
            
            self.fillEntry.xview(tk.END)

            self.readInformation()
            self.play.configure(state=tk.NORMAL)
            self.stop.configure(state=tk.DISABLED)


    def setNewPort(self,event):
        #if hasattr(self, 'sendToPort') and self.sendToPort:
        
        self.sendToPort.close()
        self.sendToPort = mido.open_output(self.selectedPort.get())
        #print("New port was setup: " + self.selectedPort.get())


    def updateInfo(self):
        if self.playingMidi == False:
            self.startTime = time.time()

        #self.portOutputList = mido.get_output_names()

        self.songTime = self.secToReadableTime(time.time() - self.startTime)
        self.song_timestamp.set("Timestamp: " + self.songTime + "/" + self.songLength)
        self.progressVar.set(time.time() - self.startTime)

        #if self.lastPortList != self.portOutputList:
        #    self.portList.set(self.portOutputList)
        #    self.lastPortList = self.portOutputList

        self.window.after(1000, self.updateInfo)



if __name__ == "__main__":
    with open('midi_instrument.json', 'r') as json_file:
        instrument_list = json.load(json_file)

    myApp()