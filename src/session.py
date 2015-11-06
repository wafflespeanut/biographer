import os, sys
from datetime import datetime
from getpass import getpass
from hashlib import sha256
from time import sleep

from core import hashed, hash_format

error, warning, success = "\n[ERROR]", "\n[WARNING]", "\n[SUCCESS]"
newline = ('\n' if sys.platform == 'darwin' else '')        # since OSX uses '\r' for newlines
capture_wait = (0.1 if sys.platform == 'win32' else 0)
# the 100ms sleep times is the workaround for catching EOFError properly in Windows since they're asynchronous

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def write_access(path):
    if not os.access(path, os.W_OK):
        if not os.path.exists(path):
            print error, "%s doesn't exist!" % path
        else:
            print error, "Couldn't get write access to %s" % path
        return False
    return True

class Session(object):
    '''
    The 'Session' object has all the information required to carry out the entire session.
    It has the location of the config file, your diary's location, and your password (among other things)
    '''
    def __init__(self):
        self.reset()
        path = os.path.expanduser('~')
        try:    # QPython (Android) uses `/data` as home directory, and so let's try with `/mnt/sdcard`
            warn = False
            if not os.access(path, os.W_OK):
                print error, "Couldn't get write access to home directory! Checking if the device is Android..."
                path = '/mnt/sdcard'
                while not write_access(path):
                    warn = True
                    path = raw_input('\nEnter a path for the config file: ')
            self.config_location = os.path.join(path, '.biographer')
            if warn:
                print warning, "If you get annoyed by this error and don't wanna do this often," \
                               + " then move the config file from %s to your home directory (%s)," \
                               + " or just modify the Session object's path to the directory of your liking" \
                               % (self.config_location, os.path.expanduser('~/.biographer'))
                sleep(3)
                raw_input('\nPress [Enter] to continue...')
        except KeyboardInterrupt:
            pass
        if os.access(path, os.W_OK):
            self.configure()

    def reset(self):
        self.location, self.key, self.birthday, self.loop = [None] * 3 + [False]

    def delete_config(self):
        if os.path.exists(self.config_location):
            print warning, 'Deleting configuration file...'
            os.remove(self.config_location)
            sleep(2)    # wait for the user to see the message (before it gets cleared)

    def get_pass(self, key_hash = None):
        while True:
            if key_hash:    # If key_hash doesn't exist, then it's a "new password" scenario
                self.key = getpass('\nEnter your password to continue: ')
                if key_hash == hashed(sha256, self.key):
                    break
                print error, 'Wrong password!'
            else:
                self.key = getpass('\nEnter your password: ')
                if len(self.key) < 8:
                    print warning, 'Choose a strong password! (at least 8 chars)'
                    continue
                if getpass('Re-enter the password: ') == self.key:
                    break
                else:
                    print error, "Passwords don't match!"

    # Configuration for authentication (well, you have to sign-in for each session!)
    def configure(self):
        try:
            if os.path.exists(self.config_location):
                print '\nConfiguration file found!'
                with open(self.config_location, 'r') as file_data:
                    config = file_data.readlines()
                try:
                    key_hash = config[0].rstrip('\n')
                    self.location = config[1].rstrip(os.sep + '\n') + os.sep
                    assert os.path.exists(self.location)
                    self.birthday = datetime.strptime(config[2].strip(), '%Y-%m-%d')
                    assert os.path.exists(self.location + hash_format(self.birthday))
                    self.get_pass(key_hash)
                    self.loop = True
                except (AssertionError, IndexError, ValueError):
                    clear_screen()
                    print 'Invalid configuration file!'
                    self.reconfigure()
            else:
                self.reconfigure()
        except (KeyboardInterrupt, EOFError):
            sleep(capture_wait)
            print '\n', error, 'Failed to authenticate!'
            self.reset()

    def reconfigure(self):
        self.delete_config()
        clear_screen()
        print "\nLet's start configuring your diary..."

        try:
            print '\nEnter the (absolute) location for your diary...' + \
                  "\n(Note that this will create a foler named 'Diary' if the path doesn't end with it)"
            self.location = os.path.expanduser(raw_input('\nPath: '))
            while not write_access(self.location):
                self.location = os.path.expanduser(raw_input('\nPlease enter a valid path: '))
            if not self.location.rstrip(os.sep).endswith('Diary'):  # just put everything in a folder for Diary
                self.location = os.path.join(self.location, 'Diary')
                print 'Reminding you that this will make use of %r' % self.location
                if not os.path.exists(self.location):
                    os.mkdir(self.location)
            self.location = self.location.rstrip(os.sep) + os.sep

            while True:
                try:    # 'birthday' of the diary is important because random stories and searching is based on that
                    birth = raw_input('''\
                                      \nWhen did you start writing this diary? (Press [Enter] for today)\
                                      \nDate should be of the form YYYY-MM-DD (Mind you, with hyphen!)
                                      \nDate: ''')
                    if not birth:
                        self.birthday = datetime.now()
                        birth = self.birthday.strftime('%Y-%m-%d')
                    else:
                        self.birthday = datetime.strptime(birth, '%Y-%m-%d')
                        if not os.path.exists(self.location + hash_format(self.birthday)):
                            print error, "A story doesn't exist on that day! (in the given path)"
                            continue
                    break
                except ValueError:
                    print error, 'Oops! Error in input. Try again...'

            self.get_pass()
            with open(self.config_location, 'w') as file_data:
                file_data.write('\n'.join([hashed(sha256, self.key), self.location, birth]))
            print success, 'Login credentials have been saved locally!'
            self.loop = True
            print "\nIf you plan to reconfigure it manually, then it's located here (%s)" % self.config_location
            print "And, be careful with that, because invalid configuration files will be deleted during startup!"
            sleep(3)
            raw_input('\nPress [Enter] to continue...')

        except (KeyboardInterrupt, EOFError):
            sleep(capture_wait)
            if not all([self.location, self.key, self.birthday, self.loop]):
                print error, "Failed to store the login credentials!"
                if os.path.exists(self.config_location):
                    os.remove(self.config_location)
                self.reset()
