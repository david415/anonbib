package main;

#####
# SERVER DATA

$server_url = "http://www.pdos.lcs.mit.edu";
$img_dir = "/img";
$cgi_dir = "/cgi-bin";
$main_dir = ""; # == top dir
$css_dir = "";  # == top dir
$pdos_bib_dir = "/home/am0/httpd/htdocs/pdosbib";


#####
# ERROR_EXIT
# &error_exit($title, $message...) prints an HTML document summarizing the
# error and exits.

sub error_exit ($@) {
  my($title) = $_[0];
  my($message) = join('', @_[1..$#_]);
  print <<"EOD;";
Content-type: text/html

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2//EN">
<html><head><title>PDOS CGI Error</title></head>
<body>

<h1>$title</h1>

<p>$message

<p><a href="$server_url">PDOS home page</a>

</body>
</html>
EOD;
  exit 0;
}

#####
# HTTP_DATE
# Given a time value (seconds since 00:00:00 UTC, Jan 1, 1970), formats an
# HTTP date and returns it. Useful for Expires:.

@PDOSCGI::weekdays = ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat');
@PDOSCGI::months =   ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
	     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec');

sub http_date ($) {
  my($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) =
      gmtime($_[0]);
  sprintf("%s, %02d %s %d %02d:%02d:%02d GMT",
	  $PDOSCGI::weekdays[$wday], $mday, $PDOSCGI::months[$mon],
	  $year, $hour, $min, $sec);
}

#####
# URL_TRANSLATE

sub url_translate ($) {
  my($x) = $_[0];
  $x =~ s/\+/ /g;
  $x =~ s/%(\w\w)/pack('C', hex($1))/eg;
  $x;
}

1;
