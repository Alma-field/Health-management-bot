from datetime import date

from flask import Blueprint, make_response, render_template, request, abort, redirect, url_for, current_app
from linebot.models import TextSendMessage

import pandas as pd
from math import pi

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, CrosshairTool, DatetimeTickFormatter
from bokeh.models.annotations import Span, Label
from bokeh.embed import components

from Config import ADMIN_BPNAME

admin = Blueprint(ADMIN_BPNAME, __name__)

@admin.route('/list')
def ShowList():
	result, names = current_app.db.get_newest_health_data()
	today = date.today()
	config = current_app.db.get_config()
	for i in range(len(result)):
		result[i].append((config[0] and result[i][3] >= config[1]) or (config[2] and result[i][4:].count(True) >= config[3]))
	response = make_response(render_template(f'{ADMIN_BPNAME}/List.html', result=result, names=names, today=today, config=config))
	return response

@admin.route('/user/<cache>')
def ShowUser(cache):
	name = current_app.db.get_name_by_cache(cache)
	results = current_app.db.get_user_health_data(cache)
	config = current_app.db.get_config()
	script, div = create_graph(results, config)
	response = make_response(render_template(f'{ADMIN_BPNAME}/User.html', script=script, div=div, results=results, name=name, count=results['exist'].count(True)))
	return response

@admin.route('/config', methods=['GET', 'POST'])
def ConfigSetting():
	if request.method in ['GET', 'HEAD']:
		config = current_app.db.get_config()
		response = make_response(render_template(f'{ADMIN_BPNAME}/Config.html', config=config))
	else:
		config = []
		config.append(request.form.get('temperature_check', 'false') == 'true')
		config.append(float(request.form.get('temperature', '37.5')))
		config.append(request.form.get('question_check', 'false') == 'true')
		config.append(int(request.form.get('question', '1')))
		current_app.db.set_config(config)
		response = redirect(url_for(f'{ADMIN_BPNAME}.ShowList'))
	return response

def create_graph(results, config):
	# Bokeh描画用データ
	df = pd.DataFrame(results, columns=['id', 'date', 'temperature', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'Y/N', 'exist'])
	source = ColumnDataSource(df)

	# 描画レイアウト
	p = figure(
		title=f"体温変化",
		plot_width=750,
		plot_height=400,
		x_axis_type="datetime",
		x_range=(df['date'][0], df['date'][df['date'].size-1]),
		y_range=(35.0, 39.0),
		x_axis_label="日付",
		y_axis_label="体温",
		#https://docs.bokeh.org/en/latest/docs/user_guide/tools.html#configuring-plot-tools
		tools="save, reset"#xpan, xwheel_pan, xwheel_zoom : ypan, ywheel_pan, ywheel_zoom
	)

	# X軸の設定
	x_format = "%Y/%m/%d"
	formatter = DatetimeTickFormatter(
		seconds=[x_format],
		minutes=[x_format],
		hours=[x_format],
		days=[x_format],
		months=[x_format],
		years=[x_format]
	)
	p.xaxis.formatter = formatter
	p.xaxis.major_label_orientation = pi/4

	if config[0]:
		#基準体温
		nowspan = Span(location=config[1], dimension="width", line_color="#e49e61", line_width=1)
		p.add_layout(nowspan)
		nowlabel = Label(x=p.x_range.start, y=config[1], text=f"基準体温", text_color="#000000", background_fill_color="#e49e61", render_mode="css", text_font_size="10px")
		p.add_layout(nowlabel)

	# メインチャート
	line = p.line('date', 'temperature', source=source, line_width=2)
	p.circle('date', 'temperature', source=source, line_width=5)

	# 吹き出し
	hover = HoverTool(
		tooltips=[
			("日付", "@date{"+x_format+"}"),
			("体温", "@temperature{00.0}")
		],
		formatters={"@date": "datetime"},
		mode="vline",
		renderers=[line]
	)
	#hover.renderers.append(line)
	p.add_tools(hover)

	# マウスの位置に縦棒を表示
	cross_hair = CrosshairTool(
		dimensions="height",
		line_alpha=0.2
	)
	p.add_tools(cross_hair)

	# FlaskでHTML上に表示するためにBokehのライブラリで生成されたJavaScriptとdiv要素を返す
	return components(p)
