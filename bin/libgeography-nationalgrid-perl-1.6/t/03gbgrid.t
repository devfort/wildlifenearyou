#!/usr/bin/perl -w
use strict;
use lib qw(./lib ../lib);
use Test;

plan tests => 21;

# lat/long->grid test for GB module
# $Revision: 1.1 $

use Geography::NationalGrid;
ok(1);

# 1. worked example from online refs
comp( [52, 39, 27.25312], [1, 43, 4.51772], 'TG 514132' );

# 2. broadcasting house
comp( '50d 47m 24.19s', '-0d 10m 15.69s', 'TQ 289006' );

# 3. origin
comp('49d 45m 58.27s', '-7d 33m 23.21s', 'SV 000000');

# 4 Llanfair
comp( '51d 26m 2.73s',  '-3d 26m 14.34s', 'ST 001716');

comp( '51d 28m 38.40s', '0d 0m 0s', 'TQ 389773'); # Greenwich
comp( '55d 57m 28.00s', '-3d 11m 3.00s', 'NT 261745'); # Edinburgh

comp( '51d 45m 35.40s', '-1d 15m 39.00s', 'SP 510071' ); #Oxford
comp( '52d 12m 51.60s', '0d 5m 42.00s', 'TL 431595' ); #Cambridge
comp( '54d 46m 6.20s', '-1d 34m 56.00s', 'NZ 269416' ); #Durham
comp( '53d 24m 5.40s', '-3d 4m 20.50s', 'SJ 287900' ); #Liverpool


# arbitrary points follow
comp( '50d 46m 40.03s', '0d 7m 40.20s' , 'TV 500998');
comp( '51d 54m 58.61s', '-5d 29m 25.12s' , 'SM 600300');
comp( '54d 13m 43.90s',  '-4d 45m 42.43s', 'SC 200850' );
comp( '55d 22m 29.85s', '-5d 37m 50.36s' , 'NR 700150');
comp( '57d 56m 11.91s', '-6d 59m 6.71s' , 'NB 050050');
comp( '60d 41m 17.87s', '-0d 54m 4.53s' , 'HP 600010');
comp( '57d 34m 44.37s', '-1d 59m 47.96s' , 'NK 002543');
comp( '54d 23m 59.37s',  '-1d 59m 43.36s', 'NZ 003005');
comp( '52d 8m 44.21s',  '-1d 16m 9.21s', 'SP 500500');
comp( '52d 33m 46.45s ', '1d 36m 55.01s' , 'TG 450023');

sub comp {
	my ($lat, $long, $grid) = @_;
	my $point = new Geography::NationalGrid( 'GB',
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
