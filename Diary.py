import os
from random import choice as rchoice
from getpass import getpass
from datetime import datetime, timedelta
from hashlib import md5, sha256

ploc = os.path.expanduser('~') + os.sep + '.diary'              # Config location

def hexed(text):                                                # Hexing function
    return map(lambda i:
        format(ord(i), '02x'), list(text))

def hashed(hashFunction, text):                                 # Hashing function (could be MD5 or SHA-256)
    hashObject = hashFunction()
    hashObject.update(text)
    return hashObject.hexdigest()

def char(text):                                                 # Hex-decoding function
    split = [text[i:i+2] for i in range(0, len(text), 2)]
    try:
        return ''.join(i.decode('hex') for i in split)
    except TypeError:
        return None

# use a random seed here...

def CXOR(text, key):                                            # Byte-wise XOR
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

def shift(text, amount):                                        # Shifts the ASCII value of the chars (Vigenere cipher? Yep!)
    try:
        shiftedText = ''
        for i, ch in enumerate(text):
            shiftChar = (ord(ch) + amount) % 256
            shiftedText += chr(shiftChar)
    except TypeError:
        return None
    return shiftedText

def zombify(mode, data, key):                                   # Linking helper function
    hexedKey = ''.join(hexed(key))
    ch = sum([ord(i) for i in hexedKey])
    if mode == 'e':
        text = ''.join(hexed(data))
        return CXOR(shift(text, ch), key)
    elif mode in ('d', 'w'):
        text = shift(CXOR(data, key), 256 - ch)
        return char(text)

def temp(fileTuple, key):                                       # Decrypts and prints the story on the screen
    if protect(fileTuple[0], 'd', key):
        print fileTuple[1]
        with open(loc + 'TEMP.tmp', 'r') as file:
            data = file.readlines()
        print "\n<----- START OF STORY ----->\n"
        print ''.join(data)
        print "<----- END OF STORY ----->"
        os.remove(loc + 'TEMP.tmp')
        return key
    else:
        return None

def check():                                                    # Allows password to be stored locally
    if not os.path.exists(ploc):
        try:
            while True:
                key = getpass('\nEnter your password: ')
                if len(key) < 8:
                    print 'Choose a strong password! (at least 8 chars)'
                    continue
                if getpass('Re-enter the password: ') == key:
                    break
                else:
                    print "\nPasswords don't match!"
            hashedKey = hashed(sha256, key)
            with open(ploc, 'w') as file:
                file.writelines([hashedKey + '\n'])
            print '\nLogin credentials have been saved locally!'
        except KeyboardInterrupt:
            print "\nInterrupted! Couldn't store login credentials!"
            return True
    else:
        try:
            with open(ploc, 'r') as file:
                hashedKey = file.readlines()[0][:-1]
            key = getpass('\nEnter your password to continue: ')
            if not hashedKey == hashed(sha256, key):            # Fails if the password doesn't match with the credential
                print 'Wrong password!'
                return None
        except KeyboardInterrupt:
            print 'Failed to authenticate!'
            return True
    return key

def protect(path, mode, key):                                   # A simple method which shifts and turns it to hex!
    with open(path, 'r') as file:
        data = file.readlines()
    if not len(data):
        print 'Nothing in file!'
        return key
    data = zombify(mode, ''.join(data), key)
    if not data:
        print '\n\tWrong password!'                             # Indicates failure while decrypting
        return None
    File = (path if mode in ('e', 'w') else (loc + 'TEMP.tmp') if mode == 'd' else None)
    with open(File, 'w') as file:
        file.writelines([data])
    return key

def write(key, fileTuple = None):                               # Does the dirty writing job
    if not fileTuple:
        now = datetime.now()                                    # For illegal dates, you'll be ending up writing today's story
        date = hashed(md5, 'Day ' + now.strftime('%d') + ' (' + now.strftime('%B') + ' ' + now.strftime('%Y') + ')')
        story = '\nYour story from {date:%B} {date:%d}, {date:%Y} ({date:%A})...'.format(date = now)
        fileTuple = (loc + date, story)
    File = fileTuple[0]
    if os.path.exists(File) and os.path.getsize(File):
        key = protect(File, 'w', key)                           # Intentionally decrypting the original file
        if not key:                                             # It's an easy workaround to modify your original story
            return None
        else:                                                 
            print '\nFile already exists! Appending to current file...'
    timestamp = str(datetime.now()).split('.')[0].split(' ')
    data = ['[' + timestamp[0] + '] ' + timestamp[1] + '\n']
    try:
        stuff = raw_input("\nStart writing... (Press Ctrl+C when you're done!)\n\n\t")
        data.append(stuff)
    except KeyboardInterrupt:
        print 'Nothing written! Quitting...'
        key = protect(File, 'e', key)
        return key
    while True:
        try:
            stuff = raw_input('\t')                             # Auto-tabbing of paragraphs (for each <RETURN>)
            data.append(stuff)
        except KeyboardInterrupt:
            break
    with open(File, 'a') as file:
        file.writelines('\n\t'.join(data) + '\n\n')
    key = protect(File, 'e', key)
    ch = raw_input('\nSuccessfully written to file! Do you wanna see it (y/n)? ')
    if ch == 'y':
        temp(fileTuple, key)
    return key

def hashDate(year = None, month = None, day = None):            # Return a path based on (day, month, year) input
    while True:
        try:
            if not year:
                year = raw_input('\nYear: ')
            if not month:
                month = raw_input('\nMonth: ')
            if not day:
                day = raw_input('\nDay: ')
            date = datetime(int(year), int(month), int(day)).date()
            if date:
                year = date.strftime('%Y')
                month = date.strftime('%B')
                day = date.strftime('%d')
                break
        except Exception as err:
            print "An error occurred:", err
            year, month, day = None, None, None
            continue
    fileName = loc + hashed(md5, 'Day ' + day + ' (' + month + ' ' + year + ')')
    if not os.path.exists(fileName):
        print '\nNo stories on {date:%B} {date:%d}, {date:%Y} ({date:%A}).'.format(date = date)
        return None                                             # So, you can't write stories for illegal dates!
    story = '\nChoosing your story from {date:%B} {date:%d}, {date:%Y} ({date:%A})...'.format(date = date)
    return fileName, story                                      # This will be useful for displaying the date of story

def random(key):                                                # Useful only when you have a lot of stories (obviously)
    stories = len(os.listdir(loc))
    while True:
        ch = rchoice(range(stories))
        d = datetime(2014, 12, 13).date() + timedelta(days = ch)    # Happy Birthday, Diary!
        fileName = hashDate(d.year, d.month, d.day)
        if fileName:
            break
    return temp(fileName, key)

def configure(delete = False):
    try:
        choice = 'y'
        if os.path.exists(ploc) and not delete:
            print 'Configuration file found!'
            with open(ploc, 'r') as file:
                config = file.readlines()
            if len(config) > 1:
                loc = config[1]
                key = check()
                if type(key) is not str:
                    return None, None, 'n'
            else:
                delete = True
        if delete:
            print 'Deleting configuration file...'
            os.remove(ploc)
        if not os.path.exists(ploc):
            print "\nLet's start configuring your diary..."
            loc = raw_input('Enter the (absolute) location for your diary: ')
            while not os.path.exists(loc):
                print 'No such path exists!'
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

def search(key):                                                # Quite an interesting function for searching
    word = raw_input("Enter a word: ")
    choice = int(raw_input("\n\t1. Search everything!\n\t2. Search between two dates\n\nChoice: "))
    if choice == 1:
        d1 = datetime(2014, 12, 13)                             # Happy Birthday, Diary!
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
            print '\nOops! Error in input. Try again...'
            continue
        break
    delta = (d2 - d1).days
    print '\nDecrypting %d stories sequentially...' % delta     # Exhaustive process might do better with a low-level language
    print '\nSit back & relax... (May take some time)\n'        # That's why I'm writing a Rust library for this...
    fileData = [], [], []
    displayProg = 0
    printed = False
    for i in range(delta):
        d = d1 + timedelta(days = i)
        File = hashDate(d.year, d.month, d.day)[0]
        if File == None:
            continue
        progress = int((float(i + 1) / delta) * 100)
        if progress is not displayProg:
            displayProg = progress
            printed = False
        occurred = 0
        if protect(File, 'd', key):
            with open(loc + 'TEMP.tmp', 'r') as file:
                data = file.readlines()
            occurred = ''.join(data).count(word)
        else:
            print 'Cannot decrypt story! Skipping...'
            continue
        if occurred:
            fileData[0].append(i)                               # difference between two days (timedelta object)
            fileData[1].append(occurred)                        # how many times the word has occurred
            fileData[2].append(File)                            # file path (so that it can be easily opened later)
        if not printed:
            print 'Progress: %d%s \t(Found: %d)' % (displayProg, '%', sum(fileData[1]))
            printed = True
    print "\nSearch results from {d1:%B} {d1:%d}, {d1:%Y} to {d2:%B} {d2:%d}, {d2:%Y}.".format(d1 = d1, d2 = d2)
    if fileData[1]:
        print "\nStories on these days have the word '%s' in them...\n" % word
    else:
        print '\nBad luck! Nothing...'
    for i, delta in enumerate(fileData[0]):
        d = datetime(d1.year, d1.month, d1.day).date() + timedelta(days = delta)
        print '%d. %s %s, %s' % (i + 1, d.strftime('%B'), d.day, d.year)
    print '\nFound %d occurrences in %d stories!' % (sum(fileData[1]), len(fileData[0]))
    os.remove(loc + 'TEMP.tmp')
    while fileData[2]:
        try:
            ch = int(raw_input('Enter a number to see the corresponding story: '))
            temp(fileData[2][ch-1], key)
        except Exception:
            print '\nOops! Bad input...\n'

if __name__ == '__main__':
    loc, key, choice = configure()
    while choice is 'y':
        if os.path.exists(loc + 'TEMP.tmp'):
            os.remove(loc + 'TEMP.tmp')
        try:
            print '\n### This program runs best in command prompt ###'
            choices = ('\n\tWhat do you wanna do?\n',
                " 1: Write today's story",
                " 2: Random story",
                " 3: View the story of someday",
                " 4. Write the story for someday you've missed",
                " 5. Search your stories",
                " 6. Reconfigure your diary",)
            print '\n\t\t'.join(choices)
            choice = raw_input('\nChoice: ')
            ch = ['write(key)', 'random(key)', 'temp(hashDate(), key)', 'write(key, hashDate())', 'search(key)', 'configure(True)']
            try:
                key = eval(ch[int(choice)-1])                   # Remembers the password throughout the session
            except Exception as err:                            # But, you have to sign-in for each session
                # print err                                     # Might be useful for detecting propagating errors...
                print "\nAh, you've failed to authenticate! Let's try it once more... (or reconfigure your diary)"
                loc, key, choice = configure()
            choice = raw_input('\nDo something again (y/n)? ')
        except KeyboardInterrupt:
            choice = raw_input('\nInterrupted! Do something again (y/n)? ')
    if choice is not 'y':
        print '\nGoodbye...'
