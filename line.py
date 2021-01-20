import os
from flask import Blueprint, abort, current_app, request

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
	MessageEvent,
	TextMessage, ImageMessage, TextSendMessage, FlexSendMessage,
	ButtonsTemplate, QuickReply, QuickReplyButton,
	BubbleContainer, BoxComponent, TextComponent, SpanComponent, ImageComponent, ButtonComponent,
	MessageAction
)

from datetime import datetime

from Config import LINE_BPNAME, debug

#データベース
from database import line_db

dbname = os.environ["DATABASE_URL"]
#環境変数取得
CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]

db = line_db(dbname)

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

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
		handler.handle(body, signature)
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
		#ここは絶対に通らない
		parrot_message(event)
	else:
		db.set_userstatus(userid, 'home:none', username)
		parrot_message(event)

def command_check(command):
	if ':' in command:
		c_l = command.split(':')
	else:
		return False
	command_list = {'home':['none']}
	return c_l[0] in command_list and c_l[1] in command_list[c_l[0]]

#画像メッセージが来た場合
@handler.add(MessageEvent, message=ImageMessage)
def comeImage(event):
	const_message(event, '画像は読み込めません\n文字で送って下さい')

def const_message(event, message, quick=[]):
	userid = event.source.user_id
	send_list = []
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

#オウム返し
def parrot_message(event):
	const_message(event, event.message.text[:2000])

def res_user_status(event):
	profile = line_bot_api.get_profile(event.source.user_id)
	status_msg = profile.status_message
	if status_msg != "None":
		# LINEに登録されているstatus_messageが空の場合は、"なし"という文字列を代わりの値とする
		status_msg = "なし"
	message=FlexSendMessage(
		alt_text='ユーザー情報',
		contents=BubbleContainer(
			header=BoxComponent(
				layout="vertical",
				background_color=f'{NOTICE_LEVEL_COLOR_LINE[level][0]}FF',
				contents=[
					TextComponent(
						text='text',
						align='center',
						gravity='center',
						contents=[
							SpanComponent(text='ユーザー情報')
						]
					)
				]
			),#Header
			hero=ImageComponent(
				url=profile.picture_url,
				size="full",
				aspect_mode="fit",
				action=None
			),
			body=BoxComponent(
				layout="vertical",
				contents=[
					TextComponent(
						text='text',
						align='center',
						gravity='center',
						contents=[
							SpanComponent(text=f'User Id: {profile.user_id}')
						]
					),
					TextComponent(
						text='text',
						align='center',
						gravity='center',
						contents=[
							SpanComponent(text=f'Status Message: {status_msg}')
						]
					)
				]
			),#Body
			footer=BoxComponent(
				layout="vertical",
				contents=[
					ButtonComponent(
						action=MessageAction(label="成功", text="？")
					)
				]
			)#Footer
		)
	)
	line_bot_api.reply_message(event.reply_token, messages=messages)

def Send_Pushmessage(user, message):
	if type(message) is str:
		line_bot_api.push_message(user, TextSendMessage(text=message))
	else:
		line_bot_api.push_message(user, message)

def Send_Multicast(users, message):
	if type(message) is str:
		line_bot_api.multicast(users, TextSendMessage(text=message))
	else:
		line_bot_api.multicast(users, message)
