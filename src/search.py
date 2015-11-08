import ctypes
from datetime import timedelta
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

def py_search(key, files, word):    # Exhaustive process (that's why I've written a Rust library for this!)
    occurrences, errors, total = [], 0, len(files)  # The library accelerates this search by about ~230 times!
    start = timer()
    for i, File in enumerate(files):
        progress = int((float(i + 1) / total) * 100)
        occurred = []
        data_tuple = protect(File, 'd', key)
        if data_tuple:
            data, key = data_tuple
            idx, jump = 0, len(word)
            while idx < len(data):              # probably inefficient
                idx = data.find(word, idx)
                if idx == -1: break
                occurred.append(idx)
                idx += jump
        else:
            errors += 1
            if errors > 10:
                print "\nMore than 10 files couldn't be decrypted! Terminating the search..."
                return ([(0, 0)], (timer() - start))
            continue
        if occurred and occurred[0] > 0:
            occurrences.append((len(occurred), occurred))
        else:
            occurrences.append((0, occurred))
        sum_value = sum(map(lambda elem: elem[0], occurrences))
        sys.stdout.write('\r  Progress: %d%s (%d/%d) [Found: %d]' \
                         % (progress, '%', i + 1, total, sum_value))
        sys.stdout.flush()
    print
    return occurrences, (timer() - start)

def rusty_search(key, path_list, word):           # FFI for giving the searching job to Rust
    lib = ctypes.cdll.LoadLibrary(rust_lib)
    list_to_send = path_list[:]
    list_to_send.extend((key, word))

    # send an array pointer full of strings (like a pointer to ['blah', 'blah', 'blah'])
    lib.get_stuff.argtypes = (ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t)     # type declarations must be done
    lib.get_stuff.restype = ctypes.c_void_p                                         # or else, segfault!
    lib.kill_pointer.argtypes = [ctypes.c_void_p]

    start = timer()
    c_array = (ctypes.c_char_p * len(list_to_send))(*list_to_send)
    c_pointer = lib.get_stuff(c_array, len(list_to_send))       # sending the list (as C-array) to Rust..
    count_string = ctypes.c_char_p(c_pointer).value
    lib.kill_pointer(c_pointer)     # sending the pointer back to Rust for destruction!
    occurrences = []
    for i in count_string.split(' '):
        idx = map(int, i.split(':'))
        l = len(idx) if idx[0] > 0 else 0
        occurrences.append((l, idx))
    stop = timer()
    return occurrences, (stop - start)

def find_nearest(text, idx, limit, dir_value):      # find the closest boundary of text for a given limit
    i, num = idx, 0
    while text[i + dir_value] not in ('\n', '\t'):
        if text[i] == ' ': num += 1
        if num == limit: return i
        i += dir_value
    return i

def search(session, grep = 7):      # Invokes both the searching functions
    sess.clear_screen()
    word = raw_input("\nEnter a word: ")
    jump = len(word)
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
    print '\nSearching %d stories...\n' % delta

    try:
        file_data = grab_stories(session.location, delta, d1)   # has both file location and the formatted datetime
        if choice in (1, 2):
            occurrences, timing = py_search(session.key, file_data[0], word)
        else:
            occurrences, timing = rusty_search(session.key, file_data[0], word)
        word_count, indices = zip(*occurrences)
    except ValueError:
        print sess.error, 'There are no stories in the given location!'
        return
    # splitting into tuple pairs for later use (only if there exists a non-zero word count)
    results = [(file_data[0][i], file_data[1][i], indices[i]) for i, count in enumerate(word_count) if count]
    total_count, num_stories = sum(word_count), len(results)
    print sess.success, 'Done! Time taken: %s seconds! (%d occurrences in %d stories!)' \
                   % (timing, total_count, num_stories)
    if not total_count:
        print sess.error, 'Bummer! No matching words...'
        return

    if grep:                # pretty printing the output (at the cost of decrypting time)
        try:
            print "\nSearch results from {d1:%B} {d1:%d}, {d1:%Y} to {d2:%B} {d2:%d}, {d2:%Y}:".format(d1 = d1, d2 = d2)
            print "\nStories on these days have the word '%s' in them...\n" % word
            start = timer()
            for i, data in enumerate(results):
                colored = []
                numbered = str(i + 1) + '. ' + data[1]      # numbered datetime results
                contents, _key = protect(results[i][0], 'd', session.key)
                text, indices = mark_text(contents, data[2], jump)
                for idx in indices:
                    begin = find_nearest(text, idx, grep, -1)
                    end = find_nearest(text, idx, grep, 1)
                    sliced = '\t' + '... ' + text[begin:end].strip() + ' ...'
                    colored.append(sliced)
                print numbered, '\n', '%s' % '\n'.join(colored)
            stop = timer()
        except (KeyboardInterrupt, EOFError):
            sleep(sess.capture_wait)
            grep = 0
            sess.clear_screen()
            print "Yep, it takes time! Let's go back to the good ol' days..."

    if not grep:
        print "\nSearch results from {d1:%B} {d1:%d}, {d1:%Y} to {d2:%B} {d2:%d}, {d2:%Y}:".format(d1 = d1, d2 = d2)
        print "\nStories on these days have the word '%s' in them...\n" % word
        for i, data in enumerate(results):
            numbered = str(i + 1) + '. ' + data[1]      # numbered datetime results
            spaces = 40 - len(numbered)                 # some formatting for the counts
            print numbered, spaces * ' ', '[ %s ]' % len(data[2])      # print only the datetime and counts in each file

    print '\n%s %sFound a total of %d occurrences in %d stories!%s\n' \
           % (sess.success, fmt('Y'), total_count, num_stories, fmt())
    print '  %sTime taken for searching: %s%s seconds!%s' % (fmt('B2'), fmt('G'), timing, fmt())
    if grep:
        print '  %sTime taken for pretty printing: %s%s seconds!%s' % (fmt('B2'), fmt('G'), stop - start, fmt())

    while file_data:
        try:
            ch = int(raw_input("\nEnter the number to see the corresponding story ('0' to exit): "))
            if not ch: return
            # I could've used the `protect()`, but I needed the number of display format (you know, DRY)
            file_tuple, indices = (results[ch - 1][0], results[ch - 1][1]), results[ch - 1][2]
            _key, (data, start, end) = view(session.key, file_tuple, True)
            print start, mark_text(data, indices, jump, 'B1')[0], end
        except Exception:
            print sess.error, 'Oops! Bad input...'
