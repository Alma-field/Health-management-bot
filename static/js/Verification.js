async function Resend(code){
	const jsFrame = new JSFrame();
	jsFrame.showToast({
		align:'top',
		html: '再送中...'
	});
	var UserAgent = platform.os.toString();
	var result = true;
	//フォーム取得
	if (UserAgent == 'Windows 10 64-bit'){
		url = 'http://localhost:5000/broadcast/mail/';
	}else{
		url = 'http://192.168.11.12:5000/broadcast/mail/';
	}
	url = 'https://pbl-ai-083.herokuapp.com/broadcast/mail/'
	try{
		resend_url = url+'resend/'+code;//document.URL.split('/').pop();
		console.log(resend_url);
		var response = await fetch(resend_url);
		var data = await response.json();
		var status = data["status"];
		console.log('status : '+status);
		if(status){
			jsFrame.showToast({
				align:'top',
				html: 'メールを送信しました'
			});
		} else {
			console.log('error / json - status');
			jsFrame.showToast({
				align:'top',
				html: 'メールを送信できませんでした'
			});
		}
	}catch(e){
		console.log('error / No.1');
		jsFrame.showToast({
			align:'top',
			html: 'メールを送信できませんでした'
		});
	}
}
