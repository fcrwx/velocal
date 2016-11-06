#!/usr/bin/perl

use strict;

use CGI qw/:all -nosticky -oldstyle_urls *table *Tr *td *div *ul escape *blockquote *p *center/;
my $q = new CGI;

print
	header(),
	start_html(
		-title => 'VeloCal Under Maintenance',
		-bgcolor => 'white',
		-text => 'black',
		-link => 'blue',
		-vlink => 'blue',
		-alink => 'red',
		-marginheight => 0,
		-marginwidth => 0,
		-leftmargin => 0,
		-topmargin => 0,
		-style=>{-src=>'maint.css'},
	);

print
	div(
		{-id=>'wrap'},
		div(
			{-id=>'logo'},
			img({-alt=>'VeloCal Logo',-src=>'http://nicola.textdrive.com/~velocal/images/velocal.png'})
		),
		hr(),
		div(
			{-id=>'content'},
			h1('Oops!'),
			p('You caught us undergoing some maintenance. Please check back soon, or you can visit us at the following, not-so-friendly URL: ', a({-href=>'http://nicola.textdrive.com/~velocal'},'http://nicola.textdrive.com/~velocal'), '.'),
			div({-class=>'clear'})
		),
		hr(),
		div(
			{-id=>'footer'},
			p(
				"&#169; Copyright 2006 Karl Olson",
# &#183; VeloCal&#8482; is a trademark of Karl Olson",
				br(),
				a({-href=>'mailto:karl.olson@gmail.com'},"Support")
			)
		)
	);

print
	end_html();


