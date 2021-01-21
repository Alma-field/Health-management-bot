function ChangeTempCheck(){
	var temperature_check = document.getElementById('temperature_check').checked;
	if (temperature_check) {
		document.getElementById('temperature').removeAttribute('disabled');
		document.getElementById('temp_limit').removeAttribute('style');
		document.getElementById('temp_nolimit').setAttribute('style', 'display: none;');
	} else {
		document.getElementById('temperature').setAttribute('disabled', 'disabled');
		document.getElementById('temp_limit').setAttribute('style', 'display: none;');
		document.getElementById('temp_nolimit').removeAttribute('style');
	}
}

function ChangeTemp(){
	var temperature = document.getElementById('temperature').value;
	document.getElementById('temp_span').innerHTML = temperature;
}

function ChangeQuesCheck(){
	var question_check = document.getElementById('question_check').checked;
	if (question_check) {
		document.getElementById('question').removeAttribute('disabled');
		document.getElementById('ques_limit').removeAttribute('style');
		document.getElementById('ques_nolimit').setAttribute('style', 'display: none;');
	} else {
		document.getElementById('question').setAttribute('disabled', 'disabled');
		document.getElementById('ques_limit').setAttribute('style', 'display: none;');
		document.getElementById('ques_nolimit').removeAttribute('style');
	}
}

function ChangeQues(){
	var question = document.getElementById('question').value;
	document.getElementById('ques_span').innerHTML = question;
}
