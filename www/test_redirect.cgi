#!/usr/bin/perl -w

use strict;

use CGI qw/:all/;

my $q = new CGI;
my $script = $q->url();
my $action = $q->param("action") || "main";

if ($action eq 'main') {
	print "Content-type: text/html\n\n";
	print "main page<br><br>\n";
	print a({-href=>"$script?action=test"},"test");
}

elsif ($action eq "test") {

	print $q->redirect("$script?action=done");

	open (FILE, ">log.log");
	print FILE `date`;
	print FILE "started\n";

	for (my $i = 0; $i < 80; $i++) {
		sleep(5);
	}

#	print $q->redirect("$script?action=done");

	print FILE `date`;
	print FILE "ended\n";
	close FILE;
}

elsif ($action eq "done") {
	print "Content-type: text/html\n\n";
	print "done<br><br>\n";
	print a({-href=>"$script?action=main"},"main");
}

else {
	print "Content-type: text/html\n\n";
	print "Oops<br><br>\n";
}

