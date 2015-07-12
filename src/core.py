import os, sys
from time import sleep
from getpass import getpass
from hashlib import md5, sha256
from datetime import datetime, timedelta

ploc = os.path.expanduser('~') + os.sep + '.diary'      # Config location (absolute)

error = "\n[ERROR]"
warning = "\n[WARNING]"
success = "\n[SUCCESS]"

def askDate(year = 0, month = 0, day = 0):      # Get the date from user
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

def hashed(hashFunction, text):     # Hashing function (could be MD5 or SHA-256)
    hashObject = hashFunction()
    hashObject.update(text)
    return hashObject.hexdigest()

def hashDate(year = 0, month = 0, day = 0):     # Return a path based on (day, month, year) input
    date = askDate(year, month, day)
    fileName = loc + hashed(md5, 'Day {date:%d} ({date:%B} {date:%Y})'.format(date = date))
    if not os.path.exists(fileName):
        if date > datetime.now():
            print error, "You can't just time-travel into the future!"
            return 'blah'
        print error, 'No stories on {date:%B} {date:%d}, {date:%Y} ({date:%A}).'.format(date = date)
        return None
    story = '{date:%B} {date:%d}, {date:%Y} ({date:%A})'.format(date = date)
    # formatted datetime will be useful for displaying the date of story
    return fileName, story

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
            hashedKey = hashed(sha256, key)
            with open(ploc, 'w') as file:
                file.writelines([hashedKey + '\n'])
            print success, 'Login credentials have been saved locally!'
        except (KeyboardInterrupt, EOFError):
            print warning, "Couldn't store login credentials!"
            sleep(wait)
            return True
    else:
        try:
            with open(ploc, 'r') as file:
                hashedKey = file.readlines()[0][:-1]
            key = getpass('\nEnter your password to continue: ')
            if not hashedKey == hashed(sha256, key):
                print error, 'Wrong password!'      # Fails if the password doesn't match with the credentials
                return None
        except KeyboardInterrupt:
            print error, 'Failed to authenticate!'
            sleep(wait)
            return True
    return key

def protect(path, mode, key):       # Invokes the cipher to encrypt/decrypt stuff
    with open(path, 'rb') as file:
        data = ''.join(file.readlines())
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

def write(key, fileTuple = None):   # Does all those dirty writing job
    keyComb = 'Ctrl+C'
    if sys.platform == 'win32':
        print warning, "If you're using the command prompt, don't press %s while writing!" % keyComb
        keyComb = 'Ctrl+Z and [Enter]'
    if not fileTuple:
        now = datetime.now()
        date = hashed(md5, 'Day ' + now.strftime('%d') + ' (' + now.strftime('%B') + ' ' + now.strftime('%Y') + ')')
        story = '{date:%B} {date:%d}, {date:%Y} ({date:%A}) ...'.format(date = now)
        fileTuple = (loc + date, story)
    elif type(fileTuple) == str:
        return key
    File = fileTuple[0]
    if os.path.exists(File) and os.path.getsize(File):
        # "Intentionally" decrypting the original file
        key = protect(File, 'w', key)
        # an easy workaround to modify your original story
        if not key:
            return None
        else:
            print '\nStory already exists! Appending to the current story...'
    timestamp = str(datetime.now()).split('.')[0].split(' ')
    data = ['[' + timestamp[0] + '] ' + timestamp[1] + '\n']
    try:
        stuff = raw_input("\nStart writing... (Once you've written something, press [Enter] to record it \
to the buffer. Further [RETURN] strokes indicate paragraphs. Press {} when you're done!)\n\n\t".format(keyComb))
        data.append(stuff)
    except (KeyboardInterrupt, EOFError):
        print '\nNothing written! Quitting...'
        sleep(wait)
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
        temp(fileTuple, key)
    return key

def temp(fileTuple, key):           # Decrypts and prints the story on the screen
    if type(fileTuple) == tuple:
        dataTuple = protect(fileTuple[0], 'd', key)
        if dataTuple:
            data, key = dataTuple
            print '\nYour story from', fileTuple[1], '...'
            print "\n<----- START OF STORY ----->\n\n", data, "<----- END OF STORY ----->\n"
            return key
        else:
            return None
    elif type(fileTuple) == str:
        return key
    else:
        return None

def configure(delete = False):      # Configuration file for authentication
    try:
        choice = 'y'
        if os.path.exists(ploc) and not delete:
            print '\nConfiguration file found!'
            with open(ploc, 'r') as file:
                config = file.readlines()
            if len(config) == 3:
                loc = config[1].strip()
                birthday = datetime.strptime(config[-1].strip(), '%Y-%m-%d')
                key = check()
                if type(key) is not str:
                    return None, None, None, 'n'
            else:
                delete = True       # consider this as an invalid configuration
        if delete:
            if os.path.exists(ploc):
                print warning, 'Deleting configuration file...'
                os.remove(ploc)
            else:
                print error, 'Configuration file has already been removed!'
        if not os.path.exists(ploc):
            print "\nLet's start configuring your diary...\n"
            loc = raw_input('Enter the (absolute) location for your diary: ')
            while not os.path.exists(loc):
                print error, 'No such path exists!'
                loc = raw_input('Please enter a valid path: ')
            if not loc[-1] == os.sep:
                loc += os.sep
            while True:
                try:
                    print '\nDate should be of the form YYYY-MM-DD (Mind you, with hyphen!)'
                    birth = raw_input("When did you start writing this diary? (Press [Enter] for today): ")
                    if not birth:
                        birthday = datetime.now()
                    else:
                        birthday = datetime.strptime(birth, '%Y-%m-%d')
                except ValueError:
                    print error, 'Oops! Error in input. Try again...'
                    continue
                break
            birth = '{date:%Y}-{date:%m}-{date:%d}'.format(date = birthday)
            key = check()
            if type(key) is not str:
                return None, None, None, 'n'
            with open(ploc, 'a') as file:
                file.writelines([loc + '\n' + birth])   # Store the location & birth of diary along with the password hash
    except (KeyboardInterrupt, EOFError):
        sleep(wait)
        return None, None, None, 'n'
    return loc, key, birthday, choice
