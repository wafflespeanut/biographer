import os
from datetime import datetime
from hashlib import md5

from cipher import zombify
import session as sess

def get_date():     # global function for getting date from the user in the absence of datetime object
    while True:
        try:
            if not all([year, month, day]):
                year = int(raw_input('\nYear: '))
                month = int(raw_input('\nMonth: '))
                day = int(raw_input('\nDay: '))
            if datetime(year, month, day) > datetime.now():
                print sess.error, "Bah! You can't just time-travel into the future!"
                year, month, day = [None] * 3
                continue
            return datetime(year, month, day)
        except ValueError:
            print sess.error, 'Invalid input! Cannot parse the given date!'
            year, month, day = [None] * 3

def hashed(hash_function, text):     # global hashing function (may use MD5 or SHA-256)
    hash_object = hash_function()
    hash_object.update(text)
    return hash_object.hexdigest()

class Story(object):
    '''
    The 'Story' object has all the information necessary for invoking a particular story.
    For example, one can get its filename hash, the data contained in it,
    tell whether it should be encrypted or decrypted, whether it's new, etc.
    '''
    def __init__(self, session, when = None):
        if when == 'today' or when == 'now':
            self.date = datetime.now()
        elif type(when) is str:
            self.date = datetime.strptime(when, '%Y-%m-%d')
        else:
            self.date = get_date()
        self.path = os.path.join(session.location, self.get_hash())
        self.key = session.key

    def get_hash(self):
        return hashed(md5, 'Day {date:%d} ({date:%B} {date:%Y})'.format(date = self.date))

    def get_path(self):
        date_format = '{date:%B} {date:%d}, {date:%Y} ({date:%A})'.format(date = self.date)
        return (self.path if os.path.exists(self.path) else None, date_format)

    def read_data(self):
        with open(self.path, 'rb') as file_data:
            return file_data.read()

    def write_data(self, data):
        with open(self.path, 'wb') as file:
            file.write(data)

    def encrypt(self):
        file_data = self.read_data()
        data = zombify(mode, sess.newline.join(file_data.split('\r')), self.key)  # to strip '\r' from the lines
        self.write_data(data)

    def decrypt(self, overwrite = False):
        data = zombify(mode, self.read_data(), self.key)
        assert data         # checking whether decryption has succeeded
        if overwrite:
            self.write_data(data)
        else:
            return data

    def write(self):
        sess.clear_screen()
        keystroke = 'Ctrl+C'
        if sys.platform == 'win32':
            print sess.warning, "If you're using the command prompt, don't press %s while writing!" % keystroke
            keystroke = 'Ctrl+Z and [Enter]'
        file_path, date_format = self.get_path()
        if file_path and os.path.getsize(file_path):
            try:
                self.decrypt(True)
            except AssertionError:
                print "Bleh! Couldn't decrypt the story!"
                return
        else:
            print '\nStory already exists! Appending to the current story...'
            print '(filename hash: %s)' % self.get_hash()
