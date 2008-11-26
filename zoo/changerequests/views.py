from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404

from zoo.shortcuts import render

from zoo.changerequests.forms import ChangeRequestActionForm
from zoo.changerequests.models import ChangeRequestGroup, ChangeRequest

def moderation_queue(request):
    if request.method == 'POST':
        form = ChangeRequestActionForm(request.POST)

        if form.is_valid():
            action = form.cleaned_data['action']
            changerequest = form.cleaned_data['changerequest']

            if action == 'delete':
                if changerequest.group.changerequest_set.count() == 1:
                    # Delete the group if this request is the last request in
                    # this group.
                    changerequest.group.delete()
                else:
                    changerequest.delete()

            return HttpResponseRedirect(reverse('admin-moderation'))

    else:
        form = ChangeRequestActionForm()

    return render(request, 'changerequests/queue.html', {
        'form': form,
        'change_request_groups': ChangeRequestGroup.objects.all(),
        'total_change_requests': ChangeRequest.objects.count(),
    })
