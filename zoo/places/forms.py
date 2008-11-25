
from django.forms import ModelForm
from zoo.places.models import Place, Enclosure, EnclosureSpecies


class EnclosureSpeciesEditForm(ModelForm):
    class Meta:
        model = EnclosureSpecies
        fields = ['number_of_inhabitants', 'species']

class EnclosureEditForm(ModelForm):
    class Meta:
        model = Enclosure
        fields = ['name']
