from datetime import datetime

import session as sess
from search import build_paths
from story import Story
from utils import DateIterator, ffi_channel, simple_counter

def rusty_stats(session):
    list_to_send = build_paths(session, date_start = session.birthday, date_end = datetime.now())
    count_string, timing = ffi_channel(list_to_send, mode = 0)
    return sum(map(int, count_string.split(' ')))

def py_stats(session):      # FIXME: shares a lot of code with `py_search` - refactor them out!
    word_count, no_stories = 0, 0
    date_iter = DateIterator(date_start = session.birthday)
    for i, day in date_iter:
        try:
            story = Story(session, day)
            if not story.get_path():
                no_stories += 1
                continue
            data = story.decrypt()
            word_count += simple_counter(data)
            date_iter.send_msg('[Total words: %s]' % word_count)
        except AssertionError:
            errors += 1
            if errors > 10:
                print sess.error, "More than 10 files couldn't be decrypted! Terminating the search..."
                return None
    assert no_stories < (i + 1)
    return word_count
