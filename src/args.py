import session as sess
from options import random, change_pass

help_string = '''
USAGE: python /path/to/biographer [OPTIONS]

NOTE: All date values should be of the form YYYY-MM-DD.
Some options can have sub-options, which are shown with indentation.

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
  date-begin [=date] (default: your diary's birthday)
                Search from this date
  date-end [=date] (default: today)
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

def no_value_error(option, value):
    if value:
        print sess.error, "'%s' doesn't take any value, but you've passed '%s'" % (option, value)

def create_session():
    session = sess.Session()
    if session.loop:
        sess.clear_screen()
    return session

def analyse_args(args):
    try:
        option, value = args[0].split('=')
    except ValueError:
        option, value = args[0], None
    except IndexError:
        return create_session()

    allowed_opts = {
        'help': 'print (help_string)',
        'configure': 'sess.Session(is_bare = True).reconfigure()',
        'change-pass': 'change_pass(create_session(), is_arg = True)',
        'random': 'random(create_session())',
    }

    try:
        exec(allowed_opts[option])
        no_value_error(option, value)
        exit('')
    except KeyError:
        print sess.error, 'Invalid arguments! Continuing with the default...'
        return create_session()
