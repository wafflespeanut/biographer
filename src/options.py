import shutil
from random import choice as rchoice

colors = { 'R': '91', 'G': '92', 'Y': '93', 'B2': '94', 'P': '95', 'B1': '96', 'W': '97', '0': '0', }

def fmt(color = '0'):
    return {'win32': ''}.get(sys.platform, '\033[' + colors[color] + 'm')

def mark_text(text, indices, length, color = 'R'):  # Mark text and return corrected indices
    text = list(text)
    if sys.platform == 'win32':         # Damn OS doesn't even support coloring
        return text, indices
    formatter = fmt(color), fmt()
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

def random(session):    # Useful only when you have a lot of stories (obviously)
    num_stories = len(os.listdir(session.location))
    if not num_stories:
        print error, "There are no stories in the given location!"
        return
    for i in range(10):
        ch = rchoice(range(num_stories))
        file_tuple = find_story(session.location, ch, session.birthday)
        if file_tuple:
            return view(session.key, file_tuple)
    print '\nPerhaps, this may not be a valid path after all...'

def backup(loc, key, bloc = None):
    if not bloc:
        print '\nBacking up to Desktop...'
        bloc = '~/Desktop'
    zloc = os.path.join(os.path.expanduser(bloc), "{d:%Y}-{d:%m}-{d:%d}".format(d = datetime.now()))
    shutil.make_archive(zloc, 'zip', loc)
    return key      # doesn't really need the key - it's much like a pipeline for the key to pass through it

def change_pass(loc, key, birthday):      # Exhaustive method to change the password
    clear_screen()
    birth = '{date:%Y}-{date:%m}-{date:%d}'.format(date = birthday)

    print "\nLet's change your password..."
    if not getpass('\nOld password: ') == key:
        print error, 'Wrong password!'
        return key
    new_key = getpass('New password: ')
    if new_key == key:
        print error, 'Both passwords are the same!'
        return key
    while not getpass('Re-enter new password: ') == new_key:
        print error, "Passwords don't match!\n"
        new_key = getpass('New password: ')

    try:
        clear_screen()
        print warning, "Working... (Your stories are vulnerable now, so don't go away!)"
        loc_stripped = loc.rstrip(os.sep)
        temp_loc = os.path.join(os.path.dirname(loc_stripped), 'TEMP')
        while True:
            temp_stripped = temp_loc.rstrip(os.sep)
            if os.path.dirname(temp_stripped) == loc_stripped:
                print "Ensure that the working directory is not within your diary's directory!"
            elif os.access(os.path.dirname(temp_stripped), os.W_OK):
                break
            temp_loc = raw_input('Enter a path to choose as working directory: ') + os.sep + 'TEMP'
        shutil.copytree(loc, temp_loc)          # always have some precautions!
        display_prog, printed = 0, False
        files = os.listdir(temp_loc)
        total = len(files)

        print '\nDecrypting using old key...\n'
        for i, File in enumerate(files):
            progress = int((float(i + 1) / total) * 100)
            if progress is not display_prog:
                display_prog = progress
                printed = False
            key = protect(os.path.join(temp_loc, File), 'w', key)
            if key == None:
                shutil.rmtree(temp_loc)
                print error, "This file couldn't be decrypted! (filename hash: %s)\
                             \nResolve it before changing the password again..." % File
                return key
            if not printed:
                sys.stdout.write('\r  Progress: %d%s' % (display_prog, '%'))
                sys.stdout.flush()
                printed = True

        print
        display_prog, printed = 0, False
        print '\nEncrypting using the new key...\n'
        for i, File in enumerate(files):
            progress = int((float(i + 1) / total) * 100)
            if progress is not display_prog:
                display_prog = progress
                printed = False
            new_key = protect(os.path.join(temp_loc, File), 'e', new_key)
            if not printed:
                sys.stdout.write('\r  Progress: %d%s' % (display_prog, '%'))
                sys.stdout.flush()
                printed = True
    except (KeyboardInterrupt, EOFError):
        sleep(wait)
        if os.path.exists(temp_loc):
            shutil.rmtree(temp_loc)
        print error, 'Interrupted! Failed to change the password!'
        return key

    print
    if os.access(loc, os.W_OK):
        shutil.rmtree(loc)
    else:
        shutil.rmtree(temp_loc)
        print error, 'Directory is read-only! Failed to change the password!'
        return key
    print "\nOverwriting the existing stories... (Please don't interrupt now!)"
    os.rename(temp_loc, loc)
    print 'Modifying the configuration file...'
    with open(ploc, 'w') as file:
        file.writelines('\n'.join([hashed(sha256, new_key), loc, birth]))
    print success, 'Password has been changed!'
    return new_key
