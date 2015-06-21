import os
from random import choice as rchoice
from getpass import getpass
from time import strftime as time
from datetime import datetime, timedelta
from hashlib import md5, sha256

if '/bin' in os.path.defpath:
    ploc = os.path.expanduser('~') + '/.diary'
    loc = os.path.expanduser('~/Desktop') + '/Desktop/Dropbox/Diary/'
else:
    ploc = os.path.expanduser('~') + '\\AppData\\Local\\TEMP.DAT'           # Config location
    loc = os.path.expanduser('~') + '\\Desktop\\Dropbox\\Diary\\'           # Storage location

months = {
    '01': 'January',
    '02': 'February',
    '03': 'March',
    '04': 'April',
    '05': 'May',
    '06': 'June',
    '07': 'July',
    '08': 'August',
    '09': 'September',
    '10': 'October',
    '11': 'November',
    '12': 'December'
}

def hexed(text):                                                # Hexing function
    return map(lambda i:
        format(ord(i), '02x'), list(text))

def hashed(hashFunction, stuff):                                # Hashing function (could be MD5 or SHA-256)
    hashObject = hashFunction()
    hashObject.update(stuff)
    return hashObject.hexdigest()

def char(text):                                                 # Hex-decoding function
    split = [text[i:i+2] for i in range(0, len(text), 2)]
    try:
        return ''.join(i.decode('hex') for i in split)
    except TypeError:
        return None

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

def temp(File, key):                                            # Decrypts and prints the story on the screen
    if protect(File, 'd', key):
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
                file.writelines([hashedKey])
            print '\nLogin credentials have been saved locally!'
        except KeyboardInterrupt:
            print "\nCouldn't store login credentials!"
            return None
    else:
        try:
            with open(ploc, 'r') as file:
                hashedKey = file.readlines()[0]
            key = getpass('\nEnter your password to continue: ')
            if not hashedKey == hashed(sha256, key):            # Fails if the password doesn't match with the credential
                print 'Wrong password!'
                return None
        except KeyboardInterrupt:
            print 'Failed to authenticate!'
            return None
    return key

def protect(path, mode, key):                                   # A simple method which shifts and turns it to hex!
    with open(path, 'r') as file:
        data = file.readlines()
    if not len(data):
        print 'Nothing in file!'
        return key
    data = zombify(mode, ''.join(data), key)
    if not data:
        print '\n\tWrong password!'                         # Indicates failure while decrypting
        return None
    File = (path if mode in ('e', 'w') else (loc + 'TEMP.tmp') if mode == 'd' else None)
    with open(File, 'w') as file:
        file.writelines([data])
    return key

def write(key, File = None):                                    # Does the dirty writing job
    if not File:
        date = hashed(md5, 'Day ' + time('%d') + ' (' + months[time('%m')] + ' ' + time('%Y') + ')')
        if not date:
            return key
        File = loc + date
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
        temp(File, key)
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
            date = str(datetime(int(year), int(month), int(day)).date()).split('-')
            if date:
                year = date[0]
                month = months[date[1]]
                day = date[2]
                break
        except Exception as err:
            print "An error occurred:", err
            year, month, day = None, None, None
            continue
    fileName = loc + hashed(md5, 'Day ' + day + ' (' + month + ' ' + year + ')')
    if not os.path.exists(fileName):
        print '\nNo stories on {} {}, {}.'.format(month, day, year)
        return None
    return fileName

def random(key):                                                # Useful only when you have a lot of stories (obviously)
    stories = len(os.listdir(loc))
    while True:
        ch = rchoice(range(stories))
        d = datetime(2014, 12, 13).date() + timedelta(days = ch)
        fileName = hashDate(d.year, d.month, d.day)
        if fileName:
            break
    d = str(d).split('-')
    print '\nChoosing your story from %s %s, %s...' % (months[d[1]], d[2], d[0])
    return temp(fileName, key)

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
    print '\nDecrypting %d stories sequentially...' % delta     # Exhaustive process requires a low-level language
    print '\nSit back & relax... (May take some time)\n'        # That's why I'm learning Rust by translating this...
    fileData = [], [], []
    displayProg = 0
    printed = False
    for i in range(delta):
        d = d1 + timedelta(days = i)
        File = hashDate(d.year, d.month, d.day)
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
            fileData[0].append(i)
            fileData[1].append(occurred)
            fileData[2].append(File)
        if not printed:
            print 'Progress: %d%s \t(Found: %d)' % (displayProg, '%', sum(fileData[1]))
            printed = True
    r1 = str(d1.date()).split('-')
    r2 = str(d2.date()).split('-')
    ranges = months[r1[1]], r1[2], r1[0], months[r2[1]], r2[2], r2[0]
    print "\nSearch results from %s %s, %s to %s %s, %s" % ranges
    if fileData[1]:
        print "\nStories on these days have the word '%s' in them...\n" % word
    else:
        print '\nBad luck! Nothing...'
    for i, delta in enumerate(fileData[0]):
        d = str(datetime(d1.year, d1.month, d1.day).date() + timedelta(days = delta)).split('-')
        print '%d. %s %s, %s' % (i + 1, months[d[1]], d[2], d[0])
    print '\nFound %d occurrences in %d stories!' % (sum(fileData[1]), len(fileData[0]))
    os.remove(loc + 'TEMP.tmp')
    while fileData[2]:
        try:
            ch = int(raw_input('Enter a number to open the corresponding story: '))
            temp(fileData[2][ch-1], key)
        except Exception:
            print '\nOops! Bad input...\n'

if __name__ == '__main__':
    choice = 'y'
    key = None
    while choice is 'y':
        if os.path.exists(loc + 'TEMP.tmp'):
            os.remove(loc + 'TEMP.tmp')
        try:
            choices = ('\n\tWhat do you wanna do?\n',
                " 1: Write today's story",
                " 2: Random story",
                " 3: View the story of someday",
                " 4. Write the story for someday you've missed",
                " 5. Search your stories",)
            print '\n\t\t'.join(choices)
            if os.path.exists(ploc):
                print '\t\t 0: Sign out'
            choice = raw_input('\nChoice: ')
            ch = ['write(key)', 'random(key)', 'temp(hashDate(), key)', 'write(key, hashDate())', 'search(key)']
            if choice == '0' and os.path.exists(ploc):
                os.remove(ploc)
                print 'Login credentials have been removed!'
                key = None
            else:
                while not key:                                  # Remembers the password throughout the session
                    key = check()                               # But, you have to sign-in for each session
                try:
                    key = eval(ch[int(choice)-1])
                except Exception:
                    print '\nAh, something bad has happened! Did you do it?'
            choice = raw_input('\nDo something again (y/n)? ')
        except KeyboardInterrupt:
            choice = raw_input('\nInterrupted! Do something again (y/n)? ')
