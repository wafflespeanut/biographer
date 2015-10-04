import inspect, os, sys

filename = inspect.getframeinfo(inspect.currentframe()).filename    # this sweetsauce should work for all cases
path = os.path.dirname(os.path.abspath(filename))

ploc = os.path.join(os.path.expanduser('~'), '.diary')              # config location (absolute)
load_list = ["core.py", "cipher.py", "options.py", "search.py"]
map(execfile, map(lambda string: os.path.join(path, "src", string), load_list))
_name, args = sys.argv[0], map(lambda string: string.strip('-'), sys.argv[1:])

# [Conventions used here]
# fileTuple = (file_path, formatted_datetime) returned by hashDate()
# dataTuple = (file_contents, key) returned by protect()
# fileData = list(word_counts) for each file sorted by date, returned by the searching functions

wait = (0.1 if sys.platform == 'win32' else 0)
# these 100ms sleep times at every KeyboardInterrupt is the workaround for catching EOFError properly in Windows

def chain_args(args):
    option = args[0]
    arg_options = {
        'backup': {'backupStories': ['loc']},
        'search': {'key = search': ['key', 'birthday']},
        'random': {'key = random': ['key', 'birthday']},
    }

    try:
        f_invoker, f_args = arg_options[option].popitem()   # it's safe because all keys have a dict of single key
        return '{}({})'.format(f_invoker, ', '.join(f_args))
    except KeyError:
        return None

if __name__ == '__main__':  # there are a hell lot of `try...except`s for smoother experience
    loc, key, birthday, choice = configure()
    # 'birthday' of the diary is important because random stories and searching is based on that

    try:
        if args and choice == 'y':
            option = chain_args(args)
            if option:
                exec(option)
                exit('\n')
            print error, 'Invalid arguments! Continuing with default...'
    except (KeyboardInterrupt, EOFError):
        sleep(wait)
        exit('\n')

    while choice == 'y':        # Main loop
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
            if 'linux' not in sys.platform:
                print '\n### This program runs best on Linux terminal ###'
            choices = ("\n\tWhat do you wanna do?\n",
                        " 1: Write today's story",
                        " 2: Random story",
                        " 3: View the story of someday",
                        " 4. Write the story for someday you've missed",
                        " 5. Search your stories",
                        " 6. Backup your stories",
                        " 7. Change your password",
                        " 8. Reconfigure your diary",
                        " 0. Exit the biographer",)
            print '\n\t\t'.join(choices)
            options =   ("key = write(key)",     # just to remember the password throughout the session
                        "key = random(key, birthday)",
                        "key = temp(hashDate(), key)",
                        "key = write(key, hashDate())",
                        "key = search(key, birthday)",
                        "backupStories(loc)",
                        "loc, key = changePass(key)",
                        "loc, key, birthday, choice = configure(True)",)
            try:
                ch = int(raw_input('\nChoice: '))
                if ch == 0:
                    choice = 'n'
                    break
                exec(options[int(ch) - 1])
                choice = raw_input('\nDo something again (y/n)? ')
            except (ValueError, IndexError):        # invalid input
                print error, "Please enter a valid input! (between 0 and %s)" % len(options)
                sleep(2)
            except (KeyboardInterrupt, EOFError):   # interrupted input
                sleep(wait)
        except Exception:       # An uncaught exception (which has probably creeped all the way up here)
            try:
                print error, 'Ah, something bad has happened! Maybe this is a bug, or try reconfigure your diary?'
                sleep(2)
            except (KeyboardInterrupt, EOFError):       # just to not quit while displaying
                sleep(wait)
        except (KeyboardInterrupt, EOFError):
            # EOFError was added just to make this script work on Windows (honestly, Windows sucks!)
            sleep(wait)
    if choice is not 'y':
        print '\n\nGoodbye...\n'
