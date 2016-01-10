from datetime import datetime

from search import build_paths
from story import Story
from utils import ERROR, SUCCESS
from utils import DateIterator, ffi_channel, fmt_text, get_lang, simple_counter

def rusty_stats(session):
    list_to_send = build_paths(session, date_start = session.birthday, date_end = datetime.now())
    count_string, timing = ffi_channel(list_to_send, mode = 0)
    return sum(map(int, count_string.split(' ')))

# NOTE: Another exhaustive process (just like `search`) - Rust library could be preferred
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
                print ERROR, "More than 10 files couldn't be decrypted! Terminating the search..."
                return None
    assert no_stories < (i + 1)
    return word_count

def time_calc(secs_float):
    '''Displays seconds in the form of days, hours & minutes'''
    units = [('second', 1), ('minute', 60), ('hour', 60), ('day', 24)]
    secs_int = int(secs_float)
    figures = secs_float - secs_int     # to get the float part (if any)
    time_vals = [secs_int]
    for _, factor in units:
        time_vals.append(time_vals[-1] / factor)
        time_vals[-2] %= factor
    if figures:
        time_vals[1] += round(figures, 2)   # we can safely neglect the first value, since that's '0'
    return ', '.join(map(lambda (i, val): '%s %s' % (val, units[i][0]) + ('' if val == 1 else 's'),  # ehm, plural
                         reversed(filter(lambda (i, val): True if val > 0 else False,
                                         enumerate(time_vals[1:])))))

def stats(session, speed = None, lang = None):
    lang = get_lang(lang)
    word_count = rusty_stats(session) if lang == 'r' else py_stats(session)
    print SUCCESS, fmt_text('There are {:,} words in your diary!'.format(word_count), 'yellow')
    speed = 30.0 if not speed else float(speed)
    print '\n(Assuming an average typing speed of %s words per minute)...' % int(speed)
    msg = fmt_text("\n  Approximate time you've spent on this diary: %s" , 'blue')
    print msg % fmt_text(time_calc((word_count / speed) * 60), 'green')
