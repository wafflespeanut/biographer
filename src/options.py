# [Functions in other modules]
# findStory() - search.py
# temp(), protect(), hashed() - core.py

import shutil
from random import choice as rchoice

colors = {
    'R': '91',
    'G': '92',
    'Y': '93',
    'B2': '94',
    'P': '95',
    'B1': '96',
    'W': '97',
    '0': '0',
}

def fmt(color):
    return {'win32': ''}.get(sys.platform, '\033[' + colors[color] + 'm')

def mark_text(text, indices, length, color = 'R'):  # Mark text and return corrected indices
    text = list(text)
    if sys.platform == 'win32':         # Damn OS doesn't even support coloring
        return text, indices
    formatter = fmt(color), fmt('0')
    lengths = map(len, formatter)
    i, limit = 0, len(indices)
    new_indices = indices[:]
    while i < limit:
        idx = indices[i]
        text[idx] = formatter[0] + text[idx]
        text[idx + length - 1] += formatter[1]
        new_indices[i] -= lengths[0]
        j = i
        while j < limit:
            new_indices[j] += sum(lengths)
            j += 1
        i += 1
    return ''.join(text), new_indices

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
    zloc = os.path.join(os.path.expanduser('~/Desktop'), "{d:%Y}{d:%m}{d:%d}".format(d = datetime.now()))
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
    temp_loc = loc + 'TEMP'
    shutil.copytree(loc, temp_loc)          # always have some precautions!
    backupStories(loc)
    print '(... just in case)'
    print 'Decrypting using old key...'
    for File in os.listdir(temp_loc):
        key = protect(os.path.join(temp_loc, File), 'w', key)
        if key == None:
            os.rmdir(temp_loc)
            print error, "This file couldn't be decrypted! (filename hash: %s)\nResolve it before changing the password..." % File
            return loc, key
    print 'Encrypting using the new key...'
    for File in os.listdir(temp_loc):
        key = protect(os.path.join(temp_loc, File), 'e', newKey)
    print "Overwriting the existing stories... (Please don't interrupt now!)"
    for File in os.listdir(loc):
        try:
            os.remove(loc + File)
            os.rename(os.path.join(temp_loc, File), loc + File)
        except OSError:
            continue                # This should leave our temporary folder
    os.rmdir(temp_loc)
    print 'Modifying the configuration file...'
    with open(ploc, 'w') as file:
        file.writelines([hashed(sha256, key), '\n', loc])
    print success, 'Password has been changed!'
    return loc, key
