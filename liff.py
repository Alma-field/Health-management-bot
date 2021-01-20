from flask import Blueprint, make_response, render_template

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

@liff.route('/helth')
def helth():
	response = make_response(render_template(f'{LIFF_BPNAME}/Helth.html'))
	response = make_response(render_template(f'{LIFF_BPNAME}/v1-sample.html'))
	return response
