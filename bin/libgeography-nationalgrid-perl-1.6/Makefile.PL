use ExtUtils::MakeMaker;

# $Id: Makefile.PL,v 1.2 2002/09/26 01:31:57 piers Exp $

WriteMakefile(
	AUTHOR		=> 'P Kent (pause@selsyn.co.uk)',
	ABSTRACT	=> 'Convert national grid references to/from lat/long',
	NAME		=> 'Geography::NationalGrid',
	DISTNAME	=> 'Geography-NationalGrid',
	dist		=> {
		COMPRESS	=> 'gzip',
		SUFFIX		=> '.gz',
	},
	VERSION_FROM	=> 'lib/Geography/NationalGrid.pm',
	PREREQ_PM	=> {
			},
);

