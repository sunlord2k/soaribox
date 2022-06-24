#!/usr/bin/env python
from configparser import ConfigParser
from tkinter import *
from tkinter.ttk import *
import os


def startmenu(*args):
    def donothing():
        print("Do nothing")

    def mainmenu(self):
        menubar = Menu(self)
        main1 = Menu(menubar, tearoff=0)
        main2 = Menu(menubar, tearoff=0)
        self.config(menu=menubar)
        menubar.add_cascade(label=config_menu['main1']['name1'], menu=main1)
        main1.add_command(label=config_menu['main1']['sub11'], command=sub11)
        main1.add_command(label=config_menu['main1']['sub12'], command=sub12)
        main1.add_command(label=config_menu['main1']['sub13'], command=sub13)
        menubar.add_cascade(label=config_menu['main2']['name2'], menu=main2)
        main2.add_command(label=config_menu['main2']['sub21'], command=sub21)
        main2.add_command(label=config_menu['main2']['sub22'], command=sub22)
        main2.add_command(label=config_menu['main2']['sub23'], command=sub23)

    # Exit to Code Xcsoar Menu
    def sub11():
        Master.destroy()

    # Exit to Shell Menu Code:
    def sub12():
        Master.destroy()

    # KILLEMALL Code:
    def sub13():
        donothing

    global cardconfig

    # CardConfig Code:
    def sub21():

        def setcard(*args):
            card1 = opttext1.get()
            card2 = opttext2.get()
            card3 = opttext3.get()
            card4 = opttext4.get()
            card5 = opttext5.get()
            config_file['SLOTCARDS']['card1'] = card1
            config_file['SLOTCARDS']['card2'] = card2
            config_file['SLOTCARDS']['card3'] = card3
            config_file['SLOTCARDS']['card4'] = card4
            config_file['SLOTCARDS']['card5'] = card5
            with open('config.ini', 'w') as configfile:
                config_file.write(configfile)

    # General Page layout
        cardconfig = Toplevel()
        cardconfig.geometry('800x400')
        cardconfig.title("Slot-Card-Configuration")
        Abstand = 10
        menu = mainmenu(cardconfig)
    # Button section
        closebutton = Button(cardconfig, text="Close Cardconfig", command=cardconfig.destroy)
        closebutton.grid(row=6, column=5, pady=5)
        savebutton = Button(cardconfig, text="Save Cardconfig", command=setcard)
        savebutton.grid(row=7, column=5, pady=5)
    # Frame section
        frame = Frame(master=cardconfig, relief=RAISED, borderwidth=3)
        frame.grid(row=3, column=1)
    # Text section
        L1 = Label(cardconfig, text="Slot 1:   ")
        L1.grid(row=1, column=2, pady=Abstand)
        L2 = Label(cardconfig, text="Slot 2:   ")
        L2.grid(row=2, column=2, pady=Abstand)
        L3 = Label(cardconfig, text="Slot 3:   ")
        L3.grid(row=3, column=2, pady=Abstand)
        L4 = Label(cardconfig, text="Slot 4:   ")
        L4.grid(row=4, column=2, pady=Abstand)
        L5 = Label(cardconfig, text="Slot 5:   ")
        L5.grid(row=5, column=2, pady=Abstand)
        clear1 = Label(cardconfig, text="                   ")
        clear2 = Label(cardconfig, text="                   ")
        clear1.grid(row=1, column=1, pady=Abstand)
        clear2.grid(row=1, column=4, pady=Abstand)
    # Start of Dropdown Section
        options = config_file.get('SLOTCARDS', 'variants').split('\n')
        opttext1 = StringVar(cardconfig)
        opttext1.set(config_file['SLOTCARDS']['card1'])
        opt1 = OptionMenu(cardconfig, opttext1, *options)
        opt1.grid(row=1, column=3, pady=Abstand)
        opttext2 = StringVar(cardconfig)
        opttext2.set(config_file['SLOTCARDS']['card2'])
        opt2 = OptionMenu(cardconfig, opttext2, *options)
        opt2.grid(row=2, column=3, pady=Abstand)
        opttext3 = StringVar(cardconfig)
        opttext3.set(config_file['SLOTCARDS']['card3'])
        opt3 = OptionMenu(cardconfig, opttext3, *options)
        opt3.grid(row=3, column=3, pady=Abstand)
        opttext4 = StringVar(cardconfig)
        opttext4.set(config_file['SLOTCARDS']['card4'])
        opt4 = OptionMenu(cardconfig, opttext4, *options)
        opt4.grid(row=4, column=3, pady=Abstand)
        opttext5 = StringVar(cardconfig)
        opttext5.set(config_file['SLOTCARDS']['card5'])
        opt5 = OptionMenu(cardconfig, opttext5, *options)
        opt5.grid(row=5, column=3, pady=Abstand)
        cardconfig.mainloop()

    def sub22():
        donothing

    def sub23():
        donothing

    def countdown(count):
        CounterLabel['text'] = count
    #    interruptcountdown = IntVar()
        if interruptcountdown.get() < 1:
            if count > 0:
                Master.after(1000, countdown, count-1)
                bar['value'] = (5-count)*20
            else:
                Master.destroy()
                return 1

    def setinterrupt(*args):
        interruptcountdown.set(1)

    Master = Tk()
    Master.geometry('800x400')
    Master.title("SoariBox Configuration")
    L1 = Label(Master, text="XcSoar will be started in:")
    L1.pack(anchor='center')
    start = mainmenu(Master)
    CounterLabel = Label(Master)
    CounterLabel.pack(anchor='center')
    L2 = Label(Master, text="Press Enter to enter Setup Menu")
    L2.pack(anchor='center')
    interruptcountdown = IntVar()
    interruptcountdown.set(0)
    bar = Progressbar(Master, length=300)
    bar['value'] = 0
    bar.pack()
    countdown(5)
    Master.bind("<Return>", setinterrupt)
    Master.mainloop()


def loadconfig(*args):
    global configfile
    config_file = ConfigParser()
    config_file.read("config.ini")
    global config_menu
    config_menu = ConfigParser()
    config_menu.read("menu.ini")


# Confif File preparation
if __name__ == '__main__':
    loadconfig()
    startmenu()
