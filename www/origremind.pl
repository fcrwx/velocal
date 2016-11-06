#!/usr/bin/perl

use strict;

use DBI;
use HTML::Entities;
use Date::Calc qw(:all);

my $debug = 0;
my $db_dbi = 'mysql';
my $db_name = 'velocal';
my $db_username = 'velocal';
my $db_password = 'c\cl1ng';
my $sendmail = '/usr/sbin/sendmail';
my $registration_email = 'support@velocal.org';
my $registration_name = 'VeloCal Support';
my $script = "http://velocal.org/";

###

my $dbh = DBI->connect("DBI:$db_dbi:$db_name",$db_username,$db_password);

my $select = "
	select
		g.group_id,
		u.email,
		e.event_id,
		g.reminder_hours,
		date_sub(n.start_time, interval g.reminder_hours hour),
		now() + interval ifnull((truncate(timezone/100,0)*60) + (timezone - truncate(timezone/100,0)*100),0) minute,
		n.title,
		n.start_time,
		n.location,
		n.pace,
		n.terrain,
		n.distance,
		n.notes,
		r.name,
		e.status,
		e.comments,
		n.map_id,
		u.user_id
	from
		group_user g,
		event_user e,
		events n,
		groups r,
		users u
	where 
		u.user_id = e.user_id and
		g.user_id = u.user_id and
		n.start_time >= now() + interval ifnull((truncate(timezone/100,0)*60) + (timezone - truncate(timezone/100,0)*100),0) minute and
		e.reminder_sent != 'yes' and
		g.reminders = 'Y' and
		n.event_id = e.event_id and
		n.group_id = g.group_id and
		g.user_id = e.user_id and
		g.group_id = r.group_id";
my $qh = $dbh->prepare($select);
$qh->execute();

while (my ($group_id,$email,$event_id,$reminder_hours,$send_reminder,$now,$title,$start_time,$location,$pace,$terrain,$distance,$notes,$name,$status,$comments,$map_id,$user_id) = $qh->fetchrow_array()) {

	$send_reminder =~ s/(-|\s|:)//g;
	$now =~ s/(-|\s|:)//g;
	$status = '' if (not defined $status);

	my ($date,$time) = split / /, $start_time;
	my ($year,$month,$day) = split /-/, $date;
	my $dow = Day_of_Week_to_Text(Day_of_Week($year,$month,$day));

	print "event_id $event_id == send_reminder $send_reminder == $email status == $status\n" if $debug;

	if ($send_reminder <= $now) {
		print "DEBUG: time to send reminder to $email\n" if $debug;

		# make link to map if there is one
		my $map_select = "select name,url,image_filename from maps where id = $map_id";
		my $map_qh = $dbh->prepare($map_select);
		$map_qh->execute();
		my ($map_name,$map_url,$map_filename) = $map_qh->fetchrow_array();
		my $map_name_link;
		$map_name_link = "<a href=\"$script?a=get_image&t=maps&c=image&l=id&r=$map_id&f=image_filename&m=image_magick\">$map_name</a>" if ($map_filename ne '');
		$map_name_link = "<a href=\"$map_url\">$map_name</a>" if ($map_url ne '');
		$map_name_link = '&nbsp;' if ($map_name_link eq '');

		$notes =~ s/\n/<br>/g;

		use IO::File;
		my $fh;
		$fh = new IO::File "| $sendmail -t" unless $debug;
#		$fh = new IO::File "> debug.txt" unless $debug;

		print { $debug ? *STDOUT : $fh } "To: $email\n";
		print { $debug ? *STDOUT : $fh } "From: $registration_name <$registration_email>\n";
		print { $debug ? *STDOUT : $fh } "Subject: $name :: Event Reminder\n";
		print { $debug ? *STDOUT : $fh } "Content-type: text/html\n\n";
		print { $debug ? *STDOUT : $fh } "This is an automatic event reminder for the group '$name'<br><br>\n\n";
		print { $debug ? *STDOUT : $fh } "VeloCal supported by <a href='http://www.stackhousemortgage.com'>www.stackhousemortgage.com</a><br><br>\n\n";
		print { $debug ? *STDOUT : $fh } "Group Name: $name<br />\n";
		print { $debug ? *STDOUT : $fh } "Event Title: $title<br />\n";
		print { $debug ? *STDOUT : $fh } "Start Time: $start_time ($dow)<br />\n";
		print { $debug ? *STDOUT : $fh } "Location: $location<br />\n";
		print { $debug ? *STDOUT : $fh } "Map: $map_name_link<br />\n";
		print { $debug ? *STDOUT : $fh } "Pace: $pace<br />\n";
		print { $debug ? *STDOUT : $fh } "Terrain: $terrain<br />\n";
		print { $debug ? *STDOUT : $fh } "Distance: $distance<br />\n";
		print { $debug ? *STDOUT : $fh } "Notes:<br />\n";
		print { $debug ? *STDOUT : $fh } "<blockquote>$notes</blockquote>\n";
		if ($status ne '') {
			print { $debug ? *STDOUT : $fh } "You have already indicated your attendance intention as " . uc($status);
			if ($comments ne '') {
				print { $debug ? *STDOUT : $fh } " and have added the comments \"$comments\"";
			}
		}
		else {
			print { $debug ? *STDOUT : $fh } "You have not yet indicated your attendance intentions";
		}
		print { $debug ? *STDOUT : $fh } ".<br><br>\n\n";
		my $yes_url = encode_entities("$script?a=att&e=$event_id&u=$user_id&attend=yes");
		my $no_url = encode_entities("$script?a=att&e=$event_id&u=$user_id&attend=no");
		my $maybe_url = encode_entities("$script?a=att&e=$event_id&u=$user_id&attend=maybe");
		my $event_url = encode_entities("$script?a=event&e=$event_id");
		my $unsub_url = encode_entities("$script?a=unsubscribe&g=$group_id");
		print { $debug ? *STDOUT : $fh } "To view this event, click <a href=\"$event_url\">here</a><br>\n";
		print { $debug ? *STDOUT : $fh } "To mark your attendance as YES, click <a href=\"$yes_url\">here</a><br>\n";
		print { $debug ? *STDOUT : $fh } "To mark your attendance as NO, click <a href=\"$no_url\">here</a><br>\n";
		print { $debug ? *STDOUT : $fh } "To mark your attendance as MAYBE, click <a href=\"$maybe_url\">here</a><br>\n";
		print { $debug ? *STDOUT : $fh } "<br>\n";
		print { $debug ? *STDOUT : $fh } "If you would like to unsubscribe from this group and no longer receive these emails, click <a href=\"$unsub_url\">here</a><br>\n";

#		$fh->close() unless $debug;
		undef $fh unless $debug;

		# mark reminder as sent
		print "DEBUG: need to update event_user to flag reminder as sent\n" if $debug;
		my $update = "update event_user set reminder_sent = 'yes' where event_id = $event_id and user_id = $user_id";
		my $qh2 = $dbh->prepare($update);
		$qh2->execute() unless $debug;
	}
}

$dbh->disconnect();

1;
