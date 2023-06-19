import random

from flask import render_template
from markupsafe import Markup


def get_paging_widget(selected_page:int=0, span:int=3, skip=10) -> 'str':
    """
    :param selected_page: currently selected page. Min value is 0
    :param span: how many buttons should be on each side of the selected button. Total buttons count will be span*2+1
    :param skip: For special buttons that can go to selected_page - skip or selected_page + skip page number
    :return: rendered html template for paging. Pages count starts from 1
    """
    start = max(selected_page - span, 0) + 1
    count = span * 2 + 1 + start
    salt = random.randint(100,200) # unique css selector name for querying
    return Markup(render_template('tpl_widget_paging.html', pages=range(start, count), start_page=selected_page+1, skip=skip))


if __name__ == '__main__':
    print(__name__)