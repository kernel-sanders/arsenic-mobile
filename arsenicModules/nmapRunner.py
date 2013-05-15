# Copyright (c) 2013 KernelSanders
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA


import os
import threading
import subprocess, shlex
import signal
import time
import re

GATEWAY = ''
IFACE = ''
MYIP = ''

'''
Return the default gateway's IP and the interface name used to connect to it as a tuple.
This function works with both Linux and OSX versions of netstat to retrieve the information.
'''
def setDefaultGatewayAndInterface():
    global GATEWAY, IFACE
    if GATEWAY == '' or IFACE == '':
        file=os.popen("netstat -nr")
        data=file.read()
        file.close()
        lines=data.strip().split('\n')
        entriesList = []
        osx = False
        for line in lines:
            if line[:7] == 'default' or line[:7] == '0.0.0.0':
                if line[:7] == 'default': 
                    osx = True
                for entries in line.split(' '):
                    if entries != '':
                        entriesList.append(entries)
        try:
            GATEWAY = entriesList[1]
        except:
            print 'No network detected'
            os.system('killall python')
            os._exit(1)
            
        if osx:
            IFACE = entriesList[5]
            return entriesList[1], entriesList[5]
        else:
            IFACE = entriesList[7]
            return entriesList[1], entriesList[7]
    else:
        return GATEWAY, IFACE

'''
Return our own IP. This allows us to exclude it from the scan so we don't accidentally
ARP spoof ourselves. 
'''
def getOwnIP():
    global MYIP
    if MYIP == '':
        f = os.popen("ifconfig en0")
        data = f.read()
        f.close()
        IPs = re.findall(r"""inet\s[0-9]+(?:\.[0-9]+){3}""", data)
        if len(IPs) < 1:
            print 'No network detected'
            os._exit(1)
        MYIP = IPs[0][5:]
        return IPs[0][5:]
    else:
        return MYIP

#=====================================================================================
'''
The code below works on iOS 5, but for some reason nmap throws a segfault on iOS 6.
Therefore the pig module is used to conduct all scans. The following code is left in
for those interested, but is unused.
'''


'''
Using the default gateway's ip, create the IP arg for nmap. Currently only supports /24
which is subnet 255.255.255.0. Subnet detection and better nmap arg creation is a possible
area of improvement. For now, if you know you are on a different subnet, manually change the /24
the correct / notation.
'''
def setArgForNmap(router):
    parts = router.split('.')
    arg = parts[0]+'.'+parts[1]+'.'+parts[2]+'.0/24'
    return arg

'''
This class runs the nmap scan. It currently runs a simple ping scan (-sP), and parses the results
into a list of IPs that is returned when the returnHosts() is called.
'''
class nmap(threading.Thread):
    def __init__(self, subnet):
        self.subnet = subnet
        self.scanning = True
        self.returnList = []
        self._stop = threading.Event()
        super(nmap,self).__init__()

    def run(self):
        self.p1 = subprocess.Popen(shlex.split('nmap -sP ' + self.subnet + ' --system-dns'), stdout=subprocess.PIPE)
        me = getOwnIP()
        router, iface = setDefaultGatewayAndInterface()
        while self.scanning:
            out = self.p1.stdout.readline()
            if len(out) > 0:
                if 'Nmap done' in out:
                    self.stop()
                elif 'up' in out:
                    ip = re.findall( r'[0-9]+(?:\.[0-9]+){3}', out )[0]
                    if ip != me and ip != router:
                        self.returnList.append(ip)

    def returnHosts(self):
        return self.returnList

    def stop(self):
        self._stop.set()
        self.scanning = False
        os.kill(self.p1.pid,signal.SIGKILL)
        # super(nmap,self).join(None)

    def stopped(self):
        return self._stop.isSet()

'''
Set up the nmap scan, run it, and return the parsed list of hosts. 
(kill it after 30 seconds no matter what)
'''
def getHosts():
    router, iface = setDefaultGatewayAndInterface()
    subnet = setArgForNmap(router)
    myNmap = nmap(subnet)
    myNmap.start()
    startTime = time.time()
    while not myNmap.stopped() and time.time() - startTime < 30:
        time.sleep(.2)
    myNmap.stop()
    myNmap.join()
    hosts = myNmap.returnHosts()
    return hosts



