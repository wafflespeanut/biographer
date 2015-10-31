import inspect, os, sys

filename = inspect.getframeinfo(inspect.currentframe()).filename    # this sweetsauce should work for all cases
path = os.path.dirname(os.path.abspath(filename))

ploc = os.path.join(os.path.expanduser('~'), '.diary')              # config location (absolute)

def write_access(path, check_path_exists = True):
    if check_path_exists and not os.path.exists(path):
        print error, "%s doesn't exist!" % path
        return False
    if not os.access(path, os.W_OK):
        print error, "Couldn't get write access to %s" % path
        return False
    return True

if not write_access(os.path.expanduser('~')):
    print error, "Couldn't get write access to home directory! Checking if the device is a mobile..."
    check_path = '/mnt/sdcard'  # QPython uses `/data` as home directory, and so let's try with `/mnt/sdcard`
    try:
        while not write_access(check_path):
            check_path = raw_input('\nEnter a path for the config file (which has write-access): ')
    except KeyboardInterrupt:
        exit("\nGoodbye...\n")
    ploc = os.path.join(check_path, '.diary')

    try:
        print warning, "If you get annoyed by this error and don't wanna do this often," \
                       + " please offer write acces to the home directory," \
                       + " move the config file from %s to your home directory (%s)" \
                       % (ploc, os.path.expanduser('~/.diary'))
        sleep(3)
        raw_input('\nPress [Enter] to continue...')
    except KeyboardInterrupt:
        pass

load_list = ["core.py", "cipher.py", "options.py", "search.py"]
map(execfile, map(lambda string: os.path.join(path, "src", string), load_list))
_name, args = sys.argv[0], map(lambda string: string.strip('-'), sys.argv[1:])

# [Conventions used here]
# file_tuple = (file_path, formatted_datetime) returned by hash_date()
# data_tuple = (file_contents, key) returned by protect()
# file_data = list(word_counts) for each file sorted by date, returned by the searching functions

wait = (0.1 if sys.platform == 'win32' else 0)
# these 100ms sleep times at every KeyboardInterrupt is the workaround for catching EOFError properly in Windows

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def chain_args(args):
    try:
        option, value = args[0].split('=')
    except ValueError:
        option = args[0]
    # CHECKLIST
    return None

if __name__ == '__main__':  # there are a hell lot of `try...except`s for smoother experience
    loc, key, birthday, choice = configure()
    # 'birthday' of the diary is important because random stories and searching is based on that
    if choice == 'y':
        clear_screen()

    try:
        if args and choice == 'y':
            option = chain_args(args)
            if option:
                exec(option)        # `exec` is a nice hack to achieve wonderful things in Python
                exit('\n')
            print error, 'Invalid arguments! Continuing with default...'
    except (KeyboardInterrupt, EOFError):
        sleep(wait)
        exit('\n')

    while choice == 'y':        # Main loop
        try:
            print '\n\t(Press Ctrl-C to get back to the main menu any time!)'
            if 'linux' not in sys.platform:
                print '\n\t### This program runs best on Linux terminal ###'
            choices = ("\n\tWhat do you wanna do?\n",
                        " 1: Write today's story",
                        " 2: Random story",
                        " 3: View the story of someday",
                        " 4. Write the story for someday you've missed",
                        " 5. Search your stories",
                        " 6. Backup your stories",
                        " 7. Change your password",
                        " 8. Reconfigure your diary",
                        # " 9. Encrypt a story",    # in case the script quits before encrypting a story
                        " 0. Exit the biographer",)
            print '\n\t\t'.join(choices)
            options =  ("key = write(key)",     # just to remember the password throughout the session
                        "key = random(loc, key, birthday)",
                        "key = view(key, hash_date())",
                        "key = write(key, hash_date(force = True))",
                        "key = search(loc, key, birthday)",
                        "key = backup(loc, key)",
                        "key = change_pass(loc, key, birthday)",
                        "loc, key, birthday, choice = configure(True)",     # hidden choice
                        "key = try_encrypt(key, hash_date())")
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
                print error, 'Ah, something bad has happened! Maybe this is a bug, or try reconfiguring your diary?'
                sleep(2)
            except (KeyboardInterrupt, EOFError):       # just to not quit while displaying
                sleep(wait)
        except (KeyboardInterrupt, EOFError):
            # EOFError was added just to make this script work on Windows (honestly, Windows sucks!)
            sleep(wait)
        if choice == 'y':
            clear_screen()
    if choice is not 'y':
        print '\n\nGoodbye...\n'
