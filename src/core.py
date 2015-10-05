from datetime import datetime, timedelta
from getpass import getpass
from hashlib import md5, sha256
from string import punctuation as punc
from time import sleep

error, warning, success = "\n[ERROR]", "\n[WARNING]", "\n[SUCCESS]"

def write_access(path, check_path_exists = True):
    if check_path_exists and not os.path.exists(path):
        print error, "%s doesn't exist!" % path
        return False
    if not os.access(path, os.W_OK):
        print error, "Couldn't get write access to %s" % path
        return False
    return True

if not write_access(os.path.expanduser('~')):
    print error, "Couldn't get write access to home directory! Checking if the device is a mobile..."
    check_path = '/mnt/sdcard'  # QPython uses `/data` as home directory, and so let's try with `/mnt/sdcard`
    try:
        while not write_access(check_path):
            check_path = raw_input('\nEnter a path for the config file (which has write-access): ')
    except KeyboardInterrupt:
        exit("\nGoodbye...\n")
    ploc = os.path.join(check_path, '.diary')

    try:
        print warning, "If you get annoyed by this error and don't wanna do this often," \
                       + " please offer write acces to the home directory," \
                       + " move the config file from %s to your home directory (%s)" \
                       % (ploc, os.path.expanduser('~/.diary'))
        sleep(3)
        raw_input('\nPress [Enter] to continue...')
    except KeyboardInterrupt:
        pass

def ask_date(year = 0, month = 0, day = 0):      # Get the date from user
    while True:
        try:
            if not year:
                year = raw_input('\nYear: ')
            if not month:
                month = raw_input('\nMonth: ')
            if not day:
                day = raw_input('\nDay: ')
            return datetime(int(year), int(month), int(day))
        except Exception as err:
            print error, err
            year, month, day = 0, 0, 0
            continue

def hashed(hash_function, text):     # Hashing function (could be MD5 or SHA-256)
    hash_object = hash_function()
    hash_object.update(text)
    return hash_object.hexdigest()

def hash_format(datetime):
    return hashed(md5, 'Day {date:%d} ({date:%B} {date:%Y})'.format(date = datetime))

def hash_date(year = 0, month = 0, day = 0):     # Return a path based on (day, month, year) input
    date = ask_date(year, month, day)
    file_name = loc + hash_format(date)
    if not os.path.exists(file_name):
        if date > datetime.now():
            print error, "You can't just time-travel into the future!"
            return 'blah!'
        print error, 'No stories on {date:%B} {date:%d}, {date:%Y} ({date:%A}).'.format(date = date)
        return None
    story = '{date:%B} {date:%d}, {date:%Y} ({date:%A})'.format(date = date)
    # formatted datetime will be useful for displaying the date of story
    return file_name, story

def check():        # Allows password to be stored locally
    if not os.path.exists(ploc):
        try:
            while True:
                key = getpass('\nEnter your password: ')
                if len(key) < 8:
                    print warning, 'Choose a strong password! (at least 8 chars)'
                    continue
                if getpass('Re-enter the password: ') == key:
                    break
                else:
                    print error, "Passwords don't match!"
            hashed_key = hashed(sha256, key)
            with open(ploc, 'w') as file:
                file.writelines(hashed_key + '\n')
            print success, 'Login credentials have been saved locally!'
        except (KeyboardInterrupt, EOFError):
            sleep(wait)
            print error, "Couldn't store login credentials!"
            return True
    else:
        try:
            with open(ploc, 'r') as file:
                hashed_key = file.readlines()[0][:-1]
            key = getpass('\nEnter your password to continue: ')
            if not hashed_key == hashed(sha256, key):
                print error, 'Wrong password!'      # Fails if the password doesn't match with the credentials
                return None
        except (KeyboardInterrupt, EOFError):
            sleep(wait)
            print '\n', error, 'Failed to authenticate!'
            return True
    return key

def protect(path, mode, key):       # Invokes the cipher to encrypt/decrypt stuff
    with open(path, 'rb') as file:
        data = file.read()
    if not len(data):
        print error, 'Nothing in file!'
        return key
    if mode == 'e':                 # a little stunt to strip '\r' from the lines
        data = zombify(mode, newline.join(data.split('\r')), key)
    else:
        data = zombify(mode, data, key)
    if not data:        # Couldn't extract the chars from bytes! Indicates failure while decrypting
        print error, 'Wrong password!'
        return None
    if mode in ('e', 'w'):
        with open(path, 'wb') as file:
            file.writelines(data)
        return key
    else:
        return data, key

newline = ('\n' if sys.platform == 'darwin' else '')        # since OSX has only '\r' for newlines

def write(key, file_tuple = None):   # Does all those dirty writing job
    clear_screen()
    keyComb = 'Ctrl+C'
    now = datetime.now()
    if sys.platform == 'win32':
        print warning, "If you're using the command prompt, don't press %s while writing!" % keyComb
        keyComb = 'Ctrl+Z and [Enter]'
    if not file_tuple:
        date_hash = hash_format(now)
        story = '{date:%B} {date:%d}, {date:%Y} ({date:%A}) ...'.format(date = now)
        file_tuple = (loc + date_hash, story)
    elif type(file_tuple) == str:
        return key
    File = file_tuple[0]
    if os.path.exists(File) and os.path.getsize(File):  # "Intentionally" decrypting the original file
        key = protect(File, 'w', key)   # an easy workaround to modify your original story
        if not key:
            return None
        else:
            print '\nStory already exists! Appending to the current story...'
            print '(filename hash: %s)' % file_tuple[0].split(os.sep)[-1]        # useful for finding the file
    timestamp = str(now).split('.')[0].split(' ')
    data = ['[' + timestamp[0] + '] ' + timestamp[1] + '\n']
    try:
        stuff = raw_input("\nStart writing... (Once you've written something, press [Enter] to record it \
to the buffer. Further [RETURN] strokes indicate paragraphs. Press {} when you're done!)\n\n\t".format(keyComb))
        data.append(stuff)
    except (KeyboardInterrupt, EOFError):
        sleep(wait)
        print '\nNothing written! Quitting...'
        if os.path.exists(File) and os.path.getsize(File):
            key = protect(File, 'e', key)
        return key
    while True:
        try:
            stuff = raw_input('\t')     # auto-tabbing of paragraphs (for each [RETURN])
            data.append(stuff)
        except (KeyboardInterrupt, EOFError):
            sleep(wait)
            break
    with open(File, 'a') as file:
        file.writelines('\n\t'.join(data) + '\n\n')
    key = protect(File, 'e', key)
    ch = raw_input(success + ' Successfully written to file! Do you wanna see it (y/n)? ')
    if ch == 'y':
        view(file_tuple, key)
    return key

def view(file_tuple, key, return_text = False):      # Decrypts and prints the story on the screen
    if type(file_tuple) == tuple:                    # also returns the text on request
        data_tuple = protect(file_tuple[0], 'd', key)
        if data_tuple:
            count = 0
            clear_screen()
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

def configure(delete = False):      # Configuration file for authentication
    loc, key, birthday, choice = None, None, None, 'n'
    try:                            # Well, you have to sign-in for each session!
        if os.path.exists(ploc) and not delete:
            print '\nConfiguration file found!'
            with open(ploc, 'r') as file:
                config = file.readlines()
            try:
                loc = config[1].rstrip(os.sep + '\n') + os.sep
                assert os.path.exists(loc)
                birthday = datetime.strptime(config[2].strip(), '%Y-%m-%d')
                key = check()
                if type(key) is str:
                    choice = 'y'
                return loc, key, birthday, choice
            except Exception:
                clear_screen()
                print '\nInvalid configuration!'
                delete = True       # consider this as an invalid configuration

        if delete:
            if os.path.exists(ploc):
                print warning, 'Deleting configuration file...'
                os.remove(ploc)
            else:
                print error, 'Configuration file has already been removed!'
            sleep(2)        # waiting for the user to see the message (before it gets cleared)

        if not os.path.exists(ploc):
            clear_screen()
            print "\nLet's start configuring your diary...\n"
            print 'Enter the (absolute) location for your diary...', \
                  "\n(Note that this will create a foler named 'Diary' if the path doesn't end with it)"
            loc = raw_input('\nPath: ')
            while not write_access(loc):
                loc = raw_input('\nPlease enter a valid path (with write access): ')
            if not loc.rstrip(os.sep).endswith('Diary'):     # just put everything in a folder for Diary
                loc = os.path.join(loc, 'Diary')
                print 'Note that this will make use of %r' % loc
                if not os.path.exists(loc):
                    os.mkdir(loc)
            loc = loc.rstrip(os.sep) + os.sep

            while True:
                try:
                    birth = raw_input('''\
                                      \nWhen did you start writing this diary? (Press [Enter] for today)\
                                      \nDate should be of the form YYYY-MM-DD (Mind you, with hyphen!)
                                      \nDate: ''')
                    if not birth:
                        birthday = datetime.now()
                    else:
                        birthday = datetime.strptime(birth, '%Y-%m-%d')
                        date_hash = hash_format(birthday)
                        if not os.path.exists(loc + date_hash):
                            print warning, "Story doesn't exist on that day! (in the given path)"
                except ValueError:
                    print error, 'Oops! Error in input. Try again...'
                    continue
                break

            birth = '{date:%Y}-{date:%m}-{date:%d}'.format(date = birthday)
            key = check()
            if type(key) is not str:
                return loc, key, birthday, choice
            with open(ploc, 'a') as file:
                file.writelines(loc + '\n' + birth)     # Store the location & birth of diary along with the password hash

            choice = 'y'
            print "\nIf you plan to reconfigure it manually, then it's located here (%s)" % ploc
            print "And, be careful with that, because invalid configuration files will be deleted during startup!"
            sleep(3)
            raw_input('\nPress [Enter] to continue...')
    except (KeyboardInterrupt, EOFError):
        sleep(wait)
    return loc, key, birthday, choice
