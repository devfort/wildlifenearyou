from django.core.management.base import BaseCommand, CommandError
from BeautifulSoup import BeautifulSoup as Soup
import urllib, urlparse, time
from rspb.models import RspbBirdPage

rspb_name_url = 'http://www.rspb.org.uk/wildlife/birdguide/name/%s/index.aspx'

class Command(BaseCommand):
    help = """
    Scrape the RSPB's awesome birdguide site.
    """.strip()
    
    requires_model_validation = True
    can_import_settings = True
    
    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")
        
        letters = 'A B C D E F G H I J K L M N O P Q R S T V W Y'.split()
        
        for letter in letters:
            url = rspb_name_url % letter.lower()
            scrape_page(url)
            time.sleep(10)
        

def scrape_page(url):
    soup = Soup(urllib.urlopen(url))
    
    for table in soup.findAll('table', {'class': 'teaser'}):
        h3 = table.find('h3')
        name = h3.text
        url = h3.find('a')['href']
        p = table.find('p')
        p.find('a').extract() # Ditch the 'more' link
        teaser = p.text
        img = table.find('img')
        if img is not None:
            image_url = urlparse.urljoin(rspb_name_url, img['src'])
        else:
            image_url = ''
        
        obj, created = RspbBirdPage.objects.get_or_create(
            url = url,
            defaults = {
                'name': name,
                'teaser': teaser,
                'image_url': image_url
            }
        )
        print "Added %s" % obj
