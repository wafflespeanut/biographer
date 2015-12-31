import os, sys
from datetime import datetime, timedelta
from hashlib import md5
from string import punctuation
from time import sleep

from cipher import zombify
from utils import simple_counter
import session as sess

REMINDER = '----- You were about to write something at this time? -----'

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
            if type(when) is datetime:
                self._date = when
            elif when == 'today' or when == 'now':
                self._date = datetime.now()
            elif when == 'yesterday':
                self._date = datetime.now() - timedelta(1)
            elif type(when) is str:     # this should be at the bottom
                self._date = datetime.strptime(when, '%Y-%m-%d')
            else:
                raise ValueError
        except ValueError:
            self._date = get_date()
        # just in case if you plan to write your past days beyond the birthday
        if is_write and self._date < session.birthday:   # you wouldn't want this when you're viewing!
            print sess.warning, "Reconfiguring your diary to include those 'past' days..."
            session.birthday = self._date
            session.write_to_config_file()
            sleep(1)
        self._path = os.path.join(session.location, self.get_hash())
        self._key = session.key     # have a copy of the password so that we don't always have to invoke Session

    def get_hash(self):
        return hasher(md5, self._date.strftime('Day %d (%B %Y)'))

    def get_path(self):     # return the path only if the file exists and it's not empty
        return self._path if os.path.exists(self._path) and os.path.getsize(self._path) else None

    # read_data(), write_data(), encrypt() & decrypt() blindly assumes that the file exists
    # catching IOErrors every time is rather boring, and so we can utilize get_path() to handle the "absence" case
    def read_data(self):
        with open(self._path, 'rb') as file_data:
            return file_data.read()

    def write_data(self, data, mode = 'wb'):
        with open(self._path, mode) as file_data:
            file_data.write(data)

    def encrypt(self, echo = True):
        try:    # just to check whether a file has already been encrypted (not much overhead for a single file)
            data = self.decrypt()
            print sess.error, "This file looks has already been encrypted! (filename hash: %s)" % self.get_hash(), \
                              "\nIt's never encouraged to use this algorithm for encryption more than once!"
            return
        except AssertionError:
            file_data = self.read_data()
            data = zombify('e', sess.newline.join(file_data.split('\r')), self._key)  # to strip '\r' from the lines
            self.write_data(data)
            if echo:
                print sess.success, 'Successfully encrypted the file! (filename hash: %s)' % self.get_hash()

    def decrypt(self, overwrite = False):
        data = zombify('d', self.read_data(), self._key)
        assert data         # checking whether decryption has succeeded
        if overwrite:       # we catch the AssertionError later to indicate the wrong password input
            self.write_data(data)
        else:
            return data

    def write(self):
        '''Write an event to the story'''
        sess.clear_screen()
        input_loop, reminder = True, False
        keystroke = 'Ctrl+C'
        if sys.platform == 'win32':
            print sess.warning, "If you're using the command prompt, don't press %s while writing!" % keystroke
            keystroke = 'Ctrl+Z and [Enter]'

        # Step 1: Pre-writing stuff - check whether the story exists and whether there's a reminder in it, decrypt it!
        if self.get_path():
            try:                    # "Intentionally" decrypting the original file
                self.decrypt(overwrite = True)  # an easy workaround to modify your original story using editors
                prev_data = self.read_data()
                if prev_data.strip().endswith(REMINDER):     # find the reminder (if any)
                    while True:
                        try:
                            stamp_idx = prev_data.rfind('[')
                            if stamp_idx == -1: break
                            time = datetime.strptime(prev_data[stamp_idx:(stamp_idx + 21)], '[%Y-%m-%d] %H:%M:%S')
                            msg = time.strftime('\n(You were to write something about this day on %B %d, %Y at %R %p)')
                            reminder = True
                            break
                        except ValueError:
                            continue
                print '\nStory already exists! Appending to the current story...'
                print '(filename hash: %s)' % self.get_hash()
                if reminder:
                    print sess.fmt_text(msg, 'yellow')
            except AssertionError:
                print sess.error, "Bleh! Couldn't decrypt today's story! Check your password!"
                return

        try:    # Step 2: Writing the first paragraph...
            data = [datetime.now().strftime('[%F] %T\n')]
            stuff = raw_input("\nStart writing... (Once you've written something, press [Enter] to record it \
to the buffer. Further [RETURN] strokes indicate paragraphs. Press %s when you're done!)\n\n\t" % keystroke)
            if not stuff:       # quitting on empty return
                raise KeyboardInterrupt
            data.append(stuff)
        except (KeyboardInterrupt, EOFError):   # quitting on Ctrl-C
            sleep(sess.capture_wait)
            print "\nAlright, let's save it for a later time then! Quitting..."
            input_loop = False
            data.append(REMINDER)   # If the user quits before writing, then add a reminder

        # Step 3: Writing loop
        if input_loop and reminder:     # user has written something at this point, remove the reminder (if any)
            self.write_data(prev_data[:stamp_idx])
            # this is necessary, or else we'll ignore the "event" that should be written on top of the reminder
            reminder = False
        while input_loop:
            try:
                stuff = raw_input('\t')     # auto-tabbing of paragraphs (for each [RETURN])
                data.append(stuff)
            except (KeyboardInterrupt, EOFError):
                sleep(sess.capture_wait)
                break

        # Step 4: Write the data to file and encrypt it
        if not reminder:
            self.write_data('\n\t'.join(data) + '\n\n', 'a')    # because the user could've written something manually
        self.encrypt(echo = False)
        if input_loop and raw_input(sess.success + ' Successfully written to file! Do you wanna see it (y/n)? ') == 'y':
            self.view()

    def view(self, return_text = False):
        '''View the entire story'''
        date_format = '\nYour story from %s ...\n' % (self._date.strftime('%B %d, %Y (%A)'))
        try:
            if self.get_path():
                data = self.decrypt()
            else:
                print sess.error, "Story doesn't exist on the given day! (%s)" % self._date.date()
        except AssertionError:
            print sess.error, "Baaah! Couldn't decrypt the story!"
            return
        sess.clear_screen()
        count = simple_counter(data)
        start = "%s\n<----- START OF STORY -----> (%d words)\n\n" % \
                (sess.fmt_text(sess.fmt_text(date_format, 'violet'), 'bold'), count)
        end = "<----- END OF STORY ----->"
        if return_text:
            return (data, start, end)
        print start, data, end
