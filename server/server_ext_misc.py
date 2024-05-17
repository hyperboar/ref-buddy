from flask import Blueprint, render_template

routes_misc = Blueprint('routes_misc', __name__)

@routes_misc.route('/misc/yesno')
def popup_yes_no():
    return render_template('tpl_widget_yesno_popup.html')