from django.shortcuts import render_to_response as render
from models import Event

def recent(request):
    return render('recent_activities.html', {
        'events': Event.objects.order_by('-created')[:200],
    })
