import sys
from time import sleep

from src.args import analyse_args
from src.options import random, backup, change_pass
from src.search import search
from src.stats import stats
from src.story import Story
from src.utils import CAPTURE_WAIT, ERROR, SlowPrinter, clear_screen


if __name__ == '__main__':
    _name, args = sys.argv[0], map(lambda string: string.strip('-'), sys.argv[1:])
    session = analyse_args(args)

    sys.stdout = SlowPrinter()      # hack for printing at variety of rates at certain code points
    sys.stdout.set_mode(1)

    while session.loop:     # Main loop (there are a hell lot of `try...except`s for smoother experience)
        try:
            sys.stdout.set_mode(3, 0.03)
            print '\n  (Press Ctrl-C to get back to the main menu any time!)'
            if 'linux' not in sys.platform:
                print '\n  ### This program runs best on Linux terminal ###'
            print '\n  What do you wanna do?\n'

            choices = {     # how the option will be displayed, and its corresponding executable line
                1: ("Write today's story", 'Story(session, "today").write()'),
                2: ("Random story", 'random(session)'),
                3: ("View the story of someday", 'Story(session, check_path = True).view()'),
                4: ("Write (or append to) the story of someday", 'Story(session, is_write = True).write()'),
                5: ("Search your stories", 'search(session)'),
                6: ("Backup your stories", 'backup(session)'),
                7: ("Change your password", 'change_pass(session)'),
                8: ("Reconfigure your diary", 'session.reconfigure()'),
                9: ("Encrypt an accidentally decrypted story", 'Story(session, check_path = True).encrypt()'),
                0: ("View your statistics", 'stats(session)'), }

            for i in range(1, len(choices)) + [0]:
                print '%s%d. %s' % (' ' * 6, i, choices[i][0])

            try:
                sys.stdout.set_mode(1)
                ch = raw_input('\n  (Press [Enter] to exit)\n\nChoice: ')
                if not ch:
                    session.loop = False
                    break

                exec(choices[int(ch)][1])   # `exec` is a nice hack to achieve wonderful things in Python
                assert session.loop         # check whether we should quit earlier
                session.loop = True if raw_input('\nDo something again (y/n)? ') == 'y' else False

            # This only checks whether the `loop` value is modified - all other AssertionErrors are handled elsewhere
            except AssertionError:
                break
            except (ValueError, KeyError):      # invalid input
                print ERROR, "Please enter a valid input! (between 0 and %s)" % (len(choices) - 1)
                sleep(2)
            except (KeyboardInterrupt, EOFError):   # interrupted input
                sleep(CAPTURE_WAIT)

        except Exception as err:       # An uncaught exception (which has probably creeped all the way up here)
            try:
                print ERROR, err, '\nAh, something bad has happened! Maybe try reconfiguring your diary?'
                sleep(2)
            except (KeyboardInterrupt, EOFError):   # just to not quit while displaying
                sleep(CAPTURE_WAIT)
        except (KeyboardInterrupt, EOFError):
            # EOFError was added just to make this script work on Windows (honestly, Windows sucks!)
            sleep(CAPTURE_WAIT)

        if session.loop:
            clear_screen()

    if not session.loop:
        print '\nGoodbye...\n'
