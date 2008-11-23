from django.http import HttpResponseRedirect

class OnlyLowercaseUrls:
    def process_request(self, request):
        if request.path.lower() != request.path:
            return HttpResponseRedirect(request.path.lower())
