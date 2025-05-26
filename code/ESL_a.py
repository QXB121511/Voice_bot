from ESL import *

con = ESLconnection("192.168.109.91","15080","ClueCon")

if con.connected:
    con.events("plain", "all")
    while True:
        e = con.recvEvent()
        if e:
            print(e.serialize())