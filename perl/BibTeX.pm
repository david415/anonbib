package BibTeX;
use Symbol 'qualify_to_ref';

%bibtex_prototypes = ('string' => 'p', 'preamble' => 'v', '_' => 'kp*');

sub parse_bibtex_key ($) {
  my($fh) = @_;
  $_ = <$fh> while ((/^\s+$/s || /^\s+%/) && !eof $fh);
  if (/^\s*([^"#%'(),={}\s]+)(.*)/s) {
    $_ = $2;
    lc($1);
  } else {
    print STDERR "no key at line $.\n";
    "";
  }
}

sub parse_bibtex_value ($$) {
  my($fh, $strings) = @_;
  my($data) = "";
  my($bracelevel, $line);
  
  # loop over concatenation
  while (1) {
    
    # loop over lines
    $_ = <$fh> while ((/^\s+$/s || /^\s+%/) && !eof $fh);
    s/^\s+//;
    if (eof $fh) {
      print STDERR "unexpected end of file\n";
      return $data;
    }
    
    # check type of thing
    if (/^\"(.*)/s) {
      $_ = $1;
      $bracelevel = 0;
      $line = $.;
      while (1) {
	if (!$bracelevel && /^([^{}\"]*)\"(.*)/s) {
	  $data .= $1;
	  $_ = $2;
	  last;
	} elsif ($bracelevel && /^([^{}]*\})(.*)/s) {
	  $data .= $1;
	  $_ = $2;
	  $bracelevel--;
	} elsif (/^([^{}]*\{)(.*)/s) {
	  $data .= $1;
	  $_ = $2;
	  $bracelevel++;
	} else {
	  $data .= $_;
	  die "end of file within quotes started at line $line" if eof $fh;
	  $_ = <$fh>;
	}
      }
      
    } elsif (/^\{(.*)/s) {
      $_ = $1;
      $bracelevel = 1;
      $line = $.;
      while ($bracelevel) {
	if (/^([^{}]*)\}(.*)/s) {
	  $data .= $1;
	  $data .= "}" if $bracelevel > 1;
	  $_ = $2;
	  $bracelevel--;
	} elsif (/^([^{}]*\{)(.*)/s) {
	  $data .= $1;
	  $_ = $2;
	  $bracelevel++;
	} else {
	  $data .= $_;
	  die "end of file within braces started at line $line" if eof $fh;
	  $_ = <$fh>;
	}
      }
      
    } elsif (/^\#/) {
      # do nothing
      print STDERR "warning: odd concatenation at line $.\n";
    } elsif (/^[\},]/) {
      print STDERR "no data after field at line $.\n" if $data eq '';
      return $data;
    } elsif (/^([^\s\},]+)(.*)/s) {
      if ($strings->{lc($1)}) {
	$data .= $strings->{lc($1)};
      } else {
	$data .= $1;
      }
      $_ = $2;
    }
    
    # got a single string, check for concatenation
    $_ = <$fh> while ((/^\s+$/s || /^\s+%/) && !eof $fh);
    s/^\s+//;
    if (/^\#(.*)/s) {
      $_ = $1;
    } else {
      return $data;
    }
  }
}

sub parse_bibtex_entry ($$$$) {
  # uses caller's $_
  my($fh, $name, $strings, $entries) = @_;
  my($entryline) = $.;
  
  $_ = <$fh> while /^\s+$/ && !eof $fh;
  if (/^\s*\{(.*)/s) {
    $_ = $1;
  } else {
    print STDERR "no open brace after \@$name starting at line $entryline\n";
    return [];
  }
  
  # get prototype
  my($prototype) = $bibtex_prototypes{$name};
  $prototype = $bibtex_prototypes{'_'} if !defined $prototype;
  
  # parse entry into `@v'
  my(@v, $a, $b);
  while (!eof $fh) {
    $_ = <$fh> while /^\s*$/ && !eof $fh;
    if (/^\s*\}(.*)/s) {
      $_ = $1;
      last;
    } elsif ($prototype =~ /^k/) {
      push @v, parse_bibtex_key($fh);
    } elsif ($prototype =~ /^v/) {
      push @v, parse_bibtex_value($fh, $strings);
    } elsif ($prototype =~ /^p/) {
      push @v, parse_bibtex_key($fh);
      $_ = <$fh> while /^\s+$/ && !eof $fh;
      s/^\s+\=?//;
      push @v, parse_bibtex_value($fh, $strings);
    }
    $_ = <$fh> while /^\s*$/ && !eof $fh;
    s/^\s*,?//;
    $prototype = substr($prototype, 1)
	if $prototype && $prototype !~ /^.\*/;
  }
  print STDERR "missing args to \@$name at line $.\n"
      if $prototype && $prototype !~ /^.\*/;
  
  # do something with entry
  if ($name eq 'string') {
    $strings->{$v[0]} = $v[1];
  } elsif ($name eq 'preamble') {
    # do nothing
  } else {
    my($key) = shift @v;
    $entries->{$key} = {@v};
    $entries->{$key}->{'_type'} = $name;
    $entries->{$key}->{'_key'} = $key;
    push @{$entries->{'_'}}, $key;
  }
}

sub parse (*;\%) {
  my($fh) = qualify_to_ref(shift, caller);
  my($initial_strings) = @_;
  my($strings) = $initial_strings;

  my($curname, $garbage, %entries);
  local($_) = '';
  while (<$fh>) {
    
    if (/^\s*[%\#]/ || /^\s*$/) {
      # comment
      
    } elsif (/^\s*\@([^\s\"\#%\'(),={}]+)(.*)/s) {
      $curname = lc($1);
      $_ = $2;
      parse_bibtex_entry($fh, $curname, $strings, \%entries);
      
    } else {
      print STDERR "garbage at line $.\n" if !defined $garbage;
      $garbage = 1;
    }
  }

  \%entries;
}

sub expand ($$) {
  my($e, $key) = @_;
  my(%d) = %{$e->{$key}};
  while ($d{'crossref'}) {
    my($v) = $d{'crossref'};
    delete $d{'crossref'};
    %d = (%{$e->{$v}}, %d);
  }
  \%d;
}


sub split_von ($$$@) {
  my($f, $v, $l, @x) = @_;
  my(@pre, $t, $in_von, $tt);
  while (@x) {
    $t = $tt = shift @x;
    if ($tt =~ /^\{\\/) {
      $tt =~ s/\\[A-Za-z@]+//g;
      $tt =~ s/\\.//g;
      $tt =~ tr/{}//d;
    }
    if ($tt =~ /^[a-z]/) {
      push @$v, $t;
      $in_von = 1;
    } elsif ($in_von || !ref($f)) {
      push @$l, $t, @x;
      return;
    } else {
      push @$f, $t;
    }
  }
  if (!$in_von) {
    push @$l, (pop @$f);
  }
}

sub parse_author ($) {
  local($_) = @_[0];
  my(@x) = ();
  my($pos, $pos0, $t, $bracelevel);
  
  # move text into @x
  while (!/^\s*$/) {
    s/^\s+//;
    $pos = 0;
    while ($pos < length) {
      $t = substr($_, $pos, 1);
      if ($t eq '{') {
	$bracelevel++;
      } elsif ($t eq '}') {
	$bracelevel--;
      } elsif ($bracelevel <= 0) {
	last if ($t =~ /[\s,]/);
      }
      $pos++;
    }
    
    push @x, substr($_, 0, $pos);
    if ($t eq ',') {
      push @x, ',';
      $pos++;
    }
    $_ = substr($_, $pos);
  }
  
  # split @x into arrays based on `and'
  my(@aa) = ([]);
  foreach $t (@x) {
    if ($t eq 'and') {
      push @aa, [] if @{$aa[-1]} > 0;
    } else {
      push @{$aa[-1]}, $t;
    }
  }
  
  # massage each subarray into four parts: first, von, last, jr
  my(@aaa) = ();
  foreach $t (@aa) {
    my(@fvl, @vl, @v, @l, @f, @j, $cur, $commas);
    $cur = \@fvl; $commas = 0;
    
    # split into subarrays if possible
    foreach $x (@$t) {
      if ($x eq ',') {
	if ($commas == 0) {
	  @vl = @fvl;
	  @fvl = ();
	  $cur = \@f;
	} else {
	  push @j, @f;
	  @f = ();
	}
	$commas++;
      } else {
	push @$cur, $x;
      }
    }
    
    # split out the `von' part
    if ($commas == 0) {
      split_von(\@f, \@v, \@l, @fvl);
    } else {
      split_von(0, \@v, \@l, @vl);
    }
    
    # store as an array of arrays
    push @aaa, [[@f], [@v], [@l], [@j]];
  }
  
  @aaa;
}

1;
