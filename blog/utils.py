import math
import re

from django.utils.html import strip_tags


def count_words(html_string):
    return len(re.findall(r'\w+', strip_tags(html_string)))


def get_read_time(html_string):
    """ round up value to the nearest minute. 200 wpm """
    return int(math.ceil(count_words(html_string) / 200))
