#!/usr/bin/perl -w
use strict;
use lib qw(./lib ../lib);
use Test;

plan tests => 8;

# lat/long->grid test for IE module
# $Revision: 1.1 $

use Geography::NationalGrid;
ok(1);

comp( '51d 37m 0.92s', '-9d 3m 40.53s', 'W 265410' ); #Reanascreana from lat/long
comp( '53d 2m 55.84s', '-9d 8m 21.65s', 'M 236004' ); #Poulnabrone from lat/long

# arbitrary points follow
comp( '53d 29m 51.45s ', ' -8d 45m 12.65s', 'M 500500' );
comp( '51d 13m 6.32s ', ' -10d 51m 47.26s', 'V 000000' );
comp( '55d 42m 14.11s ', ' -11d 10m 55.67s', 'A 000999' );
comp( '55d 42m 14.26s ', ' -4d 49m 10.05s', 'D 999999' );
comp( '51d 13m 6.45s ', ' -5d 8m 17.89s', 'Y 999000' );


sub comp {
	my ($lat, $long, $grid) = @_;
	my $point = new Geography::NationalGrid( 'IE',
		Latitude => $lat,
		Longitude => $long,
	);
	my $gr = $point->gridReference;
	if ($gr eq $grid) {
		ok(1);
	} else {
		warn "# Got '$gr' expecting '$grid'";
		ok(0);
	}
}
