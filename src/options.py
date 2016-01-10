import os, shutil
from datetime import datetime, timedelta
from hashlib import sha256
from random import random as randgen, choice as rchoice
from time import sleep

from story import Story, hasher
from utils import CAPTURE_WAIT, ERROR, SUCCESS, WARNING
from utils import DateIterator, clear_screen, write_access

def random(session):    # useful only when you have a lot of stories (obviously)
    days = range((datetime.now() - session.birthday).days + 1)
    for i in range(10):     # try 10 times
        _story_exists, date = session.find_stories(session.birthday + timedelta(rchoice(days)))
        if not date:
            break
        story = Story(session, date)
        if story.get_path():
            return story.view()
    print ERROR, 'Looks like there are no stories in the given location!'

def backup(session, backup_loc = None):
    try:
        if not (backup_loc and write_access(os.path.expanduser(backup_loc))):
            backup_loc = '~/Desktop'
        abs_path = os.path.join(os.path.expanduser(backup_loc), datetime.now().strftime('My Diary (%Y-%m-%d)'))
        print '\nBacking up to %s...' % abs_path
        shutil.make_archive(abs_path, 'zip', session.location)
    except (KeyboardInterrupt, EOFError):
        sleep(CAPTURE_WAIT)
        print ERROR, 'Interrupted!'
        if os.path.exists(abs_path + '.zip'):
            os.remove(abs_path + '.zip')

def change_pass(session, is_arg = False):
    clear_screen()
    old_key, old_loc = session.key[:], session.location[:]

    try:
        assert write_access(session.location)
        print "\nLet's change your password..."
        temp_name = 'BIOGRAPHER_' + str(randgen())[2:]
        temp_loc = os.path.join(os.path.dirname(session.location.rstrip(os.sep)), temp_name)
        # If we're changing the password through command, then there's no reason for asking the existing one twice!
        key_hash = None if is_arg else hasher(sha256, old_key)
        session.get_pass(key_hash, check_against = old_key)
        new_key = session.key[:]
        while True:
            try:
                print WARNING, 'Copying your stories to a temporary working directory (%s)...' % temp_loc
                shutil.copytree(session.location, temp_loc)
                session.location = temp_loc
                break
            except (IOError, OSError):
                print ERROR, "Couldn't get write access to the path!"
                while True:
                    working_dir = os.path.expanduser(raw_input('Enter a path to choose as working directory: '))
                    if old_loc.rstrip(os.sep) == os.path.dirname(working_dir.rstrip(os.sep)):
                        print ERROR, "Working directory shouldn't share the location of your stories!"
                    else: break
                temp_loc = os.path.join(working_dir, temp_name)

        for _i, day in DateIterator(date_start = session.birthday, progress_msg = '  Processing files: %s'):
            session.key = old_key
            story_old = Story(session, day)
            session.key = new_key
            story_new = Story(session, day)
            try:
                if story_old.get_path():
                    story_old.decrypt(overwrite = True)     # well, both are working on the same file really!
                    story_new.encrypt(echo = False)
            except AssertionError:
                print ERROR, "This file couldn't be decrypted! (filename hash: %s)" % story_old.get_hash(), \
                      "\nResolve it before changing the password again..."
                raise AssertionError

    except (AssertionError, KeyboardInterrupt, EOFError):
        session.key, session.location = old_key, old_loc
        sleep(CAPTURE_WAIT)
        if os.path.exists(temp_loc):
            shutil.rmtree(temp_loc)
        print ERROR, 'Interrupted! Failed to change the password!'
        return

    shutil.rmtree(old_loc)
    session.key, session.location = new_key, old_loc
    print "\n\nOverwriting the existing stories..."
    os.rename(temp_loc, old_loc)
    print 'Modifying the configuration file...'
    session.write_to_config_file()
    print SUCCESS, 'Password has been changed!'
