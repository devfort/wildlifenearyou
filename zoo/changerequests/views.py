from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseForbidden

from zoo.shortcuts import render

from zoo.changerequests.forms import ChangeRequestActionForm
from zoo.changerequests.models import ChangeRequestGroup, ChangeRequest

@login_required
def moderation_queue(request):
    if not request.user.is_staff:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = ChangeRequestActionForm(request.POST)

        if form.is_valid():
            action = form.cleaned_data['action']
            changerequest = form.cleaned_data['changerequest'].get_real()

            if action in ('apply', 'force'):
                changerequest.apply(request.user)
            elif action == 'delete':
                changerequest.delete()

            return HttpResponseRedirect(reverse('admin-moderation'))

    else:
        form = ChangeRequestActionForm()

    return render(request, 'changerequests/queue.html', {
        'form': form,
        'change_request_groups': ChangeRequestGroup.objects.filter(changerequest__isnull=False),
        'total_pending_change_requests':
            ChangeRequest.objects.filter(applied_by__isnull=True).count(),
    })
