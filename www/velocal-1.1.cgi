#!/usr/bin/perl

#alter table users add hide_email enum('Y','N') not null default 'N';

# make feedback email come from the user, not velocal, so I can just hit reply

# add '*' for pace, or 'varies' or 'I' for individual

# a way for administrators to remove users from a group 


# if user does not specify http:// prefix on their homepage, add it

# large charity rides for a region?


# weather forecasts

# privacy policy

# idea for group profile page: add news/events section. should only admins be allowed to post? can non-news-creators delete/edit events?

# idea: after "welcome to the group" message, have text and a link to the group preferences page

# feedback: Ann reports that the logout button wraps to the next line. also, had to "enable links" in
#    her email because of security issues, but it still worked:

# TODO: test invite->confirm, invite->register->confirm with 2 email addresses

# TODO: join_confirm is not sending email (mail account has actual bounce message)

# TODO: write copy for main welcome page

# TODO: individual preference to hide email address

# TODO: prevent moving a ride from the past to the future (?)
# TODO: prevent changing attendance for past events

# TODO: action 'unregister' - what if you are the only admin and you unregister (and what if it is a private group)?

# TODO: in the user profile screen, display a list of all the
#       groups the user belongs to. show all public and restricted
#       groups, plus any private groups where the currently logged
#       in user is also a member
# !low priority

# TODO: if an email bounces, I get the bounce.
#       setting the from: address to the user's email address doesn't seem to work
# !low priority

# TODO: in profile_edit, if error code, populate the form fields with the new values
#       question: what if the bio is actually 64K in size. what if the photo is valid but
#       the other fields are not. How about multiple database updates, one per field, 
#       including the photo
# !low priority

# TODO: add support for ride leaders
# !low priority

# TODO: column 'created' in users is actually 'last_updated'
#       make a created column?



use strict;

###
### Title: VeloCal
###
### About: A web-based ride scheduler for fans
###        of cycling. Registered users can join
###        groups, create rides, join rides, and
###        receive email reminders and 
###        ride invitations.
###
### Author: Karl Olson (karl.olson@gmail.com)
###
### Version: 0.1 (01/17/05)
###   - Registration
###   - Login/Logout
### Version: 0.2 (01/31/05)
###   - Profile Edit
###   - Photo Edit
###   - Change Password
###   - Change Email
### Version: 0.3
###   - Create/Edit groups
###   - Join/Unjoin groups
### Version: 0.4
###   - Calendar
###   - Schedule events
### Version: 0.5 (12/02/05)
###   - email notifications
###   - edit/delete existing events
###   - attendance intention tracking
### Version: 0.6 (12/06/05)
###   - CSS / graphics
### Version: 0.7 (12/09/05)
###   - cleanup
###   - reminder daemon
### Version: 0.8 (1/4/06)
###   - minor bug fixes from testing
### Version: 0.9 (2/7/06)
###   - minor enhancements
###   - ride leaders for events
###   - ride distance
###
### For more information on PerlMagick, see:
###   http://www.imagemagick.org/www/perl.html

###
### Globals
###

my $sendmail = '/usr/sbin/sendmail';
my $registration_subject = 'VeloCal Registration Confirmation';
my $registration_email = 'support@velocal.org';
my $registration_name = 'VeloCal Support';
my $password_reminder_subject = 'VeloCal Password Reminder';
my $email_change_subject = 'VeloCal Email Change Request';
my $subscription_request_subject = 'VeloCal Subscription Request';
my $default_page_title = 'VeloCal';
my $feedback_email = 'support@velocal.org';

my $db_dbi = 'mysql';
my $db_name = 'velocal';
my $db_username = 'velocal';
my $db_password = 'c\cl1ng';

my $max_profile_photo_width = 250;
my $max_profile_photo_height = 250;

my @messages;

###
### No changes required beyond this point
###

my $version = "1.1";

use DBI;
use String::Random;
use HTML::Entities;
use Date::Calc qw(:all);
use HTML::CalendarMonthSimple;
use CGI qw/:all -nosticky -oldstyle_urls *table *Tr *td *div *ul escape *blockquote *p *center/;

my $q = new CGI;
my $script = $q->url();

my $dbh = DBI->connect("DBI:$db_dbi:$db_name",$db_username,$db_password);

my %hours_labels = (
	0  => '12 am',
	1  => '1 am',
	2  => '2 am',
	3  => '3 am',
	4  => '4 am',
	5  => '5 am',
	6  => '6 am',
	7  => '7 am',
	8  => '8 am',
	9  => '9 am',
	10 => '10 am',
	11 => '11 am',
	12 => '12 pm',
	13 => '1 pm',
	14 => '2 pm',
	15 => '3 pm',
	16 => '4 pm',
	17 => '5 pm',
	18 => '6 pm',
	19 => '7 pm',
	20 => '8 pm',
	21 => '9 pm',
	22 => '10 pm',
	23 => '11 pm',
);
my @hours_values;
foreach my $hour (sort { $a <=> $b } keys %hours_labels) {
	push @hours_values, $hour;
}

my %minutes_labels = (
	0  => ':00',
	15 => ':15',
	30 => ':30',
	45 => ':45'
);
my @minutes_values;
foreach my $minutes (sort keys %minutes_labels) {
	push @minutes_values, $minutes;
}

my @months = qw/January February March April May June July August September October November December/;
my @month_values = qw/1 2 3 4 5 6 7 8 9 10 11 12/;
my @days = qw/1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31/;

my %month_labels;
for (my $i = 0; $i < scalar @month_values; $i++) {
	$month_labels{$i+1} = $months[$i];
}

my @years;
for (my $year = (localtime(time))[5]+1900; $year <= (localtime(time))[5]+1905; $year++) {
	push @years, $year;
}

## define 'pace' radio values, labels, and default value
my %pace_labels = (
	AX => 'AX',
	A => 'A',
	B => 'B',
	C => 'C',
	D => 'D',
);
my @pace_values = qw/AX A B C D/;

## define 'terrain' radio values, labels, and default value
my %terrain_labels = (
	Hilly => 'Hilly',
	'Moderately Hilly' => 'Moderately Hilly',
	Rolling => 'Rolling',
	Flat => 'Flat',
);
my @terrain_values = ('Hilly','Moderately Hilly','Rolling','Flat');


###
### subroutines
###

my $ucwords = sub {
	my $words = shift;
	my @words = split / /, $words;
	for (my $i = 0; $i < scalar @words; $i++) {
		$words[$i] = ucfirst($words[$i]);
	}
	my $string = join ' ', @words;
	return($string);
};

my $get_challenge = sub {
	my $pass = new String::Random;
	my $challenge = $pass->randpattern("CcnCCncn");
	return($challenge);
};

my $get_states = sub {
	my %states = (
		AK => 'Alaska',
		AL => 'Alabama',
		AR => 'Arkansas',
		AZ => 'Arizona',
		CA => 'California',
		CO => 'Colorado',
		CT => 'Connecticut',
		DC => 'District of Columbia',
		DE => 'Delaware',
		FL => 'Florida',
		GA => 'Georgia',
		HI => 'Hawaii',
		IA => 'Iowa',
		ID => 'Idaho',
		IL => 'Illinois',
		IN => 'Indiana',
		KS => 'Kansas',
		KY => 'Kentucky',
		LA => 'Louisiana',
		MA => 'Massachusetts',
		MD => 'Maryland',
		ME => 'Maine',
		MI => 'Michigan',
		MN => 'Minnesota',
		MO => 'Missouri',
		MS => 'Mississippi',
		MT => 'Montana',
		NC => 'North Carolina',
		ND => 'North Dakota',
		NE => 'Nebraska',
		NH => 'New Hampshire',
		NJ => 'New Jersey',
		NM => 'New Mexico',
		NV => 'Nevada',
		NY => 'New York',
		OH => 'Ohio',
		OK => 'Oklahoma',
		OR => 'Oregon',
		PA => 'Pennsylvania',
		RI => 'Rhode Island',
		SC => 'South Carolina',
		SD => 'South Dakota',
		TN => 'Tennessee',
		TX => 'Texas',
		UT => 'Utah',
		VA => 'Virginia',
		VT => 'Vermont',
		WA => 'Washington',
		WI => 'Wisconsin',
		WV => 'West Virginia',
		WY => 'Wyoming',
	);

	return(%states);
};

my $get_enum = sub {
	my ($table_name,$column_name) = @_;

	$dbh->{FetchHashKeyName} = "NAME_lc";
	my $select = "show columns from $table_name like '$column_name'";
	my $x = $dbh->selectrow_hashref($select);
	$x->{type} =~ s/^enum\(//;
	$x->{type} =~ s/\)$//;
	my @fields = split /','/, $x->{type};
	for (my $i = 0; $i < scalar @fields; $i++) {
		$fields[$i] =~ s/^'//;
		$fields[$i] =~ s/'$//;
	}

	return (@fields);
};

my $get_login_status = sub {
	my $user_id = $q->cookie('VeloCalUserID');
	my $crypt_password = $q->cookie('VeloCalPass');

	if ((defined $user_id) && (defined $crypt_password)) {
		my $select = "select password from users where user_id = $user_id"; 
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($password) = $qh->fetchrow_array();

		if ((crypt($password,$crypt_password)) eq $crypt_password) {
			return(1);
		}
	}

	return(0);
};

my $logged_in = &$get_login_status();

my $check_email_address = sub {
	use Mail::RFC822::Address qw/valid/;
	return(valid(shift));
};

my $action = $q->param('a');
$action = 'main' if ((not defined $action) && ($logged_in));
$action = 'welcome' if (not defined $action);

my $page_begin = sub {
	my $title = shift || $default_page_title;
	my $onload = shift;
	my $extra_javascript = shift;

   my $JSCRIPT=<<END;
		function do_nothing() {
		}

		function photo_check_action(selected) {
			if (selected.value == 'none') {
				if (document.getElementById('filenamediv_add')) {
					document.getElementById('filenamediv_add').style.display = 'none';
				}
			}
			if (selected.value == 'add') {
				if (document.getElementById('filenamediv_add')) {
					document.getElementById('filenamediv_add').style.display = 'block';
				}
			}
			if (selected.value == 'existing') {
				if (document.getElementById('filenamediv_replace')) {
					document.getElementById('filenamediv_replace').style.display = 'none';
				}
			}
			if (selected.value == 'remove') {
				if (document.getElementById('filenamediv_replace')) {
					document.getElementById('filenamediv_replace').style.display = 'none';
				}
			}
			if (selected.value == 'replace') {
				if (document.getElementById('filenamediv_replace')) {
					document.getElementById('filenamediv_replace').style.display = 'block';
				}
			}
		}

		function setState(state) {
			if (document.getElementById('state')) {
				document.getElementById('state').value = state;
			}
		}

		function divState(setCity) {
			if (document.getElementById('state')) {
				selected = document.getElementById('state');

				var alltags=document.all? document.all : document.getElementsByTagName("*")
				for (i = 0; i < alltags.length; i++) {
					if (alltags[i].className == 'state') {
						alltags[i].style.display = 'none';
					}
				}

				if (document.getElementById(selected.value)) {
					document.getElementById(selected.value).style.display = 'block';
				}

				if (setCity == 'NEW') {
					if (document.getElementById('newcityradio')) {
						document.getElementById('newcityradio').checked = true;
					}
				}

				if (selected.value != 'none') {
					if (document.getElementById('newcity')) {
						document.getElementById('newcity').style.display = 'block';
					}
					if (document.getElementById('group_edit_submit')) {
						document.getElementById('group_edit_submit').style.display = 'block';
					}
				}
			}
		}

		function setCityNew() {
			if (document.getElementById('newcityradio')) {
				document.getElementById('newcityradio').checked = true;
			}
		}

		function divType(edit,origType,groupType) {
			if (document.getElementById('type_change_warning')) {
				if (edit == 'Y') {
					if (groupType.value == origType) {
						document.getElementById('type_change_warning').style.display = 'none';
					}
					else {
						document.getElementById('type_change_warning').style.display = 'block';
					}
				}
			}
		}

END

	my $googleAdSense = <<END;
<script type="text/javascript"><!--
google_ad_client = "pub-5799727692728364";
google_ad_width = 468;
google_ad_height = 60;
google_ad_format = "468x60_as";
google_ad_type = "text_image";
google_ad_channel ="";
google_color_border = "CCCCCC";
google_color_bg = "FFFFFF";
google_color_link = "000000";
google_color_url = "666666";
google_color_text = "333333";
//--></script>
<script type="text/javascript"
  src="http://pagead2.googlesyndication.com/pagead/show_ads.js">
</script>
END

	$JSCRIPT .= $extra_javascript if (defined $extra_javascript);

	$onload = "do_nothing();" if ($onload eq '');

	print
		header(),
		start_html(
			-title => $title,
			-bgcolor => 'white',
			-text => 'black',
			-link => 'blue',
			-vlink => 'blue',
			-alink => 'red',
			-marginheight => 0,
			-marginwidth => 0,
			-leftmargin => 0,
			-topmargin => 0,
			-style=>{-src=>'velocal-1.1.css'},
			-script=>[
							{
								-language => 'JavaScript',
								-src      => 'velocal-1.1.js'
							},
							{
								-language => 'JavaScript',
								-code     => $JSCRIPT
							}
						],
			-onload=>$onload,
		);

	if ($logged_in) {
		my $user_id = $q->cookie('VeloCalUserID');
		my $select = "select name_first from users where user_id = $user_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($username) = $qh->fetchrow_array();

		print
			div(
				{-id=>'PageHeader'},
				table(
					{-class=>'headerTable',-width=>'100%',-cellpadding=>0,-cellspacing=>0},
					Tr(
						td(
							{-rowspan=>2,-class=>'headerTableLogo'},
							img({-src=>'images/VeloCal.png',-border=>0,-alt=>'VeloCal Logo'})
						),
						td(
							{-width=>'100%',-valign=>'bottom',-align=>'left'},
							div(
								{-class=>'ad'},
								$googleAdSense
							)
						)
					),
					Tr(
						td(
							{-valign=>'bottom'},
							div(
								{-id=>'Nav'},
								ul(
									li(
										a({-href=>"$script"},'Ride Calendar')
									),
									li(
										a({-href=>"$script?a=profile"},'Your Profile')
									),
									li(
										a({-href=>"$script?a=join"},'Join a Group')
									),
									li(
										a({-href=>"$script?a=group_edit"},'Create a Group')
									),
									li(
										a({-href=>"$script?a=support"},'Support')
									),
									li(
										a({-href=>"$script?a=logout"},'Logout')
									)
								)
							)
						)
					)
				)
			);

		$select = "
			select
				g.group_id,
				g.name
			from
				group_user u,
				groups g
			where
				g.group_id = u.group_id and
				u.user_id = $user_id";
		$qh = $dbh->prepare($select);
		$qh->execute();

		my %group_user;
		while (my ($group_id,$name) = $qh->fetchrow_array()) {
			$group_user{$group_id} = $name;
		}

		$select = "
			select
				g.group_id,
				g.name
			from
				group_admin a,
				groups g
			where
				g.group_id = a.group_id and
				a.user_id = $user_id";
		$qh = $dbh->prepare($select);
		$qh->execute();

		my %group_admin;
		while (my ($group_id,$name) = $qh->fetchrow_array()) {
			$group_admin{$group_id} = $name;
		}

		print
			start_table(),
			start_Tr(),
			start_td({-valign=>'top'});

		print
			start_div({-id=>'UserGroups'}),
			span({-style=>'white-space: nowrap;'},b("Welcome $username")),
			br(),
			br(),
			span({-style=>'white-space: nowrap;'},'Your Groups'),
			br(),
			start_ul();

		foreach my $group_id (sort { $group_user{$a} cmp $group_user{$b} } keys %group_user) {
			print
				li($group_user{$group_id});

			print
				start_ul(),
				li(a({-href=>"$script?a=group&g=$group_id"},'About')),
				li(a({-href=>"$script?a=group_prefs&g=$group_id"},'Preferences'));

			if ($group_admin{$group_id} ne '') {
				print
					li(a({-href=>"$script?a=group_admin&g=$group_id"},'Manage'));
			}

			my $select = "select homepage from groups where group_id = $group_id";
			my $qh = $dbh->prepare($select);
			$qh->execute();

			my ($homepage) = $qh->fetchrow_array();
			if (defined $homepage) {
				print
					li(a({-href=>$homepage},'Homepage'));
			}

			print
				end_ul();
		}

		print 
			end_ul();

		if (scalar keys %group_user == 0) {
			print 
				span({-style=>'white-space: nowrap; padding-left: 10px;'},i('no groups')),
				p("You must join a group before group events will appear in your ride calendar")
		}

		print
			end_div();

		print
			start_p(),
			start_center();
				

		print<<__END__;
<form action="https://www.paypal.com/cgi-bin/webscr" method="post">
<input type="hidden" name="cmd" value="_s-xclick">
<input type="image" src="https://www.paypal.com/en_US/i/btn/x-click-but04.gif" border="0" name="submit" alt="Make payments with PayPal - it's fast, free and secure!">
<input type="hidden" name="encrypted" value="-----BEGIN PKCS7-----MIIHLwYJKoZIhvcNAQcEoIIHIDCCBxwCAQExggEwMIIBLAIBADCBlDCBjjELMAkGA1UEBhMCVVMxCzAJBgNVBAgTAkNBMRYwFAYDVQQHEw1Nb3VudGFpbiBWaWV3MRQwEgYDVQQKEwtQYXlQYWwgSW5jLjETMBEGA1UECxQKbGl2ZV9jZXJ0czERMA8GA1UEAxQIbGl2ZV9hcGkxHDAaBgkqhkiG9w0BCQEWDXJlQHBheXBhbC5jb20CAQAwDQYJKoZIhvcNAQEBBQAEgYB9i3zIA25qE2l9ofGwhQ052VGIMQcJR1g73ngregIEyXsEJ7B51ftDRlbDjveSffdJRRJeqnBfj+wiDBM7IKFff6UMU6kljDE8vjgjGZ9X5MIZodvdVA7/mre6xI0eEv1/gjOMjqy8Zam6TVWow/M+KcrhQ0mQbzyryotopsAyRDELMAkGBSsOAwIaBQAwgawGCSqGSIb3DQEHATAUBggqhkiG9w0DBwQI7iPrFoMVpeGAgYihYaXXUMGGiqySYWFo53s/G3V6bZJw+plyJsPhig9FzYmqDRXiI+VzYbYWb4cTP6N3jCgEN2/uEVd4PR+iYA/64w/UJrxw6eUlgfELl+m85ABc7JnHSkCafeeJUeNLyeJRTh2YTF28o84wBvLiwZiRYyM6NV090MpNXRO5BTDixdLlSDmxMvc6oIIDhzCCA4MwggLsoAMCAQICAQAwDQYJKoZIhvcNAQEFBQAwgY4xCzAJBgNVBAYTAlVTMQswCQYDVQQIEwJDQTEWMBQGA1UEBxMNTW91bnRhaW4gVmlldzEUMBIGA1UEChMLUGF5UGFsIEluYy4xEzARBgNVBAsUCmxpdmVfY2VydHMxETAPBgNVBAMUCGxpdmVfYXBpMRwwGgYJKoZIhvcNAQkBFg1yZUBwYXlwYWwuY29tMB4XDTA0MDIxMzEwMTMxNVoXDTM1MDIxMzEwMTMxNVowgY4xCzAJBgNVBAYTAlVTMQswCQYDVQQIEwJDQTEWMBQGA1UEBxMNTW91bnRhaW4gVmlldzEUMBIGA1UEChMLUGF5UGFsIEluYy4xEzARBgNVBAsUCmxpdmVfY2VydHMxETAPBgNVBAMUCGxpdmVfYXBpMRwwGgYJKoZIhvcNAQkBFg1yZUBwYXlwYWwuY29tMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBR07d/ETMS1ycjtkpkvjXZe9k+6CieLuLsPumsJ7QC1odNz3sJiCbs2wC0nLE0uLGaEtXynIgRqIddYCHx88pb5HTXv4SZeuv0Rqq4+axW9PLAAATU8w04qqjaSXgbGLP3NmohqM6bV9kZZwZLR/klDaQGo1u9uDb9lr4Yn+rBQIDAQABo4HuMIHrMB0GA1UdDgQWBBSWn3y7xm8XvVk/UtcKG+wQ1mSUazCBuwYDVR0jBIGzMIGwgBSWn3y7xm8XvVk/UtcKG+wQ1mSUa6GBlKSBkTCBjjELMAkGA1UEBhMCVVMxCzAJBgNVBAgTAkNBMRYwFAYDVQQHEw1Nb3VudGFpbiBWaWV3MRQwEgYDVQQKEwtQYXlQYWwgSW5jLjETMBEGA1UECxQKbGl2ZV9jZXJ0czERMA8GA1UEAxQIbGl2ZV9hcGkxHDAaBgkqhkiG9w0BCQEWDXJlQHBheXBhbC5jb22CAQAwDAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQUFAAOBgQCBXzpWmoBa5e9fo6ujionW1hUhPkOBakTr3YCDjbYfvJEiv/2P+IobhOGJr85+XHhN0v4gUkEDI8r2/rNk1m0GA8HKddvTjyGw/XqXa+LSTlDYkqI8OwR8GEYj4efEtcRpRYBxV8KxAW93YDWzFGvruKnnLbDAF6VR5w/cCMn5hzGCAZowggGWAgEBMIGUMIGOMQswCQYDVQQGEwJVUzELMAkGA1UECBMCQ0ExFjAUBgNVBAcTDU1vdW50YWluIFZpZXcxFDASBgNVBAoTC1BheVBhbCBJbmMuMRMwEQYDVQQLFApsaXZlX2NlcnRzMREwDwYDVQQDFAhsaXZlX2FwaTEcMBoGCSqGSIb3DQEJARYNcmVAcGF5cGFsLmNvbQIBADAJBgUrDgMCGgUAoF0wGAYJKoZIhvcNAQkDMQsGCSqGSIb3DQEHATAcBgkqhkiG9w0BCQUxDxcNMDYwMTI2MTgxNDM5WjAjBgkqhkiG9w0BCQQxFgQUHodvdfsOXPtD4/5tYRku4q8mwPIwDQYJKoZIhvcNAQEBBQAEgYA61BtEgj/RvlLUcDRoeVWxNyMEXvt6bbTVOMSZPWNbNtie8WfvEV3rCcNZrIB7zzabDgnsHS9sGyfVX+v3DTM8xfGabbT8KoJcbYUmEhxykQ7VoEd3Aludz6n7BrenBkqDx4oNrpDmFhRJYg0nnr5Tn+C8pBbnnPACrAHJrvPZRQ==-----END PKCS7-----
">
</form>
__END__

		print
			end_center(),
			end_p(),
			end_td();
	}
	else {   # not logged in
		print
			start_table({-width=>'100%',-cellpadding=>0,-cellspacing=>0}),
			start_Tr(),
			start_td({-valign=>'top'});

		print
			div(
				{-id=>'PageHeader'},
				table(
					{-class=>'headerTable',-width=>'100%',-cellpadding=>0,-cellspacing=>0},
					Tr(
						td(
							{-rowspan=>2,-class=>'headerTableLogo'},
							img({-src=>'images/VeloCal.png',-border=>0,-alt=>'VeloCal Logo'})
						),
						td(
							{-width=>'100%',-valign=>'bottom',-align=>'left'},
							div(
								{-class=>'ad'},
								$googleAdSense
							)
						)
					),
					Tr(
						td(
							{-valign=>'bottom'},
							div(
								{-id=>'Nav'},
								ul(
									li(
										a({-href=>"$script"},'Home')
									),
									li(
										a({-href=>"$script?a=login"},'Login')
									),
									li(
										a({-href=>"$script?a=register"},'Register')
									),
									li(
										a({-href=>"$script?a=support"},'Support')
									)
								)
							)
						)
					)
				)
			);

		print
			end_td(),
			end_Tr(),
			start_Tr();
	}

	my $content_div = 'ContentWelcome';
	$content_div = 'Content' if ($logged_in);

	print
		start_td({-valign=>'top',-width=>'100%'}),
		start_div({-id=>$content_div});
};

my $get_local_timezone = sub {
	# description:
	#   returns a string describing the user's timezone
	#
	# return:
	#   a string showing offset from GMT, or if the cookie
	#   cannot be read, just '0000'
	#   for example, MDT would return '-0700' and
	#   MST would return '-0600'

	my $tz = $q->cookie({-name=>'VeloCalTZ'});

	if (defined $tz) {
		my $which_side = "-";
		$which_side = "" if ($tz < 0);
		$tz = (0 - $tz) if ($tz < 0);
		my $hrs = int($tz / 60);
		my $min = int($tz - $hrs*60);
		my $offset_time = sprintf("%02d%02d",$hrs,$min);

		return ("$which_side$offset_time");
	}
	else {
		return ('0000');
	}
};

my $get_dst = sub {
	return($q->cookie({-name=>'VeloCalDST'}));
};

my $write_timezone = sub {
	my $user_id = $q->cookie('VeloCalUserID');
	my $tz = &$get_local_timezone();
	my $dst = &$get_dst();

	if ($user_id ne '') {
		my $update = "
			update users set
				timezone = '$tz',
				observesDst = '$dst'
			where
				user_id = $user_id";
		my $qh = $dbh->prepare($update);
		$qh->execute();
	}
};

my $page_end = sub {
	print
		end_div(),
		end_td(),
		end_Tr(),
		end_table(),
		div(
			{-class=>'footer_spacer'}
		),
		div(
			{-class=>'footer'},
			"Version $version | &copy; ",
			a({-href=>'http://karlandamy.com'},'Karl Olson')
		);

	print<<END;
<script src="http://www.google-analytics.com/urchin.js" type="text/javascript">
</script>
<script type="text/javascript">
_uacct = "UA-81123-2";
urchinTracker();
</script>
END

	print<<END;
<script type="text/javascript">
checkTimeZone()
</script>
END

	&$write_timezone();

	foreach (@messages) {
		print $_, br();
	}

	print
		end_html();
};

my $convert_to_localtime = sub {
	# description:
	#   converts a timestamp into the correct timezone for the user.
	#   this reads the cookie 'VeloCalTZ' from the user's browser to
	#   determine the correct time zone. If the cookie is not available
	#   the system time is the default
	#
	# input:
	#   db_time (a timestamp in the timezone of the server)
	#
	# return:
	#   timestring (a formated string containing date and time)

	my $db_time = shift;

	my ($year,$month,$day,$hour,$minutes,$seconds) = split /:/, $db_time;

	if ($db_time eq '') {
		($seconds,$minutes,$hour,$day,$month,$year) = localtime(time);
		$year += 1900;
		$month += 1;
	}

	use Date::Calc qw/Mktime Gmtime Add_Delta_DHMS/;
	my $time = Mktime($year,$month,$day,$hour,$minutes,$seconds);
	my ($gm_year,$gm_month,$gm_day,$gm_hour,$gm_minutes,$gm_seconds) = Gmtime($time);

	my $tz = $q->cookie({-name=>'VeloCalTZ'});

	if (defined $tz) {
		$tz = 0 - $tz;
		my ($l_year,$l_month,$l_day,$l_hour,$l_minutes,$l_seconds) = Add_Delta_DHMS($gm_year,$gm_month,$gm_day,$gm_hour,$gm_minutes,$gm_seconds,0,0,$tz,0);
		my $timestring = sprintf("%04d:%02d:%02d:%02d:%02d:%02d",$l_year,$l_month,$l_day,$l_hour,$l_minutes,$l_seconds);
		return ($timestring);
	}
	else {
		my $timestring = sprintf("%04d:%02d:%02d:%02d:%02d:%02d",$gm_year,$gm_month,$gm_day,$gm_hour,$gm_minutes,$gm_seconds);
		return ($timestring);
	}
};



###
### execution begins here
###

#my $action = $q->param('a');
#$action = 'main' if ((not defined $action) && ($logged_in));
#$action = 'welcome' if (not defined $action);

if ($action eq 'welcome') {
	&$page_begin();

	print 
		h3('Welcome'),
		p("Welcome to VeloCal, a web-based ride scheduler for fans of cycling. VeloCal allows bicyclists to create groups and schedule rides. Groups can be public (allowing anyone to join at any time), restricted (requiring riders to be approved before joining), or private (where the group is essentially invisible except by group members who can join by invitation only). Registered users can join or create groups, create rides, join rides, and receive email reminders and ride invitations. Riders can also mark their attendance options and leave comments about the ride."),
		p("If you are already registered, please " . a({-href=>"$script?a=login"},'login') . "."),
		p("If you are new to VeloCal, please " . a({-href=>"$script?a=register"},'register') . "."),
		p("Note: Cookies must be enabled in your browser in order to use this site."),
		p("If you have questions, comments, or are having technical issues, please send feedback on the " . a({-href=>"$script?a=support"},'support page') . ".");

	&$page_end();
}

elsif ($action eq 'login') {
	my $email = $q->param('e');
	my $ec = $q->param('ec') || 0;
	my $redirect_url = $q->param('redirect_url');
	my $user_id = $q->cookie('VeloCalUserID');

	&$page_begin();

	print 
		h3('Login');

	if ($ec == 1) {
		print
			div(
				{-class=>'error'},
				'ERROR: Invalid login'
			);
	}
	elsif ($ec == 2) {
		print
			div(
				{-class=>'message'},
				'Password successfully changed. You now need to re-login with your new password.'
			);
	}
	elsif ($ec == 3) {
		print
			div(
				{-class=>'message'},
				'Your email address was successfully changed. You now need to re-login with your new email address. Your password is still the same.'
			);
	}
	elsif ($ec == 9) {
		print
			div(
				{-class=>'message'},
				'Your password has been sent to your email address. Please check your email and use the password provided.'
			);
	}

	print 
		p('Enter your email address and password to login. You must have cookies enabled in your browser. If you have forgotten your password, click ' . a({-href=>"$script?a=forgot"},'here') . ' to have it emailed to you.'),
		blockquote(
			start_form({-action=>$script,-method=>'POST'}),
			table(
				{-class=>'brown'},
				Tr(
					td('Email'),
					td(input({-type=>'text',-name=>'e',-size=>25,-maxlength=>255,-value=>$email,-override=>1}))
				),
				Tr(
					td('Password'),
					td(
						input({-type=>'password',-name=>'password',-size=>25,-maxlength=>16,-override=>1}),
						hidden({-name=>'a',-value=>'login_check',-override=>1}),
						hidden({-name=>'redirect_url',-value=>$redirect_url,-override=>1})
					)
				)
			),
			br(),
			submit({-value=>'Login'}),
			end_form()
		);
	
	&$page_end();
}

elsif ($action eq 'forgot') {
	my $email = $q->param('e');
	my $ec = $q->param('ec');

	&$page_begin();

	print
		h3('Password Assistance');
	
	if ($ec == 1) {
		print
			div(
				{-class=>'error'},
				"ERROR: The email address $email was not found. Please try again"
			);
	}

	print
		p('Enter your email address below and your password will be sent to you.'),
		start_form({-action=>$script,-method=>'post'}),
		table(
			{-class=>'brown'},
			Tr(
				td('Email'),
				td(
					input({-type=>'text',-name=>'e',-size=>25,-maxlength=>255,-value=>$email,-override=>1}), 
					hidden({-name=>'a',-value=>'send_password',-override=>1})
				)
			)
		),
		br(),
		submit({-value=>'Submit'}),
		end_form();

	&$page_end();
}

elsif ($action eq 'send_password') {
	my $email = $q->param('e');
	my $email_escaped = escape($email);

	my $select = "
		select
			name_last,
			name_first,
			password
		from
			users
		where
			email = '$email'";
	my $qh = $dbh->prepare($select);
	$qh->execute();
	my ($name_last,$name_first,$password) = $qh->fetchrow_array();

	if (defined $password) {
		my $name = "$name_first $name_last";
		$name =~ s/^\s//;

		open(MAIL,"| $sendmail -t");
		print MAIL "To: $name <$email>\n";
		print MAIL "From: $registration_name <$registration_email>\n";
		print MAIL "Subject: $password_reminder_subject\n";
		print MAIL "Content-type: text/html\n\n";
		print MAIL "A password reminder request has been received for the email address $email.";
		print MAIL '<br />';
		print MAIL "Here is the password: $password";
		close(MAIL);
	
		print $q->redirect("$script?a=login&ec=9");
	}
	else {
		print $q->redirect("$script?a=forgot&e=$email_escaped&ec=1");
	}
}

elsif ($action eq 'login_check') {
	my $email = $q->param('e');
	my $password = $q->param('password');
	my $redirect_url = $q->param('redirect_url') || "$script?a=main";

	my $select = "select user_id,password from users where email = '$email'"; 
	my $qh = $dbh->prepare($select);
	$qh->execute();
	my ($user_id,$db_password) = $qh->fetchrow_array();

	if ($password eq $db_password) {
		my $salt = join '', ('.', '/', 0..9, 'A'..'Z', 'a'..'z')[rand 64, rand 64];
		my $crypt_password = crypt($password,$salt);

		my $cookie_user_id = $q->cookie(-name=>'VeloCalUserID',-value=>$user_id,-expires=>'+10y');
		my $cookie_password = $q->cookie(-name=>'VeloCalPass',-value=>$crypt_password,-expires=>'+10y');

		print $q->redirect(-location=>$redirect_url,-cookie=>[$cookie_user_id,$cookie_password]);
	}
	else {
		print $q->redirect("$script?a=login&ec=1");
	}
}

elsif ($action eq 'register') {
	my $email = $q->param('e');

	if ($logged_in) {
		my $redirect_url = "$script?a=register&e=$email";
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=logout&redirect_url=$redirect_url");
	}
	else {
		my $name_last = $q->param('n');
		my $name_first = $q->param('f');

		## error codes:
		##  0 - no errors
		##  1 - passwords do not match
		##  2 - invalid email address
		##  3 - no password entered
		##  4 - invalid password length
		##  5 - email address already registered
		##  6 - name required
		my $ec = $q->param('ec') || 0;

		&$page_begin();

		print
			h3('Register');

		if ($ec == 1) {
			print 
				div(
					{-class=>'error'},
					'ERROR: Passwords do not match. Please try again.'
				);
		}
		elsif ($ec == 2) {
			print 
				div(
					{-class=>'error'},
					'ERROR: The email address you entered is not valid. Please enter a valid email address.'
				);
		}
		elsif ($ec == 3) {
			print 
				div(
					{-class=>'error'},
					'ERROR: You must enter a password.'
				);
		}
		elsif ($ec == 4) {
			print 
				div(
					{-class=>'error'},
					'ERROR: Passwords must be between 6 and 16 characters in length.'
				);
		}
		elsif ($ec == 5) {
			print 
				div(
					{-class=>'error'},
					"ERROR: $email is already a registered email address."
				);
		}
		elsif ($ec == 6) {
			print 
				div(
					{-class=>'error'},
					'ERROR: You must enter your name.'
				);
		}

		print
			p(font({-color=>'red'},'*'), " indicates a required field."),
			p('Passwords must be a minimum of six characters and a maximum of sixteen characters.'),
			blockquote(
				start_form({-action=>$script}),
				table(
					{-class=>'brown'},
					Tr(
						td('Email address', font({-color=>'red'},'*')),
						td(input({-type=>'text',-name=>'email',-value=>$email,-maxlength=>255,-size=>25,-override=>1}))
					),
					Tr(
						td('First name', font({-color=>'red'},'*')),
						td(input({-type=>'text',-name=>'name_first',-value=>$name_first,-maxlength=>255,-size=>25,-override=>1}))
					),
					Tr(
						td('Last name'),
						td(input({-type=>'text',-name=>'name_last',-value=>$name_last,-maxlength=>255,-size=>25,-override=>1}))
					),
					Tr(
						td('Password', font({-color=>'red'},'*')),
						td(input({-type=>'password',-name=>'password',-maxlength=>255,-size=>16,-override=>1}))
					),
					Tr(
						td('Confirm password', font({-color=>'red'},'*')),
						td(
							input({-type=>'password',-name=>'password_confirm',-maxlength=>255,-size=>16,-override=>1}),
							hidden({-name=>'a',-value=>'send_email_challenge',-override=>1})
						)
					)
				),
				br(),
				submit({-value=>'Register',-override=>1}),
				end_form()
			);

		&$page_end();
	}
}

elsif ($action eq 'send_email_challenge') {
	my $email = $q->param('email');
	my $password = $q->param('password');
	my $name_last = $q->param('name_last');
	my $name_first = $q->param('name_first');
	my $password_confirm = $q->param('password_confirm');

	my $everything_ok = 1;

	$name_last = encode_entities($name_last);
	$name_first = encode_entities($name_first);

	my $email_escaped = escape($email);
	my $name_last_escaped = escape($name_last);
	my $name_first_escaped = escape($name_first);

	## make sure that the email address is not already registered
	my $select = "select count(*) from users where email = '$email'";
	my $qh = $dbh->prepare($select);
	$qh->execute();
	my ($count) = $qh->fetchrow_array();
	if ($count) {
		$everything_ok = 0;
		print $q->redirect("$script?a=register&ec=5&e=$email_escaped");
	}

	## check the format of the email address
	if (&$check_email_address($email) != 1) {
		$everything_ok = 0;
		print $q->redirect("$script?a=register&ec=2&e=$email_escaped&n=$name_last_escaped&f=$name_first_escaped");
	}

	## verify that a name was entered
	if (! ($name_first =~ /\w{2,}/)) {
		$everything_ok = 0;
		print $q->redirect("$script?a=register&ec=6&e=$email_escaped&n=$name_last_escaped&f=$name_first_escaped");
	}

	## make sure that the passwords match
	if ($password ne $password_confirm) {
		$everything_ok = 0;
		print $q->redirect("$script?a=register&ec=1&e=$email_escaped&n=$name_last_escaped&f=$name_first_escaped");
	}

	## make sure a password was entered
	if (($password eq '') || ($password_confirm eq '')) {
		$everything_ok = 0;
		print $q->redirect("$script?a=register&ec=3&e=$email_escaped&n=$name_last_escaped&f=$name_first_escaped");
	}

	## check password requirements
	if ((length($password) < 6) || (length($password) > 16)) {
		$everything_ok = 0;
		print $q->redirect("$script?a=register&ec=4&e=$email_escaped&n=$name_last_escaped&f=$name_first_escaped");
	}

	if ($everything_ok) {
		## generate a random challenge password
		my $challenge = &$get_challenge();

		## delete any existing challenge passwords
		my $delete = "delete from register where email = '$email'";
		$qh = $dbh->prepare($delete);
		$qh->execute();

		## insert the challenge password
		my $insert = "
			insert into register (
				email,
				name_last,
				name_first,
				password,
				challenge,
				created
			) values (
				'$email',
				'$name_last',
				'$name_first',
				'$password',
				'$challenge',
				NULL
			)";
		$qh = $dbh->prepare($insert);
		$qh->execute();

		my $name = $name_first;
		$name .= " $name_last" if (defined $name_last);

		## send the email with the challenge password
		open(MAIL,"| $sendmail -t");
		print MAIL "To: $name <$email>\n";
		print MAIL "From: $registration_name <$registration_email>\n";
		print MAIL "Subject: $registration_subject\n";
		print MAIL "Content-type: text/html\n\n";
		print MAIL "A registration request has been received for the email address $email. ";
		print MAIL "If this is correct and you wish to complete the registration process, please ";
		print MAIL "perform one of the following options:";
		print MAIL br(), br();
		print MAIL "Enter the following registration code: ";
		print MAIL "$challenge";
		print MAIL br(), br();
		print MAIL "&nbsp; &nbsp; OR ";
		print MAIL br(), br();
		print MAIL "Use the following URL: ";
		print MAIL a({-href=>"$script?a=confirm&e=$email_escaped&c=$challenge"},"$script?a=confirm&e=$email_escaped&c=$challenge");
		print MAIL br(), br();
		close(MAIL);

		## redirect the user to the challenge verification page
		print $q->redirect("$script?a=verify&e=$email_escaped");
	}
}

elsif ($action eq 'verify') {
	my $email = $q->param('e');
	my $error_code = $q->param('ec') || 0;

	## error codes:
	##  0 = no error
	##  1 = invalid challenge entered, try again

	&$page_begin();

	print 
		h3('Verify Your Registration');

	if ($error_code) {
		print 
			div(
				{-class=>'error'},
				'ERROR: The registration code you entered was incorrect. Please verify that you have entered the correct code sent to you in email.'
			);
	}
	else {
		print 
			div(
				{-class=>'message'},
				'An email has been sent to the address you provided. Please check your email and either enter the registration code provided or click on the link in the email.'
			);
	}

	print
		blockquote(
			start_form({-action=>$script}),
			table(
				{-class=>'brown'},
				Tr(
					td('Enter registration code'),
					td(
						input({-type=>'text',-name=>'c',-maxlength=>255,-size=>10,-override=>1}),
						hidden({-name=>'e',-value=>$email,-override=>1}),
						hidden({-name=>'a',-value=>'confirm',-override=>1})
					)
				)
			),
			br(),
			submit({-value=>'Submit'}),
			end_form()
		);

	&$page_end();
}

elsif ($action eq 'confirm') {
	my $email = $q->param('e');
	my $challenge = $q->param('c');
	my $email_escaped = escape($email);

	## strip any leading or trailing whitespace
	$challenge =~ s/^\s+//;
	$challenge =~ s/\s+$//;

	my $select = "
		select
			name_first,
			name_last,
			challenge,
			password
		from
			register
		where
			email = '$email'";
	my $qh = $dbh->prepare($select);
	$qh->execute();
	my ($db_name_first,$db_name_last,$db_challenge,$db_password) = $qh->fetchrow_array();

	if ($db_challenge eq $challenge) {
		## add the user, using the password from the register table
		my $insert = "
			insert into users (
				user_id,
				email,
				name_first,
				name_last,
				password
			) values (
				NULL,
				'$email',
				'$db_name_first',
				'$db_name_last',
				'$db_password'
			)";
		$qh = $dbh->prepare($insert);
		$qh->execute();

		my $select = "select user_id from users where email = '$email'";
		$qh = $dbh->prepare($select);
		$qh->execute();
		my ($user_id) = $qh->fetchrow_array();

		## write cookies
		my $salt = join '', ('.', '/', 0..9, 'A'..'Z', 'a'..'z')[rand 64, rand 64];
		my $crypt_password = crypt($db_password,$salt);

		my $cookie_user_id = $q->cookie(-name=>'VeloCalUserID',-value=>$user_id,-expires=>'+10y');
		my $cookie_password = $q->cookie(-name=>'VeloCalPass',-value=>$crypt_password,-expires=>'+10y');

		## remove the email from the register table since registration is now complete
		my $delete = "delete from register where email = '$email'";
		$qh = $dbh->prepare($delete);
		$qh->execute();

		## redirect the user to the 'profile_edit' page
		print $q->redirect(-location=>"$script?a=profile_edit",-cookie=>[$cookie_user_id,$cookie_password]);
	}
	else {
		print $q->redirect("$script?a=verify&ec=1&e=$email_escaped");
	}
}

elsif ($action eq 'unregister') {
	if ($logged_in) {
		my $ec = $q->param('ec');
		my $gids = $q->param('g');

# TODO: need to add error message, if any

		&$page_begin();

		print 
			h3('Unregister'),
			p('WARNING: Once you unregister, it cannot be undone.'),
			p('Please confirm that you would like to unregister from the application.'),
			p('If you are the only administrator for any groups, you will need to assign other administrators before you can unregister.'),
			start_form({-action=>$script,-method=>'POST'}),
			submit({-value=>'Unregister'}),
			hidden({-name=>'a',-value=>'unregister_final',-override=>1}),
			end_form();

		&$page_end();
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

elsif ($action eq 'unregister_final') {
	if ($logged_in) {
		my $everything_ok = 1;
# TODO: add code to check for sole-administratorship
#       if found, go back to unregister, and set 'g' to list of group_ids

		if ($everything_ok) {
			my $user_id = $q->cookie('VeloCalUserID');
			my $password = $q->cookie('VeloCalPass');

			my $cookie_user_id = $q->cookie(-name=>'VeloCalUserID',-value=>$user_id,-expires=>'-1d');
			my $cookie_password = $q->cookie(-name=>'VeloCalPass',-value=>$password,-expires=>'-1d');

			my $select = "select email from users where user_id = $user_id";
			my $qh = $dbh->prepare($select);
			$qh->execute();
			my ($email) = $qh->fetchrow_array();

			my @tables = qw/group_queue register/;

			foreach my $table (@tables) {
				my $delete = "delete from $table where email = '$email'";
				my $qh = $dbh->prepare($delete);
				$qh->execute();
			}

			@tables = qw/event_user group_admin group_queue group_user users/;

			foreach my $table (@tables) {
				my $delete = "delete from $table where user_id = $user_id";
				my $qh = $dbh->prepare($delete);
				$qh->execute();
			}

			print $q->redirect(-location=>"$script?a=unregister_success",-cookie=>[$cookie_user_id,$cookie_password]);
		}
		else {
			print $q->redirect("$script?a=unregister&ec=1");
		}
	}
	else {
		print $q->redirect($script);
	}
}

elsif ($action eq 'unregister_success') {
	&$page_begin();

	print 
		h3('Unregister'),
		p('You have been successfully unregistered from the application.');

	&$page_end();
}

elsif ($action eq 'main') {
	my $user_id = $q->cookie('VeloCalUserID');

	my $select = "select mon_cal from users where user_id = $user_id";
	my $qh = $dbh->prepare($select);
	$qh->execute();
	my ($mon_cal) = $qh->fetchrow_array();
	($mon_cal eq 'Y') ? ($mon_cal = 1) : ($mon_cal = 0);

	my ($sec,$min,$hour,$day,$month,$year) = localtime(time);
	$year += 1900;
	$month += 1;
	($year,$month,$day) = split ':', &$convert_to_localtime("$year:$month:$day:$hour:$min:$sec");

	my $current_day = $day;
	my $current_month = $month;
	my $current_year = $year;

	if ((defined $q->param('y')) && (defined $q->param('m'))) {
		$year = $q->param('y');
		$month = $q->param('m');
	}

	my $cal_width = '95%';
	my $cal_cellheight = 70;  # min cell height in pixels
	my $cal_border = 0;
	my $cal_weekdayheadersbig = 1; # uses TH for column headers

	my $next_month = $month + 1;
	$next_month = 1 if ($month == 12);
	my $next_year = $year;
	$next_year = ($year + 1) if ($month == 12);

	my $prev_month = $month - 1;
	$prev_month = 12 if ($month == 1);
	my $prev_year = $year;
	$prev_year = ($year - 1) if ($month == 1);

	$month += 0;
	my $cal = new HTML::CalendarMonthSimple('year'=>$year,'month'=>$month);
	$cal->width($cal_width);
	$cal->cellheight($cal_cellheight);
	$cal->border($cal_border);
	$cal->header('');
	$cal->weekdayheadersbig($cal_weekdayheadersbig);
	$cal->weekdays('Mon','Tue','Wed','Thu','Fri');
	$cal->saturday('Sat');
	$cal->sunday('Sun');
	$cal->tableclass('brown');
#	$cal->todaycellclass('today');
	$cal->datecellclass($current_day,'today') if ($month == $current_month);
	$cal->showdatenumbers(0);
	$cal->weekstartsonmonday($mon_cal);

	for (my $i = 1; $i <= 31; $i++) {
		my $add_href = a({-href=>"$script?a=add&d=$i&m=$month&y=$year"},'Add');
		$add_href = "[$add_href]";

		my $temp_month = $month;
		$temp_month = "0$temp_month" if ($temp_month < 10);
		my $temp_day = $i;
		$temp_day = "0$temp_day" if ($temp_day < 10);

		if ("$year$temp_month$temp_day" < "$current_year$current_month$current_day") {
			$add_href = '&nbsp;';
		}

		my $content = 
			div(
				{-class=>'cal_day'},
				span($add_href),
				$i
			);
		$cal->setcontent($i,$content);
	}

	# pull all rides from the database

	$month = "0$month" if ($month < 10);
	$next_month = "0$next_month" if ($next_month < 10);
	my $month_start = "$year$month" . "01000000";
	my $month_end = "$next_year$next_month" . "01000000";

	$select = "
		select
			e.event_id,
			g.group_id,
			g.name,
			e.title,
			e.start_time,
			e.location,
			e.pace,
			e.terrain,
			e.notes,
			u.status
		from
			events e,
			event_user u,
			groups g
		where
			e.event_id = u.event_id and
			e.group_id = g.group_id and
			u.user_id = $user_id and
			e.start_time < '$month_end' and
			e.start_time >= '$month_start'
		order by
			e.start_time,
			g.name";
	$qh = $dbh->prepare($select);
	$qh->execute();

	my %EVENT_DAY;

	while (my ($event_id,$group_id,$name,$title,$start_time,$location,$pace,$terrain,$notes,$status) = $qh->fetchrow_array()) {
		my ($event_year,$event_month,$event_day,$event_hour,$event_minute,$event_second);

		if ($start_time =~ /^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/) {
			$event_year = $1;
			$event_month = $2;
			$event_day = $3;
			$event_hour = $4;
			$event_minute = $5;
			$event_second = $6;
		
			$EVENT_DAY{$event_day}++;
			my $class = 'cal_event_first';
			$class = 'cal_event' if ($EVENT_DAY{$event_day} > 1);

			$status = '' if (not defined $status);

			my $event_title = 
				div(
					{-class=>$class},
					"$event_hour:$event_minute ",
					span(
						{-class=>"status_$status"},
						$status
					), br(),
					"$name", br(),
					a({-href=>"$script?a=event&e=$event_id"},$title), br(),
				);
			$cal->addcontent($event_day,$event_title);
		}
	}

	&$page_begin();

	print 
		h3('Ride Calendar'),
		' &nbsp; ',
		a({-href=>"$script?m=$prev_month&y=$prev_year"},img({-src=>'images/action_back.gif',-border=>0})),
		a({-href=>"$script?m=$next_month&y=$next_year"},img({-src=>'images/action_forward.gif',-border=>0})),
		' &nbsp; ',
		font({-size=>'+1'},"$months[$month-1] $year"),
		br(),
		br(),
		$cal->as_HTML,
		br(),
		br();

	&$page_end();
}

elsif ($action eq 'logout') {
	my $password = $q->cookie('VeloCalPass');
	my $redirect_url = $q->param('redirect_url') || $script;

	my $cookie_user_id = $q->cookie(-name=>'VeloCalUserID',-value=>'expire_now',-expires=>'-1d');
	my $cookie_password = $q->cookie(-name=>'VeloCalPass',-value=>'expire_now',-expires=>'-1d');

	print $q->redirect(-location=>$redirect_url,-cookie=>[$cookie_user_id,$cookie_password]);
}

elsif ($action eq 'support') {
	&$page_begin();

	print 
		h3('Support'),
		p('Your feedback and questions are welcome. If reporting a problem, please provide as much detail as possible including any relevant URLs or error messages.'),
		start_form({-action=>$script,-method=>'POST'}),
		textarea({-name=>'comments',-rows=>5,-columns=>60,-override=>1}),
		hidden({-name=>'a',-value=>'thanks',-override=>1}),
		br(),
		br(),
		submit({-value=>'Send Feedback'}),
		end_form();

	&$page_end();
}

elsif ($action eq 'thanks') {
	my $user_id = $q->cookie('VeloCalUserID');
	my $comments = $q->param('comments');

	my $select = "select name_first,name_last,email,hide_email from users where user_id = $user_id";
	my $qh = $dbh->prepare($select);
	$qh->execute();
	my ($name_first,$name_last,$email,$hide_email) = $qh->fetchrow_array();

	($hide_email eq 'Y') ? ($email = '') : ($email = "&lt;$email&gt;");

	$comments = encode_entities($comments,'<>');
	$comments =~ s/\n/<br>/g;

	open(MAIL,"| $sendmail -t");
	print MAIL "To: $feedback_email\n";
	print MAIL "From: $registration_name <$registration_email>\n";
	print MAIL "Subject: VeloCal Feedback\n";
	print MAIL "Content-type: text/html\n\n";
	print MAIL "User: $name_first $name_last $email<br><br>\n\n";
	print MAIL "Comments: <br><br>\n\n";
	print MAIL "$comments\n";
	close(MAIL);

	&$page_begin();

	print 
		h3('Thanks'),
		p('Thank you for your comments. Your feedback and questions are extremely helpful. If your comments require a response, we will try to respond as quickly as possible.').
		br(),
		br();

	&$page_end();
}

elsif ($action eq 'profile') {
	if ($logged_in) {
		my $user_id = $q->cookie('VeloCalUserID');

		my $select = "
			select
				name_last,
				name_first,
				biography,
				pref_pace,
				pref_terrain,
				photo_filename,
				email,
				mon_cal,
				hide_email
			from
				users
			where
				user_id = $user_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($name_last,$name_first,$biography,$pref_pace,$pref_terrain,$photo_filename,$db_email,$mon_cal,$hide_email) = $qh->fetchrow_array();

		my $image = '&nbsp';
		if (defined $photo_filename) {
			$image = img({-src=>"$script?a=get_image&t=users&c=photo&l=user_id&r=$user_id&f=photo_filename&m=photo_magick"});
		}

		my $pref_calendar = "Week Begins on Sunday";
		$pref_calendar = "Week Begins on Monday" if ($mon_cal eq 'Y');

		my $pref_hide_email = "Email is visible to group members";
		$pref_hide_email = "Email is not displayed" if ($hide_email eq 'Y');

		$biography =~ s/\n/<br>/g;

		&$page_begin();

		print
			h3('Your Profile'),
			blockquote(
				table(
					{-class=>'brown'},
					Tr(
						td('Name'),
						td("$name_first $name_last")
					),
					Tr(
						td('Email'),
						td(a({-href=>"mailto:$db_email"},$db_email))
					),
					Tr(
						td({-nowrap=>'nowrap'},'Email Security'),
						td($pref_hide_email)
					),
					Tr(
						td('Biography'),
						td($biography)
					),
					Tr(
						td({-nowrap=>'nowrap'},'Preferred Pace'),
						td($pref_pace)
					),
					Tr(
						td({-nowrap=>'nowrap'},'Preferred Terrain'),
						td($pref_terrain)
					),
					Tr(
						td({-nowrap=>'nowrap'},'Calendar'),
						td($pref_calendar)
					),
					Tr(
					td('Photo'),
						td($image)
					)
				),
				br(),
				start_form({-action=>$script,-method=>'get',-style=>'display: inline;'}),
				hidden({-name=>'a',-value=>'profile_edit',-override=>1}),
				submit({-value=>'Edit',-override=>1}),
				end_form()
			),
			h4('User Actions'),
			blockquote(
				ul(
					{-class=>'action_list'},
					li(
						a({-href=>"$script?a=change_password"},'Change password')
					),
					li(
						a({-href=>"$script?a=change_email"},'Change email')
					),
					li(
						a({-href=>"$script?a=unregister"},'Unregister')
					)
				)
			);

		&$page_end();
	}
	else {
		print $q->redirect("$script?a=login");
	}
}

elsif ($action eq 'map_edit') {
	if ($logged_in) {
		my $user_id = $q->cookie('VeloCalUserID');
		my $map_id = $q->param('id');
		my $group_id = $q->param('g');

		my ($is_owner, $is_admin);

		if ($map_id ne '')  {
			# check if user is map owner
			my $select = "
				select
					group_id
				from
					maps
				where
					id = $map_id and
					user_id = $user_id";
			my $qh = $dbh->prepare($select);
			$qh->execute();
			($is_owner) = $qh->fetchrow_array();

			# check if user is admin for group
			$select = "
				select 
					m.id
				from
					maps m,
					group_admin g
				where 
					m.id = $map_id and
					g.group_id = m.group_id and
					g.user_id = $user_id";
			$qh = $dbh->prepare($select);
			$qh->execute();
			($is_admin) = $qh->fetchrow_array();
		}

		if (($q->param('new') == 1) || (($is_owner ne '') || ($is_admin ne ''))) {
			my $ec = $q->param('ec');

			my ($name,$description,$url,$image,$image_filename,$image_magick,$last_updated);

			if ($map_id =~ /^\d+$/) {
				my $select = "
					select
						name,
						description,
						url,
						image,
						image_filename,
						image_magick,
						last_updated
					from
						maps
					where
						id = $map_id";
				my $qh = $dbh->prepare($select);
				$qh->execute();
				($name,$description,$url,$image,$image_filename,$image_magick,$last_updated) = $qh->fetchrow_array();
			}

			$name = decode_entities($name,'<>');
			$description = decode_entities($description,'<>');

			&$page_begin('VeloCal','map_check_action();');

			my $map_default = 'existing';
			$map_default = 'add' if (defined $q->param('new'));
			$map_default = 'url' if ($url ne '');
			$map_default = 'existing' if ($image_filename ne '');

			($q->param('new') == 1) ? (print h3('Add Map')) : (print h3('Edit Map'));

			if ($ec == 1) {
				print 
					div(
						{-class=>'error'},
						'ERROR: Required fields cannot be left blank.'
					);
			}
			elsif ($ec == 2) {
				print 
					div(
						{-class=>'error'},
						'ERROR: Photo is too large.'
					);
			}
			elsif ($ec == 3) {
				print 
					div(
						{-class=>'error'},
						'ERROR: Photo can only be JPEG, GIF, or PNG.'
					);
			}
			elsif ($ec == 4) {
				print 
					div(
						{-class=>'error'},
						'ERROR: No map image selected.'
					);
			}

			print
				p(font({-color=>'red'},'*'), " indicates a required field."),
				start_div({-class=>'profile_form'}),
				start_multipart_form({-action=>$script,-method=>'POST',-name=>'velocal',-style=>'display: inline;'}),
				start_table({-class=>'brown'}),
				Tr(
					td('Map Name ' . font({-color=>'red'},'*')),
					td(input({-name=>'name',-size=>24,-maxlength=>255,-value=>$name,-override=>1}))
				),
				Tr(
					td('Map Description'),
					td(textarea({-name=>'description',-value=>$description,-cols=>35,-rows=>4,-override=>1}))
				);

			if (defined $image_filename) {
				my @values = qw/existing url replace/;
				my %labels = (
					existing => 'Use existing map',
					url => 'Specify a map URL',
					replace => 'Replace existing map'
				);

				print
					Tr(
						td('Map'),
						td(
							radio_group({-id=>'map_action',-name=>'map_action',-values=>\@values,-labels=>\%labels,-default=>$map_default,-linebreak=>'true',-override=>1,-onClick=>'map_check_action()'}),
							blockquote(
								div(
									{-id=>'map_url',-style=>'display: none;'},
									'URL: ',
									input({-name=>'url',-size=>50,-maxlength=>255,-value=>$url,-override=>1})
								),
								div(
									{-id=>'map_image',-style=>'display: none;'},
									'File Name: ',
									filefield({-name=>'image_name',-size=>20,-maxlength=>262144,-override=>1}),
									p(
										i(
											'Note: maps images must be of type PNG, GIF, or ', br(),
											'JPEG and cannot exceed 256KB in size.'
										)
									)
								)
							)
						)
					);
			}
			else {
				my @values = qw/url add/;
				my %labels = (
					url => 'Specify a map URL',
					add => 'Add a map'
				);

				print
					Tr(
						td('Map'),
						td(
							radio_group({-name=>'map_action',-values=>\@values,-labels=>\%labels,-default=>$map_default,-linebreak=>'true',-override=>1,-onClick=>'map_check_action()'}),
							blockquote(
								div(
									{-id=>'map_url',-style=>'display: none;'},
									'URL: ',
									input({-name=>'url',-size=>50,-maxlength=>255,-value=>$url,-override=>1})
								),
								div(
									{-id=>'map_image',-style=>'display: none;'},
									'File Name: ',
									filefield({-name=>'image_name',-size=>20,-maxlength=>262144,-override=>1}),
									p(
										i(
											'Note: maps images must be of type PNG, GIF, or ', br(),
											'JPEG and cannot exceed 256KB in size.'
										)
									)
								)
							)
						)
					);
			}

			print
				end_table(),
				br(),
				hidden({-name=>'a',-value=>'map_write',-override=>1}),
				hidden({-name=>'map_id',-value=>$map_id,-override=>1}),
				hidden({-name=>'group_id',-value=>$group_id,-override=>1}),
				submit({-value=>'Save'}),
				end_form();

			unless (defined $q->param('new')) {
				print
					start_multipart_form({-action=>$script,-method=>'POST',-style=>'display: inline;'}),
					hidden({-name=>'a',-value=>'map_delete',-override=>1}),
					hidden({-name=>'map_id',-value=>$map_id,-override=>1}),
					submit({-value=>'Delete'}),
					end_form();
			}

			print
				end_div();

			&$page_end();
		}
		else {
			&$page_begin();
			print "You are NOT authorized to edit this map.";
			&$page_end();
		}
	}
	else {
		print $q->redirect("$script?a=login");
	}
}

elsif ($action eq 'map_delete') {
	if ($logged_in) {
		my $user_id = $q->cookie('VeloCalUserID');
		my $map_id = $q->param('map_id');

		# check if user is map owner
		my $select = "
			select
				group_id
			from
				maps
			where
				id = $map_id and
				user_id = $user_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($is_owner) = $qh->fetchrow_array();

		# check if user is admin for group
		$select = "
			select 
				m.id
			from
				maps m,
				group_admin g
			where 
				m.id = $map_id and
				g.group_id = m.group_id and
				g.user_id = $user_id";
		$qh = $dbh->prepare($select);
		$qh->execute();
		my ($is_admin) = $qh->fetchrow_array();

		if (($is_admin ne '') || ($is_owner ne '')) {
			my $delete = "delete from maps where id = $map_id";
			$qh = $dbh->prepare($delete);
			$qh->execute();

			my $update = "update events set map_id = NULL where map_id = $map_id";
			$qh = $dbh->prepare($update);
			$qh->execute();

			print $q->redirect("$script?a=group&g=$is_owner");
		}
		else {
			&$page_begin();
			print "You are NOT authorized to delete this map.";
			&$page_end();
		}
	}
	else {
		print $q->redirect("$script?a=login");
	}
}

elsif ($action eq 'map_write') {
	if ($logged_in) {
		my $user_id = $q->cookie('VeloCalUserID');

		my $name = $q->param('name');
		my $description = $q->param('description');
		my $map_action = $q->param('map_action');
		my $url = $q->param('url');
		my $image_name = $q->param('image_name');
		my $group_id = $q->param('group_id');
		my $map_id = $q->param('map_id');

		# remove html from all inputs;
		$name = encode_entities($name,'<>');
		$description = encode_entities($description,'<>');

		$name =~ s/^\s+//g; # remove leading whitespace
		$description =~ s/\s+$//g; # remove trailing whitespace

		# check for required fields
		my $ec;
		my $everything_ok = 1;

		if ($name eq '') {
			$everything_ok = 0;
			$ec = 1;
		}

		if ((($map_action eq 'add') || ($map_action eq 'replace')) && ($image_name eq '')) {
			$everything_ok = 0;
			$ec = 4;
		}

		# upload the file
		my $image;
		if ((($map_action eq 'add') || ($map_action eq 'replace')) && ($image_name ne '')) {
			my $fh = $q->upload('image_name');
			while (<$fh>) {
				$image .= $_;
			}

			if (length $image > 256 * 1024) {
				$everything_ok = 0;
				$ec = 2;
			}
		}

		# check for valid image magick
		my $image_magick;

		if (($everything_ok) && (($map_action eq 'add') || ($map_action eq 'replace')) && ($image_name ne '')) {
			use Image::Magick;
			my $imageblob = Image::Magick->new();
			$imageblob->BlobToImage($image);

			($image_magick) = $imageblob->Get('magick');
			if (! (($image_magick eq 'JPEG') || ($image_magick eq 'GIF') || ($image_magick eq 'PNG'))) {
				$everything_ok = 0;
				$ec = 3;
			}
		}

		# everything is good, do insert or update
		if ($everything_ok) {
			if ($map_action eq 'url') {
				undef $image_name;
				undef $image;
				undef $image_magick;
			}
			else {
				undef $url;
			}

			if ($map_id eq '') {  # add
				my $insert = "
					insert into maps (
						group_id,
						user_id,
						name,
						description,
						url,
						image,
						image_filename,
						image_magick
					) values (
						$group_id,
						$user_id,
						?,
						?,
						?,
						?,
						?,
						?
					)";
				my $qh = $dbh->prepare($insert);
				$qh->execute($name,$description,$url,$image,$image_name,$image_magick);
			}
			else {  # update
				my $update = "
					update maps set
						name = ?,
						description = ?,
						url = ?,
						image = ?,
						image_filename = ?,
						image_magick = ?
					where
						id = $map_id";
				my $qh = $dbh->prepare($update);
				$qh->execute($name,$description,$url,$image,$image_name,$image_magick);
			}

			print $q->redirect("$script?a=group&g=$group_id");
		}
		else {
			print $q->redirect("$script?a=map_edit&id=$map_id&g=$group_id&ec=$ec");
		}
	}
	else {
		print $q->redirect("$script?a=login");
	}
}

elsif ($action eq 'profile_edit') {
	if ($logged_in) {
		my $user_id = $q->cookie('VeloCalUserID');
		my $ec = $q->param('ec');

		my $select = "
			select
				name_last,
				name_first,
				biography,
				pref_pace,
				pref_terrain,
				photo_filename,
				mon_cal,
				hide_email
			from
				users
			where
				user_id = $user_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($name_last,$name_first,$biography,$pref_pace,$pref_terrain,$photo_filename,$mon_cal,$hide_email) = $qh->fetchrow_array();

		$name_last = decode_entities($name_last,'<>');
		$name_first = decode_entities($name_first,'<>');
		$biography = decode_entities($biography,'<>');

		# set default values for new users
		$hide_email = 'N' if ($hide_email eq '');
		$mon_cal = 'N' if ($mon_cal eq '');

		&$page_begin();

		print 
			h3('Profile Edit');

		my @pace_values = &$get_enum('users','pref_pace');
		my @terrain_values = &$get_enum('users','pref_terrain');
		my @mon_cal_values = &$get_enum('users','mon_cal');
		my %mon_cal_labels = (
			"Y" => 'Week Begins on Monday',
			"N" => 'Week Begins on Sunday'
		);
		my @hide_email_values = &$get_enum('users','hide_email');
		my %hide_email_labels = (
			"N" => "Email is visible to group members",
			"Y" => "Email is not displayed"
		);

		if ($ec == 1) {
			print 
				div(
					{-class=>'error'},
					'ERROR: Required fields cannot be left blank.'
				);
		}
		elsif ($ec == 2) {
			print 
				div(
					{-class=>'error'},
					'ERROR: Photo is too large.'
				);
		}
		elsif ($ec == 3) {
			print 
				div(
					{-class=>'error'},
					'ERROR: Photo can only be JPEG, GIF, or PNG.'
				);
		}

		print
			p(font({-color=>'red'},'*'), " indicates a required field."),
			p('Use the following guidelines for selecting a preferred terrain.'),
			blockquote(
				table(
					{-class=>'brown'},
					Tr(
						td('Hilly'),
						td('Numerous long and steep climbs.')
					),
					Tr(
						td('Moderately Hilly'),
						td('Numerous climbs with no "killer" hills.')
					),
					Tr(
						td('Rolling'),
						td('Some small hills; farmland ups and downs.')
					),
					Tr(
						td('Flat'),
						td('Minimal gear shifting required.')
					)
				)
			),
			p('Use the following guidelines for selecting a preferred pace. Note: average speeds assume flat terrain. Speed will be lower when hills are involved. Also, the typical cruising speed will be higher than the average (about 2 mph).'),
			blockquote(
				table(
					{-class=>'brown'},
					Tr(
						td('AX'),
						td('For the very strong cyclists. Primary moving average 20+ mph.')
					),
					Tr(
						td('A'),
						td('For the strong cyclists. Primary moving average 17-19 mph.')
					),
					Tr(
						td('B'),
						td('For the average to strong cyclists. Primary moving average 15-17 mph.')
					),
					Tr(
						td('C'),
						td('For the average cyclists. Primary moving average 12-15 mph.')
					),
					Tr(
						td('D'),
						td('For the new, inexperienced riders. Primary moving average 9-12 mph, includes frequent rest stops.')
					)
				)
			),
			start_div({-class=>'profile_form'}),
			start_multipart_form({-action=>$script,-method=>'POST'}),
			start_table({-class=>'brown'}),
			Tr(
				td('First Name ' . font({-color=>'red'},'*')),
				td(input({-name=>'name_first',-size=>24,-maxlength=>255,-value=>$name_first,-override=>1}))
			),
			Tr(
				td('Last Name'),
				td(input({-name=>'name_last',-size=>24,-maxlength=>255,-value=>$name_last,-override=>1}))
			),
			Tr(
				td('Biography'),
				td(textarea({-name=>'biography',-rows=>10,-columns=>60,-value=>$biography,-override=>1}))
			),
			Tr(
				td('Preferred Pace ' . font({-color=>'red'},'*')),
				td(popup_menu({-name=>'pref_pace',-values=>\@pace_values,-default=>$pref_pace,-override=>1}))
			),
			Tr(
				td('Preferred Terrain ' . font({-color=>'red'},'*')),
				td(popup_menu({-name=>'pref_terrain',-values=>\@terrain_values,-default=>$pref_terrain,-override=>1}))
			),
			Tr(
				td('Calendar ' . font({-color=>'red'},'*')),
				td(popup_menu({-name=>'mon_cal',-values=>\@mon_cal_values,-labels=>\%mon_cal_labels,-default=>$mon_cal,-override=>1})
				)
			),
			Tr(
				td('Email Security ' . font({-color=>'red'},'*')),
				td(
					popup_menu({-name=>'hide_email',-values=>\@hide_email_values,-labels=>\%hide_email_labels,-default=>$hide_email,-override=>1}),
					hidden({-name=>'a',-value=>'profile_write',-override=>1})
				)
			);

		if (defined $photo_filename) {
			my @values = qw/existing remove replace/;
			my %labels = (
				existing => 'Use existing photo',
				remove => 'Delete existing photo',
				replace => 'Replace existing photo'
			);

			print
				Tr(
					td('Photo (max 64KB)'),
					td(
						radio_group({-id=>'photo_action',-name=>'photo_action',-values=>\@values,-labels=>\%labels,-default=>'existing',-linebreak=>'true',-override=>1,-onClick=>'photo_check_action(this)'}),
						div(
							{-id=>'filenamediv_replace',-style=>'display: none;'},
							filefield({-name=>'photo',-size=>20,-maxlength=>65536,-override=>1})
						)
					)
				);
		}
		else {
			my @values = qw/none add/;
			my %labels = (
				none => 'Do not use a photo',
				add => 'Add a photo'
			);

			print
				Tr(
					td('Photo'),
					td(
						radio_group({-name=>'photo_action',-values=>\@values,-labels=>\%labels,-default=>'none',-linebreak=>'true',-override=>1,-onClick=>'photo_check_action(this)'}),
						div(
							{-id=>'filenamediv_add',-style=>'display: none;'},
							filefield({-name=>'photo',-size=>20,-maxlength=>65536,-override=>1})
						)
					)
				);
		}

		print
			end_table(),
			br(),
			submit({-value=>'Save'}),
			end_form(),
			end_div();

		&$page_end();
	}
	else {
		print $q->redirect("$script?a=login");
	}
}

elsif ($action eq 'profile_write') {
	if ($logged_in) {
		my $user_id = $q->cookie('VeloCalUserID');
		my $name_last = $q->param('name_last');
		my $name_first = $q->param('name_first');
		my $biography = $q->param('biography');
		my $pref_pace = $q->param('pref_pace');
		my $pref_terrain = $q->param('pref_terrain');
		my $photo_action = $q->param('photo_action');
		my $mon_cal = $q->param('mon_cal');
		my $hide_email = $q->param('hide_email');

		# remove html from all inputs;
		$name_last = encode_entities($name_last,'<>');
		$name_first = encode_entities($name_first,'<>');
		$biography = encode_entities($biography,'<>');

		$name_first =~ s/^\s+//g; # remove leading whitespace
		$name_first =~ s/\s+$//g; # remove trailing whitespace
		$name_last =~ s/^\s+//g; # remove leading whitespace
		$name_last =~ s/\s+$//g; # remove trailing whitespace

		# check for required fields
		my $ec;
		my $everything_ok = 1;

		if ($name_first eq '') {
			$everything_ok = 0;
			$ec = 1;
		}

		# upload the file
		my $photo;
		if ((($photo_action eq 'add') || ($photo_action eq 'replace')) && ($q->param('photo') ne '')) {
			my $fh = $q->upload('photo');
			while (<$fh>) {
				$photo .= $_;
			}

			if (length $photo > 64 * 1024) {
				$everything_ok = 0;
				$ec = 2;
			}
		}

		if (($everything_ok) && (($photo_action eq 'add') || ($photo_action eq 'replace')) && ($q->param('photo') ne '')) {
			my $photo_filename = $q->param('photo');

			use Image::Magick;
			my $image=Image::Magick->new();
			$image->BlobToImage($photo);

			my ($photo_magick,$photo_width,$photo_height) = $image->Get('magick','width','height');

			if (($photo_magick eq 'JPEG') || ($photo_magick eq 'GIF') || ($photo_magick eq 'PNG')) {
				if (($photo_width > $max_profile_photo_width) || ($photo_height > $max_profile_photo_height)) {
					$image->Resize('geometry'=>"${max_profile_photo_width}x$max_profile_photo_height");
				}

				my $resized_photo = $image->ImageToBlob();

				my $update = "
					update users set
						photo = ?,
						photo_filename = ?,
						photo_magick = ?
					where
						user_id = $user_id";
				my $qh = $dbh->prepare($update);
				$qh->execute($resized_photo,$photo_filename,$photo_magick);
			}
			else {
				$everything_ok = 0;
				$ec = 3;
			}
		}

		if ($everything_ok) {
			my $update = "
				update users set
					name_last = ?,
					name_first = ?,
					biography = ?,
					pref_pace = ?,
					pref_terrain = ?,
					mon_cal = ?,
					hide_email = ?
				where
					user_id = $user_id";
			my $qh = $dbh->prepare($update);
			$qh->execute($name_last,$name_first,$biography,$pref_pace,$pref_terrain,$mon_cal,$hide_email);

			if ($photo_action eq 'remove') {
				$update = "
					update users set
						photo = NULL,
						photo_filename = NULL,
						photo_magick = NULL
					where
						user_id = $user_id";
				$qh = $dbh->prepare($update);
				$qh->execute();
			}

			print $q->redirect("$script?a=profile");
		}
		else {
			print $q->redirect("$script?a=profile_edit&ec=$ec");
		}
	}
	else {
		print $q->redirect("$script?a=login");
	}
}

elsif ($action eq 'change_password') {
	if ($logged_in) {
		my $ec = $q->param('ec');

		&$page_begin();

		print 
			h3('Change Password');

		my $error_message;
		if ($ec == 1) {
			$error_message = 'ERROR: The passwords you entered do not match.';
		}
		elsif ($ec == 2) {
			$error_message = 'ERROR: The password provided does not meet password requirements.';
		}

		if ($ec != 0) {
			print 
				div(
					{-class=>'error'},
					$error_message
				);
		}

		print
			p('Passwords must be at least 6 characters and no more than 16 characters.'),
			start_form({-action=>$script,-method=>'POST'}),
			table(
				{-class=>'brown'},
				Tr(
					td('New Password'),
					td(input({-type=>'password',-name=>'password',size=>12,-maxlength=>16,-override=>1}))
				),
				Tr(
					td('Retype Password'),
					td(
						input({-type=>'password',-name=>'password2',size=>12,-maxlength=>16,-override=>1}),
						hidden({-name=>'a',-value=>'verify_password_change',-override=>1})
					)
				)
			),
			br(),
			submit({-value=>'Change Password'}),
			end_form();
				
		&$page_end();
	}
	else {
		print $q->redirect("$script?a=login");
	}
}

elsif ($action eq 'change_email') {
	if ($logged_in) {
		my $user_id = $q->cookie('VeloCalUserID');
		my $ec = $q->param('ec');
		my $new_email = $q->param('e');

		my $error_message;
		if ($ec == 1) {
			$error_message = 'ERROR: The email address you entered does not appear to be valid.';
		}
		elsif ($ec == 2) {
			$error_message = 'ERROR: The email addresses you entered do not match.';
		}
		elsif ($ec == 3) {
			$error_message = 'ERROR: The email address you entered is already registered.';
		}

		&$page_begin();

		print
			h3('Change Email');

		if ($ec != 0) {
			print 
				div(
					{-class=>'error'},
					$error_message
				);
		}

		my $select = "select email from users where user_id = $user_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($email) = $qh->fetchrow_array();

		print
			p(
				"Your current email address is " . 
				a({-href=>"mailto:$email"},$email) . 
				"." . 
				br() . 
				"Enter your new desired email address below."
			),
			start_form({-action=>$script,-method=>'POST'}),
			table(
				{-class=>'brown'},
				Tr(
					td('New email'),
					td(input({-name=>'email',-value=>$new_email,size=>25,-maxlength=>255,-override=>1}))
				),
				Tr(
					td('Re-enter email'),
					td(
						input({-name=>'email2',size=>25,-maxlength=>255,-override=>1}),
						hidden({-name=>'a',-value=>'verify_email_change',-override=>1})
					)
				)
			),
			br(),
			submit({-value=>'Change Email'}),
			end_form();
				
		&$page_end();
	}
	else {
		print $q->redirect("$script?a=login");
	}
}

elsif ($action eq 'verify_password_change') {
	if ($logged_in) {
		my $user_id = $q->cookie('VeloCalUserID');
		my $password = $q->param('password');
		my $password2 = $q->param('password2');

		my $everything_ok = 1;
		if ($password ne $password2) {
			$everything_ok = 0;
			print $q->redirect("$script?a=change_password&ec=1");
		}
		elsif (length $password < 6) {
			$everything_ok = 0;
			print $q->redirect("$script?a=change_password&ec=2");
		}
		elsif (length $password > 16) {
			$everything_ok = 0;
			print $q->redirect("$script?a=change_password&ec=2");
		}

		if ($everything_ok) {
			my $update = "
				update users set
					password = ?
				where
					user_id = $user_id";
			my $qh = $dbh->prepare($update);
			$qh->execute($password);

			my $select = "
				select 
					email
				from
					users
				where
					user_id = $user_id";
			$qh = $dbh->prepare($select);
			$qh->execute();
			my ($email) = $qh->fetchrow_array();

			my $email_escaped = escape($email);
			print $q->redirect("$script?a=login&ec=2&e=$email_escaped");
		}
	}
	else {
		print $q->redirect("$script?a=login");
	}
}

elsif ($action eq 'verify_email_change') {
	if ($logged_in) {
		my $user_id = $q->cookie('VeloCalUserID');
		my $new_email = $q->param('email');
		my $new_email2 = $q->param('email2');

		my $new_email_escaped = escape($new_email);

		my $everything_ok = 1;

		## check that the two emails entered match
		if ($new_email ne $new_email2) {
			$everything_ok = 0;
			print $q->redirect("$script?a=change_email&ec=2&e=$new_email_escaped");
		}

		## check that the email is in the valid format
		if (&$check_email_address($new_email) != 1) {
			$everything_ok = 0;
			print $q->redirect("$script?a=change_email&ec=1&e=$new_email_escaped");
		}

		# check that the email address is not already registered
		my $select = "
			select
				email
			from
				users
			where
				email = '$new_email'";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($existing_email) = $qh->fetchrow_array();

		if (defined $existing_email) {
			$everything_ok = 0;
			print $q->redirect("$script?a=change_email&ec=3&e=$new_email_escaped");
		}

		## everything looks good, proceed
		if ($everything_ok) {
			my $challenge = &$get_challenge();

			my $update = "
				update users set
					email_new = '$new_email',
					email_challenge = '$challenge'
				where
					user_id = $user_id";
			my $qh = $dbh->prepare($update);
			$qh->execute();

			my $select = "
				select
					name_last,
					name_first
				from
					users
				where
					user_id = $user_id";
			$qh = $dbh->prepare($select);
			$qh->execute();
			my ($name_last,$name_first) = $qh->fetchrow_array();

			my $name = $name_first;
			$name .= " $name_last" if (defined $name_last);

			## send the email with the challenge password
			open(MAIL,"| $sendmail -t");
			print MAIL "To: $name <$new_email>\n";
			print MAIL "From: $registration_name <$registration_email>\n";
			print MAIL "Subject: $email_change_subject\n";
			print MAIL "Content-type: text/html\n\n";
			print MAIL "An email address change request has been received for the ";
			print MAIL "new email address $new_email. ";
			print MAIL "If this is correct and you wish to complete this process, please ";
			print MAIL "perform one of the following options:";
			print MAIL br(), br();
			print MAIL "Enter the following challenge password: ";
			print MAIL "$challenge";
			print MAIL br(), br();
			print MAIL "&nbsp; &nbsp; OR ";
			print MAIL br(), br();
			print MAIL "Use the following URL: ";
			print MAIL a({-href=>"$script?a=email_confirm&u=$user_id&c=$challenge"},"$script?a=email_confirm&u=$user_id&c=$challenge");
			print MAIL br(), br();
			close(MAIL);

			print $q->redirect("$script?a=email_verify");
		}
	}
	else {
		print $q->redirect("$script?a=login");
	}
}

elsif ($action eq 'email_verify') {
	if ($logged_in) {
		my $user_id = $q->cookie('VeloCalUserID');
		my $ec = $q->param('ec');

		my $select = "select email_new from users where user_id = $user_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($email) = $qh->fetchrow_array();
		&$page_begin();

		print 
			h3('Email Change Verification');

		if ($ec == 1) {
			print 
				div(
					{-class=>'error'},
					'ERROR: The challenge you entered was incorrect. Please try again.'
				);
		}
		else {
			print 
				div(
					{-class=>'message'},
					"An email has been sent to your new email address $email. Use the link or challenge password in the email to complete the email change process."
				);
		}

		print
			start_form({-action=>$script,-method=>'POST'}),
			table(
				{-class=>'brown'},
				Tr(
					td('New Email Address:'),
					td(input({-name=>'new_email',-value=>$email,-size=>25,-maxlength=>255,-override=>1}))
				),
				Tr(
					td('Challenge Password:'),
					td(
						input({-name=>'c',-size=>25,-maxlength=>255,-override=>1}),
						hidden({-name=>'u',-value=>$user_id,-override=>1}),
						hidden({-name=>'a',-value=>'email_confirm',-override=>1})
					)
				)
			),
			br(),
			submit({-value=>'Verify Email'}),
			end_form();
	
		&$page_end();
	}
	else {
		print $q->redirect("$script?a=login");
	}
}

elsif ($action eq 'email_confirm') {
	my $user_id = $q->param('u');
	my $challenge = $q->param('c');

	my $select = "
		select
			email_new,
			email_challenge
		from
			users
		where
			user_id = $user_id";
	my $qh = $dbh->prepare($select);
	$qh->execute();
	my ($email_new_db,$challenge_db) = $qh->fetchrow_array();

	if ($challenge eq $challenge_db) {
		my $update = "
			update users set
				email = '$email_new_db',
				email_new = NULL,
				email_challenge = NULL
			where
				user_id = $user_id";
		$qh = $dbh->prepare($update);
		$qh->execute();

		## logout
		my $cookie_user_id = $q->cookie(-name=>'VeloCalUserID',-value=>'expire_now',-expires=>'-1d');
		my $cookie_password = $q->cookie(-name=>'VeloCalPass',-value=>'expire_now',-expires=>'-1d');

		my $email_escaped = escape($email_new_db);
		print $q->redirect(-location=>"$script?a=login&ec=3&e=$email_escaped",-cookie=>[$cookie_user_id,$cookie_password]);
	}
	else {
		print $q->redirect("$script?a=email_verify&ec=1");
	}
}

elsif ($action eq 'join') {
	if ($logged_in) {
		## get the city values
		my %cities;
		my $select = "
			select
				distinct city,
				state
			from
				groups
			where
				type in ('public','restricted')
			group by
				city,
				state";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		while (my ($city,$state) = $qh->fetchrow_array()) {
			$cities{$state}{$city} = &$ucwords($city);
		}

		my @state_codes;
		my %states = &$get_states();
		push @state_codes, 'none';
		foreach my $code (sort { $states{$a} cmp $states{$b} } keys %cities) {
			push @state_codes, $code;
		}
		$states{'none'} = ' ';

		&$page_begin('VeloCal',"setState('none');");

		print
			h3('Join a Group'),
			p('Use this page to join a public or restricted group. Access to public groups is granted immediately. Access to restricted groups requires the authorization of a group administrator. If you would like to join a private group, you must directly contact an administrator of the private group and request an invitation.'),
			p('To browse a list of groups, first select a state.'),
			start_form(),
			'Select State: ',
			popup_menu({-name=>'state',-id=>'state',-values=>\@state_codes,-labels=>\%states,-default=>'none',-onChange=>"divState('');",-override=>1}),
			end_form();

		foreach my $state (sort keys %cities) {
			my @cities = sort keys %{$cities{$state}};

			print
				start_div({-class=>'state',-id=>$state,-style=>'display: none;'});

			foreach my $city (@cities) {
				print
					start_div({-class=>'city-join',-id=>$city,-style=>'display: block;'}),  # not sure if this div is needed
					h4(&$ucwords($city));

				$select = "
					select
						name,
						group_id,
						description,
						default_pace,
						default_terrain,
						type
					from
						groups
					where
						city = '$city' and
						state = '$state' and
						type in ('public','restricted')
					order by
						city";
				$qh = $dbh->prepare($select);
				$qh->execute();

				print 
					start_ul();

				while (my ($name,$group_id,$description,$default_pace,$default_terrain,$type) = $qh->fetchrow_array()) {
					$description =~ s/\n/<br>/g;

					print 
						li(
							a({-href=>"$script?a=join2&g=$group_id"},$name),
							" ($type)",
							blockquote("$description [$default_pace,$default_terrain]")
						);
				}

				print 
					end_ul(),
					end_div();
			}

			print
				end_div();
		}

		&$page_end();
	}
	else {
		print $q->redirect("$script?a=login");
	}
}

elsif ($action eq 'join2') {
	if ($logged_in) {
		my $group_id = $q->param('g');
		my $user_id = $q->cookie('VeloCalUserID');

		my $select = "
			select 
				count(*)
			from
				group_user
			where
				group_id = $group_id and
				user_id = $user_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($count) = $qh->fetchrow_array();

		$select = "
			select 
				count(*)
			from
				group_queue
			where
				group_id = $group_id and
				user_id = $user_id";
		$qh = $dbh->prepare($select);
		$qh->execute();
		my ($queue_count) = $qh->fetchrow_array();
		$count += $queue_count;

		$select = "
			select
				name,
				type
			from
				groups
			where
				group_id = $group_id";
		$qh = $dbh->prepare($select);
		$qh->execute();
		my ($name,$type) = $qh->fetchrow_array();

		&$page_begin();

		print
			h3("Join '$name'");

		if ($count != 0) {
			if ($queue_count != 0) {
				print 
					p("You are awaiting approval from a group administrator for permission to join '$name'.");
			}
			else {
				print 
					p("You already belong to '$name'.");
			}
		}
		else {
			print 
				start_form({-action=>$script,-method=>'POST'});

			if ($type eq 'restricted') {
				print
					p("The group '$name' is a restricted group. Your request to join the group will be sent to the group administrators and held for approval."),
					p('Please provide a message to the group administrators identifying yourself and a reason why you would like to join the group.'),
					textarea({-rows=>5,-columns=>40,-name=>'message',-override=>1});
			}
			elsif ($type eq 'public') {
				print 
					p("The group '$name' is a public group. This means that you will become a member immediately after the following confirmation. No intervention by group admisistrators is required.");
			}

			print
				hidden({-name=>'g',-value=>$group_id,-override=>1}),
				hidden({-name=>'a',-value=>'join_confirm',-override=>1});

			if ($type eq 'restricted') {
				print 
					br(),
					br(),
					submit({-value=>'Request Access'});
			}
			else {
				print 
					submit({-value=>'Join'});
			}

			print
				end_form();
		}

		&$page_end();
	}
	else {
		print $q->redirect("$script?a=login");
	}
}

elsif ($action eq 'join_confirm') {
	if ($logged_in) {
		my $group_id = $q->param('g');
		my $message = $q->param('message');
		my $user_id = $q->cookie('VeloCalUserID');

		my $select = "
			select
				name,
				type
			from
				groups
			where
				group_id = $group_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($name,$type) = $qh->fetchrow_array();

		if (($type eq 'public') || ($type eq 'restricted')) {
			if ($type eq 'public') {
				my $insert = "
					insert into group_user (
						group_id,
						user_id
					) values (
						$group_id,
						$user_id
					)";
				$qh = $dbh->prepare($insert);
				$qh->execute();

				# add all future events to the user's calendar
				my $select = "select event_id from events where group_id = $group_id and start_time >= now()";
				$qh = $dbh->prepare($select);
				$qh->execute();

				while (my ($event_id) = $qh->fetchrow_array()) {
					$insert = "insert into event_user (event_id,user_id) values ($event_id,$user_id)";
					my $qh2 = $dbh->prepare($insert);
					$qh2->execute();
				}

				&$page_begin();

				print
					h3("Join '$name' Successful"),
					p("You have been successfully added to '$name'. Click on 'Ride Calendar' to see events for this group in your calendar.");

				# send email to admins who want to receive mail

				$select = "
					select
						u.name_first,
						u.name_last,
						u.email
					from
						users u,
						group_admin g
					where
						u.user_id = g.user_id and
						g.group_id = $group_id and
						subscription_email = 'Y'";
				$qh = $dbh->prepare($select);
				$qh->execute();

				my @admins;
				while (my ($name_first,$name_last,$email) = $qh->fetchrow_array()) {
					push @admins, "$name_first $name_last <$email>";
				}
				my $admins = join ',', @admins;

				$select = "select name_first,name_last,email,hide_email from users where user_id = $user_id";
				$qh = $dbh->prepare($select);
				$qh->execute();
				my ($name_first,$name_last,$email,$hide_email) = $qh->fetchrow_array();

				($hide_email eq 'Y') ? ($email = '') : ($email = "&lt;$email&gt;");

				open(MAIL,"| $sendmail -t");
				print MAIL "To: $admins\n";
				print MAIL "From: $registration_name <$registration_email>\n";
				print MAIL "Subject: VeloCal Roster Change for $name\n";
				print MAIL "Content-type: text/html\n\n";
				print MAIL "$name_first $name_last $email has joined the group '$name'\n";
				close(MAIL);

				&$page_end();
			}
			elsif ($type eq 'restricted') {
				my $insert = "
					insert into group_queue (
						group_id,
						user_id
					) values (
						$group_id,
						$user_id
					)";
				$qh = $dbh->prepare($insert);
				$qh->execute();

				my $select = "
					select
						u.name_first,
						u.name_last,
						u.email
					from
						users u,
						group_admin g
					where
						u.user_id = g.user_id and
						g.group_id = $group_id";
				$qh = $dbh->prepare($select);
				$qh->execute();

				my @admins;
				while (my ($name_first, $name_last, $email) = $qh->fetchrow_array()) {
					push @admins, "$name_first $name_last <$email>";
				}
				my $admins = join ',', @admins;

				$select = "select name_first,name_last,email,hide_email from users where user_id = $user_id";
				$qh = $dbh->prepare($select);
				$qh->execute();
				my ($name_first,$name_last,$email,$hide_email) = $qh->fetchrow_array();

				($hide_email eq 'Y') ? ($email = '') : ($email = "&lt;$email&gt;");

				open(MAIL,"| $sendmail -t");
				print MAIL "To: $admins\n";
				print MAIL "From: $registration_name <$registration_email>\n";
				print MAIL "Subject: $subscription_request_subject for $name\n";
				print MAIL "Content-type: text/html\n\n";
				print MAIL "A subscription request has been received from $name_first $name_last $email for '$name': ";
				print MAIL '<br />';
				print MAIL "<blockquote>$message</blockquote>";
				print MAIL '<br />';
				print MAIL "To approve this request, click ", a({-href=>"$script?a=restricted_approval&m=approve&g=$group_id&u=$user_id"},'here');
				print MAIL '<br />';
				print MAIL "To deny this request, click ", a({-href=>"$script?a=restricted_approval&m=deny&g=$group_id&u=$user_id"},'here');
				print MAIL '<br />';
				print MAIL '<br />';
				print MAIL "Optionally, you can manage all users waiting for approval at the following URL: ";
				print MAIL "<br />\n";
				print MAIL a({-href=>"$script?a=join_queue&g=$group_id"},"$script?a=join_queue&g=$group_id");
				close(MAIL);

				&$page_begin();

				print 
					h3("Request Pending"),
					p("You have been added to the approval queue for '$name'. You will receive an email when a group admistrator has approved or denied your request.");

				&$page_end();
			}
		}
		else {
			&$page_begin();
			print 'ERROR: Invalid request';
			&$page_end();
		}
	}
	else {
		print $q->redirect("$script?a=login");
	}
}

elsif ($action eq 'event') {
	if ($logged_in) {
		my $user_id = $q->cookie('VeloCalUserID');
		my $event_id = $q->param('e');

		my $select = "select group_id from events where event_id = $event_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($group_id) = $qh->fetchrow_array();

		$select = "select type from groups where group_id = $group_id";
		$qh = $dbh->prepare($select);
		$qh->execute();
		my ($type) = $qh->fetchrow_array();

		my $authorized = 1;

		if ($type eq 'private') {
			$select = "select count(*) from group_user where group_id = $group_id and user_id = $user_id";
			$qh = $dbh->prepare($select);
			$qh->execute();
			my ($count) = $qh->fetchrow_array();

			$authorized = 0 unless (defined $count);
		}

		if ($authorized) {
			my $select = "
				select
					g.name,
					e.group_id,
					e.title,
					e.start_time,
					e.location,
					e.map_id,
					e.pace,
					e.terrain,
					e.distance,
					e.notes,
					e.user_id
				from
					events e,
					groups g
				where
					g.group_id = e.group_id and 
					e.event_id = $event_id";
			my $qh = $dbh->prepare($select);
			$qh->execute();

			my ($group_name,$group_id,$title,$start_time,$location,$map_id,$pace,$terrain,$distance,$notes,$event_creator) = $qh->fetchrow_array();

			my ($date,$time) = split / /, $start_time;
			my ($year,$month,$day) = split /-/, $date;
			my ($hour,$minute) = split /:/, $time;

			my $dow = Day_of_Week_to_Text(Day_of_Week($year,$month,$day));

			$select = "select name_last,name_first,email from users where user_id = $event_creator";
			$qh = $dbh->prepare($select);
			$qh->execute();
			my ($creator_name_last,$creator_name_first,$creator_email) = $qh->fetchrow_array();
			my $creator = "$creator_name_first $creator_name_last (" . a({-href=>"mailto:$creator_email"},$creator_email) . ")" if (defined $creator_email);

			$notes =~ s/\n/<br>/g;

			# get map name
			$map_id += 0;
			$select = "select name,url,image_filename,image_magick from maps where id = $map_id";
			$qh = $dbh->prepare($select);
			$qh->execute();
			my ($map_name,$url,$image_filename,$image_magick) = $qh->fetchrow_array();

			$map_name = a({-href=>"$script?a=get_image&t=maps&c=image&l=id&r=$map_id&f=image_filename&m=image_magick"},$map_name) if ($image_filename ne '');
			$map_name = a({-href=>$url},$map_name) if ($url ne '');
			$map_name = '&nbsp;' if ($map_name eq '');

			&$page_begin('VeloCal',"autoTextArea(document.attendance['comments'],45);");

			print 
				h3("Event: $title"),
				h4('Event Detail'),
				blockquote(
					table(
						{-class=>'brown'},
						Tr(
							td('Group'),
							td($group_name)
						),
						Tr(
							td({-nowrap=>'nowrap'},'Event Creator'),
							td($creator)
						),
						Tr(
							td('Title'),
							td($title),
						),
						Tr(
							td({-nowrap=>'nowrap'},'Start Time'),
							td("$month/$day/$year $hour:$minute ($dow)")
						),
						Tr(
							td({-nowrap=>'nowrap'},'Start Location'),
							td($location)
						),
						Tr(
							td({-nowrap=>'nowrap'},'Map'),
							td($map_name)
						),
						Tr(
							td('Pace'),
							td($pace)
						),
						Tr(
							td('Terrain'),
							td($terrain)
						),
						Tr(
							td('Distance'),
							td($distance)
						),
						Tr(
							td('Notes'),
							td($notes)
						)
					),
					br(),	
					start_form({-action=>$script,-method=>'POST',-style=>'display: inline;'}),
					hidden({-name=>'event_id',-value=>$event_id,-override=>1}),
					hidden({-name=>'start_hour',-value=>$hour,-override=>1}),
					hidden({-name=>'start_minutes',-value=>$minute,-override=>1}),
					hidden({-name=>'d',-value=>$day,-override=>1}),
					hidden({-name=>'m',-value=>$month,-override=>1}),
					hidden({-name=>'y',-value=>$year,-override=>1}),
					hidden({-name=>'group_id',-value=>$group_id,-override=>1}),
					hidden({-name=>'title',-value=>$title,-override=>1}),
					hidden({-name=>'location',-value=>$location,-override=>1}),
					hidden({-name=>'map_id',-value=>$map_id,-override=>1}),
					hidden({-name=>'pace',-value=>$pace,-override=>1}),
					hidden({-name=>'terrain',-value=>$terrain,-override=>1}),
					hidden({-name=>'distance',-value=>$distance,-override=>1}),
					hidden({-name=>'notes',-value=>$notes,-override=>1}),
					hidden({-name=>'a',-value=>'add',-override=>1}),
					hidden({-name=>'method',-value=>'edit',-override=>1}),
					submit({-value=>'Edit',-override=>1}),
					end_form(),
					start_form({-action=>$script,-method=>'GET',-style=>'display: inline;'}),
					hidden({-name=>'e',-value=>$event_id,-override=>1}),
					hidden({-name=>'a',-value=>'delete_event',-override=>1}),
					submit({-value=>'Delete',-override=>1}),
					end_form()
				);

			$select = "
				select
					name_last,
					name_first,
					u.user_id,
					u.photo_filename
				from
					group_user natural join
					users u
				where
					group_id = $group_id
				order by
					name_first,
					name_last";
			$qh = $dbh->prepare($select);
			$qh->execute();

			my @options = qw/yes no maybe/; 
			my %labels = (
				yes => 'Yes',
				no => 'No',
				maybe => 'Maybe'
			);

			my $select3 = "select status,comments from event_user where user_id = $user_id and event_id = $event_id";
			my $qh3 = $dbh->prepare($select3);
			$qh3->execute();
			my ($att_default,$comments) = $qh3->fetchrow_array();
			$att_default = 'none' if ($att_default eq '');

			my $comments_columns = 45;
			my $comments_rows = int((length $comments) / 45) + 1;

			print
				h4('Attendance'),
				blockquote(
					start_form({-action=>$script,-method=>'POST',-name=>'attendance'}),
					table(
						{-class=>'brown',-width=>'100%'},
						Tr(
							td(
								{-nowrap=>'nowrap'},
								'I will be attending: '
							),
							td(
								{-width=>'100%'},
								radio_group({-name=>'attend',-values=>\@options,-labels=>\%labels,-default=>$att_default,-override=>1}),
								hidden({-name=>'e',-value=>$event_id,-override=>1}),
								hidden({-name=>'u',-value=>$user_id,-override=>1}),
								hidden({-name=>'a',-value=>'att',-override=>1})
							)
						),
						Tr(
							td(
								{-nowrap=>'nowrap'},
								'Comments'
							),
							td(
								textarea(
									{
										-name=>'comments',
										-value=>$comments,
										-cols=>$comments_columns,
										-rows=>$comments_rows,
										-style=>'overflow: visible;',
										-onKeyUp=>"autoTextArea(this, $comments_columns);",
										-onKeyPress=>"autoTextArea(this, $comments_columns);",
										-onInput=>"autoTextArea(this, $comments_columns);",
										-onPaste=>"autoTextArea(this, $comments_columns);",
										-override=>1
									}
								)
							)
						)
					),
					br(),
					submit({-value=>'Update',-override=>1}),
					end_form()
				);

			print
				h4('Riders'),
				start_blockquote();

			print
				start_table({-class=>'brown',-width=>'100%'}),
				Tr(
					th({-width=>'10%',-colspan=>2},'Rider'),
					th({-width=>'10%'},'Yes'),
					th({-width=>'10%'},'No'),
					th({-width=>'10%'},'Maybe'),
					th({-width=>'10%'},'Unknown'),
					th({-width=>'50%'},'Comments')
				);

			my %count;
			$count{yes} = 0;
			$count{no} = 0;
			$count{maybe} = 0;
			$count{unknown} = 0;

			while (my ($name_last,$name_first,$user_id,$photo) = $qh->fetchrow_array()) {
				my $select2 = "select status,comments from event_user where user_id = $user_id and event_id = $event_id";
				my $qh2 = $dbh->prepare($select2);
				$qh2->execute();
				my ($status,$comments) = $qh2->fetchrow_array();

				$photo = img({-src=>'images/camera.png',-alt=>'Photo',-border=>0}) if ($photo ne '');
				my $checkmark = img({-src=>'images/check.gif',-alt=>'X'});

				my %status;
				$status{yes} = $checkmark if ($status eq 'yes');
				$status{maybe} = $checkmark if ($status eq 'maybe');
				$status{no} = $checkmark if ($status eq 'no');
				$status{unknown} = $checkmark if ($status eq '');

				$count{yes} += 1 if ($status eq 'yes');
				$count{maybe} += 1 if ($status eq 'maybe');
				$count{no} += 1 if ($status eq 'no');
				$count{unknown} += 1 if ($status eq '');

				print
					Tr(
						td($photo),
						td({-nowrap=>'nowrap'},a({-href=>"$script?a=user_profile&u=$user_id"},"$name_first $name_last")),
						td({-align=>'center'},$status{yes}),
						td({-align=>'center'},$status{no}),
						td({-align=>'center'},$status{maybe}),
						td({-align=>'center'},$status{unknown}),
						td($comments)
					);
			}

			print
				Tr(
					th({-colspan=>2},'Total'),
					th({-align=>'center'},$count{yes}),
					th({-align=>'center'},$count{no}),
					th({-align=>'center'},$count{maybe}),
					th({-align=>'center'},$count{unknown}),
					th('&nbsp;')
				);

			print
				end_table(),
				end_blockquote();

			&$page_end();
		}
		else {
			&$page_begin();
			print "Unauthorized access";
			&$page_end();
		}
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

elsif ($action eq 'group') {
	if ($logged_in) {
		my $group_id = $q->param('g');
		my $user_id = $q->cookie('VeloCalUserID');

		my $select = "select type from groups where group_id = $group_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($type) = $qh->fetchrow_array();

		my $authorized = 1;

		if ($type eq 'private') {
			$select = "select count(*) from group_user where group_id = $group_id and user_id = $user_id";
			$qh = $dbh->prepare($select);
			$qh->execute();
			my ($count) = $qh->fetchrow_array();

			$authorized = 0 unless (defined $count);
		}

		if ($authorized) {
			my $select = "
				select
					name,
					city,
					state,
					description,
					type,
					default_pace,
					default_terrain,
					default_start_location,
					default_start_time,
					homepage
				from
					groups
				where
					group_id = $group_id";
			my $qh = $dbh->prepare($select);
			$qh->execute();
			my ($name,$city,$state,$description,$type,$default_pace,$default_terrain,$default_start_location,$default_start_time,$homepage) = $qh->fetchrow_array();

			$city = &$ucwords($city);
			my ($hours,$minutes) = split /:/, $default_start_time;
			$default_start_time = "$hours:$minutes";

			($homepage eq '') ? ($homepage = '&nbsp;') : ($homepage = a({-href=>$homepage},$homepage));

			$description =~ s/\n/<br>/g;

			&$page_begin();

			print
				h3("Group Information for '$name'"),
				h4('Group Profile'),
				blockquote(
					table(
						{-class=>'brown'},
						Tr(
							td('Name'),
							td($name)
						),
						Tr(
							td('Homepage'),
							td($homepage)
						),
						Tr(
							td('Location'),
							td("$city, $state")
						),
						Tr(
							td('Description'),
							td($description)
						),
						Tr(
							td('Group Type'),
							td(ucfirst($type))
						),
						Tr(
							td('Default Pace'),
							td($default_pace)
						),
						Tr(
							td('Default Terrain'),
							td($default_terrain)
						),
						Tr(
							td('Default Start Location'),
							td($default_start_location)
						),
						Tr(
							td('Default Start Time'),
							td($default_start_time)
						)
					)
				);

			### Group Maps
			print 
				h4('Group Maps'),
				start_blockquote(),
				start_table({-class=>'brown'}),
				Tr(
					th({-colspan=>2},'Map Name'),
					th('Description'),
					th('Last Updated'),
					th('&nbsp;')
				);

			$select = "
				select
					id,
					user_id,
					group_id,
					name,
					description,
					url,
					image_filename,
					last_updated
				from
					maps
				where
					group_id = $group_id
				order by
					name";
			$qh = $dbh->prepare($select);
			$qh->execute();

			my $map_count;

			while (my ($id,$map_user_id,$map_group_id,$name,$description,$url,$image_filename,$last_updated) = $qh->fetchrow_array()) {
				$map_count++;

				my $map_is_local = 
					a(
						{-href=>"$script?a=get_image&t=maps&c=image&l=id&r=$id&f=image_filename&m=image_magick"},
						$name
					);
				if ($url ne '') { 
					$map_is_local = a({-href=>$url},$name);
				}

				my $map_image = '&nbsp;';
				$map_image = img({-src=>'images/link.png'}) if ($url ne '');

				if ($last_updated =~ /^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/) {
					my ($now_year,$now_month,$now_day,$now_hour,$now_min,$now_sec) = 
						split ':', &$convert_to_localtime("$1:$2:$3:$4:$5:$6");
					$last_updated = "$now_hour:$now_min:$now_sec $now_year-$now_month-$now_day";
				}

				my $edit_link = '&nbsp;';

				# if user owns map or is an admin, allow user to edit the map
				my $select = "select user_id from group_admin where group_id = $map_group_id and user_id = $user_id";
				my $qh = $dbh->prepare($select);
				$qh->execute();
				my ($admin) = $qh->fetchrow_array();

				if (($user_id == $map_user_id) || ($admin ne '')) {
					$edit_link = 
						a(
							{-href=>"$script?a=map_edit&id=$id&g=$group_id"},
							img({-src=>'images/edit.png',-alt=>'edit',-border=>0})
						);
				}

				print
					Tr(
						td(
							$map_image
						),
						td(
							$map_is_local
						),
						td(
							$description
						),
						td(
							{-nowrap=>'nowrap'},
							$last_updated
						),
						td(
							$edit_link
						)
					);
			}

			if ($map_count == 0) {
				print
					Tr(
						td(
							{-colspan=>5},
							'No maps available for this group'
						)
					);
			}

			print
				end_table(),
				ul(
					{-class=>'action_list'},
					li(
						a({-href=>"$script?a=map_edit&new=1&g=$group_id"},'Add a map')
					)
				),
				end_blockquote();

			$select = "
				select
					u.name_first,
					u.name_last,
					u.user_id,
					u.email,
					u.pref_pace,
					u.pref_terrain,
					u.photo_filename,
					u.hide_email
				from
					users u,
					group_user g
				where
					u.user_id = g.user_id and 
					g.group_id = $group_id
				order by
					u.name_first,
					u.name_last";
			$qh = $dbh->prepare($select);
			$qh->execute();

			### Group Members
			print 
				h4('Group Members'),
				start_blockquote(),
				start_table({-class=>'brown'}),
				Tr(
					th({-colspan=>2},'Name'),
					th('Email')
				);

			my %GROUP_PREFS;
			my $group_total_members;

			while (my ($name_first,$name_last,$user_id,$email,$pref_pace,$pref_terrain,$photo,$hide_email) = $qh->fetchrow_array()) {
				$group_total_members++;

				my $name = "$name_first $name_last";
				$name =~ s/^\s+//g;
				$name =~ s/\s+$//g;

				$photo = img({-src=>'images/camera.png',-alt=>'Photo',-border=>0}) if ($photo ne '');

				my $email_display = a({-href=>"mailto:$email"},$email);
				$email_display = div({-class=>'hidden_email'},"[ hidden ]") if ($hide_email eq 'Y');

				print 
					Tr(
						td($photo),
						td(a({-href=>"$script?a=user_profile&u=$user_id"},$name)),
						td($email_display)
					);

				$pref_pace = 'N/A' if ($pref_pace eq '');
				$pref_terrain = 'N/A' if ($pref_terrain eq '');

				$GROUP_PREFS{pace}{$pref_pace}{total}++;
				$GROUP_PREFS{terrain}{$pref_terrain}{total}++;
				$GROUP_PREFS{total}++;
			}

			print 
				Tr(
					th(
						{-class=>'brown',-colspan=>3},
						"$group_total_members Total Members"
					),
				),
				end_table(),
				ul(
					{-class=>'action_list'},
					li(
						a({-href=>"$script?a=group_email&g=$group_id"},'Send email to the group')
					)
				),
				end_blockquote();

			print 
				h4('Aggregate Group Preferences'),
				start_blockquote(),
				start_table({-class=>'brown'}),
				Tr(
					th('Pace'),
					th({-colspan=>2},'User Preference'),
					th('Group')
				);

			my $scale_x = 1.5;
			my $height = 10;

			foreach my $type (('pace','terrain')) {
				foreach my $x (keys %{$GROUP_PREFS{$type}}) {
					$GROUP_PREFS{$type}{$x}{average} = $GROUP_PREFS{$type}{$x}{total} / $GROUP_PREFS{total};
				}
			}

			push @pace_values, 'N/A';

			foreach my $pace (@pace_values) {
				$GROUP_PREFS{pace}{$pace}{average} += 0;
				$GROUP_PREFS{pace}{$pace}{average} = sprintf("%.1f\%",$GROUP_PREFS{pace}{$pace}{average} * 100);
				my $width = $GROUP_PREFS{pace}{$pace}{average} * $scale_x;

				my $default = '&nbsp;';
				$default = img({-src=>'images/check.gif'}) if (lc($default_pace) eq lc($pace));

				print
					Tr(
						td($pace),
						td(img({-src=>'images/pixel-orange.png',-width=>$width,-height=>$height,-border=>0})),
						td({-align=>'right'},$GROUP_PREFS{pace}{$pace}{average}),
						td({-align=>'center'},$default)
					);
			}

			print 
				end_table(),
				br(),
				start_table({-class=>'brown'}),
				Tr(
					th('Terrain'),
					th({-colspan=>2},'User Preference'),
					th('Group')
				);

			push @terrain_values, 'N/A';

			foreach my $terrain (@terrain_values) {
				$GROUP_PREFS{terrain}{$terrain}{average} += 0;
				$GROUP_PREFS{terrain}{$terrain}{average} = sprintf("%.1f\%",$GROUP_PREFS{terrain}{$terrain}{average} * 100);
				my $width = $GROUP_PREFS{terrain}{$terrain}{average} * $scale_x;
				my $default = '&nbsp;';
				$default = img({-src=>'images/check.gif'}) if (lc($default_terrain) eq lc($terrain));

				print
					Tr(
						td($terrain),
						td(img({-src=>'images/pixel-orange.png',-width=>$width,-height=>$height,-border=>0})),
						td({-align=>'right'},$GROUP_PREFS{terrain}{$terrain}{average}),
						td({-align=>'center'},$default)
					);
			}

			print 
				end_table(),
				end_blockquote(),
				br();

			&$page_end();
		}
		else {
			&$page_begin();
			print "Unauthorized access";
			&$page_end();
		}
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

elsif ($action eq 'group_prefs') {
	if ($logged_in) {
		my $group_id = $q->param('g');
		my $user_id = $q->cookie('VeloCalUserID');

		my $select = "
			select
				name
			from
				groups
			where
				group_id = $group_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($name) = $qh->fetchrow_array();

		$select = "
			select
				notification,
				reminders,
				reminder_hours
			from
				group_user
			where
				group_id = $group_id and
				user_id = $user_id";
		$qh = $dbh->prepare($select);
		$qh->execute();
		my ($notification,$reminders,$reminder_hours) = $qh->fetchrow_array();

		($notification eq 'Y') ? ($notification = 'Yes') : ($notification = 'No');
		($reminders eq 'Y') ? ($reminders = 'Yes') : ($reminders = 'No');
		($reminder_hours == 1) ? ($reminder_hours = "$reminder_hours Hour") : ($reminder_hours = "$reminder_hours Hours");

		&$page_begin();

		print
			h3("Preferences for '$name'"),
			h4('Email Preferences'),
			blockquote(
				table(
					{-class=>'brown'},
					Tr(
						th('Option'),
						th('Description'),
						th('Preference'),
					),
					Tr(
						td('Email notification'),
						td('Receive email about new rides and ride updates'),
						td($notification)
					),
					Tr(
						td('Ride reminders'),
						td('Receive email reminders about upcoming rides'),
						td($reminders)
					),
					Tr(
						td('Advance notice'),
						td('Amount of time in advance that email reminders should be sent'),
						td($reminder_hours)
					)
				),
				br(),
				start_form({-action=>$script,-method=>'GET'}),
				hidden({-name=>'a',-value=>'edit_prefs',-override=>1}),
				hidden({-name=>'g',-value=>$group_id,-override=>1}),
				submit({-value=>'Edit'}),
				end_form()
			),
			h4('Other Actions'),
			blockquote(
				ul(
					{-class=>'action_list'},
					li(
						a({-href=>"$script?a=unsubscribe&g=$group_id"},'Unsubscribe from this group')
					)
				)
			);

		&$page_end();
	}
	else {
		print $q->redirect("$script?a=login");
	}
}

elsif ($action eq 'edit_prefs') {
	if ($logged_in) {
		my $group_id = $q->param('g');
		my $user_id = $q->cookie('VeloCalUserID');

		my $select = "
			select
				name
			from
				groups
			where
				group_id = $group_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($name) = $qh->fetchrow_array();

		$select = "
			select
				notification,
				reminders,
				reminder_hours
			from
				group_user
			where
				group_id = $group_id and
				user_id = $user_id";
		$qh = $dbh->prepare($select);
		$qh->execute();
		my ($notification,$reminders,$reminder_hours) = $qh->fetchrow_array();

		my @yesno_values = qw/Y N/;
		my %yesno_labels = ( Y => 'Yes', N => 'No' );

		&$page_begin();

		print
			h3("Edit Preferences for '$name'"),
			start_form({-action=>$script,-method=>'GET'}),
			start_table({-class=>'brown'}),
			Tr(
				td('Email notification'),
				td(popup_menu({-name=>'notification',-default=>$notification,-values=>\@yesno_values,-labels=>\%yesno_labels,-override=>1}))
			),
			Tr(
				td('Ride reminders'),
				td(popup_menu({-name=>'reminders',-default=>$reminders,-values=>\@yesno_values,-labels=>\%yesno_labels,-override=>1}))
			),
			Tr(
				td('Advance Notice (Hours)'),
				td(
					hidden({-name=>'g',-value=>$group_id,-override=>1}),
					hidden({-name=>'a',-value=>'edit_prefs_write',-override=>1}),
					input({-name=>'reminder_hours',-value=>$reminder_hours,-size=>2,-maxlength=>2,-override=>1})
				)
			);

		print
			end_table(),
			br(),
			submit({-value=>'Update'}),
			end_form();

		&$page_end();
	}
	else {
		print $q->redirect("$script?a=login");
	}
}

elsif ($action eq 'edit_prefs_write') {
	if ($logged_in) {
		my $group_id = $q->param('g');
		my $notification = $q->param('notification');
		my $reminders = $q->param('reminders');
		my $reminder_hours = $q->param('reminder_hours') + 0;
		my $user_id = $q->cookie('VeloCalUserID');

		$reminder_hours = 24 if ($reminder_hours <= 0);

		my $update = "
			update group_user set
				notification = '$notification',
				reminders = '$reminders',
				reminder_hours = '$reminder_hours'
			where
				group_id = $group_id and
				user_id = $user_id";
		my $qh = $dbh->prepare($update);
		$qh->execute();

		## and send the user back to the group prefs page
		print $q->redirect("$script?a=group_prefs&g=$group_id");
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

elsif ($action eq 'unsubscribe') {
	if ($logged_in) {
		my $group_id = $q->param('g');

		my $select = "select name from groups where group_id = $group_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($name) = $qh->fetchrow_array();

		&$page_begin();

		print
			h3("Unsubscribe from '$name'"),
			p("Please confirm that you wish to unsubscribe from '$name'. All rides associated with this group will be removed from your calendar. Group administrators will be notified that you have unsubscribed. If you have accepted any rides with this group, you will be removed from the acceptance list and ride leaders will be notified that your status has changed."),
			start_form({-action=>$script,-method=>'POST'}),
			hidden({-name=>'a',-value=>'unsubscribe_confirm',-override=>1}),
			hidden({-name=>'g',-value=>$group_id,-override=>1}),
			submit({-value=>'Unsubscribe',-override=>1}),
			end_form();

		&$page_end();
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

elsif ($action eq 'unsubscribe_confirm') {
	if ($logged_in) {
		my $group_id = $q->param('g');
		my $user_id = $q->cookie('VeloCalUserID');

		# get the group name
		my $select = "select name from groups where group_id = $group_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($name) = $qh->fetchrow_array();

		# make sure the user is not the last remaining administrator
		$select = "
			select 
				count(*) 
			from 
				group_admin
			where
				group_id = $group_id and
				user_id != $user_id";
		$qh = $dbh->prepare($select);
		$qh->execute();
		my ($count) = $qh->fetchrow_array();

		if ($count == 0) {
			&$page_begin();

			print
				h3("Error Unsubscribing from '$name'"),
				p("You are the last remaining administrator for the group '$name'. This prevents you from unsubscribing. Please add another administrator before attempting to unsubscribe."),
				p("You can modify administrator privileges on the " . a({-href=>"$script?a=manage_users&g=$group_id"},'Manage Members') . " page.");

			&$page_end();
		}
		else {
			# send email to admins who want to receive mail
			$select = "
				select
					u.name_first,
					u.name_last,
					u.email
				from
					users u,
					group_admin g
				where
					u.user_id = g.user_id and
					g.group_id = $group_id and
					subscription_email = 'Y'";
			$qh = $dbh->prepare($select);
			$qh->execute();

			my @admins;
			while (my ($name_first, $name_last, $email) = $qh->fetchrow_array()) {
				push @admins, "$name_first $name_last <$email>";
			}
			my $admins = join ',', @admins;

			$select = "select name_first,name_last,email,hide_email from users where user_id = $user_id";
			$qh = $dbh->prepare($select);
			$qh->execute();
			my ($name_first,$name_last,$email,$hide_email) = $qh->fetchrow_array();

			($hide_email eq 'Y') ? ($email = '') : ($email = "&lt;$email&gt;");

			open(MAIL,"| $sendmail -t");
			print MAIL "To: $admins\n";
			print MAIL "From: $registration_name <$registration_email>\n";
			print MAIL "Subject: $name :: Roster Change\n";
			print MAIL "Content-type: text/html\n\n";
			print MAIL "$name_first $name_last $email has left the group '$name'";
			close(MAIL);

			# delete user from group_user table
			my $delete = "delete from group_user where group_id = $group_id and user_id = $user_id";
			my $qh = $dbh->prepare($delete);
			$qh->execute();

			# delete user from event_user table
			$delete = "delete from event_user where group_id = $group_id and user_id = $user_id";
			$qh = $dbh->prepare($delete);
			$qh->execute();

			print $q->redirect($script);
		}
	}
	else {
		&$page_begin();
		print "Error: unathorized access";
		&$page_end();
	}
}

elsif ($action eq 'restricted_approval') {
	if ($logged_in) {
		my $group_id = $q->param('g');
		my $user_id_action= $q->param('u');
		my $method = $q->param('m');
		my $user_id = $q->cookie('VeloCalUserID');

		my $title_method = "Approval";
		$title_method = "Denial" if ($method eq 'deny');
		my $method_text = lc($title_method);

		# check that the logged in user is a valid administrator for the group
		my $select = "
			select
				count(*)
			from
				group_admin
			where
				group_id = $group_id and
				user_id = $user_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($count) = $qh->fetchrow_array();

		if ($count != 0) {
			&$page_begin();

			print
				h3("Restricted Group $title_method"),
				start_form({-action=>$script,-method=>'POST'}),
				p("Enter an optional message to be included in the email sent to the user indicating $method_text."),
				textarea({-name=>'message',-rows=>4,-columns=>40,-override=>1}),
				hidden({-name=>'a',-value=>'restricted_approval2',-override=>1}),
				hidden({-name=>'g',-value=>$group_id,-override=>1}),
				hidden({-name=>'u',-value=>$user_id_action,-override=>1}),
				hidden({-name=>'m',-value=>$method,-override=>1}),
				br(),
				br(),
				submit({-value=>"Send $title_method"}),
				end_form();

			&$page_end();
		}
		else {
			&$page_begin();
			print 'unauthorized access';
			&$page_end();
		}
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

elsif ($action eq 'restricted_approval2') {
	if ($logged_in) {
		my $group_id = $q->param('g');
		my $user_id_action = $q->param('u');
		my $method = $q->param('m');
		my $message = $q->param('message');
		my $user_id = $q->cookie('VeloCalUserID');

		# check that the logged in user is a valid
		# administrator for the group
		my $select = "
			select
				count(*)
			from
				group_admin
			where
				group_id = $group_id and
				user_id = $user_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($count) = $qh->fetchrow_array();

		if ($count != 0) {
			# check to see if user is still in the queue
			my $select = "select count(*) from group_queue where group_id = $group_id and user_id = $user_id_action";
			my $qh = $dbh->prepare($select);
			$qh->execute();
			my ($count) = $qh->fetchrow_array();

			if ($count != 0) {
				if ($method eq 'approve') {
					my $insert = "insert into group_user (group_id,user_id) values ($group_id,$user_id_action)";
					$qh = $dbh->prepare($insert);
					$qh->execute();

					# add all future events to the user's calendar
					$select = "select event_id from events where group_id = $group_id and start_time >= now()";
					$qh = $dbh->prepare($select);
					$qh->execute();

					while (my ($event_id) = $qh->fetchrow_array()) {
						$insert = "insert into event_user (event_id,user_id) values ($event_id,$user_id_action)";
						my $qh2 = $dbh->prepare($insert);
						$qh2->execute();
					}
				}

				# remove user from the approval queue
				my $delete = "delete from group_queue where group_id = $group_id and user_id = $user_id_action";
				$qh = $dbh->prepare($delete);
				$qh->execute();

				my $select = "
					select
						u.name_first,
						u.name_last,
						u.email
					from
						users u,
						group_admin g
					where
						u.email = g.email and
						g.group_id = $group_id";
				$qh = $dbh->prepare($select);
				$qh->execute();

				my @admins;
				while (my ($name_first,$name_last,$email) = $qh->fetchrow_array()) {
					my $fullname = "$name_first $name_last";
					$fullname =~ s/(\s+)$//g;
					push @admins, "$fullname <$email>";
				}
				my $admins = join ',', @admins;

				$select = "select name_first,name_last,email,hide_email from users where user_id = $user_id_action";
				$qh = $dbh->prepare($select);
				$qh->execute();
				my ($name_first,$name_last,$email,$hide_email) = $qh->fetchrow_array();

# TODO: add group name to the contents of the email so the user knows what group approved them
				open(MAIL,"| $sendmail -t");
				print MAIL "To: $email\n";
				print MAIL "Bcc: $admins\n";
				print MAIL "From: $registration_name <$registration_email>\n";
				print MAIL "Subject: Registration Request Processed\n";
				print MAIL "Content-type: text/html\n\n";
				print MAIL "The subscription request for $name_first $name_last $email has been processed.";
				print MAIL '<br />';
				print MAIL "The request status was: $method";
				print MAIL '<br />';
				print MAIL "<blockquote>$message</blockquote>";
				close(MAIL);

				&$page_begin();
				
				print 
					h3('Processed'),
					p("The response has been processed and email has been sent.");

				&$page_end();
			}
			else {
				&$page_begin();

				print 
					h3('Nothing to Process'),
					p("The user has already been processed (perhaps by another group administrator).");

				&$page_end();
			}
		}
		else {
			&$page_begin();
			print 'Unauthorized access';
			&$page_end();
		}
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

elsif ($action eq 'invite_users') {
	if ($logged_in) {
		my $group_id = $q->param('g');
		my $user_id = $q->cookie('VeloCalUserID');

		# check that the logged in user is a valid administrator for the group
		my $select = "
			select
				count(*)
			from
				group_admin
			where
				group_id = $group_id and
				user_id = $user_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($count) = $qh->fetchrow_array();
		$count += 0;

		if ($count != 0) {
			$select = "
				select
					name,
					type
				from
					groups
				where
					group_id = $group_id";
			$qh = $dbh->prepare($select);
			$qh->execute();
			my ($name,$type) = $qh->fetchrow_array();

			&$page_begin();

			if ($type eq 'private') {
				print
					h3("Invite Users to '$name'"),
					start_form({-action=>$script,-method=>'POST'}),
					p('Since this is a private group, membership can only be obtained via invitations from group administrators. To send invitations, enter one or more email addresses below. Each address should be on a separate line. Individual invitations will be sent to each address. The emails will contain links allowing the users to join this restricted group.'),
					textarea({-name=>'emails',-rows=>5,-columns=>60,-override=>1}),
					p('Optionally, enter a message to be included in the email.'),
					textarea({-name=>'message',-rows=>5,-columns=>60,-override=>1}),
					hidden({-name=>'a',-value=>'send_invites',-override=>1}),
					hidden({-name=>'g',-value=>$group_id,-override=>1}),
					br(),
					br(),
					submit({-value=>'Send'}),
					end_form();
			}
			else {
				print 
					div(
						{-class=>'error'},
						"ERROR: Invitations can only be sent for 'private' groups."
					);
			}

			&$page_end();
		}
		else {
			&$page_begin();
			print 'Unauthorized access';
			&$page_end();
		}
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

elsif ($action eq 'send_invites') {
	if ($logged_in) {
		my $group_id = $q->param('g');
		my $user_id = $q->cookie('VeloCalUserID');

		my $select = "select name_last, name_first, email from users where user_id = $user_id"; 
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($name_last,$name_first,$user_email) = $qh->fetchrow_array();
		my $fullname = "$name_first $name_last";
		$fullname =~ s/(\s+)$//; # last name is optional, so remove extra spaces

		# check that the logged in user is a valid administrator for the group
		$select = "
			select
				count(*)
			from
				group_admin
			where
				group_id = $group_id and
				user_id = $user_id";
		$qh = $dbh->prepare($select);
		$qh->execute();
		my ($count) = $qh->fetchrow_array();
		$count += 0;

		$select = "select name from groups where group_id = $group_id";
		$qh = $dbh->prepare($select);
		$qh->execute();
		my ($name) = $qh->fetchrow_array();

		if ($count != 0) {
			my $emails = $q->param('emails');
			my $message = $q->param('message');

			my @emails = split /\n/, $emails;

			foreach my $email (@emails) {
				chomp($email);
				$email =~ s/^\s//;
				$email =~ s/\s$//;

				if (&$check_email_address($email)) {
					my $challenge = &$get_challenge();

					my $insert = "
						insert into group_queue (
							group_id,
							email,
							challenge
						) values (
							$group_id,
							'$email',
							'$challenge'
						)";
					my $qh = $dbh->prepare($insert);
					$qh->execute();

					my $select = "
						select
							name_first,
							name_last
						from
							users
						where
							email = '$email'";
					$qh = $dbh->prepare($select);
					$qh->execute();
					my ($name_first,$name_last) = $qh->fetchrow_array();
					my $to_name = "$name_first $name_last";
					$to_name =~ s/(\s+)$//;

					my $already_registered = 0;
					$already_registered = 1 if (defined $name_first);

					open(MAIL,"| $sendmail -t");
					print MAIL "To: $to_name <$email>\n";
					print MAIL "From: $registration_name <$registration_email>\n";
					print MAIL "Reply-To: $fullname <$user_email>\n";
					print MAIL "Subject: VeloCal Invitation :: $name\n";
					print MAIL "Content-type: text/html\n\n";
					print MAIL "You have been invited to join the group '$name'.";
					print MAIL "<br />\n<br />\n";

					if ($message ne '') {
						print MAIL "The person sending you this invitation has included the following message: \n";
						print MAIL "<blockquote>$message</blockquote> \n";
					}

					if ($already_registered) {
						print MAIL "You are already a registered user, so simply use the following ";
						print MAIL "URL to complete the process of joining this group: ";
						print MAIL "<br />\n<br />\n";
						print MAIL a({-href=>"$script?a=join_private&g=$group_id&c=$challenge"},"$script?a=join_private&g=$group_id&c=$challenge");
					}
					else {
						print MAIL "This invitation was sent to an email address that is not registered. \n";
						print MAIL "If you are already registered with a different email address, simply \n";
						print MAIL "reply to this message, and ask the person who invited you to re-send an \n";
						print MAIL "invitation to your registered email address. \n";
						print MAIL "<br />\n<br />\n";
						print MAIL "If you would like to register and join this group, then first register ";
						print MAIL "at the following URL: ";
						print MAIL "<br />\n<br />\n";
						print MAIL a({-href=>"$script?a=register&e=$email"},"$script?a=register&e=$email");
						print MAIL "<br />\n<br />\n";
						print MAIL "After completing the registration process, you can join the group using \n";
						print MAIL "the following URL: \n";
						print MAIL "<br />\n<br />\n";
						print MAIL a({-href=>"$script?a=join_private&g=$group_id&c=$challenge"},"$script?a=join_private&g=$group_id&c=$challenge");
					}

					close(MAIL);
				}
			}

			&$page_begin();

			print
				h3('Invitations Sent'),
				p('Your invitations have been sent.');

			&$page_end();
		}
		else {
			&$page_begin();
			print 'Unauthorized access';
			&$page_end();
		}
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

elsif ($action eq 'join_private') {
	if ($logged_in) {
		my $group_id = $q->param('g');
		my $challenge = $q->param('c');
		my $user_id = $q->cookie('VeloCalUserID');

		# get the user's email address and name
		my $select = "
			select 
				email,
				name_first,
				name_last
			from
				users
			where
				user_id = $user_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($email,$name_first,$name_last) = $qh->fetchrow_array();

		# make sure the invitation is valid
		$select = "
			select
				count(*)
			from
				group_queue
			where
				group_id = $group_id and
				email = '$email' and
				challenge = '$challenge'";
		$qh = $dbh->prepare($select);
		$qh->execute();
		my ($count) = $qh->fetchrow_array();

		if ($count == 0) {
			&$page_begin();

			print 
				h3('Challenge Failed'),
				p('The URL does not contain the correct credentials to join the requested private group. Please verify that you are using the correct URL and try again.');

			&$page_end();
		}
		else {
			# delete from group_queue
			my $delete = "delete from group_queue where group_id = $group_id and user_id = $user_id";
			$qh = $dbh->prepare($delete);
			$qh->execute();

			# get the group name
			$select = "select name from groups where group_id = $group_id";
			$qh = $dbh->prepare($select);
			$qh->execute();
			my ($name) = $qh->fetchrow_array();

			# add the user to the group_user table
			my $insert = "insert into group_user (group_id,user_id) values ($group_id,$user_id)";
			$qh = $dbh->prepare($insert);
			$qh->execute();

			# add user to the event_user table, adding only future events
			$select = "select event_id from events where group_id = $group_id and start_time >= now()";
			$qh = $dbh->prepare($select);
			$qh->execute();

			while (my ($event_id) = $qh->fetchrow_array()) {
				$insert = "insert into event_user (event_id,user_id) values ($event_id,$user_id)";
				my $qh2 = $dbh->prepare($insert);
				$qh2->execute();
			}

			# email admins about new member
			$select = "
				select
					u.name_first,
					u.name_last,
					u.email
				from
					users u,
					group_admin g
				where
					u.user_id = g.user_id and
					g.group_id = $group_id and
					subscription_email = 'Y'";
			$qh = $dbh->prepare($select);
			$qh->execute();

			my @admins;
			while (my ($name_first,$name_last,$email) = $qh->fetchrow_array()) {
				my $fullname = "$name_first $name_last";
				$fullname =~ s/(\s+)$//g;
				push @admins, "$fullname <$email>";
			}
			my $admins = join ',', @admins;

			open(MAIL,"| $sendmail -t");
			print MAIL "To: $admins\n";
			print MAIL "From: $registration_name <$registration_email>\n";
			print MAIL "Subject: VeloCal Roster Change for $name\n";
			print MAIL "Content-type: text/html\n\n";
			print MAIL "$name_first $name_last $email has joined the group '$name' ";
			close(MAIL);

			# print success message
			&$page_begin();

			print 
				h3('Success'),
				p("Welcome to the group '$name'");

			&$page_end();
		}
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}
elsif ($action eq 'group_admin') {
	if ($logged_in) {
		my $group_id = $q->param('g');
		my $user_id = $q->cookie('VeloCalUserID');

		# check that the logged in user is a valid administrator for the group
		my $select = "
			select
				count(*)
			from
				group_admin
			where
				group_id = $group_id and
				$user_id = $user_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($count) = $qh->fetchrow_array();
		$count += 0;

		if ($count != 0) {
			my $select = "
				select
					subscription_email
				from
					group_admin
				where
					group_id = $group_id and
					$user_id = $user_id";
			my $qh = $dbh->prepare($select);
			$qh->execute();
			my ($subscription_email) = $qh->fetchrow_array();

			$select = "
				select
					name,
					city,
					state,
					description,
					type,
					default_pace,
					default_terrain,
					default_start_location,
					default_start_time,
					homepage
				from
					groups
				where
					group_id = $group_id";
			$qh = $dbh->prepare($select);
			$qh->execute();
			my ($name,$city,$state,$description,$type,$default_pace,$default_terrain,$default_start_location,$default_start_time,$homepage) = $qh->fetchrow_array();

			$city = &$ucwords($city);
			my ($hours,$minutes) = split /:/, $default_start_time;
			$default_start_time = "$hours:$minutes";

			($homepage eq '') ? ($homepage = '&nbsp;') : ($homepage = a({-href=>$homepage},$homepage));

			$description =~ s/\n/<br>/g;

			&$page_begin();

			print
				h3("Manage '$name'"),
				h4('Your Admin Preferences'),
				blockquote(
					table(
						{-class=>'brown'},
						Tr(
							td('Email notification when members join or leave the group'),
							td($subscription_email)
						)
					),
					br(),
					start_form({-action=>$script,-method=>'get',-style=>'display: inline;'}),
					hidden({-name=>'a',-value=>'group_admin_edit',-override=>1}),
					hidden({-name=>'g',-value=>$group_id,-override=>1}),
					submit({-value=>'Edit',-override=>1}),
					end_form()
				),
				h4('Group Profile'),
				blockquote(
					table(
						{-class=>'brown'},
						Tr(
							td('Name'),
							td($name)
						),
						Tr(
							td('Homepage'),
							td($homepage)
						),
						Tr(
							td('Location'),
							td("$city, $state")
						),
						Tr(
							td('Description'),
							td($description)
						),
						Tr(
							td('Group Type'),
							td(ucfirst($type))
						),
						Tr(
							td('Default Pace'),
							td($default_pace)
						),
						Tr(
							td('Default Terrain'),
							td($default_terrain)
						),
						Tr(
							td('Default Start Location'),
							td($default_start_location)
						),
						Tr(
							td('Default Start Time'),
							td($default_start_time)
						)
					),
					br(),
					start_form({-action=>$script,-method=>'get',-style=>'display: inline;'}),
					hidden({-name=>'a',-value=>'group_edit',-override=>1}),
					hidden({-name=>'g',-value=>$group_id,-override=>1}),
					hidden({-name=>'edit',-value=>'Y',-override=>1}),
					submit({-value=>'Edit',-override=>1}),
					end_form()
				),
				h4('Other Actions'),
				start_blockquote(),
				start_ul({-class=>'action_list'}),
				li(a({-href=>"$script?a=manage_users&g=$group_id"},'Manage members'));

			if ($type eq 'private') {
				print
					li(a({-href=>"$script?a=invite_users&g=$group_id"},'Invite users'));
			}

			if ($type eq 'restricted') {
				print
					li(a({-href=>"$script?a=join_queue&g=$group_id"},'Manage the join queue'));
			}

			print
				li(a({-href=>"$script?a=group_delete&g=$group_id"},'Delete this group')),
				end_ul(),
				end_blockquote();

			&$page_end();
		}
		else {
			&$page_begin();
			print 'Unauthorized access';
			&$page_end();
		}
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

elsif ($action eq 'group_admin_edit') {
	if ($logged_in) {
		my $group_id = $q->param('g');
		my $user_id = $q->cookie('VeloCalUserID');

		# check that the logged in user is a valid
		# administrator for the group
		my $select = "
			select
				count(*)
			from
				group_admin
			where
				group_id = $group_id and
				user_id = $user_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($count) = $qh->fetchrow_array();
		$count += 0;

		if ($count != 0) {
			my $select = "
				select
					name,
					type
				from
					groups
				where
					group_id = $group_id";
			my $qh = $dbh->prepare($select);
			$qh->execute();
			my ($name,$type) = $qh->fetchrow_array();

			$select = "
				select
					subscription_email
				from
					group_admin
				where
					group_id = $group_id and
					user_id = $user_id";
			$qh = $dbh->prepare($select);
			$qh->execute();
			my ($subscription_email) = $qh->fetchrow_array();

			my @yesno_values = qw/Y N/;
			my %yesno_labels = ( Y => 'Yes', N => 'No' );

			&$page_begin();

			print
				h3("Edit Administrative Preferences for '$name'"),
				start_form({-action=>$script,-method=>'POST'}),
				table(
					{-class=>'brown'},
					Tr(
						td('Email notification when members join or leave the group'),
						td(
							popup_menu({-name=>'subscription_email',-default=>$subscription_email,-values=>\@yesno_values,-labels=>\%yesno_labels,-override=>1}),
							hidden({-name=>'a',-value=>'group_admin_write',-override=>1}),
							hidden({-name=>'g',-value=>$group_id,-override=>1})
						)
					)
				),
				br(),
				submit({-value=>'Submit',-override=>1}),
				end_form();

			&$page_end();
		}
		else {
			&$page_begin();
			print 'unauthorized access';
			&$page_end();
		}
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

elsif ($action eq 'user_profile') {
	if ($logged_in) {
		my $user_id = $q->param('u');
		my $username = $q->cookie('VeloCalUserID');
# TODO: anyone can hack the URL to view anyone's profile, this should be 
#       restricted to members of the same groups

		my $select = "
			select
				name_last,
				name_first,
				biography,
				pref_pace,
				pref_terrain,
				photo_filename,
				email,
				hide_email
			from
				users
			where
				user_id = $user_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($name_last,$name_first,$biography,$pref_pace,$pref_terrain,$photo_filename,$db_email,$hide_email) = $qh->fetchrow_array();

		my $image = '&nbsp';
		if (defined $photo_filename) {
			$image = img({-src=>"$script?a=get_image&t=users&c=photo&l=user_id&r=$user_id&f=photo_filename&m=photo_magick"});
		}

		my $email_display = a({-href=>"mailto:$db_email"},$db_email);
		$email_display = div({-class=>'hidden_email'},"[ hidden ]") if ($hide_email eq 'Y');

		$biography =~ s/\n/<br>/g;

		&$page_begin();

		print
			h3('User Profile'),
			blockquote(
				table(
					{-class=>'brown'},
						Tr(
							td('Name'),
							td("$name_first $name_last")
						),
						Tr(
							td('Email'),
							td($email_display)
						),
						Tr(
							td('Biography'),
							td($biography)
						),
						Tr(
							td('Preferred Pace'),
							td($pref_pace)
						),
						Tr(
							td('Preferred Terrain'),
							td($pref_terrain)
						),
						Tr(
							td('Photo'),
							td($image)
						)
					)
			);

		&$page_end();
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

elsif ($action eq 'group_admin_write') {
	if ($logged_in) {
		my $group_id = $q->param('g');
		my $user_id = $q->cookie('VeloCalUserID');

		# check that the logged in user is a valid administrator for the group
		my $select = "
			select
				count(*)
			from
				group_admin
			where
				group_id = $group_id and
				user_id = $user_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($count) = $qh->fetchrow_array();
		$count += 0;

		if ($count != 0) {
			my $subscription_email = $q->param('subscription_email');

			my $update = "
				update group_admin set
					subscription_email = '$subscription_email'
				where
					group_id = $group_id and 
					user_id = $user_id";
			my $qh = $dbh->prepare($update);
			$qh->execute();

			print $q->redirect("$script?a=group_admin&g=$group_id");
		}
		else {
			&$page_begin();
			print 'unauthorized access';
			&$page_end();
		}
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

elsif ($action eq 'join_queue') {
	if ($logged_in) {
		my $group_id = $q->param('g');
		my $user_id = $q->cookie('VeloCalUserID');

		# check that the logged in user is a valid administrator for the group
		my $select = "
			select
				count(*)
			from
				group_admin
			where
				group_id = $group_id and
				user_id = $user_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($count) = $qh->fetchrow_array();
		$count += 0;

		if ($count != 0) {
			my $select = "
				select
					count(*)
				from
					group_queue
				where
					group_id = $group_id";
			my $qh = $dbh->prepare($select);
			$qh->execute();
			my ($number) = $qh->fetchrow_array();

			$select = "
				select
					u.user_id,
					u.email,
					u.name_first,
					u.name_last
				from
					group_queue q,
					users u
				where
					q.group_id = $group_id and
					q.user_id = u.user_id
				order by
					u.name_last,
					u.name_first";
			$qh = $dbh->prepare($select);
			$qh->execute();

			$select = "select name from groups where group_id = $group_id";
			my $qh3 = $dbh->prepare($select);
			$qh3->execute();
			my ($name) = $qh3->fetchrow_array();

			&$page_begin();

			print
				h3("Join Queue for '$name'");

			if ($number > 0) {
				print 
					p('Use the links on this page to approve or deny pending requests to join your restricted group. After clicking on a link, you will be prompted to provide an optional email response to the requesting user.'),
					start_table({-class=>'brown'}),
					Tr(
						th('Name'),
						th('Email'),
						th('Approve'),
						th('Deny')
					);

				while (my ($user_id,$email,$name_first,$name_last) = $qh->fetchrow_array()) {
					my $full_name = "$name_first $name_last";
					$full_name =~ s/(\s+)$//;

					print
						Tr(
							td($full_name),
							td(a({-href=>"mailto:$email"},$email)),
							td(a({-href=>"$script?a=restricted_approval&m=approve&g=$group_id&u=$user_id"},'Approve')),
							td(a({-href=>"$script?a=restricted_approval&m=deny&g=$group_id&u=$user_id"},'Deny'))
						);
				}

				print 
					end_table(),
					br();
			}
			else {
				print 
					p('This page is used to approve or deny pending requests to join your restricted group.'),
					p('The join queue is empty.');
			}

			&$page_end();
		}
		else {
			&$page_begin();
			print 'unauthorized access';
			&$page_end();
		}
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

elsif ($action eq 'manage_users') {
	if ($logged_in) {
		my $group_id = $q->param('g');
		my $ec = $q->param('ec');
		my $user_id = $q->cookie('VeloCalUserID');

		# check that the logged in user is a valid
		# administrator for the group
		my $select = "
			select
				count(*)
			from
				group_admin
			where
				group_id = $group_id and
				user_id = $user_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($count) = $qh->fetchrow_array();
		$count += 0;

		if ($count != 0) {
			my $select = "
				select
					u.user_id,
					u.email,
					u.name_last,
					u.name_first
				from
					users u,
					group_user g
				where
					g.group_id = $group_id and
					u.user_id = g.user_id
				order by
					u.name_last,
					u.name_first";
			my $qh = $dbh->prepare($select);
			$qh->execute();

			$select = "select name from groups where group_id = $group_id";
			my $qh3 = $dbh->prepare($select);
			$qh3->execute();
			my ($name) = $qh3->fetchrow_array();

			&$page_begin();

			print
				h3("Manage Members for '$name'");

			if ($ec == 1) {
				print 
					div(
						{-class=>'error'},
						'ERROR: You cannot delete all the administrators'
					);
			}
			elsif ($ec == 2) {
				print
					div(
						{-class=>'message'},
						'Administrator list updated'
					);
			}

			print
				p('Use this page to grant or revoke administrator privileges for this group. You cannot remove all the administrators, but you can remove yourself. No email notification will be sent following administrator rights updates.'),
				start_form({-action=>$script,-method=>'POST'}),
				start_table({-class=>'brown'}),
				Tr(
					th('Name'),
					th('Email'),
					th('Admin')
				);

			while (my ($user_id,$email,$name_last,$name_first) = $qh->fetchrow_array()) {
				my $full_name = $name_first;
				$full_name = "$name_first $name_last" if (defined $name_last);

				$select = "
					select
						user_id
					from
						group_admin
					where
						group_id = $group_id and
						user_id = $user_id";
				my $qh2 = $dbh->prepare($select);
				$qh2->execute();
				my ($admin) = $qh2->fetchrow_array();

				my $admin_checked;
				$admin_checked = 'checked' if (defined $admin);

				print
					Tr(
						td($full_name),
						td(a({-href=>"mailto:$email"},$email)),
						td({-align=>'center'},input({-type=>'checkbox',-name=>"admin:$user_id",-$admin_checked=>$admin_checked,-override=>1}))
					);
			}

			print
				end_table(),
				hidden({-name=>'a',-value=>'manage_users_write',-override=>1}),
				hidden({-name=>'g',-value=>$group_id,-override=>1}),
				br(),
				submit({-value=>'Update',-override=>1}),
				end_form();

			&$page_end();
		}
		else {
			&$page_begin();
			print 'unauthorized access';
			&$page_end();
		}
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

elsif ($action eq 'manage_users_write') {
	if ($logged_in) {
		my $group_id = $q->param('g');
		my $user_id = $q->cookie('VeloCalUserID');

		# check that the logged in user is a valid administrator for the group
		my $select = "
			select
				count(*)
			from
				group_admin
			where
				group_id = $group_id and
				user_id = $user_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($count) = $qh->fetchrow_array();
		$count += 0;

		if ($count != 0) {
			my %admins;
			foreach my $name ($q->param()) {
				if ($name =~ /^admin:/) {
					my ($admin) = (split /:/, $name)[1];
					$admins{$admin} = $admin;
				}
			}

			# make sure first that all the admins have not been removed
			if ((keys %admins) == 0) {
				print $q->redirect("$script?a=manage_users&g=$group_id&ec=1");
			}
			else {
				$select = "select user_id from group_user where group_id = $group_id";
				$qh = $dbh->prepare($select);
				$qh->execute();

				while (my ($user_id) = $qh->fetchrow_array()) {
					if (! (defined $admins{$user_id})) {
						my $delete = "delete from group_admin where group_id = $group_id and user_id = $user_id";
						my $qh2 = $dbh->prepare($delete);
						$qh2->execute();
					}
					else {
						$select = "select count(*) from group_admin where group_id = $group_id and user_id = $user_id";
						my $qh3 = $dbh->prepare($select);
						$qh3->execute();
						my ($count) = $qh3->fetchrow_array();

						if ($count == 0) {
							my $insert = "insert into group_admin (group_id,user_id) values ($group_id,$user_id)";
							my $qh2 = $dbh->prepare($insert);
							$qh2->execute();
						}
					}
				}
			}

			print $q->redirect("$script?a=manage_users&g=$group_id&ec=2");
		}
		else {
			&$page_begin();
			print 'Unauthorized access';
			&$page_end();
		}
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

elsif ($action eq 'group_delete') {
	if ($logged_in) {
		my $group_id = $q->param('g');
		my $user_id = $q->cookie('VeloCalUserID');

		# check that the logged in user is a valid administrator for the group
		my $select = "
			select
				count(*)
			from
				group_admin
			where
				group_id = $group_id and
				user_id = $user_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($count) = $qh->fetchrow_array();
		$count += 0;

		if ($count != 0) {
			&$page_begin();

			print
				h3('Delete Group'),
				p('WARNING: Deleting a group will cancel all group rides, remove all users from the group, notify all users about the group deletion, and remove all record of the group. It CANNOT be undone.'),
				p('Confirm that you would like to delete this group.'),
				start_form({-action=>$script,-method=>'POST'}),
				hidden({-name=>'a',-value=>'group_delete_confirm',-override=>1}),
				hidden({-name=>'g',-value=>$group_id,-override=>1}),
				submit({-value=>'Delete'}),
				end_form();

			&$page_end();
		}
		else {
			&$page_begin();
			print 'unauthorized access';
			&$page_end();
		}
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

elsif ($action eq 'group_delete_confirm') {
	if ($logged_in) {
		my $group_id = $q->param('g');
		my $user_id = $q->cookie('VeloCalUserID');

		# check that the logged in user is a valid administrator for the group
		my $select = "
			select
				count(*)
			from
				group_admin
			where
				group_id = $group_id and
				user_id = $user_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($count) = $qh->fetchrow_array();
		$count += 0;

		if ($count != 0) {
			# get the name of the group (used in the emails sent to users)
			$select = "
				select
					name
				from
					groups
				where
					group_id = $group_id";
			$qh = $dbh->prepare($select);
			$qh->execute();
			my ($name) = $qh->fetchrow_array();

			# delete from group_admin
			my $delete = "delete from group_admin where group_id = $group_id";
			my $qh = $dbh->prepare($delete);
			$qh->execute();

			# delete from group_queue
			$delete = "delete from group_queue where group_id = $group_id";
			$qh = $dbh->prepare($delete);
			$qh->execute();

			# notify users here
# TODO: this SQL needs to be fixed
			$select = "
				select 
					u.email,
					u.name_first,
					u.name_last
				from 
					group_user g,
					users u
				where 
					u.user_id = g.user_id and
					group_id = $group_id";
			$qh = $dbh->prepare($select);
			$qh->execute();

			while (my ($email,$name_first,$name_last) = $qh->fetchrow_array()) {
				my $fullname = "$name_first $name_last";
				$fullname =~ s/(\s+)$//g;

				open(MAIL,"| $sendmail -t");
				print MAIL "To: $fullname <$email>\n";
				print MAIL "From: $registration_name <$registration_email>\n";
				print MAIL "Subject: VeloCal Group '$name' Deleted\n";
				print MAIL "Content-type: text/html\n\n";
				print MAIL "You are currently a member of the group '$name'. Unfortunately this group has just been deleted. All future rides for this group have been deleted from your ride calendar.";
				close(MAIL);
			}

			# delete from group_user
			$delete = "delete from group_user where group_id = $group_id";
			$qh = $dbh->prepare($delete);
			$qh->execute();

			# delete from event_user
			$delete = "delete from event_user where event_id in (select event_id from events where group_id=$group_id)";
			$qh = $dbh->prepare($delete);
			$qh->execute();

			# delete from events
			$delete = "delete from events where group_id = $group_id";
			$qh = $dbh->prepare($delete);
			$qh->execute();

			# remove any references to this group's maps (that are about to be deleted)
			my $update = "update events set map_id = NULL where map_id in (select id from maps where group_id = $group_id)";
			$qh = $dbh->prepare($update);
			$qh->execute();

			# delete from maps
			$delete = "delete from maps where group_id = $group_id";
			$qh = $dbh->prepare($delete);
			$qh->execute();

			# delete from groups
			$delete = "delete from groups where group_id = $group_id";
			$qh = $dbh->prepare($delete);
			$qh->execute();

			print $q->redirect($script);
		}
		else {
			&$page_begin();
			print 'Unauthorized access';
			&$page_end();
		}
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

elsif ($action eq 'group_edit') {
	if ($logged_in) {
		my $edit = $q->param('edit');
		my $group_id = $q->param('g');
		my $method = $q->param('m');

		# set default values first
		my $city = 'NEW';
		my $state = 'none';
		my $name;
		my $description;
		my $type;
		my $default_pace = 'B';
		my $default_terrain = 'Rolling';
		my $default_start_location;
		my $default_start_time_hour = '08';
		my $default_start_time_minute = '00';
		my $homepage;
		my $new_city;

		## if method is 'edit', then get existing values
		if ($edit eq 'Y') {
			my $select = "
				select
					city,
					state,
					description,
					type,
					name,
					default_pace,
					default_terrain,
					default_start_location,
					default_start_time,
					homepage
				from
					groups
				where
					group_id = $group_id";
			my $qh = $dbh->prepare($select);
			$qh->execute();
			my $default_start_time;
			($city,$state,$description,$type,$name,$default_pace,$default_terrain,$default_start_location,$default_start_time,$homepage) = $qh->fetchrow_array();
			($default_start_time_hour,$default_start_time_minute) = split /:/, $default_start_time;
		}

		my $original_group_type = $type;
		my $type_change_warning;
		if ($edit eq 'Y') {
			$type_change_warning =
				div(
					{-class=>'type_change_warning',-id=>'type_change_warning'},
					"WARNING: Changing the group type will delete any outstanding invitations or requests for approval."
				);
		}

		## get entered values
		$city = $q->param('city') if (defined $q->param('city'));
		$state = $q->param('state') if (defined $q->param('state'));
		$name = $q->param('name') if (defined $q->param('name'));
		$description = $q->param('description') if (defined $q->param('description'));
		$type = $q->param('type') if (defined $q->param('type'));
		$default_pace = $q->param('default_pace') if (defined $q->param('default_pace'));
		$default_terrain = $q->param('default_terrain') if (defined $q->param('default_terrain'));
		$default_start_location = $q->param('default_start_location') if (defined $q->param('default_start_location'));
		$default_start_time_hour = $q->param('default_start_time_hour') if (defined $q->param('default_start_time_hour'));
		$default_start_time_minute = $q->param('default_start_time_minute') if (defined $q->param('default_start_time_minute'));
		$new_city = $q->param('new_city') if (defined $q->param('new_city')); 
		$homepage = $q->param('homepage') if (defined $q->param('homepage')); 

		my @errors;
		my $print_form = 1;
		if ($method eq 'validate') {
			my $city_name = $city;
			$city_name = $new_city if ($city eq 'NEW');
			$city_name =~ s/^\s+//g; # remove leading whitespace
			$city_name =~ s/\s+$//g; # remove trailing whitespace

			$name =~ s/^\s+//g; # remove leading whitespace
			$name =~ s/\s+$//g; # remove trailing whitespace

			$homepage =~ s/^\s+//g; # remove leading whitespace
			$homepage =~ s/\s+$//g; # remove trailing whitespace

			$default_start_location =~ s/^\s+//g; # remove leading whitespace
			$default_start_location =~ s/\s+$//g; # remove trailing whitespace

			if ($state eq '') {
				push @errors, 'ERROR: You must select a state.';
			}
			if ($city_name eq '') {
				push @errors, 'ERROR: You must select a city.';
			}
			if ($name eq '') {
				push @errors, 'ERROR: You must specify a group name.';
			}
			## TODO: need to check for duplicate group names for a city
			## TODO: need to check for duplicate city name  (case changes, spaces, etc.)

			if (scalar @errors == 0) {
				## all the data is good !!

				$city_name = lc($city_name);
				$city_name = encode_entities($city_name, '<>');
				$name = encode_entities($name, '<>');
				$description = encode_entities($description,'<>');
				$default_start_location = encode_entities($default_start_location, '<>');

				if ($edit eq 'Y') {
					# update
					my $update = "
						update groups set
							city = ?,
							state = '$state',
							description = ?,
							type = '$type',
							name = ?,
							default_pace = '$default_pace',
							default_terrain = '$default_terrain',
							default_start_location = ?,
							default_start_time = '$default_start_time_hour:$default_start_time_minute',
							homepage = ?
						where
							group_id = $group_id";
					my $qh = $dbh->prepare($update);
					$qh->execute($city_name,$description,$name,$default_start_location,$homepage);

					# if the group type is changing, just delete eveyone in the group_queue for this group
					if ($original_group_type ne $type) {
						my $delete = "delete from group_queue where group_id = $group_id";
						$qh = $dbh->prepare($delete);
						$qh->execute();
					}

					## that's it, don't print the form and redirect
					$print_form = 0;
					print $q->redirect("$script?a=group_admin&g=$group_id");
				}
				else {
					## add the new group into the groups table
					my $insert = "
						insert into groups (
							group_id,
							city,
							state,
							description,
							type,
							name,
							default_pace,
							default_terrain,
							default_start_location,
							default_start_time,
							homepage
						) values (
							NULL,
							?,
							'$state',
							?,
							'$type',
							?,
							'$default_pace',
							'$default_terrain',
							?,
							'$default_start_time_hour:$default_start_time_minute',
							?
						)";
					my $qh = $dbh->prepare($insert);
					$qh->execute($city_name,$description,$name,$default_start_location,$homepage);

					## add the user as the admin of the new group
					my $group_id = $dbh->{'mysql_insertid'};
					my $user_id = $q->cookie('VeloCalUserID');

					$insert = "
						insert into group_admin (
							group_id,
							user_id,
							subscription_email
						) values (
							$group_id,
							$user_id,
							'Y'
						)";
					$qh = $dbh->prepare($insert);
					$qh->execute();

					## add the user as a member of the new group
					$insert = "
						insert into group_user (
							group_id,
							user_id	
						) values (
							$group_id,
							$user_id
						)";
					$qh = $dbh->prepare($insert);
					$qh->execute();

					## that's it, don't print the form and redirect
					$print_form = 0;
					print $q->redirect($script);
				}
			}
		}

		if ($print_form == 1) {
			## call divState javascript function on initial page load
			## this peserves div show/hide states on reloads
			&$page_begin('VeloCal',"divState('$city');");

			($edit eq 'Y') ? (print h3('Update Group Profile')) : (print h3('Create a New Group'));

			if (scalar @errors > 0) {
				print start_div({-class=>'error'});
				foreach my $error (@errors) {
					print 
						$error,
						br();
				}
				print end_div();
			}

			print 
				p(font({-color=>'red'},'*'), " indicates a required field."),
				p('Use the following guidelines for selecting a group type.'),
				blockquote(
					table(
						{-class=>'brown'},
						Tr(
							td('Public'),
							td('The group is visible. Users can join without any authorization required.')
						),
						Tr(
							td('Restricted'),
							td('The group is visible. Users must request access. Administrators can allow or deny access.')
						),
						Tr(
							td('Private'),
							td('The group is not visible to the public. Access is by invitation only.')
						)
					)
				),
				p('Use the following guidelines for selecting a preferred terrain.'),
				blockquote(
					table(
						{-class=>'brown'},
						Tr(
							td('Hilly'),
							td('Numerous long and steep climbs.')
						),
						Tr(
							td('Moderately Hilly'),
							td('Numerous climbs with no "killer" hills.')
						),
						Tr(
							td('Rolling'),
							td('Some small hills; farmland ups and downs.')
						),
						Tr(
							td('Flat'),
							td('Minimal gear shifting required.')
						)
					)
				),
				p('Use the following guidelines for selecting a preferred pace. Note: average speeds assume flat terrain. Speed will be lower when hills are involved. Also, the typical cruising speed will be higher than the average (about 2 mph).'),
				blockquote(
					table(
						{-class=>'brown'},
						Tr(
							td('AX'),
							td('For the very strong cyclists. Primary moving average 20+ mph.')
						),
						Tr(
							td('A'),
							td('For the strong cyclists. Primary moving average 17-19 mph.')
						),
						Tr(
							td('B'),
							td('For the average to strong cyclists. Primary moving average 15-17 mph.')
						),
						Tr(
							td('C'),
							td('For the average cyclists. Primary moving average 12-15 mph.')
						),
						Tr(
							td('D'),
							td('For the new, inexperienced riders. Primary moving average 9-12 mph, includes frequent rest stops.')
						)
					)
				);
	
			## define 'type' radio values, labels, and default value
			my %type_labels = (
				public => 'Public', 
				restricted => 'Restricted', 
				private => 'Private',
			);
			my @type_values = qw/public restricted private/;
			my $type_default = 'public';


			## define hours and minutes values
			my @hours_values = qw/00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 21 22 23/;
			my @minutes_values = qw/00 15 30 45/;

			## get the state values
			my @state_codes;
			my %states = &$get_states();
			push @state_codes, 'none';

			foreach my $code (sort { $states{$a} cmp $states{$b} } keys %states) {
				push @state_codes, $code;
			}
			$states{'none'} = ' ';

			print
				start_form({-action=>$script,-method=>'POST'}),
				start_table({-class=>'brown'}),
				Tr(
					td('State ' . font({-color=>'red'},'*')),
					td(popup_menu({-name=>'state',-id=>'state',-values=>\@state_codes,-labels=>\%states,-default=>$state,-onChange=>"divState('NEW');",-override=>1}))
				);

			## get the city values
			my %cities;
			my $select = "
				select
					distinct city,
					state
				from
					groups
				group by
					city,
					state";
			my $qh = $dbh->prepare($select);
			$qh->execute();
			while (my ($city,$state) = $qh->fetchrow_array()) {
				$cities{$state}{$city} = &$ucwords($city);
			}

			print
				start_Tr(),
				td('City ' . font({-color=>'red'},'*')),
				start_td();

			foreach my $state (keys %cities) {
				my @cities = sort keys %{$cities{$state}};

				print
					div(
						{-class=>'state',-id=>$state,-style=>'display: none;'},
						radio_group({-name=>'city',-id=>'city',-values=>\@cities,-labels=>\%{$cities{$state}},-default=>$city,-linebreak=>'true',-override=>1})
					);
			}

			my @new_city_value = ('NEW');
			my %new_city_label = ( NEW => 'New City: ' );

			print
				div(
					{-class=>'state',-id=>'newcity',-style=>'display: none;'},
					radio_group({-name=>'city',-id=>'newcityradio',-values=>\@new_city_value,-labels=>\%new_city_label,-default=>$city,-override=>1}),
					input({-name=>'new_city',-size=>16,-maxlength=>255,-value=>$new_city,-onFocus=>'setCityNew();',-override=>1})
				);

			print
				end_td(),
				end_Tr();

			## now the easy stuff
			print
				Tr(
					td('Group Name ' . font({-color=>'red'},'*')),
					td(input({-name=>'name',-size=>25,-maxlength=>255,-value=>$name,-override=>1}))
				),
				Tr(
					td('Homepage '),
					td(input({-name=>'homepage',-size=>60,-maxlength=>255,-value=>$homepage,-override=>1}))
				),
				Tr(
					td('Group Description'),
					td(textarea({-name=>'description',-rows=>5,-columns=>60,-value=>$description,-override=>1}))
				),
				Tr(
					td('Group Type ' . font({-color=>'red'},'*')),
					td(radio_group({-name=>'type',-values=>\@type_values,-labels=>\%type_labels,-default=>$type,-linebreak=>'true',-onchange=>"divType('$edit','$original_group_type',this);",-override=>1}), $type_change_warning)
				),
				Tr(
					td('Default Pace ' . font({-color=>'red'},'*')),
					td(radio_group({-name=>'default_pace',-values=>\@pace_values,-labels=>\%pace_labels,-default=>$default_pace,-linebreak=>'true',-override=>1}))
				),
				Tr(
					td('Default Terrain ' . font({-color=>'red'},'*')),
					td(radio_group({-name=>'default_terrain',-values=>\@terrain_values,-labels=>\%terrain_labels,-default=>$default_terrain,-linebreak=>'true',-override=>1}))
				),
				Tr(
					td('Default Start Location'),
					td(input({-name=>'default_start_location',-size=>25,-maxlength=>255,-value=>$default_start_location,-override=>1}))
				),
				Tr(
					td('Default Start Time'),
					td(
						popup_menu({-name=>'default_start_time_hour',-values=>\@hours_values,-default=>$default_start_time_hour,-override=>1}),
						':',
						popup_menu({-name=>'default_start_time_minute',-values=>\@minutes_values,-default=>$default_start_time_minute,-override=>1})
					)
				),
				end_table(),
				br();

			my $submit_text = 'Create Group';
			$submit_text = 'Update' if ($edit eq 'Y');

			print
				div(
					{-class=>'state',-id=>'group_edit_submit',-style=>'display: none;'},
					hidden({-name=>'a',-value=>'group_edit',-override=>1}),
					hidden({-name=>'g',-value=>$group_id,-override=>1}),
					hidden({-name=>'m',-value=>'validate',-override=>1}),
					hidden({-name=>'edit',-value=>$edit,-override=>1}),
					submit({-value=>$submit_text,-override=>1})
				),
				end_form(),
				br();

			&$page_end();
		}
	}
	else {
		print $q->redirect("$script?a=login");
	}
}

### not yet implemented
elsif ($action eq 'routes') {
	if ($logged_in) {
		my $group_id = $q->param('g');
		my $user_id = $q->cookie('VeloCalUserID');

		my $select = "select name, type from groups where group_id = $group_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($name,$type) = $qh->fetchrow_array();

		my $authorized = 1;

		if ($type eq 'private') {
			$select = "select count(*) from group_user where group_id = $group_id and user_id = $user_id";
			$qh = $dbh->prepare($select);
			$qh->execute();
			my ($count) = $qh->fetchrow_array();

			$authorized = 0 unless (defined $count);
		}

		if ($authorized) {
			&$page_begin();

			print 
				h3("Route Library for '$name'"),
				'[route library goes here]';

			&$page_end();
		}
		else {
			&$page_begin();
			print "Unauthorized access";
			&$page_end();
		}
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

elsif ($action eq 'get_image') {
	my $table = $q->param('t');
	my $column = $q->param('c');
	my $column_filename = $q->param('f');
	my $column_magick = $q->param('m');
	my $where_left = $q->param('l');
	my $where_right = $q->param('r');

#	$dbh->{LongReadLen} = 64 * 1024; # 64Kb
#	$dbh->{LongReadLen} = 256 * 1024; # 256Kb

	my $select = "
		select
			$column,
			$column_filename,
			$column_magick
		from
			$table
		where
			$where_left = '$where_right'";
	my $qh = $dbh->prepare($select);
	$qh->execute();
	my ($image,$filename,$magick) = $qh->fetchrow_array();
	my $image_size = length($image);

	print "Content-disposition: inline; filename=$filename\n";
	print "Content-Length: $image_size\n";
	print "Content-Type: image/$magick\n\n";
	print $image;
}

elsif ($action eq 'add') {
	if ($logged_in) {
		my ($sec,$min,$hour,$day,$month,$year) = localtime(time);
		$year += 1900;
		$month += 1;
		($year,$month,$day) = split ':', &$convert_to_localtime("$year:$month:$day:$hour:$min:$sec");

		$day = $q->param('d') if (defined $q->param('d'));
		$month = $q->param('m') if (defined $q->param('m'));
		$year = $q->param('y') if (defined $q->param('y'));

		$day += 0;    # converts, for example, '02' to '2'
		$month += 0;

		my $group_id = $q->param('group_id');
		my $title = $q->param('title');
		my $location = $q->param('location');
		my $pace = $q->param('pace');
		my $terrain = $q->param('terrain');
		my $distance = $q->param('distance');
		my $notes = $q->param('notes');
		my $check = $q->param('check');
		my $method = $q->param('method') || 'add';
		my $event_id = $q->param('event_id');
		my $map_id = $q->param('map_id');

		my $user_id = $q->cookie('VeloCalUserID');

		my $select = "
			select
				group_id
			from
				group_user
			where
				user_id = $user_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();

		my @groups;
		while (my ($group_id) = $qh->fetchrow_array()) {
			push @groups, $group_id;
		}
		my $group_id_string = join ',', @groups;

		$select = "
			select
				group_id,
				name,
				default_pace,
				default_terrain,
				default_start_location,
				default_start_time
			from
				groups
			where
				group_id in ($group_id_string)";
		$qh = $dbh->prepare($select);
		$qh->execute();

		my %groups;
		while (my ($group_id,$name,$default_pace,$default_terrain,$default_start_location,$default_start_time) = $qh->fetchrow_array()) {
			$groups{$group_id}{name} = $name;
			$groups{$group_id}{default_pace} = $default_pace;
			$groups{$group_id}{default_terrain} = $default_terrain;
			$groups{$group_id}{default_start_location} = $default_start_location;
			my ($hours,$minutes) = split /:/, $default_start_time;
			$hours += 0; # strip leading 0s to match values in form elements
			$minutes += 0;
			$groups{$group_id}{default_start_time_hours} = $hours;
			$groups{$group_id}{default_start_time_minutes} = $minutes;
		}

		my @group_values = keys %groups;
		my %group_labels;
		foreach my $group_id (keys %groups) {
			$group_labels{$group_id} = $groups{$group_id}{name};
		}

		# disallow changing the group when editing an existing event
		if ($method eq 'edit') {
			@group_values = ($group_id);
		}

		# get list of group's maps
		my %maps;

		$select = "
			select
				id,
				name,
				url,
				image_filename,
				image_magick
			from
				maps
			where
				group_id in ($group_id_string)";
		$qh = $dbh->prepare($select);
		$qh->execute();

		my %map_labels;
		while (my ($map_id,$name,$url,$image_filename,$image_magick) = $qh->fetchrow_array()) {
			$map_labels{$map_id} = $name;
			$maps{$map_id}{name} = $name;
			$maps{$map_id}{url} = $url;
			$maps{$map_id}{image_filename} = $image_filename;
			$maps{$map_id}{image_magick} = $image_magick;
		}
		my @maps = sort { $maps{$a}{name} cmp $maps{$b}{name} } keys %maps;
		$map_labels{0} = 'No Map';
		$maps{0}{name} = 'No Map';
		@maps = (0, @maps);

# TODO - add javascript to change list of maps when the group changes
#        whenever the group changes it should be set to 'No Map'

		# default values
		my $default_start_hour = 8;
		my $default_start_minutes = 0;
		$default_start_hour = $q->param('start_hour') if (defined $q->param('start_hour'));
		$default_start_minutes = $q->param('start_minutes') if (defined $q->param('start_minutes'));
		$default_start_hour += 0;
		$default_start_minutes += 0;
		my $default_map = 0;
		$default_map = $q->param('map_id') if (defined $q->param('map_id'));

		my $JS = <<END;
			function setGroupDefaults() {
				if (document.getElementById('group_id')) {
					group = document.getElementById('group_id').value;
END

		foreach my $group_id (keys %groups) {
			$JS .= <<END;
					if (group == $group_id) {
						if (document.getElementById('default_location')) {
							document.getElementById('default_location').value = '$groups{$group_id}{default_start_location}';
						}
						if (document.getElementById('start_hour')) {
							document.getElementById('start_hour').value = '$groups{$group_id}{default_start_time_hours}';
						}
						if (document.getElementById('start_minutes')) {
							document.getElementById('start_minutes').value = '$groups{$group_id}{default_start_time_minutes}';
						}
						if (document.getElementById('default_pace')) {
							document.getElementById('default_pace').value = '$groups{$group_id}{default_pace}';
						}
						if (document.getElementById('default_terrain')) {
							document.getElementById('default_terrain').value = '$groups{$group_id}{default_terrain}';
						}
					}
END
		}

		$JS .= <<END;
				}
			}
END

		my $onload;
		$onload = 'setGroupDefaults();' if (($q->param('check') ne 'true') && ($q->param('method') ne 'edit'));

		my $data_valid = 1;
		my $date_valid = 1;
		my $time_valid = 1;
		my @errors;

		if ($check eq 'true') {
			unless (check_date($year,$month,$day)) { 
				$data_valid = 0;
				$date_valid = 0;
				push @errors, "Date selected is not a valid date";
			}
			unless (check_time($default_start_hour,$default_start_minutes,0)) { 
				$data_valid = 0;
				$time_valid = 0;
				push @errors, "Time selected is not a valid time";
			}
			if (($date_valid == 1) && ($time_valid == 1)) {
				my ($now_sec,$now_min,$now_hour,$now_day,$now_month,$now_year) = localtime(time);
				$now_year += 1900;
				$now_month += 1;
				($now_year,$now_month,$now_day,$now_hour,$now_min,$now_sec) = split ':', &$convert_to_localtime("$now_year:$now_month:$now_day:$now_hour:$now_min:$now_sec");

				my ($Dd,$Dh,$Dm,$Ds) = Delta_DHMS(
												$now_year,$now_month,$now_day,
												$now_hour,$now_min,$now_sec,
												$year,$month,$day,
												$default_start_hour,$default_start_minutes,0);
				unless (($Dd >= 0) && ($Dh >= 0) && ($Dm >= 0) && ($Ds >= 0)) {
					$data_valid = 0;
					push @errors, "The date and time selected is not in the future";
				}
			}
			unless (length($title) > 0) {
				$data_valid = 0;
				push @errors, "An event title must be provided";
			}
			unless (length($title) < 512) { 
				$data_valid = 0;
				push @errors, "Event title is too long (max. 512 characters)";
			}
			unless (length($location) > 0) {
				$data_valid = 0;
				push @errors, "An event location must be provided";
			}
			unless (length($location) < 512) { 
				$data_valid = 0;
				push @errors, "Event location is too long (max. 512 characters)";
			}
			# should the length of the 'distance' field also be checked?
		}

		if (($check eq 'true') && ($data_valid == 1)) {
			$month = "0$month" if ($month < 10);
			$day = "0$day" if ($day < 10);
			$default_start_hour = "0$default_start_hour" if ($default_start_hour < 10);
			$default_start_minutes = "0$default_start_minutes" if ($default_start_minutes < 10);

			my $dow = Day_of_Week_to_Text(Day_of_Week($year,$month,$day));

			my $start_time = "$year-$month-$day $default_start_hour:$default_start_minutes:" . "00";

			if ($method eq 'edit') {	# update event
				my $update = "
					update events set
						title = ?,
						start_time = '$start_time',
						location = ?,
						map_id = $map_id,
						pace = '$pace',
						terrain = '$terrain',
						distance = ?,
						notes = ?
					where
						event_id = $event_id";
				my $qh = $dbh->prepare($update);
				$qh->execute($title,$location,$distance,$notes);
			}
			else {	# insert event
				my $insert = "
					insert into events (
						event_id,
						group_id,
						title,
						start_time,
						location,
						map_id,
						pace,
						terrain,
						notes,
						distance,
						user_id
					) values (
						NULL,
						$group_id,
						?,
						'$start_time',
						?,
						$map_id,
						'$pace',
						'$terrain',
						?,
						?,
						$user_id
					)";
				my $qh = $dbh->prepare($insert);
				$qh->execute($title,$location,$notes,$distance);

				$select = "
					select 
						user_id
					from 
						group_user
					where
						group_id = $group_id";
				$qh = $dbh->prepare($select);
				$qh->execute();

				while (my ($user_id) = $qh->fetchrow_array()) {
					my $insert = "insert into event_user (event_id,user_id) values (last_insert_id(),$user_id)";
					my $qh2 = $dbh->prepare($insert);
					$qh2->execute();
				}

				$select = "select last_insert_id()";
				$qh = $dbh->prepare($select);
				$qh->execute();
				$event_id = $qh->fetchrow_array();
			}

			# send email to those who want email notification
			my %emails;
			my %userids;
			my $select = "
				select 
					u.name_first,
					u.name_last,
					u.email,
					u.user_id
				from 
					group_user natural join 
					users u 
				where 	
					group_id = $group_id and 
					notification = 'Y'";
			my $qh = $dbh->prepare($select);
			$qh->execute();
			while (my ($name_first,$name_last,$email,$user_id) = $qh->fetchrow_array()) {
				$emails{$email} = "$name_first $name_last";
				$emails{$email} =~ s/(\s+)$//; # remove trailing space if no last name
				$userids{$email} = $user_id;
			}

			$select = "select name from groups where group_id = $group_id";
			$qh = $dbh->prepare($select);
			$qh->execute();
			my ($group_name) = $qh->fetchrow_array();
			
			$select = "select name_last,name_first,email,hide_email from users where user_id = $user_id";
			$qh = $dbh->prepare($select);
			$qh->execute();
			my ($name_last,$name_first,$email,$hide_email) = $qh->fetchrow_array();

			($hide_email eq 'Y') ? ($email = '') : ($email = "&lt;$email&gt;");
			
			# this will not scale well, but each email is customized
			foreach my $member_email (keys %emails) {

				my $member_user_id = $userids{$member_email};

				my $select2 = "select status,comments from event_user where user_id = $member_user_id and event_id = $event_id";
				my $qh2 = $dbh->prepare($select2);
				$qh2->execute();
				my ($status,$comments) = $qh2->fetchrow_array();

				$notes =~ s/\n/<br>/g;

				my $map_name;
				$map_name = a({-href=>"$script?a=get_image&t=maps&c=image&l=id&r=$map_id&f=image_filename&m=image_magick"},$maps{$map_id}{name}) if ($maps{$map_id}{image_filename} ne '');
				$map_name = a({-href=>$maps{$map_id}{url}},$maps{$map_id}{name}) if ($maps{$map_id}{url} ne '');
				$map_name = '&nbsp;' if ($map_name eq '');

				open(MAIL,"| $sendmail -t");
				print MAIL "To: $emails{$member_email} <$member_email>\n";
				print MAIL "From: $registration_name <$registration_email>\n";
				print MAIL "Subject: $group_name Event :: $title\n";
				print MAIL "Content-type: text/html\n\n";
				print MAIL "Event " . uc($method) . "ed by $name_first $name_last $email<br>\n";
				print MAIL "<br>\n";
				print MAIL "Group Name: $group_name<br>\n";
				print MAIL "Event Title: $title<br>\n";
				print MAIL "Start Time: $start_time ($dow)<br>\n";
				print MAIL "Location: $location<br>\n";
				print MAIL "Map: $map_name<br>\n";
				print MAIL "Pace: $pace<br>\n";
				print MAIL "Terrain: $terrain<br>\n";
				print MAIL "Distance: $distance<br>\n";
				print MAIL "Notes: <br>\n";
				print MAIL "<blockquote>$notes</blockquote>\n";
				if ($status ne '') {
					print MAIL "You have already indicated your attendance intention as " . uc($status);
					if ($comments ne '') {
						print MAIL " and have added the comments \"$comments\"";
					}
				}
				else {
					print MAIL "You have not yet indicated your attendance intentions";
				}
				print MAIL ".<br><br>\n";
				print MAIL "To view this event, click <a href=\"$script?a=event&e=$event_id\">here</a><br>\n";
				print MAIL "To mark your attendance as YES, click <a href=\"$script?a=att&e=$event_id&u=$member_user_id&attend=yes\">here</a><br>\n";
				print MAIL "To mark your attendance as NO, click <a href=\"$script?a=att&e=$event_id&u=$member_user_id&attend=no\">here</a><br>\n";
				print MAIL "To mark your attendance as MAYBE, click <a href=\"$script?a=att&e=$event_id&u=$member_user_id&attend=maybe\">here</a><br>\n";
				print MAIL "<br>\n";
				print MAIL "If you would like to unsubscribe from this group and no longer receive these emails, click <a href=\"$script?a=unsubscribe&g=$group_id\">here</a>\n";
				close(MAIL);
			}

			print $q->redirect("$script?action=main&y=$year&m=$month");
		}
		else {
			&$page_begin($default_page_title,$onload,$JS);

			print 
				h3(ucfirst($method) . ' Event');

			# print error messages
			if (scalar @errors > 0) {
				foreach my $error (@errors) {
					print
						div(
							{-class=>'error'},
							"ERROR: $error"
						);
				}

				print
					br();
			}

			$notes =~ s/<br>//g;

			print 
				p(font({-color=>'red'},'*'), " indicates a required field."),
				start_form({-action=>$script,-method=>'POST'}),
				table(
					{-class=>'brown'},
					Tr(
						td(
							{-class=>'add_left'},
							'Group ' . font({-color=>'red'},'*')
						),
						td(
							popup_menu({-name=>'group_id',-id=>'group_id',-values=>\@group_values,-labels=>\%group_labels,-default=>$group_id,-onChange=>'setGroupDefaults();',-override=>1}),
						)
					),
					Tr(
						td(
							{-class=>'add_left'},
							'Title ' . font({-color=>'red'},'*')
						),
						td(
							{-class=>'add_right'},
							input({-name=>'title',-value=>$title,-size=>50,-maxlength=>80,-override=>1}),
							br(),
							'max. 80 characters'
						)
					),
					Tr(
						td(
							{-class=>'add_left'},
							'Date ' . font({-color=>'red'},'*')
						),
						td(
							{-class=>'add_right'},
							popup_menu({-name=>'m',-values=>\@month_values,-labels=>\%month_labels,-default=>$month,-override=>1}),
							popup_menu({-name=>'d',-values=>\@days,-default=>$day,-override=>1}),
							popup_menu({-name=>'y',-values=>\@years,-default=>$year,-override=>1})
						)
					),
					Tr(
						td(
							{-class=>'add_left'},
							'Time ' . font({-color=>'red'},'*')
						),
						td(
							{-class=>'add_right'},
							popup_menu({-name=>'start_hour',-id=>'start_hour',-values=>\@hours_values,-labels=>\%hours_labels,-default=>$default_start_hour,-override=>1}),
							popup_menu({-name=>'start_minutes',-id=>'start_minutes',-values=>\@minutes_values,-labels=>\%minutes_labels,-default=>$default_start_minutes,-override=>1}),
						)
					),
					Tr(
						td(
							{-class=>'add_left'},
							'Location ' . font({-color=>'red'},'*')
						),
						td(
							{-class=>'add_right'},
							input({-name=>'location',-id=>'default_location',-value=>$location,-size=>50,-maxlength=>80,-override=>1}),
						)
					),
					Tr(
						td(
							{-class=>'add_left'},
							'Map '
						),
						td(
							popup_menu({-name=>'map_id',-id=>'default_map',-values=>\@maps,-labels=>\%map_labels,-default=>$default_map,-override=>1}),
							a(
								{-href=>"javascript:toggleDiv('map_help');"},
								img({-src=>'images/question.png',-border=>0})
							),
							div(
								{-id=>'map_help',-style=>'display: none; padding: 15px;'},
								'To add group maps, select "About" for your desired group, and then select "Add a map" in the Group Maps section.'
							)
						)
					),
					Tr(
						td(
							{-class=>'add_left'},
							'Pace ' . font({-color=>'red'},'*')
						),
						td(
							popup_menu({-name=>'pace',-id=>'default_pace',-values=>\@pace_values,-labels=>\%pace_labels,-default=>$pace,-override=>1}),
							a(
								{-href=>"javascript:toggleDiv('pace_help');"},
								img({-src=>'images/question.png',-border=>0})
							),
							div(
								{-id=>'pace_help',-style=>'display: none; padding: 15px;'},
								table(
									{-class=>'brown'},
									Tr(
										td('AX'),
										td('For the very strong cyclists. Primary moving average 20+ mph.')
									),
									Tr(
										td('A'),
										td('For the strong cyclists. Primary moving average 17-19 mph.')
									),
									Tr(
										td('B'),
										td('For the average to strong cyclists. Primary moving average 15-17 mph.')
									),
									Tr(
										td('C'),
										td('For the average cyclists. Primary moving average 12-15 mph.')
									),
									Tr(
										td('D'),
										td('For the new, inexperienced riders. Primary moving average 9-12 mph, includes frequent rest stops.')
									)
								)
							)
						)
					),
					Tr(
						td(
							{-class=>'add_left'},
							'Terrain ' . font({-color=>'red'},'*')
						),
						td(
							popup_menu({-name=>'terrain',-id=>'default_terrain',-values=>\@terrain_values,-labels=>\%terrain_labels,-default=>$terrain,-override=>1}),
							a(
								{-href=>"javascript:toggleDiv('terrain_help');"},
								img({-src=>'images/question.png',-border=>0})
							),
							div(
								{-id=>'terrain_help',-style=>'display: none; padding: 15px;'},
								table(
									{-class=>'brown'},
									Tr(
										td('Hilly'),
										td('Numerous long and steep climbs.')
									),
									Tr(
										td('Moderately Hilly'),
										td('Numerous climbs with no "killer" hills.')
									),
									Tr(
										td('Rolling'),
										td('Some small hills; farmland ups and downs.')
									),
									Tr(
										td('Flat'),
										td('Minimal gear shifting required.')
									)
								)
							)
						)
					),
					Tr(
						td(
							{-class=>'add_left'},
							'Distance '
						),
						td(
							input({-name=>'distance',-id=>'distance',-value=>$distance,-size=>32,-maxlength=>32,-override=>1}),
						)
					),
					Tr(
						td(
							{-class=>'add_left'},
							'Notes'
						),
						td(
							{-class=>'add_right'},
							textarea({-name=>'notes',-rows=>5,-cols=>60,-value=>$notes,-override=>1}),
						)
					)
				),
				br(),
				'Email will be sent to all group members when you click "' . ucfirst($method) . '"',
				br(), 
				br(), 
				submit({-value=>ucfirst($method)}),
				hidden({-name=>'a',-value=>$action}),
				hidden({-name=>'method',-value=>$method}),
				hidden({-name=>'event_id',-value=>$event_id}),
				hidden({-name=>'check',-value=>'true'}),
				end_form();

	# repeating:
	#  every, every other, every third, every fourth - day, week, month, year, MWF, TuTh, M-F, SaSu
	#    or
	#  on the first, second, third, fourth, last - SMTWTFS - of the month every month, other month, 3 mo, 4mo, 6mo,yr
	#
	# end date
	#  no end date
	#    or
	#  specific date

			&$page_end();
		}
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

elsif ($action eq 'delete_event') {
	if ($logged_in) {
		my $event_id = $q->param('e');
		my $user_id = $q->cookie('VeloCalUserID');
		my $confirmed = $q->param('c') || 0;

		my $select = "
			select 
				g.group_id,
				name,
				title,
				start_time,
				location,
				pace,
				terrain,
				notes 
			from 
				events natural join 
				groups g
			where 
				event_id = $event_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($group_id,$group_name,$title,$start_time,$location,$pace,$terrain,$notes) = $qh->fetchrow_array();

		my ($date) = split / /, $start_time;
		my ($y,$m,$d) = split /-/, $date;
		my $dow = Day_of_Week_to_Text(Day_of_Week($y,$m,$d));

		my $authorized = 1;
		$select = "select count(*) from group_user where group_id = $group_id and user_id = $user_id";
		$qh = $dbh->prepare($select);
		$qh->execute();
		my ($count) = $qh->fetchrow_array();
		$authorized = 0 unless (defined $count);

		if ($authorized) {
			if ($confirmed == 1) {
				my $message = $q->param('message');
				# send email notification
				my %emails;
				my $select = "
					select 
						u.name_first,
						u.name_last,
						u.email 
					from 
						group_user natural join 
						users u 
					where 	
						group_id=$group_id and 
						notification='Y'";
				my $qh = $dbh->prepare($select);
				$qh->execute();
				while (my ($name_first,$name_last,$email) = $qh->fetchrow_array()) {
					$emails{$email} = "$name_first $name_last";
					$emails{$email} =~ s/(\s+)$//; # remove trailing space if no last name
				}

				$select = "select name from groups where group_id = $group_id";
				$qh = $dbh->prepare($select);
				$qh->execute();
				my ($group_name) = $qh->fetchrow_array();

				$select = "select name_last,name_first,email,hide_email from users where user_id = $user_id";
				$qh = $dbh->prepare($select);
				$qh->execute();
				my ($name_last,$name_first,$email,$hide_email) = $qh->fetchrow_array();

				($hide_email eq 'Y') ? ($email = '') : ($email = "&lt;$email&gt;");

				$notes =~ s/\n/<br>/g;

				# this will not scale well, but each email is customized
				foreach my $member_email (keys %emails) {
					open(MAIL,"| $sendmail -t");
					print MAIL "To: $emails{$member_email} <$member_email>\n";
					print MAIL "From: $registration_name <$registration_email>\n";
					print MAIL "Subject: $group_name Event :: $title\n";
					print MAIL "Content-type: text/html\n\n";
					print MAIL "Event deleted by $name_first $name_last $email<br>\n";
					print MAIL "Message: $message<br>\n";
					print MAIL "<br>\n";
					print MAIL "Group: $group_name<br>\n";
					print MAIL "Title: $title<br>\n";
					print MAIL "Start Time: $start_time ($dow)<br>\n";
					print MAIL "Location: $location<br>\n";
					print MAIL "Pace: $pace<br>\n";
					print MAIL "Terrain: $terrain<br>\n";
					print MAIL "Notes:<br>\n";
					print MAIL "<blockquote>$notes</blockquote>\n";
					print MAIL "This event has been cancelled.<br><br>\n\n";
					print MAIL "To view your ride calendar, click <a href=\"$script\">here</a><br>\n";
					close(MAIL);
				}

				# delete
				my $delete = "delete from events where event_id = $event_id";
				$qh = $dbh->prepare($delete);
				$qh->execute();

				# print confirmation message
				&$page_begin();

				print 
					h3("Delete Successful"),
					p("Your event was successfully deleted and all group members have been sent email notification");

				&$page_end();
			}
			else {
				&$page_begin();

				print 
					h3("Delete '$title'"),
					p("Please confirm that you would like to delete the event titled \"$title\". Optionally, provide a message that will be included with the email sent to all group members."),
					start_form({-action=>$script,-method=>'post'}),
					textarea({-name=>'message',-rows=>5,-cols=>60,-override=>1}),
					br(),
					hidden({-name=>'e',-value=>$event_id}),
					hidden({-name=>'a',-value=>'delete_event'}),
					hidden({-name=>'c',-value=>'1'}),
					br(),
					submit({-value=>'Delete'}),
					end_form();

				&$page_end();
			}
		}
		else {
			&$page_begin();
			print "Unauthorized access";
			&$page_end();
		}
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

elsif ($action eq 'att') {
	if ($logged_in) {
		my $event_id = $q->param('e');
		my $user_id_action = $q->param('u');
		my $comments = $q->param('comments');
		my $user_id = $q->cookie('VeloCalUserID');

		$comments = encode_entities($comments,'<>');

		my $select = "
			select 
				group_id
			from 
				events
			where 
				event_id = $event_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($group_id) = $qh->fetchrow_array();

		my $authorized = 1;
		$select = "select count(*) from group_user where group_id = $group_id and user_id = $user_id";
		$qh = $dbh->prepare($select);
		$qh->execute();
		my ($count) = $qh->fetchrow_array();

		$authorized = 0 unless (defined $count);

		if ($user_id_action ne $user_id) {
			$authorized = 0;
		}

		if ($authorized) {
			my $attend = $q->param('attend');

			$select = "select reminder_sent from event_user where event_id = $event_id and user_id = $user_id";
			$qh = $dbh->prepare($select);
			$qh->execute();
			my ($reminder_sent) = $qh->fetchrow_array();

			my $delete = "delete from event_user where event_id = $event_id and user_id = $user_id";
			$qh = $dbh->prepare($delete);
			$qh->execute();

			my $insert = "insert into event_user (event_id, user_id, status, comments, reminder_sent) values ($event_id,$user_id,'$attend',?,?)";
			$qh = $dbh->prepare($insert);
			$qh->execute($comments,$reminder_sent);

			print $q->redirect("$script?a=event&e=$event_id");
		}
		else {
			&$page_begin();
			print "Unauthorized access. Verify that the email address in event email matches the email address of the account you are logged into.";
			&$page_end();
		}
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

elsif ($action eq 'group_email') {
	if ($logged_in) {
		my $group_id = $q->param('g');
		my $user_id = $q->cookie('VeloCalUserID');

		my $authorized = 1;
		my $select = "select count(*) from group_user where group_id = $group_id and user_id = $user_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($count) = $qh->fetchrow_array();

		$authorized = 0 unless ($count > 0);

		if ($authorized) {
			$select = "select name from groups where group_id = $group_id";
			$qh = $dbh->prepare($select);
			$qh->execute();
			my ($group_name) = $qh->fetchrow_array();

			&$page_begin();

			print 
				h3("Send Group Email :: $group_name"),
				p(
					"Use the following form to send email to all members of the group '" .
					b($group_name) .
					"'."
				),
				start_form({-action=>$script,-method=>'POST'}),
				table(
					{-class=>'brown'},
					Tr(
						td('Subject'),
						td(input({-name=>'subject',-size=>60,-override=>1,-tabindex=>1}))
					),
					Tr(	
						td('Message'),
						td(
							textarea({-name=>'message',-rows=>5,-columns=>60,-override=>1,-tabindex=>2}),
							hidden({-name=>'a',-value=>'group_email_send',-override=>1}),
							hidden({-name=>'g',-value=>'group_id',-value=>$group_id,-override=>1})
						)
					),
					Tr(
						td('&nbsp;'),
						td(submit({-value=>'Send Group Email'}))
					)
				),
				end_form();
	
			&$page_end();
		}
		else {
			&$page_begin();
			print "Unauthorized access to group_email ($group_id:$user_id).";
			&$page_end();
		}
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

elsif ($action eq 'group_email_send') {
	if ($logged_in) {
		my $group_id = $q->param('g');
		my $user_id = $q->cookie('VeloCalUserID');

		my $authorized = 1;
		my $select = "select count(*) from group_user where group_id = $group_id and user_id = $user_id";
		my $qh = $dbh->prepare($select);
		$qh->execute();
		my ($count) = $qh->fetchrow_array();

		$authorized = 0 unless (defined $count);

		if ($authorized) {
			my $subject = $q->param('subject');
			my $message = $q->param('message');

			$message =~ s/\r//g;

			$select = "select name from groups where group_id = $group_id";
			$qh = $dbh->prepare($select);
			$qh->execute();
			my ($group_name) = $qh->fetchrow_array();

			&$page_begin();

			print 
				h3("Email Sent :: $group_name"),
				p(
					"The following email was sent to all members of '" .
					b($group_name) .
					"'."
				),
				hr(),
				pre(
					$subject .
					"\n\n" .
					$message
				);
	
			&$page_end();
	
			# send email to all group members
			my %emails;
			my $select = "
				select 
					u.name_first,
					u.name_last,
					u.email,
					u.user_id
				from 
					group_user natural join 
					users u 
				where 	
					group_id = $group_id";
			my $qh = $dbh->prepare($select);
			$qh->execute();
			while (my ($name_first,$name_last,$email,$user_id) = $qh->fetchrow_array()) {
				$emails{$email} = "$name_first $name_last";
				$emails{$email} =~ s/(\s+)$//; # remove trailing space if no last name
			}

			$select = "select name_last,name_first,email,hide_email from users where user_id = $user_id";
			$qh = $dbh->prepare($select);
			$qh->execute();
			my ($name_last,$name_first,$email,$hide_email) = $qh->fetchrow_array();

			($hide_email eq 'Y') ? ($email = '') : ($email = "&lt;$email&gt;");
			
			# this will not scale well, but each email is customized
			foreach my $member_email (keys %emails) {
				open(MAIL,"| $sendmail -t");
				print MAIL "To: $emails{$member_email} <$member_email>\n";
				print MAIL "From: $registration_name <$registration_email>\n";
				print MAIL "Subject: $group_name Message :: $subject\n";
				print MAIL "Content-type: text/html\n\n";
				print MAIL "Message from $name_first $name_last $email<br>\n";
				print MAIL "<br>\n";
				print MAIL "<blockquote><pre>\n";
				print MAIL "$subject\n";
				print MAIL "\n";
				print MAIL "$message";
				print MAIL "</pre></blockquote>\n";
				close(MAIL);
			}
		}
		else {
			&$page_begin();
			print "Unauthorized access to group_email ($group_id:$user_id).";
			&$page_end();
		}
	}
	else {
		my $redirect_url = $q->url({-path=>1,-query=>1});
		$redirect_url = escape($redirect_url);
		print $q->redirect("$script?a=login&redirect_url=$redirect_url");
	}
}

else {
	&$page_begin();
	print 'ERROR: unknown action';
	&$page_end();
}

1;
