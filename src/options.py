import os, sys, shutil
from datetime import datetime, timedelta
from hashlib import sha256
from random import random as randgen, choice as rchoice
from time import sleep

import session as sess
from story import Story, hasher
from utils import DateIterator

def random(session):    # Useful only when you have a lot of stories (obviously)
    story_dates = session.find_stories(return_on_first_story = False)
    if story_dates:
        story = Story(session, rchoice(story_dates))
        story.view()
    print sess.error, 'There are no stories in the given location!'

def backup(session, backup_loc = None):
    try:
        if not (backup_loc and sess.write_access(os.path.expanduser(backup_loc))):
            backup_loc = '~/Desktop'
        abs_path = os.path.join(os.path.expanduser(backup_loc), datetime.now().strftime('My Diary (%F)'))
        print '\nBacking up to %s...' % abs_path
        shutil.make_archive(abs_path, 'zip', session.location)
    except (KeyboardInterrupt, EOFError):
        sleep(sess.capture_wait)
        print sess.error, 'Interrupted!'
        if os.path.exists(abs_path + '.zip'):
            os.remove(abs_path + '.zip')

def change_pass(session, is_arg = False):
    sess.clear_screen()
    old_key, old_loc = session.key[:], session.location[:]

    try:
        assert sess.write_access(session.location)
        print "\nLet's change your password..."
        temp_name = 'BIOGRAPHER_' + str(randgen())[2:]
        temp_loc = os.path.join(os.path.dirname(session.location.rstrip(os.sep)), temp_name)
        # If we're changing the password through command, then there's no reason for asking the existing one twice!
        key_hash = None if is_arg else hasher(sha256, old_key)
        session.get_pass(key_hash, check_against = old_key)
        new_key = session.key[:]
        while True:
            try:
                print sess.warning, 'Copying your stories to a temporary working directory (%s)...' % temp_loc
                shutil.copytree(session.location, temp_loc)
                session.location = temp_loc
                break
            except (OSError, IOError):
                print sess.error, "Couldn't get write access to the path!"
                while True:
                    working_dir = os.path.expanduser(raw_input('Enter a path to choose as working directory: '))
                    if old_loc.rstrip(os.sep) == os.path.dirname(working_dir.rstrip(os.sep)):
                        print sess.error, "Working directory shouldn't share the location of your stories!"
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
