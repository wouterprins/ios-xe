#!/usr/bin/python
import sys
import argparse
from netmiko import ConnectHandler

ar = {
    'device_type': 'cisco_ios',
    'ip':   '<ip>',
    'username': '<username>',
    'password': 'password>',
    'port' : 22,          # optional, defaults to 22
    'secret': 'secret',     # optional, defaults to ''
    'verbose': False,       # optional, defaults to False
}

try:
     parser = argparse.ArgumentParser()
     parser.add_argument("username", help="display information for this username")
     parser.add_argument("route", help="route that belongs to the username")
     args = parser.parse_args()

except:
    e = sys.exc_info()[0]
    sys.exit()

net_connect = ConnectHandler(**ar)
userinfo = net_connect.send_command('show users | incl ' + args.username)
routeinfo = net_connect.send_command('show ip route ' + args.route + ' | incl /32')
totalusers = net_connect.send_command('show users summary  | incl total')
totaluserspppoa = net_connect.send_command('show users summary  | incl PPPOA')

#totalpppoe = net_connect.send_command('show pppoe session')

## userinfo
userinfo=userinfo.split()
#convert to strings
userinfo=[str(userinfo[x]) for x in range(len(userinfo))]

## total users
totalusers=totalusers.split()
#convert to strings
totalusers=[str(totalusers[x]) for x in range(len(totalusers))]

totaluserspppoa=totaluserspppoa.split()
#convert to strings
totaluserspppoa=[str(totaluserspppoa[x]) for x in range(len(totaluserspppoa))]
pppoeusers=int(totalusers[0])-int(totaluserspppoa[1])

#check if the user is either PPPoA or PPPoE
if userinfo[4] == args.route:
        print "User %s is connected for %s by using %s and has ip address: %s(%s)" % (userinfo[1],userinfo[3],userinfo[2],userinfo[4],userinfo[0])
        print "PPPoA users: %s" % totaluserspppoa[1]
        print "PPPoE users: %d" % pppoeusers
        print "Total users: %s" % totalusers[0]
else:

#/32 route check
        if routeinfo == "":             
                print "no route is present from Y"
        else:
                print "route is present from X"

## Detailed PPPoE user output - to be done

## total users
#totalpppoe=totalpppoe.split()
#convert to strings
#totalpppoe=[str(totalpppoe[x]) for x in range(len(totalpppoe))]

#if userinfo[2] == "PPPoE":
# print totalpppoe[2]
