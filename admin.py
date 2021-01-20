from sys import version_info

if version_info.minor >= 9:
	from datetime import date
	from zoneinfo import ZoneInfo
	JST = ZoneInfo("Asia/Tokyo")
else:
	from datetime import date, timedelta, timezone
	JST = timezone(timedelta(hours=+9), 'JST')

from flask import Blueprint, make_response, render_template, request, abort, redirect, current_app
from linebot.models import TextSendMessage

from Config import ADMIN_BPNAME

admin = Blueprint(ADMIN_BPNAME, __name__)

@admin.route('/list')
def ShowList():
	result, names = current_app.db.get_newest_helth_data()
	today = date.today()
	print(result[0][2], today, result[0][2] == today)
	response = make_response(render_template(f'{ADMIN_BPNAME}/List.html', result=result, names=names, today=today))
	return response

@admin.route('/user/<cache>')
def ShowUser(cache):
	return 'UserPage'
