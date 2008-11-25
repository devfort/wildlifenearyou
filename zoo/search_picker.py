from django.forms.fields import MultiValueField
from django.forms.widgets import MultiWidget, TextInput, Select
from django import forms


class SearchPickerWidget(MultiWidget):
    def __init__(self, attrs=None):
        widgets = (TextInput(attrs=attrs), Select(attrs=attrs))
        super(SearchPickerWidget, self).__init__(widgets, attrs)
    
    def decompress(self, value):
        #if value:
        #    return [value.date(), value.time().replace(microsecond=0)]
        return [None, None]

    
# TODO: What if SearchPickerInput is not required?
# TODO: What if they should be associating with more than one?

class SearchPickerInput(MultiValueField):
    
    # TODO: We need to tell Django that the two fields that make up a 
    # SearchPickerInput have their own widgets, and Django should use those 
    # instead of instantiating two duplicate widgets when it creates the 
    # SearchPickerWidget instance
    
    widget = SearchPickerWidget
    
    def __init__(self, *args, **kwargs):
        self.choices = (
            ('', '-- enter a search term --'),
        )
        self.search_field = forms.CharField(required = False)
        self.picker = forms.ChoiceField(
            required = True, choices = self.choices
        )
        super(SearchPickerInput, self).__init__(
            fields = (self.search_field, self.picker), *args, **kwargs
        )
    
    def clean(self, value):
        # The widget is responsible for 'value' being a list because of 
        # value = field.widget.value_from_datadict (forms.py line 225)
        #import pdb; pdb.set_trace()
        
        # If they've picked a valid choice, we're done
        if self.is_valid_choice(value[1]):
            return value[1] 
        
        if not value[0]:
            raise forms.ValidationError, 'Try searching for something'
        else:
            self.choices = self.search(value[0])
            self.widget.widgets[1].choices = self.choices
            raise forms.ValidationError, 'Ambiguous entry'

    def search(self, q):
        raise NotImplementedError, 'You should override the search() method'
    
    def is_valid_choice(self, value):
        raise NotImplementedError, \
            'You should override the is_valid_choice() method'

class LocationPickerInput(SearchPickerInput):
    
    def search(self, q):
        from zoo.geonames.models import Geoname
        return [('0', '-- none of these --')] + [
            (g.id, g.place_name) for g in Geoname.objects.filter(
                place_name__icontains = q
            )[:10]
        ]
    
    def is_valid_choice(self, value):
        from zoo.geonames.models import Geoname
        return Geoname.objects.filter(pk = value).count() == 1

