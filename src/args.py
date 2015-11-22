from time import sleep

import session as sess
from options import backup, change_pass, random
from search import search
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

  lang [=py|rs]
                Whether to use Python or the Rust library
  start [=date] (default: your diary's birthday)
                Search from this date
  end [=date] (default: today)
                Search until this date

  ugly          Just show the stories and occurrences (shorthand for `grep=0`)
  grep [=N] (default: 7)
                Pretty print the precise region containing your word
                Extract [N] words surrounding the search word while printing
'''

help_string = '\n  '.join(help_string.split('\n'))

def create_session():
    session = sess.Session()
    if session.loop:
        sess.clear_screen()
        return session
    exit('\nGoodbye...\n')

def split_arg(arg):
    thing = arg.split('=')
    opt, val = thing[0], thing[1] if len(thing) == 2 else None
    val = None if val in ['0', 'None', '""', "''"] else val
    return opt, val

def analyse_args(args):
    try:
        option, value = split_arg(args[0])
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
    }

    try:
        if option == 'search':      # special handling for `search`
            args.extend(['lang=None', 'start=start', 'end=end', 'grep'])
            options, values = zip(*map(split_arg, args))
            grep_val = values[options.index('grep')] if 'ugly' not in options else '0'
            grep_val = grep_val if grep_val else 7      # '7' is rather smooth
            search_args = dict(session = create_session(),
                               word = value,
                               lang = values[options.index('lang')],
                               start = values[options.index('start')],
                               end = values[options.index('end')],
                               grep = int(grep_val))
            search(**search_args)
        else:
            exec(allowed_opts[option])
        exit('')
    except KeyError:
        print sess.error, 'Invalid arguments! Continuing with the default...'
        return create_session()
    except (KeyboardInterrupt, EOFError):
        sleep(sess.capture_wait)
        exit('\nGoodbye...\n')
