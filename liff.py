import requests

from flask import Blueprint, make_response, render_template, request, abort, redirect, current_app
from linebot.models import TextSendMessage

from Config import LIFF_BPNAME

liff = Blueprint(LIFF_BPNAME, __name__)

@liff.route('/')
def life_toppage():
	response = make_response(render_template(f'{LIFF_BPNAME}/starter.html'))
	return response

@liff.route('/v1')
def v1_sample():
	response = make_response(render_template(f'{LIFF_BPNAME}/v1-sample.html'))
	return response

@liff.route('/health', methods=['GET', 'POST'])
def Health():
	if request.method in ['GET', 'HEAD']:
		response = make_response(render_template(f'{LIFF_BPNAME}/Health.html'))
	else:
		accesstoken = request.form.get('accesstoken', '')
		if not accesstoken:abort(400)
		url = f'https://api.line.me/oauth2/v2.1/verify?access_token={accesstoken}'
		response = requests.get(url)
		if response.status_code == requests.codes.ok:
			data = response.json()
			#print(data)
			if not data['client_id'] == '1655595024':abort(400)
			#print('client_id : ok')
			url = 'https://api.line.me/v2/profile'
			headers = {'Authorization': f'Bearer {accesstoken}'}
			data = requests.get(url, headers=headers).json()
			#print(data)
			#print('userid : ok')
			userid = data['userId']
			#print(userid)
			temperature = float(request.form.get('temperature', ''))
			question = []
			for i in range(1,7):
				question.append(request.form.get(f'q{i}', 'false') == 'true')
			#print(temperature, question)
			data = [temperature] + question
			cache = current_app.db.get_user_by_id(userid, key=['cache'])
			current_app.db.set_health_data(cache, data)
			config = current_app.db.get_config()
			message = '回答ありがとうございます。\n'
			if (config[0] and temperature >= config[1]) or (config[2] and question.count(True) >= config[3]):
				message += '出社することはできません。'
			else:
				message += '出社することが可能です。'
			current_app.line_bot_api.push_message(userid, TextSendMessage(text=message))
			response = redirect('https://liff.line.me/1655595024-vRM2ojo9')
		else:
			abort(400)
	return response

@liff.route('/close')
def Close():
	response = make_response(render_template(f'{LIFF_BPNAME}/HealthAccept.html'))
	return response
