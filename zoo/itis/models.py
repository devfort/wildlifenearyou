from django.db import models

class Kingdom(models.Model):
    name = models.CharField(max_length = 50)
    
    def __unicode__(self):
        return self.name

class Rank(models.Model):
    name = models.CharField(max_length = 50)
    kingdom = models.ForeignKey(Kingdom)
    itis_id = models.IntegerField(db_index = True)
    dir_parent_rank = models.ForeignKey('self', related_name='dir_ranks_rev',
        null = True, blank = True
    )
    req_parent_rank = models.ForeignKey('self', related_name='req_ranks_rev',
        null = True, blank = True
    )
    
    def __unicode__(self):
        return self.name

class Species(models.Model):
    name1 = models.CharField(max_length = 100, blank = True)
    name2 = models.CharField(max_length = 100, blank = True)
    name3 = models.CharField(max_length = 100, blank = True)
    name4 = models.CharField(max_length = 100, blank = True)
    parent = models.ForeignKey('self', blank = True, null = True)
    rank = models.ForeignKey(Rank)
    kingdom = models.ForeignKey(Kingdom)
    
    def __unicode__(self):
        names = []
        for attr in ('name1', 'name2', 'name3', 'name4'):
            value = getattr(self, attr)
            if value:
                names.append(value)
        return ' '.join(names)

class Vernaculars(models.Model):
    name = models.CharField(max_length = 255)
    language = models.CharField(max_length = 30, blank = True)
    is_approved = models.BooleanField()
    
    def __unicode__(self):
        return self.name
