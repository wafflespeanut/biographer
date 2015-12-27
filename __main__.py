import sys
from time import sleep

from src import session as sess
from src.args import analyse_args
from src.options import random, backup, change_pass
from src.search import search
from src.stats import stats
from src.story import Story

if __name__ == '__main__':
    _name, args = sys.argv[0], map(lambda string: string.strip('-'), sys.argv[1:])
    session = analyse_args(args)

    while session.loop:     # Main loop (there are a hell lot of `try...except`s for smoother experience)
        try:
            print '\n\t(Press Ctrl-C to get back to the main menu any time!)'
            if 'linux' not in sys.platform:
                print '\n\t### This program runs best on Linux terminal ###'
            print '\n\tWhat do you wanna do?\n'
            choices = {     # how the option will be displayed, and its corresponding executable line
                1: ("Write today's story", 'Story(session, "today").write()'),
                2: ("Random story", 'random(session)'),
                3: ("View the story of someday", 'Story(session).view()'),
                4: ("Write (or append to) the story of someday", 'Story(session, is_write = True).write()'),
                5: ("Search your stories", 'search(session)'),
                6: ("Backup your stories", 'backup(session)'),
                7: ("Change your password", 'change_pass(session)'),
                8: ("Reconfigure your diary", 'session.reconfigure()'),
                9: ("View your statistics", 'stats(session)'),
                # hidden choice (in case the script somehow quits before encrypting a story)
                10: ("Encrypt a story", 'Story(session).encrypt()'),
                0: ("Exit the biographer", '') }
            for i in range(1, len(choices) - 1) + [0]:
                print '\t\t%d. %s' % (i, choices[i][0])

            try:
                ch = int(raw_input('\nChoice: '))
                if ch == 0:
                    session.loop = False
                    break
                exec(choices[ch][1])    # `exec` is a nice hack to achieve wonderful things in Python
                assert session.loop
                session.loop = True if raw_input('\nDo something again (y/n)? ') == 'y' else False
            # This only checks whether the `loop` value is modified - all other AssertionErrors are handled elsewhere
            except AssertionError:
                break
            except (ValueError, KeyError):      # invalid input
                print sess.error, "Please enter a valid input! (between 0 and %s)" % (len(choices) - 1)
                sleep(2)
            except (KeyboardInterrupt, EOFError):   # interrupted input
                sleep(sess.capture_wait)
        except Exception as err:       # An uncaught exception (which has probably creeped all the way up here)
            try:
                print sess.error, err, '\nAh, something bad has happened! Maybe try reconfiguring your diary?'
                sleep(2)
            except (KeyboardInterrupt, EOFError):   # just to not quit while displaying
                sleep(sess.capture_wait)
        except (KeyboardInterrupt, EOFError):
            # EOFError was added just to make this script work on Windows (honestly, Windows sucks!)
            sleep(sess.capture_wait)
        if session.loop:
            sess.clear_screen()
    if not session.loop:
        print '\nGoodbye...\n'
