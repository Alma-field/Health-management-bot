import os
from flask import Blueprint, Response, abort, url_for

from Config import STATIC_BPNAME, ALLOWED_EXTENSIONS

static = Blueprint(STATIC_BPNAME, __name__)

@static.route("/css/<path:file_name>",methods=['GET'])
def css(file_name=''):
	if os.path.isfile(f'static/css/{file_name}.css'):
		with open(f'static/css/{file_name}.css',"rb")as file:
			css_text = file.read()
	else:
		file_name=''
		abort(404)
	file_name = ''
	return Response(css_text, mimetype='text/css')

@static.route("/js/<path:file_name>",methods=['GET'])
def js(file_name=''):
	if os.path.isfile(f'static/js/{file_name}.js'):
		with open(f'static/js/{file_name}.js',"rb")as file:
			js_text = file.read()
	else:
		file_name=''
		abort(404)
	file_name = ''
	return Response(js_text, mimetype='text/javascript')

@static.route("/images/<path:file_name>",methods=['GET'])
def images(file_name=''):
	#if pfile_name:
	#	file_name = f'product/{pfile_name}'
	#	pfile_name = ''
	#print(url_for('images', file_name=file_name))
	extend = file_name.split('.')[-1].lower()
	#print(extend)
	if extend not in ALLOWED_EXTENSIONS:
		file_name = ''
		abort(404)
	if extend in ['png','gif','bmp']:
		minetype = f'image/{extend}'
	elif extend in ['jpeg','jpg']:
		minetype = 'image/jpeg'
	elif extend == 'svg':
		minetype = 'image/svg+xml'
	elif extend == 'ico':
		minetype = 'image/vnd.microsoft.icon'
	#print(minetype)
	if os.path.isfile(f'static/images/{file_name}'):
		if minetype == 'image/jpeg':
			f_name = file_name.split('.')
			f_name[-2] += '_noexif'
			f_name = '.'.join(f_name)
			#print(not os.path.isfile(f'static/images/{f_name}'))
			if not os.path.isfile(f'static/images/{f_name}'):
				img_tmp = Image.open(f'static/images/{file_name}')
				#exif情報取得
				exifinfo = img_tmp._getexif()
				#exif情報からOrientationの取得
				if exifinfo is not None:
					orientation = exifinfo.get(0x112, 1)
					#画像を回転
					img_tmp_rotate = rotateImage(img_tmp, orientation)
					#回転した画像を保存（元の画像に上書き）
					img_tmp_rotate.save(f'static/images/{f_name}')
				else:
					f_name = file_name
			with open(f'static/images/{f_name}',"rb")as file:
				image = file.read()
		else:
			with open(f'static/images/{file_name}',"rb")as file:
				image = file.read()
	else:
		file_name = ''
		abort(404)
	file_name = ''
	response = Response(mimetype=minetype)
	response.set_data(image)
	return response

###################画像回転
def rotateImage(img, orientation):
	"""
	画像ファイルをOrientationの値に応じて回転させる
	"""
	#orientationの値に応じて画像を回転させる
	if orientation == 1:
		img_rotate = img
	elif orientation == 2:
		#左右反転
		img_rotate = img.transpose(Image.FLIP_LEFT_RIGHT)
	elif orientation == 3:
		#180度回転
		img_rotate = img.transpose(Image.ROTATE_180)
	elif orientation == 4:
		#上下反転
		img_rotate = img.transpose(Image.FLIP_TOP_BOTTOM)
	elif orientation == 5:
		#左右反転して90度回転
		img_rotate = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_90)
	elif orientation == 6:
		#270度回転
		img_rotate = img.transpose(Image.ROTATE_270)
	elif orientation == 7:
		#左右反転して270度回転
		img_rotate = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270)
	elif orientation == 8:
		#90度回転
		img_rotate = img.transpose(Image.ROTATE_90)
	else:
		pass
	return img_rotate
