from django.conf import settings
if settings.DATABASE_ENGINE == 'mysql':
    from dmigrations.mysql import migrations as m
elif settings.DATABASE_ENGINE == 'sqlite3':
    from dmigrations.sqlite3 import migrations as m

# This field should be NOT NULL, we add it as NULL to avoid breaking our data
add_column = m.AddColumn(
    'trips', 'trip', 'place', 'integer NULL', 'places_place'
)

class CustomMigration(m.Migration):
    
    def __init__(self):
        super(CustomMigration, self).__init__(sql_up=[], sql_down=[])
    
    def up(self):
        add_column.up()
        
        # Now loop through the existing trips, figure out their place from 
        # their sightings and use that to update their new 'place' column
        trip_ids = [r[0] for r in self.execute_sql(
            ["SELECT id FROM trips_trip"], return_rows=True
        )]
        for trip_id in trip_ids:
            place_ids = [r[0] for r in self.execute_sql(["""
                SELECT DISTINCT place_id FROM trips_sighting WHERE trip_id = 
            """ + str(trip_id)], return_rows=True)]
            if not place_ids:
                print "Trip with ID %s has no sightings!" % trip_id
            else:
                self.execute_sql([
                    "UPDATE trips_trip SET place_id = %s WHERE id = %s" % (
                        place_ids[0], trip_id
                    )
                ])
    
    def down(self):
        add_column.down()
        print """If down() on migration 128 fails, you can fix it with this:
alter table trips_trip drop foreign key place_refs_id_4d32f94e;
alter table trips_trip drop column place_id;
"""

migration = CustomMigration()
