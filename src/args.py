import sys
from time import sleep

from options import backup, change_pass, random
from search import search
from session import Session
from stats import stats
from story import Story
from utils import CAPTURE_WAIT, ERROR, SlowPrinter, clear_screen

help_string = '''
USAGE: python /path/to/biographer [OPTIONS]

NOTE: Formatting works only on Unix-based OS
      (Windows doesn't conform to standards)

help            Print this help message
write [=YYYY-MM-DD] (default: today)
                Write a story for a given date
view [=YYYY-MM-DD] (default: today)
                View a story written on a given date
random          View a random story
stats [=speed] (default: 30)
                Show the statistics of your diary
                (based on how fast you type - 'speed' in words/min)
- lang [=py|rs] - Whether to use Python or the Rust library
configure       Reconfigure (reset) your diary
change-pass     Change your diary's password
backup [=path] (default: Desktop)
                Zip your diary folder to a given location
encrypt [=YYYY-MM-DD]
                Encrypt an accidentally decrypted story
search [=word]  Search for a given word (with optional arguments)
- lang [=py|rs] - Whether to use Python or the Rust library
- start [=YYYY-MM-DD] (default: your diary's birthday)
                - Search from this date
- end [=YYYY-MM-DD] (default: today)
                - Search until this date
- ugly          - Just show the stories and occurrences
                  (shorthand for `grep=0`)
- grep [=N] (default: 7)
                - Pretty print the region containing your word
                - [N] words surrounding the search word
                  (size of the region to print)
'''

help_string = '\n  '.join(help_string.split('\n'))      # FIXME: this should be a decorator

def create_session():
    sys.stdout = SlowPrinter()
    sys.stdout.set_mode(1)
    session = Session()
    if session.loop:
        clear_screen()
        return session
    exit('\nGoodbye...\n')

def split_arg(arg):
    thing = arg.split('=')
    opt, val = thing[0], thing[1] if len(thing) == 2 else None
    val = None if val and val.lower() in ['none', '""', "''"] else val
    return opt, val

def analyse_args(args):
    try:
        option, value = split_arg(args[0])
    except IndexError:
        return create_session()

    allowed_opts = {
        # these don't take any value, and don't respond if an invalid value is passed
        'help': 'print (help_string)',
        'configure': 'Session(is_bare = True).reconfigure()',
        'change-pass': 'change_pass(create_session(), is_arg = True)',
        'random': 'random(create_session())',
        # these demand one value (`backup` requires a valid location, while the other three require a datetime format)
        'write': 'Story(create_session(), when = value, is_write = True).write()',
        'view': 'Story(create_session(), when = value, check_path = True).view()',
        'backup': 'backup(create_session(), backup_loc = value)',
        'encrypt': 'Story(create_session(), when = value, check_path = True).encrypt()',
    }

    try:
        if option == 'search':      # special handling for `search`
            args.extend(['lang=None', 'start=start', 'end=end', 'grep'])
            options, values = zip(*map(split_arg, args))
            grep_val = '0' if 'ugly' in options else values[options.index('grep')]
            search(session = create_session(),
                   word = value,
                   lang = values[options.index('lang')],
                   start = values[options.index('start')],
                   end = values[options.index('end')],
                   grep = int(grep_val) if grep_val and grep_val.isdigit() else 7)      # '7' is rather smooth
        elif option == 'stats':     # ... and `stats`
            args.extend(['lang=None'])
            options, values = zip(*map(split_arg, args))
            stats(session = create_session(),
                  speed = int(value) if value and value.isdigit() else None,
                  lang = values[options.index('lang')])
        else:
            exec(allowed_opts[option])
        exit('')
    except KeyError:
        print ERROR, 'Invalid arguments! Continuing with the default...'
        return create_session()
    except (KeyboardInterrupt, EOFError):
        sleep(CAPTURE_WAIT)
        exit('\nGoodbye...\n')
