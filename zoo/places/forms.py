from django import forms

from zoo.forms import UberForm
from zoo.places.models import Place, PlaceOpening, PlaceFacility

class PlaceEditForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ('known_as', 'legal_name', 'description', 'url', 'country',
           'address_line_1', 'address_line_2', 'town', 'state', 'zip', 'phone',
           'price_notes')

class PlaceOpeningEditForm(forms.ModelForm):
    class Meta:
        model = PlaceOpening
        fields = ('start_date', 'end_date', 'days_of_week')

class PlaceOpeningEditForm(forms.ModelForm):
    class Meta:
        model = PlaceOpening
        fields = ('start_date', 'end_date', 'days_of_week', 'times', 'closed',
            'section')

class PlaceFacilityEditForm(forms.ModelForm):
    class Meta:
        model = PlaceFacility
        fields = ('facility', 'specific_desc')

    specific_desc = forms.CharField(label='Description',
                                    required=False)

# Uber form instances

class PlaceOpeningUberForm(UberForm):
    model = PlaceOpening
    parts = [('main', PlaceOpeningEditForm)]
    relation = 'place'

class PlaceFacilityUberForm(UberForm):
    model = PlaceFacility
    parts = [('main', PlaceFacilityEditForm)]
    relation = 'place'

class PlaceUberForm(UberForm):
    model = Place
    parts = [
        ('main', PlaceEditForm),
        ('facility', PlaceFacilityUberForm,
         lambda instance: instance.place_facilities.all()),
        ('opening', PlaceOpeningUberForm,
         lambda instance: instance.placeopening_set.all()),
        ]
