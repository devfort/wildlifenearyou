from django.contrib.syndication.feeds import Feed
from models import Event

class RecentEvents(Feed):
    title = "Recent changes on sparkabout"
    link = "http://sparkabout.net/recent/"
    description = "Recent changes on sparkabout.net"
    
    def items(self):
        return Event.objects.order_by('-created')[:30]
        
    def item_link(self, item):
        if item.url:
            return 'http://sparkabout.net' + item.url
        else:
            return self.link
