import os, ctypes, shutil
from random import choice as rchoice
from getpass import getpass
from datetime import datetime, timedelta
from hashlib import md5, sha256
from timeit import default_timer as timer

ploc = os.path.expanduser('~') + os.sep + '.diary'      # Config location
rustLib = "target/release/libanecdote.so"               # Library location

error = "[ERROR]"
warning = "[WARNING]"
success = "[SUCCESS]"

def rustySearch(key, pathList, word):           # FFI for giving the searching job to Rust
    if not os.path.exists(rustLib):
        print error, 'Rust library not found!'
        return 0, 0
    lib = ctypes.cdll.LoadLibrary(rustLib)
    list_to_send = pathList[:]
    list_to_send.extend((key, word))

    # send an array pointer full of string pointers (like a pointer to ['blah', 'blah', 'blah'])
    lib.get_stuff.argtypes = (ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t)     # type declarations must be done
    lib.get_stuff.restype = ctypes.c_void_p                                         # or else, segfault!
    lib.kill_pointer.argtypes = [ctypes.c_void_p]

    start = timer()
    c_array = (ctypes.c_char_p * len(list_to_send))(*list_to_send)
    c_pointer = lib.get_stuff(c_array, len(list_to_send))
    count_string = ctypes.c_char_p(c_pointer).value
    lib.kill_pointer(c_pointer)                 # Sending the pointer back to Rust for destruction
    occurrences = [int(i) for i in count_string.split(' ')]
    stop = timer()
    return occurrences, (stop - start)

def hexed(text):                                # Hexing function
    return map(lambda i:
        format(ord(i), '02x'), list(text))

def hashed(hashFunction, text):                 # Hashing function (could be MD5 or SHA-256)
    hashObject = hashFunction()
    hashObject.update(text)
    return hashObject.hexdigest()

def char(text):                                 # Hex-decoding function
    split = [text[i:i+2] for i in range(0, len(text), 2)]
    try:
        return ''.join(i.decode('hex') for i in split)
    except TypeError:
        return None

def CXOR(text, key):                            # Byte-wise XOR
    def xor(char1, char2):
        return chr(ord(char1) ^ ord(char2))
    out = ''
    i, j = 0, 0
    while i < len(text):
        out += xor(text[i], key[j])
        (i, j) = (i + 1, j + 1)
        if j == len(key):
            j = 0
    return ''.join(out)

def shift(text, amount):                        # Shifts the ASCII value of the chars
    try:
        shiftedText = ''
        for i, ch in enumerate(text):
            shiftChar = (ord(ch) + amount) % 256
            shiftedText += chr(shiftChar)
    except TypeError:
        return None
    return shiftedText

def zombify(mode, data, key):                   # Linking helper function
    hexedKey = ''.join(hexed(key))
    ch = sum([ord(i) for i in hexedKey])
    if mode == 'e':
        text = ''.join(hexed(data))
        return CXOR(shift(text, ch), key)
    elif mode in ('d', 'w'):
        text = shift(CXOR(data, key), 256 - ch)
        return char(text)

def temp(fileTuple, key):                       # Decrypts and prints the story on the screen
    if type(fileTuple) == tuple:
        if protect(fileTuple[0], 'd', key):
            print 'Your story from', fileTuple[1], '...'
            with open(loc + 'TEMP.tmp', 'r') as file:
                data = file.readlines()
            print "\n<----- START OF STORY ----->\n"
            print ''.join(data)
            print "<----- END OF STORY ----->"
            os.remove(loc + 'TEMP.tmp')
            return key
        else:
            return None
    elif type(fileTuple) == str:
        return key
    else:
        return None

def check():                                    # Allows password to be stored locally
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
                    print error, "\nPasswords don't match!"
            hashedKey = hashed(sha256, key)
            with open(ploc, 'w') as file:
                file.writelines([hashedKey + '\n'])
            print '\n', success, 'Login credentials have been saved locally!'
        except KeyboardInterrupt:
            print "\n", warning, "Interrupted! Couldn't store login credentials!"
            return True
    else:
        try:
            with open(ploc, 'r') as file:
                hashedKey = file.readlines()[0][:-1]
            key = getpass('\nEnter your password to continue: ')
            if not hashedKey == hashed(sha256, key):
                # Fails if the password doesn't match with the credentials
                print error, 'Wrong password!'
                return None
        except KeyboardInterrupt:
            print '\n', error, 'Failed to authenticate!'
            return True
    return key

def protect(path, mode, key):                   # A simple method which shifts and turns it to hex!
    with open(path, 'r') as file:
        data = file.readlines()
    if not len(data):
        print error, 'Nothing in file!'
        return key
    data = zombify(mode, ''.join(data), key)
    if not data:
        # Couldn't extract the chars from bytes! Indicates failure while decrypting
        print '\n\t', error, 'Wrong password!'
        return None
    File = (path if mode in ('e', 'w') else (loc + 'TEMP.tmp') if mode == 'd' else None)
    with open(File, 'w') as file:
        file.writelines([data])
    return key

def write(key, fileTuple = None):               # Does the dirty writing job
    if not fileTuple:
        now = datetime.now()
        date = hashed(md5, 'Day ' + now.strftime('%d') + ' (' + now.strftime('%B') + ' ' + now.strftime('%Y') + ')')
        story = '\nYour story from {date:%B} {date:%d}, {date:%Y} ({date:%A}) ...'.format(date = now)
        fileTuple = (loc + date, story)
    elif type(fileTuple) == str:
        return key
    File = fileTuple[0]
    if os.path.exists(File) and os.path.getsize(File):
        # Intentionally decrypting the original file
        key = protect(File, 'w', key)
        # It's an easy workaround to modify your original story
        if not key:
            return None
        else:
            print '\nFile already exists! Appending to current file...'
    timestamp = str(datetime.now()).split('.')[0].split(' ')
    data = ['[' + timestamp[0] + '] ' + timestamp[1] + '\n']
    try:
        stuff = raw_input("\nStart writing... (Press Ctrl+C when you're done!)\n\n\t")
        data.append(stuff)
    except KeyboardInterrupt:
        print '\nNothing written! Quitting...'
        if os.path.exists(File) and os.path.getsize(File):
            key = protect(File, 'e', key)
        return key
    while True:
        try:
            stuff = raw_input('\t')
            # Auto-tabbing of paragraphs (for each <RETURN>)
            data.append(stuff)
        except KeyboardInterrupt:
            break
    with open(File, 'a') as file:
        file.writelines('\n\t'.join(data) + '\n\n')
    key = protect(File, 'e', key)
    ch = raw_input('\n' + success + ' Successfully written to file! Do you wanna see it (y/n)? ')
    if ch == 'y':
        temp(fileTuple, key)
    return key

def hashDate(year = 0, month = 0, day = 0):     # Return a path based on (day, month, year) input
    while True:
        try:
            if not year:
                year = raw_input('\nYear: ')
            if not month:
                month = raw_input('\nMonth: ')
            if not day:
                day = raw_input('\nDay: ')
            date = datetime(int(year), int(month), int(day))
            if date:
                year = date.strftime('%Y')
                month = date.strftime('%B')
                day = date.strftime('%d')
                break
        except Exception as err:
            print '\n', error, err
            year, month, day = None, None, None
            continue
    fileName = loc + hashed(md5, 'Day ' + day + ' (' + month + ' ' + year + ')')
    if not os.path.exists(fileName):
        if date > datetime.now():
            print '\n', error, 'You cannot write/view a story for a day in the future!'
            return 'blah'
        print error, '\nNo stories on {date:%B} {date:%d}, {date:%Y} ({date:%A}).'.format(date = date)
        return None
    story = '{date:%B} {date:%d}, {date:%Y} ({date:%A})'.format(date = date)
    # will be useful for displaying the date of story
    return fileName, story

def findStory(delta, date = datetime(2014, 12, 13)):            # Finds the file name using the timedelta from the birth of the diary to a specified date
    stories = len(os.listdir(loc))
    d = date + timedelta(days = delta)
    fileName = hashDate(d.year, d.month, d.day)
    if not fileName:
        return None
    return fileName

def random(key):                                                # Useful only when you have a lot of stories (obviously)
    stories = len(os.listdir(loc))
    while True:
        ch = rchoice(range(stories))
        fileName = findStory(ch)
        if fileName:
            break
    return temp(fileName, key)

def configure(delete = False):                                  # Configuration file for authentication
    try:
        choice = 'y'
        if os.path.exists(ploc) and not delete:
            print 'Configuration file found!'
            with open(ploc, 'r') as file:
                config = file.readlines()
            if len(config) == 2:
                loc = config[1]
                if loc[-1] == '\n':
                    loc = loc[:-1]
                key = check()
                if type(key) is not str:
                    return None, None, 'n'
            else:
                delete = True
        if delete:
            print warning, 'Deleting configuration file...'
            os.remove(ploc)
        if not os.path.exists(ploc):
            print "\nLet's start configuring your diary..."
            loc = raw_input('Enter the (absolute) location for your diary: ')
            while not os.path.exists(loc):
                print error, 'No such path exists!'
                loc = raw_input('Please enter a valid path: ')
            if loc[-1] is not os.sep:
                loc += os.sep
            key = check()
            if type(key) is not str:
                return None, None, 'n'
            with open(ploc, 'a') as file:
                file.writelines([loc])                          # Store the location along with the password hash
    except KeyboardInterrupt:
        return None, None, 'n'
    return loc, key, choice

def grabStories(delta, date):                                   # Grabs the story paths for a given datetime and timedelta objects
    fileData = [], []
    for i in range(delta):
        fileName = findStory(i, date)
        if fileName == None:
            continue
        fileData[0].append(fileName[0])
        fileData[1].append(fileName[1])
    return fileData

def pySearch(key, files, word):                                 # Exhaustive process might do better with a low-level language
    occurrences = []                                            # That's why I'm writing a Rust library for this...
    displayProg = 0
    printed = False
    total = len(files)
    start = timer()
    for i, File in enumerate(files):
        progress = int((float(i + 1) / total) * 100)
        if progress is not displayProg:
            displayProg = progress
            printed = False
        occurred = 0
        if protect(File, 'd', key):
            with open(loc + 'TEMP.tmp', 'r') as file:
                data = file.readlines()
            occurred = ''.join(data).count(word)
        else:
            print warning, 'Cannot decrypt story! Skipping... (filename hash: %s)' % File.split(os.sep)[-1]
        occurrences.append(occurred)
        if not printed:
            print 'Progress: %d%s \t(Found: %d)' % (displayProg, '%', sum(occurrences))
            printed = True
    stop = timer()
    return occurrences, (stop - start)

def search(key):
    word = raw_input("Enter a word: ")
    choice = 0
    while choice not in (1, 2, 3):
        choices = ('\n\t1. Search everything! (Python)',
                    '2. Search between two dates (Python)',
                    '3. Search everything! (Rust)')
        choice = int(raw_input('\n\t'.join(choices) + '\n\nChoice: '))
    if choice in (1, 3):
        d1 = datetime(2014, 12, 13)
        d2 = datetime.now()
    while choice == 2:
        try:
            print '\nEnter dates in the form YYYY-MM-DD (Mind you, with hyphen!)'
            d1 = datetime.strptime(raw_input('Start date: '), '%Y-%m-%d')
            d2 = raw_input("End date (Press <Enter> for today's date): ")
            if not d2:
                d2 = datetime.now()
            else:
                d2 = datetime.strptime(d2, '%Y-%m-%d')
        except ValueError:
            print error, '\nOops! Error in input. Try again...'
            continue
        break
    delta = (d2 - d1).days
    print '\nDecrypting %d stories...\n' % delta
    files = grabStories(delta, d1)
    # has both file location and the formatted datetime
    if choice in (1, 2):
        fileData, timing = pySearch(key, files[0], word)
    else:
        fileData, timing = rustySearch(key, files[0], word)
    print "\nSearch results from {d1:%B} {d1:%d}, {d1:%Y} to {d2:%B} {d2:%d}, {d2:%Y}.".format(d1 = d1, d2 = d2)
    if sum(fileData):
        print "\nStories on these days have the word '%s' in them...\n" % word
    else:
        print '\nTime taken:', timing, 'seconds!'
        print '\nBummer! Nothing...'
        return key
    # splitting into pairs (for later use)
    results = [(files[0][i], files[1][i]) for i, count in enumerate(fileData) if count]
    for i, data in enumerate(results):
        print str(i + 1) + '. ' + data[1]               # print only the datetime
    print '\nTime taken:', timing, 'seconds!'
    print '\n', success, 'Found %d occurrences in %d stories!\n' % (sum(fileData), len(results))
    if os.path.exists(loc + 'TEMP.tmp'):
        os.remove(loc + 'TEMP.tmp')
    while files:
        try:
            ch = int(raw_input('Enter the number to see the corresponding story: '))
            temp((results[ch-1][0], results[ch-1][1]), key)
        except Exception:
            print error, '\nOops! Bad input...\n'
    return key

def changePass(key):                            # Exhaustive method to change the password
    if not getpass('\nOld password: ') == key:
        print '\n', error, 'Wrong password!'
        return loc, key
    newKey = getpass('New password: ')
    if newKey == key:
        print '\n', error, 'Both passwords are the same!'
        return loc, key
    if not getpass('Re-enter new password: ') == newKey:
        print '\n', error, "Passwords don't match!"
        return loc, key
    print '\nWorking...'
    shutil.copytree(loc, loc + 'TEMP')          # always have precautions!
    print 'Decrypting using old key...'
    for File in os.listdir(loc + 'TEMP'):
        key = protect(loc + 'TEMP' + os.sep + File, 'w', key)
        if key == None:
            os.rmdir(loc + 'TEMP')
            print error, 'This file has issue (filename hash: %s)\nResolve it before changing the password...' % File
            return loc, key
    print 'Encrypting using the new key...'
    for File in os.listdir(loc + 'TEMP'):
        key = protect(loc + 'TEMP' + os.sep + File, 'e', newKey)
    print 'Overwriting the existing stories...'
    for File in os.listdir(loc):
        try:
            os.remove(loc + File)
            os.rename(loc + 'TEMP' + os.sep + File, loc + File)
        except OSError:
            continue                            # This should leave our temporary folder
    os.rmdir(loc + 'TEMP')
    print 'Modifying the configuration file...'
    with open(ploc, 'w') as file:
        file.writelines([hashed(sha256, key), '\n', loc])
    return loc, key

if __name__ == '__main__':
   loc, key, choice = configure()
   while choice is 'y':
       if os.path.exists(loc + 'TEMP.tmp'):
           os.remove(loc + 'TEMP.tmp')
       try:
           print '\n### This program runs best on Linux terminal ###'
           while True:
               choices = ('\n\tWhat do you wanna do?\n',
                   " 1: Write today's story",
                   " 2: Random story",
                   " 3: View the story of someday",
                   " 4. Write the story for someday you've missed",
                   " 5. Search your stories",
                   " 6. Change your password",
                   " 7. Reconfigure your diary",)
               print '\n\t\t'.join(choices)
               try:
                   ch = int(raw_input('\nChoice: '))
                   if ch in range(1, 7):
                       break
                   else:
                       print '\n', error, 'Please enter a value between 0 and 6!'
               except ValueError:
                   print '\n', error, "C'mon, quit playing around and start writing..."
           options =   ['key = write(key)',     # just to remember the password throughout the session
                        'key = random(key)',
                        'key = temp(hashDate(), key)',
                        'key = write(key, hashDate())',
                        'key = search(key)',
                        'loc, key = changePass(key)',
                        'loc, key, choice = configure(True)']
           try:
               exec(options[int(ch)-1])
           except Exception as err:             # But, you have to sign-in for each session!
               print err, '\n', error, 'Ah, something bad has happened! Did you do it?'
           choice = raw_input('\nDo something again (y/n)? ')
       except KeyboardInterrupt:
           choice = raw_input('\n\nInterrupted! Do something again (y/n)? ')
   if choice is not 'y':
       print '\nGoodbye...'
