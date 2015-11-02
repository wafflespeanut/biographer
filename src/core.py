from datetime import datetime
from hashlib import md5
from string import punctuation as punc
from time import sleep

def ask_date(year = 0, month = 0, day = 0):      # Get the date from user
    while True:
        try:
            if not all([year, month, day]):
                year = int(raw_input('\nYear: '))
                month = int(raw_input('\nMonth: '))
                day = int(raw_input('\nDay: '))
            return datetime(year, month, day)
        except Exception:
            print error, 'Invalid input! Cannot parse the given date!'
            year, month, day = 0, 0, 0
            continue

def hashed(hash_function, text):     # Hashing function (could be MD5 or SHA-256)
    hash_object = hash_function()
    hash_object.update(text)
    return hash_object.hexdigest()

def hash_format(datetime):
    return hashed(md5, 'Day {date:%d} ({date:%B} {date:%Y})'.format(date = datetime))

def hash_date(location, year = 0, month = 0, day = 0, force = False):     # Return a path based on (day, month, year) input
    date = ask_date(year, month, day)
    file_name = location + hash_format(date)
    # formatted datetime will be useful for displaying the date of story
    story = '{date:%B} {date:%d}, {date:%Y} ({date:%A})'.format(date = date)
    if not os.path.exists(file_name):
        if date > datetime.now():
            print sess.error, "You can't just time-travel into the future!"
            return 'blah!'
        if date < datetime.now() and force:
            return file_name, story
        print sess.error, 'No stories on {date:%B} {date:%d}, {date:%Y} ({date:%A}).'.format(date = date)
        return None
    return file_name, story

def protect(path, mode, key):       # Invokes the cipher to encrypt/decrypt stuff
    with open(path, 'rb') as file:
        data = file.read()
    if not len(data):
        print sess.error, 'Nothing in file!'
        return key
    if mode == 'e':                 # a little stunt to strip '\r' from the lines
        data = zombify(mode, sess.newline.join(data.split('\r')), key)
    else:
        data = zombify(mode, data, key)
    if not data:        # Couldn't extract the chars from bytes! Indicates failure while decrypting
        print sess.error, 'Cannot decrypt the story! (probably wrong ciphertext-key combination)'
        return None
    if mode in ('e', 'w'):
        with open(path, 'wb') as file:
            file.writelines(data)
        return key
    else:
        return data, key

def try_encrypt(key, file_tuple, encrypt = True):
    if not file_tuple:
        return
    file_path = file_tuple[0]
    try:    # just to check whether a file has already been encrypted
        if encrypt and protect(file_path, 'd', key):
            print sess.error, "This file looks like it's already been encrypted.", \
                         "\nIt's never encouraged to use this algorithm for encryption more than once!"
            return
    except TypeError:
        if encrypt:
            protect(file_path, 'e', key)
            print sess.success, 'Successfully encrypted the file! (%s)' % file_path
            return
    return

def write(session, file_tuple = None):  # Does all those dirty writing job
    if type(file_tuple) == str:
        return
    sess.clear_screen()
    keystroke = 'Ctrl+C'
    now = datetime.now()
    if sys.platform == 'win32':
        print sess.warning, "If you're using the command prompt, don't press %s while writing!" % keystroke
        keystroke = 'Ctrl+Z and [Enter]'
    if not file_tuple:
        date_hash = hash_format(now)
        story = '{date:%B} {date:%d}, {date:%Y} ({date:%A}) ...'.format(date = now)
        file_tuple = (session.location + date_hash, story)
    File = file_tuple[0]
    if os.path.exists(File) and os.path.getsize(File):  # "Intentionally" decrypting the original file
        if not protect(File, 'w', session.key): # an easy workaround to modify your original story
            return None
        else:
            print '\nStory already exists! Appending to the current story...'
            print '(filename hash: %s)' % file_tuple[0].split(os.sep)[-1]        # useful for finding the file
    timestamp = str(now).split('.')[0].split(' ')
    data = ['[' + timestamp[0] + '] ' + timestamp[1] + '\n']
    try:
        stuff = raw_input("\nStart writing... (Once you've written something, press [Enter] to record it \
to the buffer. Further [RETURN] strokes indicate paragraphs. Press {} when you're done!)\n\n\t".format(keystroke))
        data.append(stuff)
    except (KeyboardInterrupt, EOFError):
        sleep(sess.capture_wait)
        print '\nNothing written! Quitting...'
        if os.path.exists(File) and os.path.getsize(File):
            protect(File, 'e', session.key)
        return
    while True:
        try:
            stuff = raw_input('\t')     # auto-tabbing of paragraphs (for each [RETURN])
            data.append(stuff)
        except (KeyboardInterrupt, EOFError):
            sleep(sess.capture_wait)
            break
    with open(File, 'a') as file:
        file.writelines('\n\t'.join(data) + '\n\n')
    protect(File, 'e', session.key)
    if raw_input(success + ' Successfully written to file! Do you wanna see it (y/n)? ') == 'y':
        view(session.key, file_tuple)

def view(key, file_tuple, return_text = False):      # Decrypts and prints the story on the screen
    if type(file_tuple) == tuple:                    # also returns the text on request
        data_tuple = protect(file_tuple[0], 'd', key)
        if data_tuple:
            count = 0
            sess.clear_screen()
            data, key = data_tuple
            split_data = data.split()
            for word in split_data:
                if word not in punc:
                    try:
                        timestamp = datetime.strptime(word, '[%Y-%m-%d]')
                        count += 2          # "2" for both date and time
                    except ValueError:
                        pass
            start = "\nYour story from %s ...\n\n<----- START OF STORY -----> (%d words)\n\n"\
                    % (file_tuple[1], len(split_data) - count)
            end = "<----- END OF STORY ----->"
            if return_text:
                return key, (data, start, end)
            print start, data, end
            return key
        else:
            return None
    elif type(file_tuple) == str:
        return key
    else:
        return None
