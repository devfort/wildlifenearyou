from django.shortcuts import get_object_or_404

from zoo.shortcuts import render

from zoo.changerequests.models import ChangeRequestGroup, ChangeRequest

def moderation_queue(request):
    return render(request, 'changerequests/queue.html', {
        'change_request_groups': ChangeRequestGroup.objects.all(),
        'total_change_requests': ChangeRequest.objects.count(),
    })

