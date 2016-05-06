#!/usr/bin/perl
#
# CGI script to create image using RRD graph 
use CGI qw(:all);
use RRDs;
use POSIX qw(locale_h);

$ENV{'LANG'}='de_DE.UTF-8';
setlocale(LC_ALL, 'de_DE.UTF-8');

# path to database
$rrd='../../water-counter/water.rrd';

# force to always create image from rrd 
#$force=1;

$query=new CGI;
#$query=new CGI("type=consumweek&size=small");

$size=$query->param('size');
$type=$query->param('type');
if ($size eq 'big') {
  $width=900;
  $height=700;
  $size="b";
} else {
  $width=500;
  $height=160;
  $size="s";
}
die "invalid type\n" unless $type =~ /(count|consum)(day|week|month|year)/; 
$ds=$1;
$range=$2;
$filename="/tmp/wai${type}_${size}.png";

# create new image if existing file is older than rrd file
my $maxdiff = 10;
if ((mtime($rrd) - mtime($filename) > $maxdiff) or $force) {
  $tmpfile="/tmp/wai${type}_${size}_$$.png";
  # call sub to create image according to type
  &$ds($range);
  # check error
  my $err=RRDs::error;
  die "$err\n" if $err;
  rename $tmpfile, $filename;
}

# feed image to stdout
open(IMG, $filename) or die "can't open $filename";
print header('image/png');
print <IMG>;
close IMG;

# end MAIN

# Return modification date of file
sub mtime {
  my $file=shift;
  my ($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$fsize,
       $atime,$mtime,$ctime,$blksize,$blocks)
           = stat($file);
  return $mtime;
}

sub count {
  my $range = shift;
  my @opts=(
    "-w", $width,
    "-h", $height,
    "-s", "now - 1 $range",
    "-e", "now",
    "-D",
    "-Y",
    "-A");
  RRDs::graph($tmpfile,
    @opts,
    "DEF:counter=$rrd:counter:LAST",
    "LINE2:counter#000000:Zähler",
    "VDEF:countlast=counter,LAST",
    "GPRINT:countlast:%.3lf m³"
  );
}

sub consum {
  my $range = shift;
  my @opts=(
    "-w", $width,
    "-h", $height,
    "-D",
    "-Y",
    "-A",
    "-e", "now",
    "-s"
    );
  if ($range eq 'month') {
    push(@opts, "now - 30 days");
  } else {
    push(@opts, "now - 1 $range");
  }
  
  if ($range eq 'day') {
    RRDs::graph($tmpfile,
      @opts,
      "DEF:consum=$rrd:consum:AVERAGE",
      "CDEF:conlpmin=consum,60000,*",
      "CDEF:conlpd=conlpmin,60,*,24,*",
      "VDEF:conlpdtotal=conlpd,AVERAGE",
      "GPRINT:conlpdtotal:Total %4.0lf l/d",
      "LINE2:conlpmin#00FF00:Verbrauch [l/min]" 
    );
  } else {
    RRDs::graph($tmpfile,
      @opts,
      "DEF:consum=$rrd:consum:AVERAGE",
      "CDEF:conlpd=consum,60000,*,60,*,24,*",
      "LINE2:conlpd#00FF00:l/d"
    );
  }
}
