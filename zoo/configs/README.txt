Since we're now running different environments in production, it makes sense
to keep their configurations in SVN. That way we can launch different 
environment settings by pointing at e.g. zoo.configs.alpha as our settings.py

This can optionally be used in place of the local_settings.py idiom.
