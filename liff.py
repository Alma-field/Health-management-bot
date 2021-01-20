import requests

from flask import Blueprint, make_response, render_template, request, abort

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
			print(data)
			if not data['client_id'] == '1655595024':abort(400)
			print('client_id : ok')
			url = 'https://api.line.me/v2/profile'
			headers = {'Authorization': f'Bearer {accesstoken}'}
			data = requests.get(url, headers=headers).json()
			print(data)
			print('userid : ok')
			userid = data['userId']
			print(userid)
			temperature = request.form.get('temperature', '')
			question = []
			for i in range(1,7):
				question.append(request.form.get(f'q{i}', 'false') == 'true')
			print(temperature, question)
			response = make_response(render_template(f'{LIFF_BPNAME}/HealthAccept.html'))
		else:
			abort(400)
	return response
