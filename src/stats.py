from datetime import datetime

from search import build_paths
from story import Story
from utils import date_iter, ffi_channel, simple_counter

def rusty_stats(session):
    list_to_send = build_paths(session, date_start = session.birthday, date_end = datetime.now())
    count_string, timing = ffi_channel(list_to_send, mode = 0)
    print '\nTotal number of words:', sum(map(int, count_string.split(' ')))
