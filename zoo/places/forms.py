
from django.forms import ModelForm
from zoo.forms import UberForm
from zoo.places.models import Place, Enclosure, EnclosureSpecies, PlaceOpening


class EnclosureSpeciesEditForm(ModelForm):
    class Meta:
        model = EnclosureSpecies
        fields = ['number_of_inhabitants', 'species']

class EnclosureEditForm(ModelForm):
    class Meta:
        model = Enclosure
        fields = ['name']

class PlaceEditForm(ModelForm):
    class Meta:
        model = Place
        fields = ['known_as', 'legal_name', 'description', 'url',
                  'country']

class PlaceOpeningEditForm(ModelForm):
    class Meta:
        model = PlaceOpening
        fields = ['start_date', 'end_date', 'days_of_week']

# UBER FORMS!

class PlaceUberForm(UberForm):
    model = Place
    parts = [
        ('main', PlaceEditForm),
        ('enclosure', lambda instance: instance.enclosures.all()),
        ('openings', lambda instance: instance.placeopening_set.all()),
        ]

class PlaceOpeningUberForm(UberForm):
    model = PlaceOpening
    parts = [
        ('main', PlaceOpeningEditForm),
        ]

class EnclosureUberForm(UberForm):
    model = Enclosure
    parts = [
        ('main', EnclosureEditForm),
        ('enc_species', lambda instance: instance.enclosurespecies_set.all()),
        ]

class EnclosureSpeciesUberForm(UberForm):
    model = EnclosureSpecies
    parts = [
        ('main', EnclosureSpeciesEditForm),
        ]

    
