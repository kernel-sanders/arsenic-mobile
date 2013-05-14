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
'''
This simple class fires off sslstip on port 8080, logging only https POSTs. Although --killsessions
is on, and sslstrip does send expired cookies to previously unseen domains, this doesn't seem to work
properly. More testing is needed to determine if the issue is how sslstrip is implemented or if it 
is a problem with ssltrip itself.
'''
class sslStrip(threading.Thread):
    def __init__(self):
        self.p1 = '' # have to declare instance variables in __init()__
        super(sslStrip,self).__init__()

    def run(self):
        self.p1 = subprocess.Popen(shlex.split('sslstrip -f -k -l 8080'), preexec_fn=os.setsid) # sslstrip from http://www.thoughtcrime.org/software/sslstrip/

    def stop(self):
        os.kill(self.p1.pid, signal.SIGTERM) 
        self.p1.terminate()
        super(sslStrip,self).join(None)
        #os.kill(self.p1.pid,signal.SIGKILL)
