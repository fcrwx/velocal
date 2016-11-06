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

