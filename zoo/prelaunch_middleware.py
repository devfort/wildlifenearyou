from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

LOGIN_TEMPLATE = """
<h1>Password required</h1>
%(msg)s
<form action="%(path)s" method="POST">
<p>
    <input type="password" name="%(form_field_name)s">
    <input type="submit" value="Go">
</p>
</form>
"""

class PreLaunchMiddleware(object):
    cookie_name = 'prelaunch'
    form_field_name = 'set_the_prelaunch_cookie'
    
    def get_password(self):
        return settings.PRELAUNCH_PASSWORD
    
    def process_request(self, request):
        # Process POST if our particular form has been submitted
        if request.method == 'POST' and self.form_field_name in request.POST:
            return self.login_screen(request)
        
        if request.COOKIES.get(self.cookie_name, '') != self.get_password():
            return self.login_screen(request)
    
    def login_screen(self, request):
        msg = ''
        if request.method == 'POST':
            password = request.POST.get(self.form_field_name, '')
            if password == self.get_password():
                response = HttpResponseRedirect(request.path)
                self.set_cookie(response, password)
                return response
            else:
                msg = 'Incorrect password'
        return HttpResponse(LOGIN_TEMPLATE % {
            'msg': msg and ('<p>%s</p>' % msg) or '',
            'form_field_name': self.form_field_name,
            'path': request.path,
        })
    
    def set_cookie(self, response, password):
        response.set_cookie(self.cookie_name, password)
