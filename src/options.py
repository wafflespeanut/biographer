import shutil
from datetime import datetime, timedelta
from hashlib import sha256
from random import random as randgen, choice as rchoice

from hashlib import sha256
from src.story import hasher

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

def backup(session, backup_loc = None):
    if not backup_loc:
        print '\nBacking up to Desktop...'
        backup_loc = '~/Desktop'
    abs_path = os.path.join(os.path.expanduser(backup_loc), datetime.now().strftime('My Diary (%Y-%m-%d})'))
    shutil.make_archive(abs_path, 'zip', session.location)

def change_pass(session):
    sess.clear_screen()
    old_key, old_loc = session.key[:], session.location[:]

    try:
        assert sess.write_access(session.location)
        print "\nLet's change your password..."
        temp_name = str(randgen())[2:]
        temp_loc = os.path.join(os.path.dirname(session.location.rstrip(os.sep)), temp_name)
        session.get_pass(hasher(sha256, old_key), check_against = old_key)
        new_key = session.key[:]
        while True:
            try:
                print sess.warning, "Moving the stories to a working directory (always have some precautions!)...\n"
                shutil.copytree(session.location, temp_loc)
                session.location = temp_loc
                break
            except IOError:
                print sess.error, "Couldn't get write access to the path!"
                while True:
                    working_dir = os.path.expanduser(raw_input('Enter a path to choose as working directory: '))
                    if old_loc.rstrip(os.sep) == os.path.dirname(working_dir.rstrip(os.sep)):
                        print sess.error, "Working directory shouldn't share the location of your stories!"
                    else: break
                temp_loc = os.path.join(working_dir, temp_name)

        total = (datetime.now() - session.birthday).days + 1    # accounting the last day
        for i in range(total):
            day = session.birthday + timedelta(i)
            progress = int((float(i + 1) / total) * 100)
            session.key = old_key
            story_old = Story(session, day)
            session.key = new_key
            story_new = Story(session, day)
            if story_old.get_path():
                try:
                    story_old.decrypt(overwrite = True)     # well, both are working on the same file really!
                    story_new.encrypt(echo = False)
                    sys.stdout.write('\r  Processing files... %d%s (%d/%d days)' % (progress, '%', i + 1, total))
                    sys.stdout.flush()
                except AssertionError:
                    print sess.error, "This file couldn't be decrypted! (filename hash: %s)\
                                       \nResolve it before changing the password again..." % story_old.get_hash()
                    raise AssertionError

    except (AssertionError, KeyboardInterrupt, EOFError):
        session.key, session.location = old_key, old_loc
        sleep(sess.capture_wait)
        if os.path.exists(temp_loc):
            shutil.rmtree(temp_loc)
        print sess.error, 'Interrupted! Failed to change the password!'
        return

    shutil.rmtree(old_loc)
    session.key, session.location = new_key, old_loc
    print "\n\nOverwriting the existing stories..."
    os.rename(temp_loc, old_loc)
    print 'Modifying the configuration file...'
    session.write_to_config_file()
    print sess.success, 'Password has been changed!'
