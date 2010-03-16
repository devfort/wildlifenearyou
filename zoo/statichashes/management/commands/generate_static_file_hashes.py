import hashlib, os, glob
from django.utils import simplejson
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = """
    Calculate MD5 filenames for static files, create copies of those files 
    that incorporate the MD5 in to the filename and save a mapping in a 
    settings file. Also deletes older MD5 filename files.
    """.strip()
    can_import_settings = True
    
    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")
        
        delete_existing_hashnamed_files()
        generate_static_file_hashes(
            static_root = settings.STATIC_ROOT,
            static_files = settings.STATIC_FILES,
            hashdir_path = settings.STATIC_HASHDIR_PATH,
            config_to_write = settings.STATIC_FILE_SETTINGS,
        )

def delete_existing_hashnamed_files():
    hashdir = os.path.join(settings.STATIC_ROOT, settings.STATIC_HASHDIR_PATH)
    for filepath in glob.glob(hashdir + '/*.*'):
        os.remove(filepath)

def generate_static_file_hashes(
        static_root, static_files, hashdir_path, config_to_write
    ):
    """
    Given a static root directory and a list of paths relative to that 
    directory, loops through that list of paths and for each one creates a 
    copy of the file in the same directory but with a truncated MD5 hash of 
    the file's contents baked in to the name of the file - e.g.:
        
        'css/general.css' => 'hs/general-37170795c244.css'
    
    Writes out a Python file declaring a STATIC_FILE_HASHES dictionary to the 
    file specified in config_to_write.
    """
    mapping = {}
    hashdir_fullpath = os.path.join(static_root, hashdir_path)
    if not os.path.exists(hashdir_fullpath):
        os.makedirs(hashdir_fullpath)
    for path in static_files:
        fullpath = os.path.join(static_root, path)
        fp = open(fullpath)
        content = fp.read()
        fp.close()
        hash = hashlib.md5(content).hexdigest()[:12]
        pathbit, filename = os.path.split(fullpath)
        filebit, ext = os.path.splitext(filename)
        new_filename = '%s-%s%s' % (filebit, hash, ext)
        fp = open(os.path.join(hashdir_fullpath, new_filename), 'w')
        fp.write(content)
        fp.close()
        mapping[path] = '/'.join((hashdir_path, new_filename))
    
    fp = open(config_to_write, 'w')
    fp.write('STATIC_FILE_HASHES = ')
    fp.write(simplejson.dumps(mapping, indent=4))
    fp.write('\n')
    fp.close()
