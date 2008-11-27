#!/usr/bin/perl -w
use strict;
use lib qw(./lib ../lib);
use Test;

plan tests => 46;

# grid->lat/long test for GB module
# $Revision: 1.2 $

use Geography::NationalGrid;
ok(1);

my $point;

# 1. worked example from online refs
$point = new Geography::NationalGrid( 'GB',
	Easting => 651409.903,
	Northing => 313177.270,
	Userdata => { Name => 'Worked Example from east/north' },
);

ok( qeq($point->latitude, [52, 39, 27.25312]) );
ok( qeq($point->longitude, [1, 43, 4.51772]) );
ok( $point->gridReference() eq 'TG 514131' );
ok( $point->gridReference(1) eq 'TG 5140913177' );
ok( $point->gridReference(10) eq 'TG 51401317' );
ok( $point->gridReference(100) eq 'TG 514131' );
ok( $point->gridReference(1000) eq 'TG 5113' );

# 2. broadcasting house
comp( 'TQ 289006', '50d 47m 24.19s', '-0d 10m 15.69s');

# 3. origin
comp( 'sv000000', '49d 45m 58.27s', '-7d 33m 23.21s' );

# 4 Llanfair
$point = new Geography::NationalGrid( 'GB',
	Easting => 300100,
	Northing => 171600,
);
ok( qeq($point->latitude, '51d 26m 2.73s') );
ok( qeq($point->longitude, '-3d 26m 14.34s') );

comp( 'TQ 389773', '51d 28m 38.40s', '0d 0m 0s' ); # Greenwich
comp( 'NT 261745', '55d 57m 28.00s', '-3d 11m 2.00s' ); # Edinburgh
comp( 'SP 510071', '51d 45m 35.40s', '-1d 15m 39.00s' ); #Oxford
comp( 'TL 431595', '52d 12m 51.60s', '0d 5m 42.00s' ); #Cambridge
comp( 'NZ 269416', '54d 46m 6.20s', '-1d 34m 56.00s' ); #Durham
comp( 'SJ 287900', '53d 24m 5.40s', '-3d 4m 20.50s' ); #Liverpool

# arbitrary points follow
comp('TV 500998','50d 46m 40.03s', '0d 7m 40.20s');
comp('SM 600300', '51d 54m 58.61s', '-5d 29m 25.12s' );
comp('SC 200850', '54d 13m 43.90s', '-4d 45m 42.43s' );
comp('NR 700150', '55d 22m 29.85s', '-5d 37m 50.36s');
comp('NB 050050', '57d 56m 11.91s', '-6d 59m 6.71s' );
comp('HP 600010', '60d 41m 17.87s', '-0d 54m 4.53s' );
comp('NK 002543', '57d 34m 44.37s', '-1d 59m 47.96s' );
comp('NZ 003005', '54d 23m 59.37s', '-1d 59m 43.36s' );
comp('SP 500500', '52d 8m 44.21s', '-1d 16m 9.21s' );
comp('TG 450023', '52d 33m 46.45s ', '1d 36m 55.01s' );


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
	my $point = new Geography::NationalGrid( 'GB',
		GridReference => $grid
	);
	ok( qeq($point->latitude, $lat) );
	ok( qeq($point->longitude, $long) );
}

