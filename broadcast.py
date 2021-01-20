import os

from linebot import LineBotApi
from linebot.models import (
	FlexSendMessage,
	BubbleContainer, BoxComponent, TextComponent, SpanComponent, ImageComponent, ButtonComponent,
	URIAction
)

import Config

#環境変数取得
CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

message = FlexSendMessage(
	alt_text='体調登録',
	contents=BubbleContainer(
		hero=ImageComponent(
			url="https://vos.line-scdn.net/bot-designer-template-images/bot-designer-icon.png",
			size="full",
			aspect_ratio="1.51:1",
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
						SpanComponent(text='体調登録', weight="bold")
					]
				),
				TextComponent(
					text='text',
					align='center',
					gravity='center',
					offsetTop='10px',
					contents=[
						SpanComponent(text='本日の体調を登録してください')
					]
				)
			]
		),#Body
		footer=BoxComponent(
			layout="vertical",
			contents=[
				ButtonComponent(
					action=URIAction(label="登録する", uri="https://liff.line.me/1655595024-8ZXeW3Ww")
				)
			]
		)#Footer
	)
)
line_bot_api.broadcast(messages=message)
