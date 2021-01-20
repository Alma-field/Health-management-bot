import os, json
from flask import Blueprint, abort, current_app, request

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
	MessageEvent, TextMessage, ImageMessage, TextSendMessage, TemplateSendMessage,
	FlexSendMessage, CarouselTemplate, CarouselColumn, ButtonsTemplate, MessageAction,
	URIAction,  QuickReply, QuickReplyButton
)

from datetime import datetime

from Config import LINE_BPNAME, debug

#データベース
from database import line_db

from broadcast import db as mail_db, ConfirmMail

dbname = os.environ["DATABASE_URL"]
#環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

db = line_db(dbname)

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

line = Blueprint(LINE_BPNAME, __name__)

@line.route("/callback", methods=['POST'])
def callback():
	# get X-Line-Signature header value
	signature = request.headers['X-Line-Signature']
	# get request body as text
	body = request.get_data(as_text=True)
	current_app.logger.info("Request body: " + body)
	# handle webhook body
	try:
		current_app.handler.handle(body, signature)
	except InvalidSignatureError:
		abort(400)
	return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def response_replay(event):
	message = event.message.text
	userid = event.source.user_id
	username = line_bot_api.get_profile(userid).display_name
	#print(db.get_role(userid))
	if os.environ["MAINTENANCE"] == 'TRUE' and not db.get_role(userid) == 'admin':
		finish_date = os.environ["MAINTENANCE_FINISH"]
		const_message(event, ['現在メンテナンス中です...', f'終了するまでしばらくお待ちください\n(終了予定日時 : {finish_date})'])
		return None
	user_status = db.get_userstatus(userid)
	cansel = ['キャンセル', 'きゃんせる', 'cansel', '取り消す', 'とりけす', 'トリケス', '取り消し', 'とりけし', 'トリケシ', '止める', 'やめる', 'ヤメル']
	if message.lower() in cansel:
		db.set_userstatus(userid, 'home:none', username)
		const_message(event, 'キャンセルしました')
		return True
	if user_status == 'home:none':
		if message == 'template':
			response_message(event)
		elif message == 'user':
			res_user_status(event)
		elif message == 'now':
			const_message(event, f'現在は{db.now_str(string=True)}です')
		elif message == 'メール登録':
			db.set_userstatus(userid, 'mail:registration', username)
			const_message(event, 'メール通知の登録を行います。\n登録するメールアドレスを送信してください。', quick=['キャンセル'])
		elif message == 'メール解除':
			mailids = db.get_user_by_id(userid, key=['mail_address'])
			if mailids == '0,':#メールアドレスが登録されていない
				const_message(event, 'メールアドレスが登録されていません。')
			else:
				addresses = []
				for i in mailids[2:-1].split(','):
					addresses.append(f'{i} : [{mail_db.address_from_mailid(i)[1]}]')
				db.set_userstatus(userid, 'mail:release', username)
				const_message(event, ['解除するメールアドレスを選択してください。', '\n'.join(addresses)], quick=['キャンセル']+mailids[2:-1].split(','))
		else:
			parrot_message(event)
	else:
		event_of_command(event, user_status)
	#ここを通る

def event_of_command(event, command):
	userid = event.source.user_id
	username = line_bot_api.get_profile(userid).display_name
	message = event.message.text
	if command == 'home:none':
		parrot_message(event)
	elif command == 'mail:registration':
		if '@' in message:
			if mail_db.mail_exist(message):
				is_change = True
				result, mailid = mail_db.mailid_from_address(message)
				pins = mail_db.mail_pin_generate(mailid, type='change', value=f'000,')
			else:
				is_change = False
				pins = mail_db.mail_init(message, place=f'000,')
			db.set_user_by_id(userid, key=['cache'], value=[pins[1]])
			ConfirmMail(message, pins)
			db.set_userstatus(userid, 'mail:verification', username)
			const_message(event, f'「{message}」へ確認メールを送信しました。\n認証コードを送信してください。', quick=['再送', 'キャンセル'])
		else:
			const_message(event, '不正なメールアドレスです。\nもう一度メールアドレスを送信してください。', quick=['キャンセル'])
	elif command == 'mail:verification':
		onetime_code = db.get_user_by_id(userid, ['cache'])
		if message == '再送':
			result, pins, mail_address = mail_db.resend_preparation(onetime_code)
			if result:
				ConfirmMail(mail_address, pins)
				const_message(event, 'メールを再送しました。', quick=['キャンセル', '再送'])
			else:
				const_message(event, 'メールの再送に失敗しました。', quick=['キャンセル', '再送'])
		else:
			result, data = mail_db.check_from_onetimecode(onetime_code, pincode=message)
			if result:
				mailid = mail_db.mailid_from_onetimecode(onetime_code)[1]
				mail_db.update_status_and_place(mailid, 'none')
				mailids = db.get_user_by_id(userid, ['mail_address'])
				if f',{mailid},' in mailids:
					db.set_user_by_id(userid, key=['cache'], value=[''])
				else:
					#TODO メールデータベースにもユーザーIDを追加する
					db.set_user_by_id(userid, key=['mail_address', 'cache'], value=[f'{mailids}{mailid},', ''])
				db.set_userstatus(userid, 'home:none', username)
				const_message(event, 'メールアドレスを登録しました。\n通知する地点の設定は\nメニューの地点変更から行ってください。')
			else:
				const_message(event, 'コードの認証に失敗しました。\n再度確認してください。', quick=['再送'])
	elif command == 'mail:release':
		mailids = db.get_user_by_id(userid, key=['mail_address'])
		if f',{message},' in mailids:
			mailids = mailids.replace(f',{message},', ',')
			db.set_user_by_id(userid, key=['mail_address'], value=[mailids])
			address = mail_db.address_from_mailid(message)[1]
			mail_db.update_status_and_place(message, 'delete', '')
			db.set_userstatus(userid, 'home:none', username)
			const_message(event, f'[{address}]の登録を解除しました。')
		else:
			const_message(event, '値が不正です。\nもう一度送信してください。', quick=['キャンセル']+mailids[2:-1].split(','))
			return None
	else:
		db.set_userstatus(userid, 'home:none', username)
		parrot_message(event)

def command_check(command):
	try:
		if len(command.split(':')) != 2:int('error!')
		c_l = command.split(':')
	except:
		return False
	command_list = {'home':['none','hello'],'mail':['registration', 'release'],'opinion':['home']}
	return c_l[0] in command_list.keys() and c_l[1] in command_list[c_l[0]]

def const_message(event, message, quick=[]):
	userid = event.source.user_id
	send_list = []
	#print(bool(quick))
	if quick:
		q_reply = []
		for i in quick:
			q_reply.append(QuickReplyButton(action=MessageAction(label=i, text=i)))
	if type(message) is str:
		if quick:
			send_list = [TextSendMessage(text=message, quick_reply=QuickReply(items=q_reply))]
		else:
			send_list = [TextSendMessage(text=message)]
	elif type(message) is list:
		if quick:
			for i in message:
				if i == message[-1]:
					send_list.append(TextSendMessage(text=i, quick_reply=QuickReply(items=q_reply)))
				else:
					send_list.append(TextSendMessage(text=i))
		else:
			for i in message:
				send_list.append(TextSendMessage(text=i))
	else:
		return True
	line_bot_api.reply_message(event.reply_token, send_list)
	quick = []

@handler.add(MessageEvent, message=ImageMessage)
def comeImage(event):
	const_message(event, '画像は読み込めません\n文字で送って下さい')

#オウム返し
def parrot_message(event):
	const_message(event, event.message.text[:2000])

def response_message(event):
	# notesのCarouselColumnの各値は、変更してもらって結構です。
	notes = [CarouselColumn(thumbnail_image_url="https://renttle.jp/static/img/renttle02.jpg",
							title="【ReleaseNote】トークルームを実装しました。",
							text="creation(創作中・考え中の何かしらのモノ・コト)に関して、意見を聞けるようにトークルーム機能を追加しました。",
							actions=[{"type": "message", "label": "サイトURL", "text": "https://renttle.jp/notes/kota/7"}]),
			 CarouselColumn(thumbnail_image_url="https://renttle.jp/static/img/renttle03.jpg",
							title="ReleaseNote】創作中の活動を報告する機能を追加しました。",
							text="創作中や考え中の時点の活動を共有できる機能を追加しました。",
							actions=[{"type": "message", "label": "サイトURL", "text": "https://renttle.jp/notes/kota/6"}]),
			 CarouselColumn(thumbnail_image_url="https://renttle.jp/static/img/renttle04.jpg",
							title="【ReleaseNote】タグ機能を追加しました。",
							text="「イベントを作成」「記事を投稿」「本を登録」にタグ機能を追加しました。",
							actions=[{"type": "message", "label": "サイトURL", "text": "https://renttle.jp/notes/kota/5"}])]
	messages = TemplateSendMessage(
		alt_text='template',
		template=CarouselTemplate(columns=notes)
	)
	line_bot_api.reply_message(event.reply_token, messages=messages)

def res_user_status(event):
	profile = line_bot_api.get_profile(event.source.user_id)
	status_msg = profile.status_message
	if status_msg != "None":
		# LINEに登録されているstatus_messageが空の場合は、"なし"という文字列を代わりの値とする
		status_msg = "なし"
	messages = TemplateSendMessage(alt_text="ユーザー情報",
									template=ButtonsTemplate(
										thumbnail_image_url=profile.picture_url,
										title=profile.display_name,
										text=f"User Id: {profile.user_id[:5]}...\n"
										f"Status Message: {status_msg}",
										actions=[MessageAction(label="成功", text="？")]))
	line_bot_api.reply_message(event.reply_token, messages=messages)

def Send_Multicast(users, message):
	if type(message) is str:
		line_bot_api.multicast(users, TextSendMessage(text=message))
	else:
		line_bot_api.multicast(users, message)
