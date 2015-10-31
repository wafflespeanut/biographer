class Session(object):
    """This object has all the information required to carry out the entire session"""
    def __init__(self):
        self.reset()
        self.configure()

    def reset(self):
        self.location, self.key, self.birthday, self.loop_again = None, None, None, False

    def delete_config(self):
        if os.path.exists(ploc):
            print warning, 'Deleting configuration file...'
            os.remove(ploc)
        else:
            print error, 'Configuration file has already been removed!'
        sleep(2)        # waiting for the user to see the message (before it gets cleared)

    # Configuration for authentication (well, you have to sign-in for each session!)
    def configure(self):
        try:
            if os.path.exists(ploc):
                print '\nConfiguration file found!'
                with open(ploc, 'r') as file:
                    config = file.readlines()
                try:
                    self.location = config[1].rstrip(os.sep + '\n') + os.sep
                    assert os.path.exists(self.location)
                    self.birthday = datetime.strptime(config[2].strip(), '%Y-%m-%d')
                    self.key = check()
                    if type(key) is str:
                        self.loop_again = True
                except Exception:
                    clear_screen()
                    print '\nInvalid configuration file!'
                    self.reconfigure()
        except (KeyboardInterrupt, EOFError):
            sleep(wait)
            print '\n', error, 'Failed to authenticate!'
            self.reset()

    def reconfigure(self):
        try:
            self.delete_config()
            clear_screen()
            print "\nLet's start configuring your diary...\n"
            print 'Enter the (absolute) location for your diary...', \
                  "\n(Note that this will create a foler named 'Diary' if the path doesn't end with it)"
            self.location = raw_input('\nPath: ')
            while not write_access(self.location):
                self.location = raw_input('\nPlease enter a valid path (with write access): ')
            if not self.location.rstrip(os.sep).endswith('Diary'):      # just put everything in a folder for Diary
                self.location = os.path.join(self.location, 'Diary')
                print 'Note that this will make use of %r' % self.location
                if not os.path.exists(self.location):
                    os.mkdir(self.location)
            self.location = self.location.rstrip(os.sep) + os.sep

            while True:
                try:
                    birth = raw_input('''\
                                      \nWhen did you start writing this diary? (Press [Enter] for today)\
                                      \nDate should be of the form YYYY-MM-DD (Mind you, with hyphen!)
                                      \nDate: ''')
                    if not birth:
                        self.birthday = datetime.now()
                    else:
                        self.birthday = datetime.strptime(birth, '%Y-%m-%d')
                        date_hash = hash_format(birthday)
                        if not os.path.exists(loc + date_hash):
                            print error, "Story doesn't exist on that day! (in the given path)"
                            continue
                except ValueError:
                    print error, 'Oops! Error in input. Try again...'
                    continue
                break

            birth = '{date:%Y}-{date:%m}-{date:%d}'.format(date = birthday)
            self.key = check()
            if type(key) is not str:
                return
            with open(ploc, 'a') as file:
                file.writelines(loc + '\n' + birth)     # Store the location & birth of diary along with the password hash

            self.loop_again = True
            print "\nIf you plan to reconfigure it manually, then it's located here (%s)" % ploc
            print "And, be careful with that, because invalid configuration files will be deleted during startup!"
            sleep(3)
            raw_input('\nPress [Enter] to continue...')
        except (KeyboardInterrupt, EOFError):
            sleep(wait)
            self.reset()