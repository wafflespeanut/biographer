import ctypes
from datetime import datetime, timedelta
from timeit import default_timer as timer

prefix = {'win32': ''}.get(sys.platform, 'lib')
ext = {'darwin': '.dylib', 'win32': '.dll'}.get(sys.platform, '.so')
rust_lib = os.path.join(path, 'target', 'release', prefix + 'biographer' + ext)    # Library location (relative)
# And, you'll be needing the Nightly rust, because the library depends on a future method and a deprecated method

# Finds the file name using the timedelta from the birth of the diary to a specified date
def find_story(location, delta, date_start):
    stories = len(os.listdir(location))
    date = date_start + timedelta(days = delta)
    file_tuple = hash_date(location, date.year, date.month, date.day)
    return file_tuple

# Grabs the absolute paths of stories for a given datetime and timedelta objects
def grab_stories(location, delta, date):
    file_data = [], []
    for i in range(delta):
        file_tuple = find_story(location, i, date)
        if not file_tuple: continue
        file_data[0].append(file_tuple[0])
        file_data[1].append(file_tuple[1])
    return file_data

# Exhaustive process (that's why I've written a Rust library for this!)
# The library accelerates this search by about ~100 times!
def py_search(session, date_start, date_end, word):
    occurrences, errors, no_stories = [], 0, 0
    start = timer()
    for day, n, total, progress in options.date_iter(date_start, date_end):
        occurred, story = [], Story(session, day)
        try:
            if not story.get_path():
                no_stories += 1
                continue
            data = story.decrypt()
            idx, jump, data_len = 0, len(word), len(data)
            while idx < data_len:   # probably an inefficient way to find the word indices
                idx = data.find(word, idx)
                if idx == -1: break
                occurred.append(idx)
                idx += jump
        except AssertionError:
            errors += 1
            if errors > 10:
                print sess.error, "More than 10 files couldn't be decrypted! Terminating the search..."
                return [], (timer() - start)
        if occurred and occurred[0] > 0:    # "n - 1" indicates the Nth day from the birthday
            occurrences.append((n - 1, len(occurred), occurred))
        sum_value = sum(map(lambda stuff: stuff[1], occurrences))
        sys.stdout.write('\r  Progress: %d%s (%d/%d) [Found: %d]' % (progress, '%', n, total, sum_value))
        sys.stdout.flush()
    print
    assert no_stories < total
    return occurrences, (timer() - start)

def rusty_search(session, date_start, date_end, word):      # FFI for giving the searching job to Rust
    path_list = []
    for day, n, total, progress in options.date_iter(date_start, date_end):
        file_path = Story(session, day).get_path()
        if file_path:
            path_list.append(file_path)
        sys.stdout.write('\rBuilding the path list... %d%s (%d/%d)' % (progress, '%', n, total))
        sys.stdout.flush()
    assert path_list

    print '\nSending the paths to the Rust FFI...'
    lib = ctypes.cdll.LoadLibrary(rust_lib)
    list_to_send = path_list[:]
    list_to_send.extend((session.key, word))

    # send an array pointer full of strings (like a pointer to ['blah', 'blah', 'blah'])
    lib.get_stuff.argtypes = (ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t)
    lib.get_stuff.restype = ctypes.c_void_p         # type declarations must be done or else, segfault!
    lib.kill_pointer.argtypes = [ctypes.c_void_p]

    start = timer()     # Timer begins once we send the proper data to Rust
    c_array = (ctypes.c_char_p * len(list_to_send))(*list_to_send)
    c_pointer = lib.get_stuff(c_array, len(list_to_send))       # sending the list (as C-array) to Rust..
    count_string = ctypes.c_char_p(c_pointer).value
    lib.kill_pointer(c_pointer)     # sending the pointer back to Rust for destruction!
    stop = timer()      # Timer ends here, because we don't wanna include Python's parsing time

    occurrences = []
    print 'Parsing the data stream from Rust...'
    for i, string in enumerate(count_string.split(' ')):    # spaces in the data stream represents individual files
        idx = map(int, string.split(':'))       # ... and colons represent the indices where the word has occurred
        # Rust fills the indices of the file paths with the number of occurrences
        # So, "i" indicates the Nth from the birthday
        if idx[0] > 0:
            occurrences.append((i, len(idx), idx))
    return occurrences, (stop - start)

def find_line_boundary(text, idx, limit, direction_value):  # find the closest boundary of text for a given limit
    i, num = idx, 0
    while text[i + direction_value] not in ('\n', '\t'):
        if text[i] == ' ': num += 1
        if num == limit: return i
        i += direction_value
    return i

def search(session, grep = 7):      # Invokes both the searching functions
    sess.clear_screen()
    word = raw_input("\nEnter a word: ")
    while True:
        choices = ('Search everything! (Python)',
                   'Search between two dates (Python)',
                   'Search everything! (using the Rust library)')
        if not os.path.exists(rust_lib):
            choices = choices[:-1]
        try:
            choice = int(raw_input('\n\t' + '\n\t'.join(['%d. %s' % (i + 1, opt) for i, opt in enumerate(choices)]) \
                                   + '\n\nChoice: '))
            if choice - 1 not in range(len(choices)):
                raise ValueError    # Because we also encounter ValueError if you enter other characters
            else: break
        except ValueError:
            print sess.error, 'Invalid choice!'
    if choice == 1 or (choice == 3 and len(choices) > 2):
        d1 = session.birthday
        d2 = datetime.now()
    while choice == 2:
        try:
            print '\nEnter dates in the form YYYY-MM-DD (Mind you, with hyphen!)'
            d1 = datetime.strptime(raw_input('Start date: '), '%Y-%m-%d')
            d2 = raw_input("End date (Press [Enter] for today's date): ")
            if not d2: d2 = datetime.now()
            else: d2 = datetime.strptime(d2, '%Y-%m-%d')
        except ValueError:
            print sess.error, 'Oops! Error in input. Try again...'
            continue
        break
    delta = (d2 - d1).days
    print '\nSearching the past %d days...\n' % (delta + 1)

    try:
        file_data = grab_stories(session.location, delta, d1)   # has both file location and the formatted datetime
        if choice in (1, 2):
            occurrences, timing = py_search(session, d1, d2, word)
        else:
            occurrences, timing = rusty_search(session, d1, d2, word)
    except AssertionError:
        print sess.error, 'There are no stories in the given location!'
        return

    jump, num_stories = len(word), len(occurrences)
    total_count = sum(map(lambda stuff: stuff[1], occurrences))
    print sess.success, 'Done! Time taken: %s seconds! (%d occurrences in %d stories!)' \
                   % (timing, total_count, num_stories)
    if not total_count:
        print sess.error, "Bummer! There are no stories containing '%s'..." % word
        return

    def print_stuff(grep):
        results_begin = '\nSearch results from {} to {}:'.format(d1.strftime('%B %d, %Y'), d2.strftime('%B %d, %Y')) + \
                        "\n\nStories on these days have the word '%s' in them...\n" % word
        if grep:    # pretty printing the output (at the cost of decrypting time)
            try:
                start = timer()
                print results_begin
                for i, (n, word_count, indices) in enumerate(occurrences):
                    colored = []
                    date = session.birthday + timedelta(n)
                    content = Story(session, date).decrypt()
                    numbers = str(i + 1) + '. ' + date.strftime('%B %d, %Y (%A)')
                    text, indices = options.mark_text(content, indices, jump)   # precisely indicate the word in text
                    for idx in indices:     # find the word occurrences
                        begin = find_line_boundary(text, idx, grep, -1)
                        end = find_line_boundary(text, idx, grep, 1)
                        sliced = '\t' + '... ' + text[begin:end].strip() + ' ...'
                        colored.append(sliced)
                    print numbers, '\n%s' % '\n'.join(colored)  # print the numbers along with the word occurrences
                stop = timer()
            except (KeyboardInterrupt, EOFError):
                sleep(sess.capture_wait)
                grep = 0
                sess.clear_screen()
                print "\n Yep, it takes time! Let's go back to the good ol' days...\n"

        if not grep:    # Yuck, but cleaner way to print the results
            print results_begin
            for i, (n, word_count, _indices) in enumerate(occurrences):
                date = session.birthday + timedelta(n)
                numbers = ' ' + str(i + 1) + '. ' + date.strftime('%B %d, %Y (%A)')
                spaces = 40 - len(numbers)
                print numbers, ' ' * spaces, '[ %s ]' % word_count  # print only the datetime and counts in each file

        print '\n%s %sFound a total of %d occurrences in %d stories!%s\n' % \
              (sess.success, options.fmt('Y'), total_count, num_stories, options.fmt())
        print '  %sTime taken for searching: %s%s seconds!%s' % \
              (options.fmt('B2'), options.fmt('G'), timing, options.fmt())
        if grep:
            print '  %sTime taken for pretty printing: %s%s seconds!%s' \
                  % (options.fmt('B2'), options.fmt('G'), stop - start, options.fmt())

    print_stuff(grep)
    while occurrences:
        try:
            print '\nEnter a number to see the corresponding story...'
            print "(Enter 'pretty' or 'ugly' to print those search results again, or press [Enter] to exit)"
            ch = raw_input('\nInput: ')
            if ch == 'pretty':
                print_stuff(grep)
                continue
            elif ch == 'ugly':
                print_stuff(None)
                continue
            elif not ch or int(ch) - 1 < 0:
                return
            else:
                n_day, word_count, indices = occurrences[int(ch) - 1]
                date = session.birthday + timedelta(n_day)
                (data, start, end) = Story(session, date).view(return_text = True)
                print start, options.mark_text(data, indices, jump, 'B1')[0], end
        except (ValueError, IndexError):
            print sess.error, 'Oops! Bad input...'
