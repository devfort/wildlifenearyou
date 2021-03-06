from django.conf.urls.defaults import *
from django.conf import settings
from django import http
from django.views.generic.simple import direct_to_template

import os

from django.contrib import admin
admin.autodiscover()
# Disable dependency check, since it's hard coded to look for the 'auth'
# context processor and we've replaced that with our own.
admin.site.check_dependencies = lambda *args: True

from django.contrib import databrowse
from django.contrib.auth.models import User
from django.db.models import get_models
from dmigrations.migration_state import table_present
#for model in get_models():
#    if table_present(model._meta.db_table):
#        databrowse.site.register(model)
import activities.signals
from activities.feeds import RecentEvents

from django.template import add_to_builtins
add_to_builtins('zoo.common.templatetags.switch')

from accounts import views as accounts
from faces import views as faces
from photos import views as photos

from accounts.openid import RegistrationConsumer
#from invitereg.views import InviteRegistrationConsumer as RegistrationConsumer

registration_consumer = RegistrationConsumer()

from animals.models import Species
from photos.models import Photo
from favourites.views import FavouriteView
from favourites.models import FavouriteSpecies, FavouritePhoto

fave_species = FavouriteView(FavouriteSpecies, 'species', Species)
fave_photo = FavouriteView(FavouritePhoto, 'photo', Photo)

def redirect_to(path):
    def redirect(request, **kwargs):
        return http.HttpResponsePermanentRedirect(path % kwargs)
    return redirect

urlpatterns = patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': os.path.join(settings.OUR_ROOT, 'static')
    }),
    
    # Activity stream stuff
    (r'^recent/$', 'activities.views.recent'),
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {
        'feed_dict': {
            'recent': RecentEvents,
        }
    }),
    
    # Invitation URL (sent out in invite e-mail)
    url(r'^invitation/$', 'zoo.invitereg.views.enter_invite_code',
        name = 'enter-invite-code'
    ),
    url(r'^invitation/clear/$', 'zoo.invitereg.views.clear_invite_code',
        name = 'clear-invite-code'
    ),
    (r'^invitation/(\w+)/$', 'zoo.invitereg.views.invitation'),
    
    url(r'^account/register/$', registration_consumer, {
        'rest_of_url': 'register/',
    }, name = 'accounts-register'),
    url(r'^account/login/$', registration_consumer, {
        'rest_of_url': 'login/',
    }, name = 'accounts-login'),
    url(r'^account/logout/$', registration_consumer, {
        'rest_of_url': 'logout/',
    }, name = 'accounts-logout'),
    (r'^account/(.*?)$', registration_consumer),
    
    (r'^blog/', include('basic.blog.urls')),
    
    # Landing Page
    url(r'^$', 'zoo.homepage.views.homepage',
        name='homepage'
    ),
    
    url(r'^debug/urls/$', 'zoo.debug.views.show_url_patterns'),
    
    # Launch signups POST handler
    (r'^launchsignups/$', 'zoo.launchsignups.views.signup'),
    
    # shortcuts
    url(r'^tripbook/$', redirect_to('/trips/')),
    url(r'^trips/$', 'zoo.trips.views.tripbook_default',
        name='tripbook-default'),
    url(r'^profile/$', accounts.profile_default,
        name='accounts-default'),
    url(r'^invite/$', accounts.invite_friends,
        name='invite-friends'),
    
    url(r'^search/species/$', 'zoo.search.views.search_species', 
        name='species-search'),
    url(r'^search/$', 'zoo.search.views.search',
        name='search'),
    
    # Ajax autocompleters
    url(r'^autocomplete/species/(\d+)/$', 
        'zoo.trips.views.autocomplete_species',
        name='autocomplete-species-place'),

    # Flickr integration
    url(r'^flickr/$', 'zoo.flickr.views.index',
        name='flickr'),
    url(r'^flickr/callback/$', 'zoo.flickr.views.flickr_callback',
        name='flickr-callback'),
    url(r'^flickr/prefs/$', 'zoo.flickr.views.prefs',
        name='flickr-prefs'),
    url(r'^flickr/search/$', 'zoo.flickr.views.search',
        name='flickr-search'),
    url(r'^flickr/your-places/$', 'zoo.flickr.views.places',
        name='flickr-places'),
    url(r'^flickr/your-places/(.*?)/$', 'zoo.flickr.views.place',
        name='flickr-place'),
    url(r'^flickr/your-groups/$', 'zoo.flickr.views.groups',
        name='flickr-groups'),
    url(r'^flickr/your-groups/(.*?)/$', 'zoo.flickr.views.group',
        name='flickr-group'),
    url(r'^flickr/your-sets/$', 'zoo.flickr.views.sets',
        name='flickr-sets'),
    url(r'^flickr/your-sets/(.*?)/$', 'zoo.flickr.views.single_set',
        name='flickr-set'),
    url(r'^flickr/selected/$', 'zoo.flickr.views.selected',
        name='flickr-selected'),
    
    url(r'^forgotten_password/$', 'accounts.views.forgotten_password',
        name='forgotten-password'),
    url(r'^password_key_sent/$', 'accounts.views.password_key_sent',
        name='password-key-sent'),
    url(r'^recover_password/(\w+)/([a-f0-9]+)/([a-f0-9]{32})/$', 
        'accounts.views.recover_password',
        name='recover-password'),
    url(r'^change_password/$', 'django.contrib.auth.views.password_change', {
            'template_name': 'accounts/change_password.html'
        }, name='change-password'),
    url(r'^change_password_done/$', 
        'django.contrib.auth.views.password_change_done', {
            'template_name': 'accounts/change_password_done.html'
        }, name='change-password-done'),
    
    url(r'^register/validate/(\w+)/([a-f0-9]+)/([a-f0-9]{32})/$', 
        'accounts.views.validate_email',
        name='validate-email'),
    url(r'^register/validated/$', 'accounts.views.validate_email_success',
        name='validate-email-success'),
    
    url(r'^profiles/$', accounts.all_profiles,
        name='accounts-all-profiles'),
    
    url(r'^add-trip/$', 'trips.views.add_trip_select_place', name='add-trip'),
    url(r'^add-trip/add-place/$', 'trips.views.add_trip_add_place', 
        name='add-trip-add-place'),
    url(r'^add-trip/add-place/nearby/$', 'trips.views.ajax_nearby_places', 
        name='add-trip-add-place-nearby-places'),
    
    (r'^faces/profile-images.xml$', faces.profile_images_xml),
    (r'^faces/profile.xml$', faces.profile_xml),
    url(r'^faces/large/(?P<username>\w+).png$',
        'faces.generate.profile_image_response',
        name="profile-image",
        kwargs = {'size': 'large'}
    ),
    url(r'^faces/small/(?P<username>\w+).png$',
        'faces.generate.profile_image_response',
        name="profile-image-resized",
        kwargs = {'size': 'small'}
    ),
    url(r'^faces/medium/(?P<username>\w+).png$',
        'faces.generate.profile_image_response',
        name="profile-image-resized-medium",
        kwargs = {'size': 'medium'}
    ),
    (r'^faces/users/(\w+).xml$', faces.profile_image_xml),
    (r'^faces/update/$', faces.update),
    
    url(r'^photos/upload/$', photos.upload, name="upload-photos"),
    (r'^photos/$', photos.all),
    url(r'^moderation/photos/$', 'zoo.photos.views.moderate', 
        name='moderate-photos'),
    
    (r'^set-location/$', 'zoo.accounts.views.set_location'),
    (r'^set-location/delete/$', 'zoo.accounts.views.delete_location'),
    url(r'location-complete/$', 'zoo.search.views.location_complete',
        name="location-complete"),
    
    (r'^comments/', include('django.contrib.comments.urls')),
    url(r'^feedback/$', 'zoo.feedback.views.submit', name='feedback'),
    
    # Django built-in admin
    (r'^admin2/(.*)', admin.site.root),
    
    # Gimmicks
    (r'^gimmicks/(.*)/$', 'gimmicks.views.gimmick'),
    
    # Status / debugging tools
    (r'^status/innodb/$', 'debug.views.show_innodb_status'),
    
    # Databrowse
    (r'^databrowse/(.*)', databrowse.site.root),
    
    url(r'^animals/$', redirect_to('/species/')),
    url(r'^species/$', 'zoo.animals.views.all_species',
        name='all-species'),
    url(r'^animals/all\.xml$', redirect_to('/species/all.xml')),
    url(r'^species/all\.xml$', 'zoo.animals.views.species_xml',
        name='species-xml'),
    url(r'^animals/(?P<slug>[^/]+)/$', redirect_to('/species/%(slug)s/')),
    url(r'^species/(?P<slug>[^/]+)/$', 'zoo.animals.views.species',
        name='species'),
    url(r'^animals/(?P<slug>[^/]+)/spotters/$',
        redirect_to('/species/%(slug)s/spotters/')),
    url(r'^species/(?P<slug>[^/]+)/spotters/$', 
        'zoo.animals.views.species_spotters',
        name='species-spotters'),
    url(r'^animals/(?P<slug>[^/]+)/photos/$',
        redirect_to('/species/%(slug)s/photos/')),
    url(r'^species/(?P<slug>[^/]+)/photos/$', 
        'zoo.animals.views.species_photos',
        name='species-photos'),
    url(r'^animals/(?P<slug>[^/]+)/photos/best/$',
        redirect_to('/species/%(slug)s/photos/best/')),
    url(r'^species/(?P<slug>[^/]+)/photos/best/$',
        'zoo.bestpic.views.bestpic_of_species',
        name='bestpic-of-species'),
    url(r'^animals/(?P<slug>[^/]+)/fans/$',
        redirect_to('/species/%(slug)s/fans/')),
    url(r'^species/(?P<slug>[^/]+)/fans/$', 
        'zoo.animals.views.species_fans',
        name='species-fans'),
    
    url(r'^favourites/species/(add|remove)/(\d+)/$', fave_species),
    url(r'^favourites/photo/(add|remove)/(\d+)/$', fave_photo),
    
    url(r'^latin/$', 'zoo.animals.views.all_species_latin',
        name='all-species-latin'),
    url(r'^latin/(?P<latin_name>[^/]+)/$', 
        'zoo.animals.views.species_latin',),
    
    url(r'^popular/$', 'zoo.favourites.views.hit_parade',
        name='popular'),
    
    url(r'^api/$', 'zoo.api.views.index',
        name='api'),
    url(r'^api/your-keys/$', 'zoo.api.views.your_keys',
        name='api-your-keys'),
    url(r'^api/your-keys/(\w+)/$', 'zoo.api.views.key_details',
        name='api-key-details'),
    url(r'^api/(\w{2})/(.*)/$', 'zoo.api.views.place',
        name='api-place'),
    url(r'^api/species-identifiers/$', 'zoo.api.views.species_identifiers',
        name='api-species-identifierskeys'),
    url(r'^api/metadata/(.*)/?$', 'zoo.api.views.metadata',
        name='api-metadata'),
    url(r'^api/(\w{3,})/$', 'zoo.api.views.user',
        name='api-user'),
    url(r'^api/(\w{3,})/species/$', 'zoo.api.views.user_species',
        name='api-user-species'),
    url(r'^api/(\w{3,})/trips/$', 'zoo.api.views.user_trips',
        name='api-user-trips'),
    url(r'^api/(\w{3,})/trips/(\d+)/$', 'zoo.api.views.trip',
        name='api-trip'),
    
    url(r'^explore/$', 'zoo.explore.views.index',
        name='explore'),
    
    url(r'^shorturl/(\w)(\w+)/?$', 'zoo.shorturl.views.index',
        name='shorturl'),
    url(r'^shorturl/?$', 'django.views.generic.simple.redirect_to', {
        'url': 'http://www.wildlifenearyou.com/',
    }),
    url(r'^users/(.*)/$', 'zoo.accounts.views.users_redirect'),
    
    url(r'^stats/$', 'zoo.stats.views.index'),
    url(r'^stats/top-users/$', 'zoo.stats.views.top_users'),
    
    url(r'^help/$', 'zoo.crowdsource.views.index',
        name='help'),
    url(r'^help/identify-species/$', 'zoo.crowdsource.views.identify_species',
        name='help-identify-species'),
    url(r'^best/$', 'zoo.bestpic.views.bestpic',
        name='bestpic'),
    url(r'^best/activity/$', 'zoo.bestpic.views.activity',
        name='bestpic-activity'),
    
    url(r'^lists/$', 'zoo.lists.views.index',
        name='lists'),
    url(r'^lists/(.*)/edit/$', 'zoo.lists.views.edit',
        name='list-edit'),
    url(r'^lists/(.*)/$', 'zoo.lists.views.view_list',
        name='list'),
    
    url(r'^cleanup/places/$', 'zoo.cleanup.views.cleanup_places',
        name='cleanup-places'),
    url(r'^cleanup/merge-places/$', 'zoo.cleanup.views.merge_places',
        name='cleanup-merge-places'),
    url(r'^cleanup/merge-places/(\d+)/(\d+)/$',
        'zoo.cleanup.views.confirm_merge_places',
        name='cleanup-confirm-merge-places'),
    
    url(r'^facebook/canvas/$', 'zoo.facebookapp.views.canvas',
        name='facebook-canvas'),
    url(r'^facebook/canvas/post/$', 'zoo.facebookapp.views.canvas_post',
        name='facebook-canvas-post'),
    url(r'^facebook/canvas/ajax/$', 'zoo.facebookapp.views.canvas_ajax',
        name='facebook-canvas-ajax'),
    url(r'^facebook/post_add/', 'zoo.facebookapp.views.post_add',
        name='facebook-post-add'),
    
    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+)/$', 
        'zoo.places.views.place',
        name='place'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>.*?)/photos/$',
        'zoo.places.views.place_photos', name='place-photos'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>.*?)/suggest-changes/$',
        'zoo.places.views.place_edit', name='place-edit'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>.*?)/changes-suggested/$',
        'zoo.places.views.place_edit_done', name='place-edit-done'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>.*?)/summary/$', 
        'zoo.places.views.place_summary',
        name='place-summary'),
    
    url(r'^places/$', 'zoo.places.views.all_places',
        name='places'),
    url(r'^places/autocomplete/$', 'zoo.search.views.place_complete',
        name='places-autocomplete'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+)/animal-checklist/$', 
        'zoo.places.views.place_animal_checklist',
        name='place-animal-checklist'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+)/animals/$',
        redirect_to('/%(country_code)s/%(slug)s/species/')),
    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+)/species/$',
        'zoo.places.views.place_species',
        name='place-species'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+)/animals/(?P<sp>[^/]+)/$',
        redirect_to('/%(country_code)s/%(slug)s/species/%(sp)s/')),
    url(r'^(?P<country>\w{2})/(?P<place>[^/]+)/species/(?P<species>[^/]+)/$',
        'zoo.places.views.place_species_view',
        name='place-species-view'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+)/add-trip/$',
        'zoo.trips.add_trip.add_trip',
        name='place-add-trip'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+)/add-trip/ajax-search/$',
        'zoo.trips.add_trip.ajax_search_species',
        name='place-add-trip-ajax-search-species'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+)/pick-sightings/$',
        'zoo.trips.views.pick_sightings_for_place',
        name='place-pick_sightings_for_place'),
    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+)/add-sightings/$',
        'zoo.trips.views.finish_add_sightings_to_place',
        name='place-add_sightings_to_place'),
    
    url(r'^(?P<country_code>\w{2})/(?P<slug>[^/]+)/support/$',
        'zoo.places.views.support',
        name='place-support'),    
    
    url(r'^(?P<country_code>\w{2})/by-category/(?P<slug>[^/]+)/$',
        'zoo.places.views.country_by_category',
        name='country-by-category'),
    url(r'^(?P<country_code>\w{2})/$', 'zoo.places.views.country',
        name='country'),
    
    url(r'^countries/$', 'zoo.places.views.all_countries',
        name='countries'),
    
    url(r'^404/$', direct_to_template, {'template':'404.html'}),
    url(r'^500/$', direct_to_template, {'template':'500.html'}),
)

urlpatterns += patterns('zoo.changerequests.views',
    url(r'moderation/', 'moderation_queue',
        name='admin-moderation'),
)

# User patterns come last, because they are greedy
urlpatterns += patterns('',
    url(r'^(?P<username>\w+)/$', accounts.profile,
        name='accounts-profile'),
    url(r'^(?P<username>\w+)/edit/$', accounts.profile_edit,
        name='accounts-profile-edit'),
    
    url(r'^(?P<username>\w+)/photos/$', 'zoo.photos.views.user_photos',
        name='user-photos'),
    url(r'^(?P<username>\w+)/photos/by-trip/$', 
        'zoo.photos.views.user_photos_by_trip',
        name='user-photos-by-trip'),
    url(r'^(?P<username>\w+)/photos/unassigned/$',
        'zoo.photos.views.user_photos_unassigned',
        name='user-photos-unassigned'),
    url(r'^(?P<username>\w+)/photos/unassigned/by-flickr-set/$',
        'zoo.photos.views.user_photos_unassigned_flickr_sets',
        name='user-photos-unassigned-flickr-sets'),
  url(r'^(?P<username>\w+)/photos/unassigned/by-flickr-set/(?P<set_id>\d+)/$',
        'zoo.photos.views.user_photos_unassigned_by_flickr_set',
        name='user-photos-unassigned-by-flickr-set'),
    url(r'^(?P<username>\w+)/photos/favourites/$',
        'zoo.photos.views.user_favourite_photos',
        name='user-photos-favourites'),
    url(r'^(?P<username>\w+)/photos/no-species/$',
        'zoo.photos.views.user_photos_nospecies',
        name='user-photos-nospecies'),
    url(r'^(?P<username>\w+)/photos/suggestions/$',
        'zoo.photos.views.suggestions',
        name='user-photos-suggestions'),
    url(r'^(?P<username>\w+)/photos/suggestions/(?P<suggestion_id>\d+)/$',
        'zoo.photos.views.process_suggestion',
        name='user-photos-process-suggestion'),
    
    url(r'^(?P<username>\w+)/photos/(?P<photo_id>\d+)/$',
        'zoo.photos.views.photo',
        name='photo'),
    url(r'^(?P<username>\w+)/photos/(?P<photo_id>\d+)/fans/$',
        'zoo.photos.views.photo_fans',
        name='photo-fans'),
    url(r'^(?P<username>\w+)/photos/(?P<photo_id>\d+)/edit/$',
        'zoo.photos.views.edit_photo',
        name='photo-edit'),
    url(r'^(?P<username>\w+)/photos/(?P<photo_id>\d+)/delete/$',
        'zoo.photos.views.delete_photo',
        name='photo-delete'),
    
    url(r'^(?P<username>\w+)/photos/(?P<photo_id>\d+)/set-species/$',
        'zoo.photos.views.set_species',
        name='photo-set-species'),
    url(r'^(?P<username>\w+)/photos/(?P<photo_id>\d+)/add-species/$',
        'zoo.photos.views.add_species',
        name='photo-add-species'),
    url(r'^(?P<username>\w+)/photos/(?P<photo_id>\d+)/suggest-species/$',
        'zoo.photos.views.suggest_species',
        name='photo-suggest-species'),
    url(r'^(?P<username>\w+)/photos/(?P<photo_id>\d+)/set-has-no-species/$',
        'zoo.photos.views.set_has_no_species',
        name='photo-set-has-no-species'),
    url(r'^(?P<username>\w+)/photos/(?P<photo_id>\d+)/' + 
        'remove-species/(?P<sighting_id>\d+)/$',
        'zoo.photos.views.remove_species',
        name='photo-remove-species'),
    
    url(r'^(?P<user>\w+)/tripbook/$', redirect_to('/%(user)s/trips/')),
    url(r'^(?P<username>\w+)/trips/$', 'zoo.trips.views.tripbook',
        name='tripbook'),
    url(r'^(?P<username>\w+)/trip/(?P<trip_id>\d+)/$',
        redirect_to('/%(username)s/trips/%(trip_id)s/')),
    url(r'^(?P<username>\w+)/trips/(?P<trip_id>\d+)/$', 
        'zoo.trips.views.trip_view', name='trip-view'),
    url(r'^(?P<username>\w+)/trip/(?P<trip_id>\d+)/photos/$',
        redirect_to('/%(username)s/trips/%(trip_id)s/photos/')),
    url(r'^(?P<username>\w+)/trips/(?P<trip_id>\d+)/photos/$',
        'zoo.trips.views.trip_photos', name='trip-photos'),
    url(r'^(?P<username>\w+)/trip/(?P<trip_id>\d+)/edit/$',
        redirect_to('/%(username)s/trips/%(trip_id)s/edit/')),
    url(r'^(?P<username>\w+)/trips/(?P<trip_id>\d+)/edit/$',
        'zoo.trips.views.edit_trip', name='edit-trip'),
    url(r'^(?P<username>\w+)/trip/(?P<trip_id>\d+)/add-sightings/$',
        redirect_to('/%(username)s/trips/%(trip_id)s/add-sightings/')),
    url(r'^(?P<username>\w+)/trips/(?P<trip_id>\d+)/add-sightings/$',
        'zoo.trips.add_trip.add_sightings_to_trip',
        name='add-sightings-to-trip'),
    # url(r'^(?P<username>\w+)/trip/(?P<trip_id>\d+)/upload/$',
    #     photos.upload_trip, name='upload-photos-trip'),
    url(r'^(?P<username>\w+)/trip/(?P<trip_id>\d+)/delete/$',
        redirect_to('/%(username)s/trips/%(trip_id)s/delete/')),
    url(r'^(?P<username>\w+)/trips/(?P<trip_id>\d+)/delete/$', 
        'zoo.trips.views.trip_delete',
        name='trip-delete'),
)

urlpatterns += patterns('django.contrib.flatpages.views',
    url(r'^(?P<url>.*)$', 'flatpage', name='flatpage'),
)
