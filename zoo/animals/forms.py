from models import Species
from zoo.search_picker import SearchPickerField

class SpeciesField(SearchPickerField):
    pick_one_text = '-- pick a species --'
    def search(self, q):
        return [
            (s.id, s.common_name)
            for s in Species.objects.filter(common_name__icontains = q)
        ]
    
    def is_valid_choice(self, value):
        return Species.objects.filter(id = value).count()


    