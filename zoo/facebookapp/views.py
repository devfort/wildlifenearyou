from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.utils.decorators import decorator_from_middleware
from facebook.djangofb import FacebookMiddleware
import facebook.djangofb as facebook

@decorator_from_middleware(FacebookMiddleware) 
@facebook.require_login()
def canvas(request):
    # If you're using FBML, it'd be better to use <fb:name> than to do this 
    # - this is just as an example
    values = request.facebook.users.getInfo(
        [request.facebook.uid],
        ['first_name', 'is_app_user', 'has_added_app']
    )[0]
    
    name = values['first_name']
    is_app_user = values['is_app_user']
    has_added_app = values['has_added_app']
    
    if has_added_app == '0':
        return request.facebook.redirect(request.facebook.get_add_url())
    
    return render_to_response('facebookapp/canvas.fbml', {'name': name})

@decorator_from_middleware(FacebookMiddleware)
@facebook.require_login()
def canvas_post(request):
    request.facebook.profile.setFBML(
        request.POST['profile_text'], request.facebook.uid
    )
    
    return request.facebook.redirect(
        request.facebook.get_url('profile', id=request.facebook.uid)
    )

@decorator_from_middleware(FacebookMiddleware)
@facebook.require_login()
def post_add(request):
    request.facebook.profile.setFBML(
        uid = request.facebook.uid,
        profile = 'Demo text'
    )
    return request.facebook.redirect(
        'http://apps.facebook.com/wildlifenearyou/'
    )

@decorator_from_middleware(FacebookMiddleware)
@facebook.require_login()
def canvas_ajax(request):
    return HttpResponse('Hello, world!')
