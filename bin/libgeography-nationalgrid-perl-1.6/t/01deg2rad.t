#!/usr/bin/perl -w
use strict;
use lib qw(./lib ../lib);
use Test;

plan tests => 421;

use Geography::NationalGrid;

# as the degrees -> radians convertor is so important and used so often, I've tested it separately
# $Revision: 1.1 $

for my $x (-30 .. 30) {
	my $exp = Geography::NationalGrid::PI * $x / 1800;
	my $rv = Geography::NationalGrid::deg2rad( '', $x/10 );
	if (abs($rv - $exp) < 0.0000001) {	# they agree by a micro-radian
		ok(1);
	} else {
		ok(0);
		warn "rv was $rv expecting $exp";
	}
}

for my $deg (-2 .. 2) {
	for my $min (0 .. 5) {
		for my $sec (0 .. 5) {
			my $r1 = Geography::NationalGrid::deg2rad( '', "${deg}d " . ($min*10) . 'm ' . ($sec*10) . 's' );
			my $r2 = Geography::NationalGrid::deg2rad( '', [$deg, $min*10, $sec*10] );
			my $r3 = Geography::NationalGrid::deg2rad( '', (abs($deg) + $min/6 + $sec/360) )*(($deg<0)?-1:1);
			ok($r1 == $r2);
			ok($r1 == $r3);
		}
	}
}

# End of test