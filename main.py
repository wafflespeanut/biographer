import inspect, os, sys
from src import session as sess

filename = inspect.getframeinfo(inspect.currentframe()).filename    # this sweetsauce should work for all cases
path = os.path.dirname(os.path.abspath(filename))

load_list = ["core.py", "cipher.py", "options.py", "search.py"]
map(execfile, map(lambda string: os.path.join(path, "src", string), load_list))
_name, args = sys.argv[0], map(lambda string: string.strip('-'), sys.argv[1:])

# [Conventions used here]
# file_tuple = (file_path, formatted_datetime) returned by hash_date()
# data_tuple = (file_contents, key) returned by protect()
# file_data = list(word_counts) for each file sorted by date, returned by the searching functions

def chain_args(args):
    try:
        option, value = args[0].split('=')
    except ValueError:
        option = args[0]
    # CHECKLIST
    return None

if __name__ == '__main__':  # there are a hell lot of `try...except`s for smoother experience
    session = sess.Session()
    if session.loop:
        sess.clear_screen()

    try:
        if args and session.loop:
            option = chain_args(args)
            if option:
                exec(option)        # `exec` is a nice hack to achieve wonderful things in Python
                exit('\n')
            print sess.error, 'Invalid arguments! Continuing with default...'
    except (KeyboardInterrupt, EOFError):
        sleep(sess.capture_wait)
        exit('\n')

    while session.loop:     # Main loop
        try:
            print '\n\t(Press Ctrl-C to get back to the main menu any time!)'
            if 'linux' not in sys.platform:
                print '\n\t### This program runs best on Linux terminal ###'
            choices = ("\n\tWhat do you wanna do?\n",
                        " 1: Write today's story",
                        " 2: Random story",
                        " 3: View the story of someday",
                        " 4. Write the story for someday you've missed",
                        # " 5. Search your stories",
                        # " 6. Backup your stories",
                        # " 7. Change your password",
                        # " 8. Reconfigure your diary",
                        # " 9. Encrypt a story",    # in case the script quits before encrypting a story
                        " 0. Exit the biographer",)
            print '\n\t\t'.join(choices)
            options =  ("write(session)",     # just to remember the password throughout the session
                        "random(session)",
                        "view(session.key, hash_date(session.location))",
                        "write(session, hash_date(session.location, True))",
                        # "search(session)",
                        # "backup(session)",
                        # "change_pass(session)",
                        # "session.reconfigure()",
                        "try_encrypt(session.key, hash_date(session.location))")    # hidden choice
            try:
                ch = int(raw_input('\nChoice: '))
                if ch == 0:
                    session.loop = False
                    break
                exec(options[int(ch) - 1])
                session.loop = True if raw_input('\nDo something again (y/n)? ') == 'y' else False
            except (ValueError, IndexError):        # invalid input
                print sess.error, "Please enter a valid input! (between 0 and %s)" % len(options)
                sleep(2)
            except (KeyboardInterrupt, EOFError):   # interrupted input
                sleep(sess.capture_wait)
        except Exception as err:       # An uncaught exception (which has probably creeped all the way up here)
            try:
                print sess.error, err, 'Ah, something bad has happened! Maybe this is a bug, or try reconfiguring your diary?'
                sleep(2)
            except (KeyboardInterrupt, EOFError):       # just to not quit while displaying
                sleep(sess.capture_wait)
        except (KeyboardInterrupt, EOFError):
            # EOFError was added just to make this script work on Windows (honestly, Windows sucks!)
            sleep(sess.capture_wait)
        if session.loop:
            sess.clear_screen()
    if not session.loop:
        print '\nGoodbye...\n'
