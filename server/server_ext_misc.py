from quart import Blueprint, render_template

routes_misc = Blueprint('routes_misc', __name__)

@routes_misc.route('/misc/yesno')
async def popup_yes_no():
    return await render_template('tpl_widget_yesno_popup.html')