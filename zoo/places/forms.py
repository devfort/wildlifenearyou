
from django.forms import ModelForm
from zoo.forms import UberForm
from zoo.places.models import Place, PlaceOpening


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

class PlaceOpeningUberForm(UberForm):
    parts = [
        ('main', PlaceOpeningEditForm),
        ]

class PlaceUberForm(UberForm):
    parts = [
        ('main', PlaceEditForm),
        ('opening', PlaceOpeningUberForm,
         lambda instance: instance.placeopening_set.all()),
        ]

