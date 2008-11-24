#!/usr/bin/env python

import os
import sys

sys.path.insert(0, os.path.join('zoo', 'ext'))
sys.path.insert(0, os.path.join('.'))

import sys
import random
import datetime

from zoo import settings
from django.core.management import setup_environ
setup_environ(settings)

from pygen import generate_string
from pygen import StringTerminal as S
from pygen import Alternation as A

from django.contrib.auth.models import User
from zoo.animals.models import Species, SpeciesGroup
from zoo.places.models import Place, Enclosure, EnclosureSpecies, Country

user = User.objects.get(username='sedf')

from django.template.defaultfilters import slugify

def main():
    place = A("London", "Birmingham", "Coventry", "Alderney", "Loch Ness", "Springfield", "Huddersfield", "England", "Bournemouth")
    zootype = A("Petting ", "City ", "", "German ", "Yellow ", "Broke ", "Friendly ", "Confident ", "Burnin' ")
    ending = A("Animal Shelter", "Zoo", "Farm", "Abattoir", "Asylum", "House", "Campsite", "Commune", "Cockfighting Ring")
    zooname = place, " ", zootype, ending

    address_1 = 'No. ', A(range(10)), ' ', S('New') | S('Old'), ' ', A('Avenue', 'Street', 'Road', 'Crescent')
    address_2 = A('New', 'Old'), A('town', 'shire')

    g_enclosure = A("Pen", "Cage", "Plains", "Tunnel", "Nest", "Enclosure", "Aquarium", "Pocket")

    start = A("Dung", "Sea", "Land", "Air", "Amphibuous", "Snake", "Dwarf", "Lesser-spotted")
    ending = A("lion", "beetle", "bird", "dolphin", "fucking narwhal", "dwarf", "wolf")
    speshul_ending = A(*([""] * 19) + [" on a plane"])
    g_species = start, " ", ending, speshul_ending

    species_groups = []
    for name in ('Fish', 'Tigers', 'Cute things', 'Lolcats', 'Badass animals'):
        species_groups.append(SpeciesGroup.objects.create(name=name))

    species = []
    for a_idx in range(100):
        name = generate_string(g_species)
        species.append(Species.objects.create(
            common_name=name,
            latin_name=' '.join(["%sus" % x for x in name.split(' ')]),
            slug="%s%s" % (slugify(name), random.random()),
            species_group=random.choice(species_groups),
        ))

    for p_idx in range(100):
        name = generate_string(zooname)
        place = Place.objects.create(
            known_as=name,
            slug="%s%s" % (slugify(name), random.random()),
            legal_name=generate_string([name, A('', ' Plc.', ' Ltd.', ' and Son', ' Inc.', ' and Rendering Plant')]),
            address_line_1=generate_string(address_1),
            address_line_2=generate_string(address_2),
            country=random.choice(Country.objects.all()),
            town='Town',
            zip='Zip',
            created_at=datetime.datetime.now(),
            modified_at=datetime.datetime.now(),
        )

        for e_idx in range(random.randrange(0, 15)):
            enclosure = Enclosure.objects.create(
                place=place,
                name=generate_string(g_enclosure),
            )

            for ea_idx in range(random.randrange(0, 15)):
                EnclosureSpecies.objects.create(
                    enclosure=enclosure,
                    species=random.choice(species),
                    number_of_inhabitants=random.randrange(0, 250),
                    modified_at=datetime.datetime.now(),
                    modified_by=user,
                )

    return 0

if __name__ == "__main__":
    sys.exit(main())
