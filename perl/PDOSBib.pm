package main;

# maps regexps, which are applied to authors, to their home page URLs
@author_urls =
    ('Engler' => 'http://www.pdos.lcs.mit.edu/~engler/',
     'Kaashoek' => 'http://www.pdos.lcs.mit.edu/~kaashoek/',
     'Blake' => 'http://www.pdos.lcs.mit.edu/cb/',
     'Mazi&egrave;res' => 'http://www.scs.cs.nyu.edu/~dm/',
     'Ganger' => 'http://www.ece.cmu.edu/~ganger/',
     'Grimm' => 'http://www.cs.washington.edu/homes/rgrimm/',
     'Hsieh' => 'http://www2.cs.utah.edu/~wilson/',
     'Brice&ntilde;o' => 'http://mit.edu/hbriceno/www/',
     'Wallach' => 'http://www.pdos.lcs.mit.edu/~kerr/',
     'Candea' => 'http://www.cs.stanford.edu/~candea/',
     'Kohler' => 'http://www.pdos.lcs.mit.edu/~eddietwo/',
     'Kirk.*Johnson' => 'http://www.cs.colorado.edu/~tuna/',
     'Weihl' => 'http://www.research.digital.com/SRC/staff/weihl/',
     'Nygren' => 'http://www.mit.edu/people/nygren/',
     'Anthony.*Joseph' => 'http://www.cs.berkeley.edu/~adj/',
     'Poletto' => 'http://www.pdos.lcs.mit.edu/~maxp/',
     'Kaminsky' => 'http://www.pdos.lcs.mit.edu/~kaminsky/',
     'Morris' => 'http://www.pdos.lcs.mit.edu/~rtm/',
     'Jannotti' => 'http://www.jannotti.com/',
     'Benjie' => 'http://www.pdos.lcs.mit.edu/~benjie/',
     'Jinyang' => 'http://www.pdos.lcs.mit.edu/~jinyang/',
     'Douglas.*outo' => 'http://www.pdos.lcs.mit.edu/~decouto/',
     'Kevin.*Fu' => 'http://snafu.fooworld.org/~fubob/',
     'Karger' => 'http://theory.lcs.mit.edu/~karger/',
     'Dabek' => 'http://pdos.lcs.mit.edu/~fdabek/',
     'Brunskill' => 'http://pdos.lcs.mit.edu/~emma/',
     'Balakrishnan' => 'http://nms.lcs.mit.edu/~hari/',
     'Stoica' => 'http://www.cs.berkeley.edu/~istoica/',
     'Andersen' => 'http://nms.lcs.mit.edu/~dga/',
     'Snoeren' => 'http://nms.lcs.mit.edu/~snoeren/',
     'Freedman' => 'http://www.pdos.lcs.mit.edu/~mfreed/',
     'Emil.*Sit' => 'http://www.mit.edu/~sit/',
     'Nick.*Feamster' => 'http://nms.lcs.mit.edu/~feamster/',
     );

# don't print entries for these types, which are only used for crossreferences
%dont_print =
    ('proceedings' => 1, 'journal' => 1);

%initial_strings =
    ('jan' => 'January',	'feb' => 'February',
     'mar' => 'March',		'apr' => 'April',
     'may' => 'May',		'jun' => 'June',
     'jul' => 'July',		'aug' => 'August',
     'sep' => 'September',	'oct' => 'October',
     'nov' => 'November',	'dec' => 'December');


sub dont_print ($) {
  my($d) = @_;
  $dont_print{$d->{'_type'}} || ($d->{'www_show'} eq 'no');
}

sub htmlize ($) {
  my($x) = @_;
  $x =~ s/&([^a-z0-9])/&amp;$1/g;
  $x =~ s/\\i([^a-zA-Z@])/i$1/g;
  $x =~ s/\\'(.)/&$1acute;/g;
  $x =~ s/\\`(.)/&$1grave;/g;
  $x =~ s/\\~(.)/&$1tilde;/g;
  $x =~ s/\\\^(.)/&$1circ;/g;
  $x =~ s/\\"(.)/&$1uml;/g;
  $x =~ s/\\[a-zA-Z@]+//g;
  $x =~ s/\\.//g;
  $x =~ tr/{}//d;
  $x =~ s/(\d)--(\d)/$1-$2/g;
  $x;
}

sub htmlize_author ($) {
  my($aaa) = @_;
  my($x) = join(' ', @{$aaa->[0]}, @{$aaa->[1]}, @{$aaa->[2]});
  if (@{$aaa->[3]}) {
    $x .= ', ' . join(' ', @{$aaa->[3]});
  }
  htmlize($x);
}

sub push_availability ($$\@$) {
  my($d, $key, $availability, $name) = @_;
  if ($d->{$key}) {
    my($url) = $d->{$key};
    $url = $server_url . $url if $url =~ /^\//;
    push @$availability, '<a href="' . $url . '">' . $name . '</a>';
  }
}

sub htmlize_biblio_info ($) {
  my($d) = @_;
  my($_type) = $d->{'_type'};
  my($x, $i);
  
  if ($_type eq 'inproceedings') {
    $x = "In the " . $d->{'booktitle'};
    if ($d->{'bookurl'}) {
      if ($x =~ /^(in the proceedings of( the)? )(.*)/i
	  || $x =~ /^(in the workshop record of( the)? )(.*)/i) {
	$x = $1 . "<a href=\"$d->{'bookurl'}\">" . $3 . "</a>";
      } else {
	$x = "In the <a href=\"$d->{'bookurl'}\">$d->{'booktitle'}</a>";
      }
    }
    $x .= ", " . $d->{'edition'} if $d->{'edition'};
    $x .= ", " . $d->{'address'} if $d->{'address'};
    $x .= ", " . $d->{'month'} . " " . $d->{'year'}
       if $d->{'month'} || $d->{'year'};
    $x .= ($d->{'pages'} =~ /^\d+$/ ? ", page&nbsp;" : ", pages&nbsp;")
	. $d->{'pages'} if $d->{'pages'};
    
  } elsif ($_type eq 'article') {
    $x = "In " . $d->{'journal'};
    if ($d->{'journalurl'}) {
      $x =~ s/^(in )(.*)$/$1<a href="$d->{'journalurl'}">$2<\/a>/;
    }
    $x .= " <b>" . $d->{'volume'} . "</b>" if $d->{'volume'};
    $x .= "(" . $d->{'number'} . ")" if $d->{'number'};
    $x .= ", " . $d->{'month'} . " " . $d->{'year'}
       if $d->{'month'} || $d->{'year'};
    $x .= ($d->{'pages'} =~ /^\d+$/ ? ", page&nbsp;" : ", pages&nbsp;")
	. $d->{'pages'} if $d->{'pages'};
    
  } elsif ($_type eq 'techreport') {
    $x = $d->{'institution'};
    $x .= " " . ($d->{'type'} ? $d->{'type'} : "technical report");
    $x .= " " . $d->{'number'};
    $x .= ", " . $d->{'month'} . " " . $d->{'year'}
       if $d->{'month'} || $d->{'year'};
    
  } elsif ($_type eq 'mastersthesis' || $_type eq 'phdthesis') {
    $x = ($_type eq 'mastersthesis' ? "Master's thesis" : "Ph.D. thesis");
    $x = $d->{'type'} if $d->{'type'};
    $x .= ", " . $d->{'school'} if $d->{'school'};
    $x .= ", " . $d->{'month'} . " " . $d->{'year'}
       if $d->{'month'} || $d->{'year'};
    
  } elsif ($_type eq 'misc') {
    $x = $d->{'howpublished'};
    $x .= ", " . $d->{'month'} . " " . $d->{'year'}
       if $d->{'month'} || $d->{'year'};
    $x .= ($d->{'pages'} =~ /^\d+$/ ? ", page&nbsp;" : ", pages&nbsp;")
	. $d->{'pages'} if $d->{'pages'};
    
  } else {
    $x = "&lt;odd type $_type&gt;";
  }
  
  $x = '<span class="biblio">' . $x . ".</span> ";
  $x .= "<span class=\"availability\">(<a href=\"$cgi_dir/bibtex-entry.cgi?key=";
  $x .= $d->{'_key'} . "\">BibTeX&nbsp;entry</a>)</span>";
  htmlize($x);
}

sub htmlize_entry ($) {
  my($d) = @_;
  my(@availability, @a, $a, $i, $j, $x);
  
  # print title
  $x .= '<li><p class="entry"><span class="title">' . htmlize($d->{'title'}) . ".</span>";
  
  # print availability
  @availability = ();
  push_availability $d, 'www_abstract_url', @availability, 'abstract';
  push_availability $d, 'www_html_url', @availability, 'HTML';
  push_availability $d, 'www_pdf_url', @availability, 'PDF';
  push_availability $d, 'www_ps_url', @availability, 'PS';
  push_availability $d, 'www_ps_gz_url', @availability, 'gzipped&nbsp;PS';
  if (@availability) {
    $x .= ' <span class="availability">(';
    $x .= join(',&nbsp;', @availability) . ")</span>";
  }
  $x .= "<br>\n";
  
  # print authors
  $x .= '<span class="author">by ';
  @a = BibTeX::parse_author($d->{'author'});
  foreach $i (0..$#a) {
    $x .= ", " if ($i > 0 && $i < $#a);
    $x .= " and " if ($i == $#a && $#a == 1);
    $x .= ", and " if ($i == $#a && $#a > 1);
    $a = htmlize_author($a[$i]);
    for ($j = 0; $j < @author_urls; $j += 2) {
      if ($a =~ /$author_urls[$j]/) {
	$x .= '<a href="' . $author_urls[$j+1] . '">' . $a . '</a>';
	undef $a;
	last;
      }
    }
    $x .= $a if defined $a;
  }
  $x .= "." if $a !~ /\.$/;
  $x .= "</span><br>\n";
  
  $x .= htmlize_biblio_info($d);
  $x .= "</p></li>\n\n";
  
  $x;
}


sub url_untranslate ($) {
  my($x) = $_[0];
  $x =~ s/ /+/g;
  $x =~ s/([%<>])/sprintf("%02x", chr($1))/eg;
  $x;
}

1;
