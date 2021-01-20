window.onload = function() {
	const useNodeJS = false;   // if you are not using a node server, set this value to false
	const defaultLiffId = "1655595024-vRM2ojo9";   // change the default LIFF value if you are not using a node server

	// DO NOT CHANGE THIS
	let myLiffId = "";

	myLiffId = defaultLiffId;
	initializeLiffOrDie(myLiffId);
};

/**
* Check if myLiffId is null. If null do not initiate liff.
* @param {string} myLiffId The LIFF ID of the selected element
*/
function initializeLiffOrDie(myLiffId) {
	if (!myLiffId) {
		document.getElementById("liffAppContent").classList.add('hidden');
		document.getElementById("liffIdErrorMessage").classList.remove('hidden');
	} else {
		initializeLiff(myLiffId);
	}
}

/**
* Initialize LIFF
* @param {string} myLiffId The LIFF ID of the selected element
*/
function initializeLiff(myLiffId) {
	liff.init({
		liffId: myLiffId
	})
	.then(() => {
		// start to use LIFF's api
		initializeApp();
	})
	.catch((err) => {
		document.getElementById("liffAppContent").classList.add('hidden');
		document.getElementById("liffInitErrorMessage").classList.remove('hidden');
		console.log(err.code, err.message);
	});
}

/**
 * Initialize the app by calling functions handling individual app components
 */
function initializeApp() {
	liff.closeWindow();
	displayIsInClientInfo();
	registerButtonHandlers();
	if (!liff.isLoggedIn() && !liff.isInClient()) {
		alert('To get an access token, you need to be logged in. Please tap the "login" button below and try again.');
	} else {
		const accessToken = liff.getAccessToken();
		document.idform.accesstoken.value = accessToken;
	}

	// check if the user is logged in/out, and disable inappropriate button
	if (liff.isLoggedIn()) {
		document.getElementById('liffLoginButton').disabled = true;
	} else {
		document.getElementById('liffLogoutButton').disabled = true;
	}
}

/**
* Toggle the login/logout buttons based on the isInClient status, and display a message accordingly
*/
function displayIsInClientInfo() {
	if (liff.isInClient()) {
		document.getElementById('liffLoginButton').classList.toggle('hidden');
		document.getElementById('liffLogoutButton').classList.toggle('hidden');
		document.getElementById('isInClientMessage').textContent = 'You are opening the app in the in-app browser of LINE.';
	} else {
		document.getElementById('isInClientMessage').textContent = 'You are opening the app in an external browser.';
	}
}

/**
* Register event handlers for the buttons displayed in the app
*/
function registerButtonHandlers() {
	// closeWindow call
	document.getElementById('closeWindowButton').addEventListener('click', function() {
		if (!liff.isInClient()) {
			sendAlertIfNotInClient();
		} else {
			liff.closeWindow();
		}
	});

	// get profile call
	document.getElementById('getProfileButton').addEventListener('click', function() {
		liff.getProfile().then(function(profile) {
			document.getElementById('displayNameField').textContent = profile.displayName;

			const profilePictureDiv = document.getElementById('profilePictureDiv');
			if (profilePictureDiv.firstElementChild) {
				profilePictureDiv.removeChild(profilePictureDiv.firstElementChild);
			}
			const img = document.createElement('img');
			img.src = profile.pictureUrl;
			img.alt = 'Profile Picture';
			profilePictureDiv.appendChild(img);

			document.getElementById('statusMessageField').textContent = profile.statusMessage;
			toggleProfileData();
		}).catch(function(error) {
			window.alert('Error getting profile: ' + error);
		});
	});

	// login call, only when external browser is used
	document.getElementById('liffLoginButton').addEventListener('click', function() {
		if (!liff.isLoggedIn()) {
			// set `redirectUri` to redirect the user to a URL other than the front page of your LIFF app.
			liff.login();
		}
	});

	// logout call only when external browse
	document.getElementById('liffLogoutButton').addEventListener('click', function() {
		if (liff.isLoggedIn()) {
			liff.logout();
			window.location.reload();
		}
	});
}

/**
* Alert the user if LIFF is opened in an external browser and unavailable buttons are tapped
*/
function sendAlertIfNotInClient() {
	alert('This button is unavailable as LIFF is currently being opened in an external browser.');
}

/**
* Toggle access token data field
*/
function toggleAccessToken() {
	toggleElement('accessTokenData');
}

/**
* Toggle profile info field
*/
function toggleProfileData() {
	toggleElement('profileInfo');
}

/**
* Toggle specified element
* @param {string} elementId The ID of the selected element
*/
function toggleElement(elementId) {
	const elem = document.getElementById(elementId);
	if (elem.offsetWidth > 0 && elem.offsetHeight > 0) {
		elem.style.display = 'none';
	} else {
		elem.style.display = 'block';
	}
}
