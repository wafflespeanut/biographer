import os, sys
from datetime import datetime
from getpass import getpass
from hashlib import sha256
from time import sleep

from story import Story, hasher
from utils import DateIterator

formats = {
    'black': 90, 'red': 91, 'green': 92, 'yellow': 93, 'blue': 94, 'violet': 95, 'skyblue': 96, 'white': 97,
    'null': 0, 'bold': 1, 'italic': 3, 'underline': 4, 'strike': 9 }

def fmt(color = 'null', dark = False):
    format_code = formats[color] - 60 if dark else formats[color]
    return {'win32': ''}.get(sys.platform, '\033[' + str(format_code) + 'm')

def fmt_text(text, formatting, dark = False):
    return '%s%s%s' % (fmt(formatting, dark), text, fmt())

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

error, warning, success = map(lambda s: '\n' + fmt_text(s, 'bold'),
                              (fmt_text('[ERROR]', 'red'),
                               fmt_text('[WARNING]', 'yellow', True),
                               fmt_text('[SUCCESS]', 'green')))
newline = ('\n' if sys.platform == 'darwin' else '')        # since OSX uses '\r' for newlines
capture_wait = (0.1 if sys.platform == 'win32' else 0)
# the 100ms sleep times is the workaround for catching EOFError properly in Windows since they're asynchronous

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
    def __init__(self, is_bare = False):
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
        except KeyboardInterrupt:   # we don't have to worry if the user interrupts anywhere along the way
            pass                # because, the session doesn't have any information, and so the program quits!
        if is_bare:     # for some command-line options which shouldn't require a password (`help` or `configure`)
            return
        if os.access(path, os.W_OK):
            self.configure()

    def reset(self):
        self.location, self.key, self.birthday, self.loop = (None,) * 4

    def delete_config_file(self):
        if os.path.exists(self.config_location):
            print warning, 'Deleting the configuration file...'
            os.remove(self.config_location)
            raw_input('\nPress [Enter] to continue...')

    def get_pass(self, key_hash = None, check_against = None, life_time = 'new'):
        '''A method for getting passwords in three different situations'''
        check_current_pass = True if key_hash else False
        while True:
            if check_current_pass:
                self.key = getpass('\nEnter your current password to continue: ')
                if key_hash:    # If key_hash doesn't exist, then it's a "new password" scenario
                    if hasher(sha256, self.key) == key_hash:
                        if not check_against:
                            break
                        else:   # so that we don't come back during the future password check
                            check_current_pass = False
                    else:
                        print error, 'Wrong password!'
                        continue
            self.key = getpass("\nEnter your '%s' password: " % life_time)
            if check_against and self.key == check_against:
                print error, 'Both passwords are the same!'
                continue
            if len(self.key) < 8:
                print warning, 'Password should be of at least 8 chars!'
                continue
            if getpass('Re-enter the %s password: ' % life_time) == self.key:
                break
            else:
                print error, "Passwords don't match!"

    def find_stories(self, return_on_first_story = True):
        if return_on_first_story:
            for i, date in DateIterator(self.birthday, progress_msg = None):
                if Story(self, date).get_path():
                    return (i is 0, date)
            return False, None
        return [date for _i, date in DateIterator(self.birthday, progress_msg = None) if Story(self, date).get_path()]

    def configure(self):
        '''Configuration for authentication (of course, you have to sign-in for each session!)'''
        try:
            if os.path.exists(self.config_location):
                print '\nConfiguration file found!'
                with open(self.config_location, 'r') as file_data:
                    config = file_data.read().splitlines()
                try:
                    assert len(config) >= 3, "there's not enough information in the configuration file!"
                    key_hash, config_loc, birth = config[:3]
                    self.location = config_loc.rstrip(os.sep) + os.sep
                    assert os.path.exists(self.location), "a diary doesn't exist on the configured location!"
                    try:
                        self.birthday = datetime.strptime(birth, '%Y-%m-%d')
                    except ValueError:
                        raise AssertionError, \
                              "we can't parse the diary's birthday (expected format: YYYY-MM-DD, found %s)" % birth
                    self.get_pass(key_hash)
                    if (datetime.now() - self.birthday).days:   # if you've created your diary more than a day ago...
                        first_story_exists, date = self.find_stories()
                        if first_story_exists:
                            _data = Story(self, birth).decrypt()
                        elif date:
                            print error, "Your first story doesn't exist!", \
                                  date.strftime('However, a story exists on %B %d, %Y (%A)\n')
                            if raw_input('Do you wanna begin from there (y), or reconfigure your diary (n)? ') == 'y':
                                self.birthday = date
                                _data = Story(self, date).decrypt()
                                self.write_to_config_file()
                            else:
                                raise AssertionError, "you asked for it!"
                        else:
                            print error, "You haven't written any stories yet!", \
                                  'Modifying the configuration file to set today as the start...'
                            self.birthday = datetime.now()
                            self.write_to_config_file()
                            raw_input('\nPress [Enter] to continue...')
                    self.loop = True
                except AssertionError as err:
                    reason = err if err.args else "the first story couldn't be decrypted!"
                    print error, "The configuration file is invalid, because %s" % reason
                    self.reconfigure()
            else:
                self.reconfigure()
        except (KeyboardInterrupt, EOFError):
            sleep(capture_wait)
            print '\n', error, 'Failed to authenticate!'
            self.reset()

    def write_to_config_file(self):
        '''
        This is handy whenever we wanna rewrite the configuration file,
        because we could just overwrite the object and call this function
        '''
        msg = 'Configuration file has been updated!' if os.path.exists(self.config_location) and \
                                                        os.path.getsize(self.config_location) \
                                                     else 'Login credentials have been saved locally!'
        with open(self.config_location, 'w') as file_data:
            file_data.write('\n'.join([hasher(sha256, self.key),
                                       self.location,
                                       self.birthday.strftime('%F')]))
        print success, msg

    def reconfigure(self):      # FIXME: Could take arguments via command-line?
        '''Reset the diary's configuration'''
        try:
            self.reset()
            self.delete_config_file()
            clear_screen()
            print "\nLet's start configuring your diary...\n" + \
                  '\nEnter the location for your diary...' + \
                  "\n(Note that this will create a foler named 'Diary' if the path doesn't end with it)"
            self.location = os.path.expanduser(raw_input('\nPath: '))
            while not write_access(self.location):
                self.location = os.path.expanduser(raw_input('\nPlease enter a valid path: '))
            if not self.location.rstrip(os.sep).endswith('Diary'):  # just put everything in a folder for Diary
                self.location = os.path.join(self.location, 'Diary')
                print '(Reminding you that this will make use of %r)' % self.location
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
                        self.birthday, life_time = datetime.now(), 'new'
                    else:
                        self.birthday, life_time = datetime.strptime(birth, '%Y-%m-%d'), 'old'
                        first_story_exists, date = self.find_stories()
                        if first_story_exists:
                            break
                        elif date:
                            print error, "Your 'first' story doesn't exist!", \
                            date.strftime('However, a story exists on %B %d, %Y (%A)\n')
                            if raw_input('Do you wanna begin from there (y), or go for another date (n)? ') == 'y':
                                self.birthday = date
                                break
                            continue
                        else:
                            print error, "The story doesn't exist (in the given path) on that day!"
                            continue
                except ValueError:
                    print error, 'Oops! Error in input. Check the date format and try again...'

            while True:
                self.get_pass(life_time = life_time)
                first_story = Story(self, self.birthday)
                try:
                    if first_story.get_path():
                        _data = first_story.decrypt()
                        break
                    elif (datetime.now() - self.birthday).days:
                        raise ValueError
                    else:   # first-timer...
                        break
                except AssertionError:
                    print error, "Couldn't decrypt your 'first' story with the given password! Try again..."
                except ValueError:
                    print error, 'Unreachable code!'

            self.write_to_config_file()
            self.loop = True
            print "\nIf you plan to reconfigure it manually, then it's located here (%s)" % self.config_location
            print "And, be careful with that, because invalid configuration files will be deleted during startup!"
            raw_input('\nPress [Enter] to continue...')

        except (KeyboardInterrupt, EOFError):
            sleep(capture_wait)
            if not all([self.location, self.key, self.birthday, self.loop]):
                print '\n', error, "Failed to store the login credentials!"
                if os.path.exists(self.config_location):
                    os.remove(self.config_location)
                self.reset()
