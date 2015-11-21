from time import sleep

import session as sess
from options import backup, change_pass, random
from story import Story

help_string = '''
USAGE: python /path/to/biographer [OPTIONS]

NOTE: All date values should be of the form YYYY-MM-DD.
Some options can have sub-options, which are shown with indentation.
Formatting works only on Unix-based OS (Windows doesn't conform to standards)

help            Print this help message
write [=date]   Write a story for a given date (default: today)
view [=date]    View a story written on a given date (default: today)
random          View a random story
configure       Reconfigure (reset) your diary
change-pass     Change your diary's password
backup [=location] (default: Desktop)
                Backup to a given location
encrypt [=date]
                Encrypt an accidentally decrypted story
search [=word]  Search for a given word (with optional arguments)

  lang [=python|rust]
                Whether to use Python or the Rust library
  begin [=date] (default: your diary's birthday)
                Search from this date
  end [=date] (default: today)
                Search until this date

  format [=red|green|blue|skyblue|violet|black|white|bold|italic|strike|underline]
                Format for marking the words after searching (default: skyblue)

  ugly          Just show the stories and occurrences
  pretty [=format] (default: red)
                Show the precise sentence which contains your word
    grep [=N] (default: 7)
                Number of words that should be extracted surrounding
                the search word while pretty printing
'''

help_string = '\n  '.join(help_string.split('\n'))

def create_session():
    session = sess.Session()
    if session.loop:
        sess.clear_screen()
        return session
    exit('\nGoodbye...\n')

def analyse_args(args):
    try:
        option, value = args[0].split('=')
    except ValueError:
        option, value = args[0], None
    except IndexError:
        return create_session()

    allowed_opts = {
        # these don't take any value, and don't respond if an invalid value is passed
        'help': 'print (help_string)',
        'configure': 'sess.Session(is_bare = True).reconfigure()',
        'change-pass': 'change_pass(create_session(), is_arg = True)',
        'random': 'random(create_session())',
        # these demand one value (`backup` requires a valid location, while the other three require a datetime format)
        'write': 'Story(create_session(), when = value, is_write = True).write()',
        'view': 'Story(create_session(), when = value).view()',
        'backup': 'backup(create_session(), backup_loc = value)',
        'encrypt': 'Story(create_session(), when = value).encrypt()',
        # `search` is not done here, because it requires some special handling
    }

    try:
        exec(allowed_opts[option])
        exit('\nGoodbye...\n')
    except KeyError:
        print sess.error, 'Invalid arguments! Continuing with the default...'
        return create_session()
    except (KeyboardInterrupt, EOFError):
        sleep(sess.capture_wait)
        exit('')
