#!/usr/bin/perl -w
                
use strict;

my $from_email_address = 'support@velocal.org';
my $from_email_name = "VeloCal Support";
my $from_email = "$from_email_name <$from_email_address>";

my $to_email = 'Karl Olson <karl.olson@gmail.com>';
#my $to_email = 'jerryk2007 <jerryk2007@mchsi.com>';

my $sendmail = "/usr/sbin/sendmail";
my $sendmail_options = "";

my $email_pattern = "";


# email A
# 
# from      set
# reply-to  set
# -f        undefined
#
$sendmail_options = "-t";
$email_pattern = "A";

open(MAIL,"| $sendmail $sendmail_options");
print MAIL "To: $to_email\n";
print MAIL "From: $from_email\n";
print MAIL "Reply-to: $from_email\n";
print MAIL "Subject: email $email_pattern\n";
print MAIL "Content-type: text/html\n\n";
print MAIL "This is email $email_pattern\n";
close(MAIL);

print "email $email_pattern sent\n";


# email B
# 
# from      set
# reply-to  undefined
# -f        undefined
#
$sendmail_options = "-t";
$email_pattern = "B";

open(MAIL,"| $sendmail $sendmail_options");
print MAIL "To: $to_email\n";
print MAIL "From: $from_email\n";
print MAIL "Subject: email $email_pattern\n";
print MAIL "Content-type: text/html\n\n";
print MAIL "This is email $email_pattern\n";
close(MAIL);

print "email $email_pattern sent\n";


# email C
# 
# from      undefined
# reply-to  set 
# -f        undefined
#
$sendmail_options = "-t";
$email_pattern = "C";

open(MAIL,"| $sendmail $sendmail_options");
print MAIL "To: $to_email\n";
print MAIL "Reply-to: $from_email\n";
print MAIL "Subject: email $email_pattern\n";
print MAIL "Content-type: text/html\n\n";
print MAIL "This is email $email_pattern\n";
close(MAIL);

print "email $email_pattern sent\n";


# email D
# 
# from      undefined
# reply-to  undefined
# -f        undefined
#
$sendmail_options = "-t";
$email_pattern = "D";

open(MAIL,"| $sendmail $sendmail_options");
print MAIL "To: $to_email\n";
print MAIL "Subject: email $email_pattern\n";
print MAIL "Content-type: text/html\n\n";
print MAIL "This is email $email_pattern\n";
close(MAIL);

print "email $email_pattern sent\n";


# email E
# 
# from      undefined
# reply-to  set
# -f        set
#
$sendmail_options = "-t -f $from_email_address";
$email_pattern = "E";

open(MAIL,"| $sendmail $sendmail_options");
print MAIL "To: $to_email\n";
print MAIL "Reply-to: $from_email\n";
print MAIL "Subject: email $email_pattern\n";
print MAIL "Content-type: text/html\n\n";
print MAIL "This is email $email_pattern\n";
close(MAIL);

print "email $email_pattern sent\n";



# email F
# 
# from      undefined
# reply-to  undefined
# -f        set
#
$sendmail_options = "-t -f $from_email_address";
$email_pattern = "F";

open(MAIL,"| $sendmail $sendmail_options");
print MAIL "To: $to_email\n";
print MAIL "Subject: email $email_pattern\n";
print MAIL "Content-type: text/html\n\n";
print MAIL "This is email $email_pattern\n";
close(MAIL);

print "email $email_pattern sent\n";














