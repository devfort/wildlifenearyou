#!/usr/bin/perl -w
use strict;
use lib qw(./lib ../lib);
use Test;

plan tests => 15;

# grid->lat/long test for IE module
# $Revision: 1.1 $

use Geography::NationalGrid;
ok(1);

comp( 'W 265410', '51d 37m 3.20s', '-9d 3m 40.71s' ); #Reanascreana from grid ref
comp( 'M 236004', '53d 2m 56.18s', '-9d 8m 21.80s' ); #Poulnabrone from grid ref

# arbitrary points follow
comp( 'M 500500', '53d 29m 51.45s', '-8d 45m 12.65s');
comp( 'V 000000', '51d 13m 8.32s', '-10d 51m 47.26s');
comp( 'A 000999', '55d 42m 14.11s', '-11d 10m 55.67s');
comp( 'D 999999', '55d 42m 14.26s', '-4d 49m 10.05s');
comp( 'Y 999000', '51d 13m 8.45s', '-5d 8m 17.89s');

sub qeq {
	my $rv = 0;
	
	my $i = Geography::NationalGrid->deg2rad($_[0]);
	my $j = Geography::NationalGrid->deg2rad($_[1]);
	
	if (abs($i - $j) < 0.000007) {
		$rv = 1;
	} else {
		warn "# got $i, expecting $j, difference " . ($i - $j);
	}
	return $rv;
}

sub comp {
	my ($grid, $lat, $long) = @_;
	my $point = new Geography::NationalGrid( 'IE',
		GridReference => $grid
	);
	ok( qeq($point->latitude, $lat) );
	ok( qeq($point->longitude, $long) );
}

