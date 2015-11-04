import shutil
from getpass import getpass
from hashlib import sha256
from random import random as randgen, choice as rchoice

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
        print sess.error, "There are no stories in the given location!"
        return
    for i in range(10):
        file_tuple = find_story(session.location, rchoice(range(num_stories)), session.birthday)
        if file_tuple:
            return view(session.key, file_tuple)
    print '\nPerhaps, this may not be a valid path?'

def backup(session, bloc = None):
    if not bloc:
        print '\nBacking up to Desktop...'
        bloc = '~/Desktop'
    zloc = os.path.join(os.path.expanduser(bloc), "My Diary ({d:%Y}-{d:%m}-{d:%d})".format(d = datetime.now()))
    shutil.make_archive(zloc, 'zip', session.location)

def change_pass(session):   # Exhaustive method to change the password
    sess.clear_screen()
    birth = '{date:%Y}-{date:%m}-{date:%d}'.format(date = session.birthday)

    print "\nLet's change your password..."
    if not getpass('\nOld password: ') == session.key:
        print sess.error, 'Wrong password!'
        return
    new_key = getpass('New password: ')
    if new_key == session.key:
        print sess.error, 'Both passwords are the same!'
        return
    while not getpass('Re-enter new password: ') == new_key:
        print sess.error, "Passwords don't match!\n"
        new_key = getpass('New password: ')

    try:
        sess.clear_screen()
        print sess.warning, "Working... (Your stories are vulnerable now, so don't go away!)"
        loc_stripped = session.location.rstrip(os.sep)
        temp_name = str(randgen())[2:]
        temp_loc = os.path.join(os.path.dirname(loc_stripped), temp_name)
        while True:
            temp_stripped = temp_loc.rstrip(os.sep)
            if os.path.dirname(temp_stripped) == loc_stripped:
                print "Ensure that the working directory is not within your diary's directory!"
            elif os.access(os.path.dirname(temp_stripped), os.W_OK):
                break
            working_dir = os.path.expanduser(raw_input('Enter a path to choose as working directory: '))
            temp_loc = os.path.join(working_dir, temp_name)
        shutil.copytree(session.location, temp_loc)     # always have some precautions!
        files = os.listdir(temp_loc)
        total = len(files)

        print
        for i, File in enumerate(files):
            progress = int((float(i + 1) / total) * 100)
            if not protect(os.path.join(temp_loc, File), 'w', session.key):
                shutil.rmtree(temp_loc)
                print sess.error, "This file couldn't be decrypted! (filename hash: %s)\
                                   \nResolve it before changing the password again..." % File
                return
            sys.stdout.write('\rDecrypting using old key... %d%s (%d/%d)' % (progress, '%', i + 1, total))
            sys.stdout.flush()

        print
        for i, File in enumerate(files):
            progress = int((float(i + 1) / total) * 100)
            protect(os.path.join(temp_loc, File), 'e', new_key)
            sys.stdout.write('\rEncrypting using new key... %d%s (%d/%d)' % (progress, '%', i + 1, total))
            sys.stdout.flush()

    except (KeyboardInterrupt, EOFError):
        sleep(sess.capture_wait)
        if os.path.exists(temp_loc):
            shutil.rmtree(temp_loc)
        print sess.error, 'Interrupted! Failed to change the password!'
        return

    if os.access(session.location, os.W_OK):
        shutil.rmtree(session.location)
    else:
        shutil.rmtree(temp_loc)
        print sess.error, 'Directory is read-only! Failed to change the password!'
        return
    print "\nOverwriting the existing stories... (Please don't interrupt now!)"
    os.rename(temp_loc, session.location)
    print 'Modifying the configuration file...'
    with open(session.config_location, 'w') as file_data:
        file_data.writelines('\n'.join([hashed(sha256, new_key), session.location, birth]))
    print sess.success, 'Password has been changed!'
    session.key = new_key
