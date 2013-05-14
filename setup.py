import os

def main():
    if not os.path.isdir('/var/root/arsenic-mobile/Dependencies'):
        print 'The required dependencies folder is not present'
        print "Ensure you scp'd arsenic-mobile to /var/root"
        os._exit(1)
    else:
        print 'Installing GCC...',
        os.chdir('/var/root/arsenic-mobile/Dependencies/GCC')
        os.system('dpkg -i uuid_1.6.0-2p_iphoneos-arm.deb')
        os.system('dpkg -i csu_232-2_iphoneos-arm.deb') 
        os.system('dpkg -i libgcc_4.2-20080410-1-6_iphoneos-arm.deb') 
        os.system('dpkg -i odcctools_286-8_iphoneos-arm.deb') 
        os.system('dpkg -i iphone-gcc_4.2-20080604-1-8_iphoneos-arm.deb') 
        os.system('dpkg -i ldid_610-5_iphoneos-arm.deb')
        os.system('dpkg -i com.sull.iphone-gccheaders_1.0-11_iphoneos-arm.deb') 
        print 'Done'
        os.chdir('/var/root/arsenic-mobile/Dependencies')
        print 'Installing dsniff (arpspoof) and network-cmds...',
        os.system('dpkg -i org.mulliner.dsniff_2.4b1_iphoneos-arm.deb') 
        os.system('dpkg -i network-cmds_307.0.1-6rev1_iphoneos-arm.deb') 
        print 'Done'
        print 'Installing MobileTerminal...',
        os.system('dpkg -i coreutils_8.12-12p_iphoneos-arm.deb') 
        os.system('dpkg -i MobileTerminal_520-2_iphoneos-arm.deb')
        print 'Done'
        print 'Installing the custom python Makefile...' 
        os.system('mv Makefile /usr/lib/python2.7/config')
        print 'Done'
        print 'Installing zope.interface...',
        os.chdir('/var/root/arsenic-mobile/Dependencies/zope.interface-4.0.5')
        os.system('python setup.py install')
        print 'Done'
        print 'Installing Twisted-Web...',
        os.chdir('/var/root/arsenic-mobile/Dependencies/Twisted-13.0.0')
        os.system('python setup.py install')
        print 'Done'
        print 'Installing pyOpenSSL...'
        os.chdir('/var/root/arsenic-mobile/Dependencies/pyOpenSSL-0.11')
        os.system('python setup.py install')
        print 'Done'
        print 'Installing sslstrip...'
        os.chdir('/var/root/arsenic-mobile/Dependencies/sslstrip')
        os.system('python setup.py install')
        print 'Done'
        # Remove previous versions
        if os.path.isfile('/usr/bin/arsenic'):
            os.system('rm /usr/bin/arsenic')
        if os.path.isdir('/usr/bin/arsenicModules'):
            os.system('rm -r /usr/bin/arsenicModules')
        print 'Making arsenic executable... ',
        os.chdir('/var/root/arsenic-mobile')
        os.system('chmod a+x arsenic')
        print 'Done'
        print 'Moving files... ',
        if not os.path.isfile('/etc/pf.os'):
            os.system('mv ' + os.getcwd() + '/arsenicModules/pf.os' + ' /etc/')
        os.system('mv arsenic /usr/bin/')
        os.system('mv arsenicModules /usr/bin')
        print 'Done'
        # print 'Cleaning up...',
        # os.system('rm setup.py')
        # print 'Done'
        print 'arsenic-mobile installed. Enjoy!'




if __name__ == '__main__':
    main()
