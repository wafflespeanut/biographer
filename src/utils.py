import inspect, os, sys, ctypes
from datetime import datetime, timedelta
from timeit import default_timer as timer

filename = inspect.getframeinfo(inspect.currentframe()).filename    # this sweetsauce should work for all cases
exec_path = os.path.dirname(os.path.abspath(filename))

prefix = {'win32': ''}.get(sys.platform, 'lib')
ext = {'darwin': '.dylib', 'win32': '.dll'}.get(sys.platform, '.so')
rustlib_path = os.path.join(os.path.dirname(exec_path), 'target', 'release', prefix + 'biographer' + ext)

# tirelessly provide datetimes along with optional progress
def date_iter(date_start, date_end = datetime.now(), progress = True):
    total = (date_end - date_start).days + 1      # include the final day
    for i in xrange(total):
        if progress:
            yield (date_start + timedelta(i), i + 1, total, int((float(i + 1) / total) * 100))
        else:
            yield date_start + timedelta(i)

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
