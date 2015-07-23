# [Functions in other modules]
# findStory() - search.py
# temp(), protect(), hashed() - core.py

import shutil
from random import choice as rchoice

def random(key, birthday):          # Useful only when you have a lot of stories (obviously)
    stories = len(os.listdir(loc))
    for i in range(10):
        ch = rchoice(range(stories))
        fileName = findStory(ch, birthday)
        if fileName:
            return temp(fileName, key)
    print '\nPerhaps, this may not be a valid path after all...'
    return key

def backupStories(loc):
    print 'Backing up to Desktop...'
    zloc = os.path.expanduser('~/Desktop') + os.sep + "{d:%Y}{d:%m}{d:%d}".format(d = datetime.now())
    shutil.make_archive(zloc, 'zip', loc)

def changePass(key):                # Exhaustive method to change the password
    os.system('cls' if os.name == 'nt' else 'clear')
    print "\nLet's change your password..."
    if not getpass('\nOld password: ') == key:
        print error, 'Wrong password!'
        return loc, key
    newKey = getpass('New password: ')
    if newKey == key:
        print error, 'Both passwords are the same!'
        return loc, key
    if not getpass('Re-enter new password: ') == newKey:
        print error, "Passwords don't match!"
        return loc, key
    print '\nWorking...'
    shutil.copytree(loc, loc + 'TEMP')          # always have some precautions!
    backupStories(loc)
    print '(... just in case)'
    print 'Decrypting using old key...'
    for File in os.listdir(loc + 'TEMP'):
        key = protect(loc + 'TEMP' + os.sep + File, 'w', key)
        if key == None:
            os.rmdir(loc + 'TEMP')
            print error, "This file couldn't be decrypted! (filename hash: %s)\nResolve it before changing the password..." % File
            return loc, key
    print 'Encrypting using the new key...'
    for File in os.listdir(loc + 'TEMP'):
        key = protect(loc + 'TEMP' + os.sep + File, 'e', newKey)
    print "Overwriting the existing stories... (Please don't interrupt now!)"
    for File in os.listdir(loc):
        try:
            os.remove(loc + File)
            os.rename(loc + 'TEMP' + os.sep + File, loc + File)
        except OSError:
            continue                # This should leave our temporary folder
    os.rmdir(loc + 'TEMP')
    print 'Modifying the configuration file...'
    with open(ploc, 'w') as file:
        file.writelines([hashed(sha256, key), '\n', loc])
    print success, 'Password has been changed!'
    return loc, key
