#!/usr/bin/python
import sys
import argparse
from netmiko import ConnectHandler
from netaddr import *

ar = {
    'device_type': 'cisco_ios',
    'ip':   '192.168.255.238',
    'username': 'rancid',
    'password': 'r4nc1d',
    'port' : 22,          # optional, defaults to 22
    'secret': 'secret',     # optional, defaults to ''
    'verbose': False,       # optional, defaults to False
}

try:
     parser = argparse.ArgumentParser()
     parser.add_argument("username", help="display information for this username")
     parser.add_argument("route", help="route that belongs to the username")
     args = parser.parse_args()
     #strip everything behind @ from username (no match for username in local router)
     args.username=args.username.split('@')[0]

except:
    e = sys.exc_info()[0]
    sys.exit()

net_connect = ConnectHandler(**ar)
userinfo = net_connect.send_command('show users | incl ' + args.username)
routeinfo = net_connect.send_command('show ip route ' + args.route + ' | incl /32')
totalusers = net_connect.send_command('show users summary  | incl total')
totaluserspppoa = net_connect.send_command('show users summary  | incl PPPOA')

# determine if the username can be found in the show output:
#print userinfo.find(args.username) == -1 and routeinfo.find(args.route) == -1 #username and route not present
#print userinfo.find(args.username) == -1 and routeinfo.find(args.route) != -1 #username is not found, route is present
#print userinfo.find(args.username) != -1 and routeinfo.find(args.route) != -1 #username present and route present

# total users
totalusers=totalusers.split()
#convert to strings
totalusers=[str(totalusers[x]) for x in range(len(totalusers))]
totaluserspppoa=totaluserspppoa.split()
#convert to strings
totaluserspppoa=[str(totaluserspppoa[x]) for x in range(len(totaluserspppoa))]
pppoeusers=int(totalusers[0])-int(totaluserspppoa[1])


if (userinfo.find(args.username) == -1 and routeinfo.find(args.route) == -1):
        print "username and route not present... user is offline \r\n"
        sys.exit()
elif (userinfo.find(args.username) == -1 and routeinfo.find(args.route) != -1):
        #username is not found, route is present
        routeinfo=routeinfo.split()
        #convert to strings
        routeinfo=[str(routeinfo[x]) for x in range(len(routeinfo))]
        print routeinfo[3] + ' is active from Nextpertise' + '\r\n'
elif (userinfo.find(args.username) != -1 and routeinfo.find(args.route) != -1):
        #username present and route present
        userinfo=userinfo.split()
        #convert to strings
        userinfo=[str(userinfo[x]) for x in range(len(userinfo))]
        print "User %s is connected for %s by using %s and has ip address: %s(%s)\r\n" % (userinfo[1],userinfo[3],userinfo[2],userinfo[4],userinfo[0])

        # get detailed info from either PPPoE or PPPoA
        if userinfo[2]=="PPPoE":
                pppoeclient=net_connect.send_command('show pppoe session | incl ' + userinfo[0])
                pppoeclient=pppoeclient.split()
                #convert to strings
                pppoeclient=[str(pppoeclient[x]) for x in range(len(pppoeclient))]
                mac=EUI(pppoeclient[2])
                oui = mac.oui
                ouiorg=str(oui.registration().org)
                print 'Customer MAC address is: ' + str(mac) + ' Vendor-ID: ' + ouiorg + '\r\n'
                print 'Customer session is present on interface: ' + pppoeclient[3] + '\r\n'
                print 'Total # of PPPoE sessions is: %d ' % pppoeusers + '\r\n'
                print "Total # of PPP users: %s \r\n" % totalusers[0]
        else:
                #Fetch the ATM PVC number
                atmclient=net_connect.send_command('show interfaces ' + userinfo[0] + ' | incl Bound')
                atmpvc=atmclient.split()
                #convert to strings
                atmpvc=[str(atmpvc[x]) for x in range(len(atmpvc))]
                #fetch more info
                atmclient2=net_connect.send_command('show atm pvc interface ' + atmpvc[2] + ' | incl 2/0')
                atmpvc2=atmclient2.split()
                atmpvc2=[str(atmpvc2[x]) for x in range(len(atmpvc2))]
                print 'Interface is: ' + atmpvc2[0] + ' VPI: ' + atmpvc2[2] + ' VCI: ' + atmpvc2[3] + ' PeakRate: ' + atmpvc2[7] + 'Kbps Status: ' + atmpvc2[8] + '\r\n'
                atmping=net_connect.send_command('ping atm interface atm' + atmpvc2[0] + ' ' + atmpvc2[2] + ' ' + atmpvc2[3] + ' end')
                print 'Results of ATM ping: %s' % atmping + '\r\n'
                print "Total # of PPPoA users: %s \r\n" % totaluserspppoa[1]
                print "Total # of PPP users: %s \r\n" % totalusers[0]

