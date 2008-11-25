from django.forms.fields import MultiValueField
from django.forms.widgets import MultiWidget, TextInput, Select
from django import forms


class SearchPickerWidget(MultiWidget):
    def __init__(self, widgets, attrs=None):
        super(SearchPickerWidget, self).__init__(widgets, attrs)
    
    def decompress(self, value):
        #if value:
        #    return [value.date(), value.time().replace(microsecond=0)]
        return [None, None]

# TODO: we need a way to clear the search field and preselect
#       a (the only) result when an exact match is entered.
#       This will most likely involve overriding the Widget.value_from_datadict
#       method.
# TODO: What if SearchPickerField is not required?
# TODO: What if they should be associating with more than one?

class SearchPickerField(MultiValueField):
    def __init__(self, *args, **kwargs):
        self.choices = (
            ('', '-- enter a search term --'),
        )
        self.search_field = forms.CharField(required = False)
        self.picker = forms.ChoiceField(
            required = True, choices = self.choices
        )
        self.widget = SearchPickerWidget(
            widgets = (self.search_field.widget, self.picker.widget)
        )

        super(SearchPickerField, self).__init__(
            fields = (self.search_field, self.picker), *args, **kwargs
        )
    
    def clean(self, value):
        # The widget is responsible for 'value' being a list because of 
        # value = field.widget.value_from_datadict (forms.py line 225)
        search_val, picked_val = value

        # If they've picked a valid choice, we're done
        if picked_val and self.is_valid_choice(picked_val):
            return search_val, picked_val
        
        if not search_val:
            raise forms.ValidationError, 'Try searching for something'
        else:
            results = list(self.search(search_val))

            self.picker.choices = self.choices = \
                [('', '-- choose a location --')] + results

            for val, name in results:
                if name.lower() == search_val.lower():
                    # an exact match! take it.
                    return name, unicode(val)

            raise forms.ValidationError, 'Ambiguous entry'

    def search(self, q):
        raise NotImplementedError, 'You should override the search() method'
    
    def is_valid_choice(self, value):
        raise NotImplementedError, \
            'You should override the is_valid_choice() method'

class LocationPickerField(SearchPickerField):
    def search(self, q):
        from zoo.geonames.models import Geoname
        return [
            (g.id, g.place_name) for g in Geoname.objects.filter(
                place_name__icontains = q
            ).order_by('place_name')[:20]
        ]

    def is_valid_choice(self, value):
        from zoo.geonames.models import Geoname
        return Geoname.objects.filter(pk = value).count() == 1


