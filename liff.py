import os, json
import requests
from flask import Blueprint, make_response, request, abort, current_app, render_template

from datetime import datetime

from Config import *

liff = Blueprint(LIFF_BPNAME, __name__)

@liff.route('/')
def life_toppage():
	response = make_response(render_template('liff/starter.html',title='LIFF APP'))
	return response

@liff.route('/v1')
def v1_sample():
	response = make_response(render_template('liff/v1-sample.html',title='LIFF APP'))
	return response

@liff.route('/mailsetting')
def MailSetting():
	return 'setting'

@liff.route('/maildata/<access_token>')
def GetMailData(access_token):
	url = f'https://api.line.me/oauth2/v2.1/verify?access_token={access_token}'
	response = requests.get(url)
	print(response.text)
	if response.status_code == requests.codes.ok:
		url = 'https://api.line.me/v2/profile'
		headers = {'Authorization' : f'Bearer {YOUR_CHANNEL_ACCESS_TOKEN}'}
	response = make_response(jsonify({'code':200, 'status':True}), 200)
	return response
