from flask import Blueprint, make_response, render_template

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
