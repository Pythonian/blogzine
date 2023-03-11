import math
import re

from django.utils.html import strip_tags

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


def mk_paginator(request, items, num_items):
    """
    Function to paginate querysets.

    :param request: The current request object
    :param items: The queryset to be paginated
    :param num_items: The number of items to be displayed per page
    :return: A paginated queryset
    """
    paginator = Paginator(items, num_items)
    page = request.GET.get('page', 1)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, return the first page.
        items = paginator.page(1)
    except EmptyPage:
        # If page is out of range, return the last page of results.
        items = paginator.page(paginator.num_pages)
    return items


def count_words(html_string):
    return len(re.findall(r'\w+', strip_tags(html_string)))


def get_read_time(html_string):
    """ round up value to the nearest minute. 200 wpm """
    return int(math.ceil(count_words(html_string) / 200))
