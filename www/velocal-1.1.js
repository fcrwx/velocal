function checkTimeZone() {
	var rightNow = new Date();
	var myzone = rightNow.getTimezoneOffset();
	document.cookie = "VeloCalTZ=" + escape(myzone);

	var date1 = new Date(rightNow.getFullYear(), 0, 1, 0, 0, 0, 0); // January 1st
	var date2 = new Date(rightNow.getFullYear(), 6, 1, 0, 0, 0, 0); // June 1st

	var temp = date1.toGMTString();
	var date3 = new Date(temp.substring(0, temp.lastIndexOf(" ")-1));
	var temp = date2.toGMTString();
	var date4 = new Date(temp.substring(0, temp.lastIndexOf(" ")-1));

	var hoursDiffStdTime = (date1 - date3) / (1000 * 60 * 60);
	var hoursDiffDaylightTime = (date2 - date4) / (1000 * 60 * 60);

	if (hoursDiffDaylightTime == hoursDiffStdTime) {
		document.cookie = "VeloCalDST=0";
	}
	else {
		document.cookie = "VeloCalDST=1";
	}
}

function expandTextArea(textarealabel, e, columns) {
	if ((textarealabel.textLength % columns == 0) && (textarealabel.textLength > 1 ))
		if (e.which == 8)
			textarealabel.rows = textarealabel.rows - 1;
		else
			textarealabel.rows = textarealabel.rows + 1;
}

function autoTextArea(textareaname, columns) {
	var rows = Math.round(textareaname.textLength / columns) + 1;
	textareaname.rows = rows;
}

function MakeSizeAdjustment(oTextArea) {
	if (navigator.appName.indexOf("Microsoft Internet Explorer") == 0) {
		return;
	}

	while (oTextArea.scrollHeight > oTextArea.offsetHeight) {
		oTextArea.rows++;
	}
}

function map_check_action() {
	if (document.velocal['map_action']) {
		for (var i = 0; i < document.velocal['map_action'].length; i++) {
			if (document.velocal['map_action'][i].checked) {
				if (document.velocal['map_action'][i].value == 'url') {
					document.getElementById('map_url').style.display = 'block';
					document.getElementById('map_image').style.display = 'none';
				}
				else if (document.velocal['map_action'][i].value == 'existing') {
					document.getElementById('map_url').style.display = 'none';
					document.getElementById('map_image').style.display = 'none';
				}
				else {
					document.getElementById('map_url').style.display = 'none';
					document.getElementById('map_image').style.display = 'block';
				}
			}
		}
	}
}

function toggleDiv(divName) {
	if (document.getElementById(divName)) {
		if (document.getElementById(divName).style.display == 'none') {
			document.getElementById(divName).style.display = 'block';
		}
		else {
			document.getElementById(divName).style.display = 'none';
		}
	}
}

