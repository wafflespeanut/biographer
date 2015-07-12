# [Functions in other modules]
# temp(), hashDate(), protect() - core.py

import ctypes
from timeit import default_timer as timer

prefix = {'win32': ''}.get(sys.platform, 'lib')
ext = {'darwin': '.dylib', 'win32': '.dll'}.get(sys.platform, '.so')
rustLib = "target/release/" + prefix + 'biographer' + ext       # Library location (relative)
# And, you'll be needing Nightly rust (v1.3.0), because this library depends on a future method

def findStory(delta, birthday):     # Finds the file name using the timedelta from the birth of the diary to a specified date
    stories = len(os.listdir(loc))
    d = birthday + timedelta(days = delta)
    fileTuple = hashDate(d.year, d.month, d.day)
    if not fileTuple:
        return None
    return fileTuple

def grabStories(delta, date):       # Grabs the story paths for a given datetime and timedelta objects
    fileData = [], []
    for i in range(delta):
        fileTuple = findStory(i, date)
        if fileTuple == None:
            continue
        fileData[0].append(fileTuple[0])
        fileData[1].append(fileTuple[1])
    return fileData

def pySearch(key, files, word):     # Exhaustive process (that's why I've written a Rust library for this!)
    occurrences = []                # Rust is about ~230 times faster than Python (in this searching)
    displayProg, printed = 0, False
    total = len(files)
    start = timer()
    for i, File in enumerate(files):
        progress = int((float(i + 1) / total) * 100)
        if progress is not displayProg:
            displayProg = progress
            printed = False
        occurred = 0
        dataTuple = protect(File, 'd', key)
        if dataTuple:
            data, key = dataTuple
            occurred = data.count(word)
        else:
            print warning, 'Cannot decrypt story! Skipping... (filename hash: %s)\n' % File.split(os.sep)[-1]
        occurrences.append(occurred)
        if not printed:
            print 'Progress: %d%s \t(Found: %d)' % (displayProg, '%', sum(occurrences))
            printed = True
    stop = timer()
    return occurrences, (stop - start)

def rustySearch(key, pathList, word):           # FFI for giving the searching job to Rust
    if not os.path.exists(rustLib):
        print error, 'Rust library not found!'
        return [0] * len(pathList), 0
    lib = ctypes.cdll.LoadLibrary(rustLib)
    list_to_send = pathList[:]
    list_to_send.extend((key, word))

    # send an array pointer full of strings (like a pointer to ['blah', 'blah', 'blah'])
    lib.get_stuff.argtypes = (ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t)     # type declarations must be done
    lib.get_stuff.restype = ctypes.c_void_p                                         # or else, segfault!
    lib.kill_pointer.argtypes = [ctypes.c_void_p]

    start = timer()
    c_array = (ctypes.c_char_p * len(list_to_send))(*list_to_send)
    print 'Sending the list (as C-array) to Rust...'
    c_pointer = lib.get_stuff(c_array, len(list_to_send))
    count_string = ctypes.c_char_p(c_pointer).value
    print 'Got the string. Sending the pointer back for destruction...'
    lib.kill_pointer(c_pointer)     # sending the pointer back to Rust for destruction
    occurrences = [int(i) for i in count_string.split(' ')]
    stop = timer()
    return occurrences, (stop - start)

def search(key, birthday):          # this invokes the other two searching functions and gathers their output
    word = raw_input("Enter a word: ")
    choice = 0
    while choice not in (1, 2, 3):
        choices = ('\n\t1. Search everything! (Python)',
                    '2. Search between two dates (Python)',
                    '3. Search everything! (Rust)')
        choice = int(raw_input('\n\t'.join(choices) + '\n\nChoice: '))
    if choice in (1, 3):
        d1 = birthday
        d2 = datetime.now()
    while choice == 2:
        try:
            print '\nEnter dates in the form YYYY-MM-DD (Mind you, with hyphen!)'
            d1 = datetime.strptime(raw_input('Start date: '), '%Y-%m-%d')
            d2 = raw_input("End date (Press [Enter] for today's date): ")
            if not d2:
                d2 = datetime.now()
            else:
                d2 = datetime.strptime(d2, '%Y-%m-%d')
        except ValueError:
            print error, 'Oops! Error in input. Try again...'
            continue
        break
    delta = (d2 - d1).days
    print '\nDecrypting %d stories...\n' % delta
    fileData = grabStories(delta, d1)               # has both file location and the formatted datetime
    if choice in (1, 2):
        wordCount, timing = pySearch(key, fileData[0], word)
    else:
        wordCount, timing = rustySearch(key, fileData[0], word)
    print "\nSearch results from {d1:%B} {d1:%d}, {d1:%Y} to {d2:%B} {d2:%d}, {d2:%Y}.".format(d1 = d1, d2 = d2)
    if sum(wordCount):
        print "\nStories on these days have the word '%s' in them...\n" % word
    else:
        print '\nTime taken:', timing, 'seconds!\n\nBummer! No matching words...'
        return key
    # splitting into tuple pairs for later use (only if there exists a non-zero word count)
    results = [(fileData[0][i], fileData[1][i]) for i, count in enumerate(wordCount) if count]
    for i, data in enumerate(results):
        print str(i + 1) + '. ' + data[1]           # print only the datetime
    print '\nTime taken:', timing, 'seconds!'
    print success, 'Found %d occurrences in %d stories!\n' % (sum(wordCount), len(results))
    while fileData:
        try:
            ch = int(raw_input("Enter the number to see the corresponding story ('0' to exit): "))
            if ch == 0:
                return key
            temp((results[ch-1][0], results[ch-1][1]), key)
        except Exception:
            print error, 'Oops! Bad input...\n'
    return key
