from flask import render_template
from markupsafe import Markup

from models.models_lump import Board, Session


def get_paging_widget(selected_page:int=0, span:int=3, skip=10) -> 'str':
    """
    :param selected_page: currently selected page. Min value is 0
    :param span: how many buttons should be on each side of the selected button. Total buttons count will be span*2+1
    :param skip: For special buttons that can go to selected_page - skip or selected_page + skip page number
    :return: rendered html template for paging. Pages count starts from 1
    """
    start = max(selected_page - span, 0) + 1
    count = span * 2 + 1 + start
    return Markup(render_template('tpl_widget_paging.html', pages=range(start, count), start_page=selected_page+1, skip=skip))

def get_boards_all(session=None):
    auto_close = False
    if session is None:
        session = Session()

    items = session.query(Board).all()

    out = Markup(render_template('tpl_widget_boards_all.html', boards=items))
    if auto_close:
        session.close()
    return out

if __name__ == '__main__':
    print(__name__)