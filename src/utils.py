import inspect, os, sys, ctypes
from datetime import datetime, timedelta
from timeit import default_timer as timer

filename = inspect.getframeinfo(inspect.currentframe()).filename    # this sweetsauce should work for all cases
exec_path = os.path.dirname(os.path.abspath(filename))

prefix = {'win32': ''}.get(sys.platform, 'lib')
ext = {'darwin': '.dylib', 'win32': '.dll'}.get(sys.platform, '.so')
rustlib_path = os.path.join(os.path.dirname(exec_path), 'target', 'release', prefix + 'biographer' + ext)

def simple_counter(story_data):   # simple word counter (which ignores the timestamps)
    stamp_count = 0
    split_data = story_data.split()
    for word in split_data:
        if word[0] == '[':
            try:
                timestamp = datetime.strptime(word, '[%Y-%m-%d]')
                stamp_count += 2        # "2" for both date and time
            except ValueError:
                pass
    return len(split_data) - stamp_count

# You'll be needing the Nightly rust for compiling the library
# because the library depends on a future method and a deprecated method

# Currently, mode is one of the following:
# 0     =>  Statistics
# 1     =>  Search

def ffi_channel(list_to_send, mode):
    print '\nSending the paths to the Rust FFI...'
    lib = ctypes.cdll.LoadLibrary(rustlib_path)
    # send an array pointer full of strings (like a pointer to ['blah', 'blah', 'blah'])
    lib.get_stuff.argtypes = (ctypes.POINTER(ctypes.c_char_p), ctypes.c_size_t, ctypes.c_uint)
    lib.get_stuff.restype = ctypes.c_void_p         # type declarations must be done or else, segfault!
    lib.kill_pointer.argtypes = [ctypes.c_void_p]
    length = len(list_to_send)

    start = timer()     # Timer begins once we send the proper data to Rust
    c_array = (ctypes.c_char_p * length)(*list_to_send)
    c_pointer = lib.get_stuff(c_array, length, mode)    # sending the list (as C-array) to Rust..
    string_result = ctypes.c_char_p(c_pointer).value
    lib.kill_pointer(c_pointer)     # sending the pointer back to Rust for destruction!
    stop = timer()      # Timer ends here, because we don't wanna include Python's parsing time
    return string_result, (stop - start)

def force_input(input_val, input_msg, error, func = lambda s: s):
    # force the user to enter an input (with an optional function to check the given input)
    if not input_val:
        input_val = func(raw_input(input_msg))
        while not input_val:
            print error
            input_val = func(raw_input(input_msg))
    return input_val

def get_lang(lang, error, warning):
    # get language from user if it's not passsed as a command-line argument
    def check_lang(input_val):
        return 'p' if input_val in ['p', 'py', 'python'] else 'r' if input_val in ['r', 'rs', 'rust'] else None

    lang = force_input(check_lang(lang),
                       '\nSearch using Python (or) Rust libarary (py/rs)? ',
                       error + ' Invalid choice!',
                       check_lang)
    if lang == 'r' and not os.path.exists(rustlib_path):
        print warning, "Rust library not found! (Please ensure that it's in the `target/release` folder)"
        print 'Falling back to the default search using Python...'
        lang = 'p'
    return lang

class DateIterator(object):
    '''Tireless generator to provide datetimes along with optional progress display'''
    def __init__(self, date_start, date_end = datetime.now(), progress_msg = '  Progress: %s'):
        self._idx = 0
        assert type(date_start) is datetime and type(date_end) is datetime, 'expected datetime object for dates!'
        self._date = date_start
        self._bound = (date_end - date_start).days + 1      # include the final day
        # The `progress_msg` string should have a '%s' to indicate where the progress should be printed
        self._progress_msg = progress_msg
        self._tail_msg = ''
        if progress_msg:
            print   # just to isolate the progress

    def __iter__(self):
        return self

    def next(self):
        idx, date = self._idx, self._date
        self._idx += 1
        self._date += timedelta(1)
        if self._progress_msg:
            progress = '%d%% (%d/%d)' % (int((float(idx + 1) / self._bound) * 100), idx, self._bound)
            sys.stdout.write('\r%s %s' % (self._progress_msg % progress, self._tail_msg))
            sys.stdout.flush()
        if self._idx <= self._bound:
            return (idx, date)
        else:
            if self._progress_msg:
                print
            raise StopIteration

    def send_msg(self, msg):
        '''Send a string to the iterator to append it to the progress'''
        assert type(msg) is str, 'message should be a string!'
        self._tail_msg = msg
