import os, json
from flask import Flask, abort, Markup, make_response, render_template

#各種設定
from Config import *

#static(images/css/js)
from static import static

#line bot
import line

#life app
from liff import liff

dbname = os.environ["DATABASE_URL"]

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = JSON_AS_ASCII
app.register_blueprint(static, url_prefix='/static')
app.register_blueprint(line.line, url_prefix='/line')
app.register_blueprint(liff, url_prefix='/liff')

try:
	setattr(app, 'db', line.db)
	setattr(app, 'line_bot_api', line.line_bot_api)
	setattr(app, 'handler', line.handler)
except:
	from sys import exit
	print('初期設定に失敗しました')
	exit()

dictionary = {}
#print(list(app.url_map.iter_rules())[0].__repr__())
for self in app.url_map.iter_rules():
	tmp = []
	for is_dynamic, data in self._trace:
		if is_dynamic:
			tmp.append(u'<%s>' % data)
		else:
			tmp.append(data)
	dictionary[(''.join(tmp).lstrip(u'|')).lstrip(u'u')] = self.endpoint
setattr(app, 'route_dictionary', dictionary)
#print(dictionary['/admin/denselect'])
del dictionary

@app.errorhandler(400)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(405)
@app.errorhandler(500)
@app.errorhandler(503)
def error_handler(error):
	if True:
		with open('templates/error/error.json', "r", encoding='utf-8')as file:
			error_json = json.load(file)[str(error.code)]
		response = make_response(render_template('error/index.html', ErrorCode=str(error.code), Summary=error_json["summary"], Detail=error_json["detail"]), error.code)
	else:
		try:
			response = make_response(render_template('error/'+str(error.code)+'.html'), error.code)
		except:
			response = make_response(render_template('error/500.html'), 500)
	return response

@app.route("/error/<int:code>",methods=['GET'])
def error(code):
	abort(code)

@app.route('/')
def RootPage():
	return 'Hello World!'

@app.route('/robots.txt')
def ShowRobots_txt():
	with open('templates/robots.txt', "r", encoding='utf-8') as file:
		text = file.read()
	return text

@app.route('/now')
def NowString():
	return app.db.now_str()

###################カスタムフィルター
@app.template_filter('linebreaksbr')
def linebreaksbr(arg):
	return Markup(arg.replace("\n", "<br>\n"))

@app.template_filter('hexstring')
def linebreaksbr(arg):
	return Markup('{:016X}'.format(arg)[-16:])

@app.template_filter('halfmask')
def halfmask(arg):
	length = int(len(arg) / 2)
	return Markup(arg[:length]+''.join(['*']*length))

@app.template_filter('stringmask')
def stringmask(arg):
	return Markup(''.join(['*']*len(arg)))

###################その他
if __name__ == '__main__':
	if debug:
		app.run(host='localhost', debug=True)#'0.0.0.0'
	else:
		port = int(os.getenv("PORT"))
		app.run(host='0.0.0.0', port=port)
