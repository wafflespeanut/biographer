import os, sys
from datetime import datetime
from hashlib import md5
from string import punctuation
from time import sleep

from cipher import zombify
from utils import simple_counter
import session as sess

def get_date():     # global function for getting date from the user in the absence of datetime object
    while True:
        try:
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

def hasher(hash_function, text):     # global hashing function (may use MD5 or SHA-256)
    hash_object = hash_function()
    hash_object.update(text)
    return hash_object.hexdigest()

class Story(object):
    '''
    The 'Story' object has all the information necessary for invoking a particular story.
    For example, one can get its filename hash, the data contained in it,
    tell whether it should be encrypted or decrypted, whether it's new, etc.
    '''
    def __init__(self, session, when = None, is_write = False):
        try:
            if when == 'today' or when == 'now':
                self.date = datetime.now()
            elif type(when) is str:
                self.date = datetime.strptime(when, '%Y-%m-%d')
            elif type(when) is datetime:
                self.date = when
            else:
                raise ValueError
        except ValueError:
            self.date = get_date()
        # just in case if you plan to write your past days beyond the birthday
        if is_write and self.date < session.birthday:   # you wouldn't want this when you're viewing!
            print sess.warning, "Reconfiguring your diary to include those 'past' days..."
            session.birthday = self.date
            session.write_to_config_file()
            sleep(1)
        self.path = os.path.join(session.location, self.get_hash())
        self.key = session.key      # have a copy of the password so that we don't always have to invoke Session

    def get_hash(self):
        return hasher(md5, self.date.strftime('Day %d (%B %Y)'))

    def get_path(self):     # return the path only if the file exists and it's not empty
        return self.path if os.path.exists(self.path) and os.path.getsize(self.path) else None

    # read_data(), write_data(), encrypt() & decrypt() blindly assumes that the file exists
    # catching for IOErrors every time is rather boring, and so we can utilize get_path() to handle the "absence" case
    def read_data(self):
        with open(self.path, 'rb') as file_data:
            return file_data.read()

    def write_data(self, data, mode = 'wb'):
        with open(self.path, mode) as file:
            file.write(data)

    def encrypt(self, echo = True):
        try:    # exhaustive process, just to check whether a file has already been encrypted
            data = self.decrypt()
            print sess.error, "This file looks has already been encrypted! (filename hash: %s)" % self.get_hash(), \
                              "\nIt's never encouraged to use this algorithm for encryption more than once!"
            return
        except AssertionError:
            file_data = self.read_data()
            data = zombify('e', sess.newline.join(file_data.split('\r')), self.key)  # to strip '\r' from the lines
            self.write_data(data)
            if echo:
                print sess.success, 'Successfully encrypted the file! (filename hash: %s)' % self.get_hash()

    def decrypt(self, overwrite = False):
        data = zombify('d', self.read_data(), self.key)
        assert data         # checking whether decryption has succeeded
        if overwrite:       # we catch the AssertionError later to indicate the wrong password input
            self.write_data(data)
        else:
            return data

    def write(self):
        sess.clear_screen()
        input_loop, keystroke = True, 'Ctrl+C'
        if sys.platform == 'win32':
            print sess.warning, "If you're using the command prompt, don't press %s while writing!" % keystroke
            keystroke = 'Ctrl+Z and [Enter]'
        if self.get_path():
            try:                    # "Intentionally" decrypting the original file
                self.decrypt(overwrite = True)  # an easy workaround to modify your original story
            except AssertionError:
                print sess.error, "Bleh! Couldn't decrypt today's story! Check your password!"
                return
            print '\nStory already exists! Appending to the current story...'
            print '(filename hash: %s)' % self.get_hash()
        data = [datetime.now().strftime('[%Y-%m-%d] %H:%M:%S\n')]
        try:
            stuff = raw_input("\nStart writing... (Once you've written something, press [Enter] to record it \
to the buffer. Further [RETURN] strokes indicate paragraphs. Press {} when you're done!)\n\n\t".format(keystroke))
            data.append(stuff)
        except (KeyboardInterrupt, EOFError):
            sleep(sess.capture_wait)
            print "\nAlright, let's save it for a later time then! Quitting..."
            input_loop = False
            if self.get_path():
                data = []
            else:   # If the file doesn't exist (i.e., a new story), then add a reminder for the user
                data.append('--- You were about to write something at this time? ---')
        while input_loop:
            try:
                stuff = raw_input('\t')     # auto-tabbing of paragraphs (for each [RETURN])
                data.append(stuff)
            except (KeyboardInterrupt, EOFError):
                sleep(sess.capture_wait)
                break
        if data:
            self.write_data('\n\t'.join(data) + '\n\n', 'a')
        self.encrypt(echo = False)
        if input_loop and raw_input(sess.success + ' Successfully written to file! Do you wanna see it (y/n)? ') == 'y':
            self.view()

    def view(self, return_text = False):
        date_format = '\nYour story from %s ...\n' % (self.date.strftime('%B %d, %Y (%A)'))
        try:
            if self.get_path():
                data = self.decrypt()
            else:
                print sess.error, "Story doesn't exist on the given day! (%s)" % self.date.date()
        except AssertionError:
            print sess.error, "Baaah! Couldn't decrypt the story!"
            return
        sess.clear_screen()
        count = simple_counter(data)
        start = "%s\n<----- START OF STORY -----> (%d words)\n\n" % \
                (sess.format_text(sess.format_text(date_format, 'violet'), 'bold'), count)
        end = "<----- END OF STORY ----->"
        if return_text:
            return (data, start, end)
        print start, data, end
