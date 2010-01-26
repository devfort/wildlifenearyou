from baseconv import BaseConverter

class Base32Converter(BaseConverter):
    # Human-friendly, see http://www.crockford.com/wrmg/base32.html
    replacements = {
        'o': '0',
        'O': '0',
        'I': '1',
        'i': '1',
        'L': '1',
        'l': '1',
    }
    def __init__(self):
        super(Base32Converter, self).__init__(
            '0123456789abcdefghjkmnpqrstvwxyz'
        )
    
    def to_int(self, s):
        for key, value in self.replacements.items():
            s = s.replace(key, value)
        return super(Base32Converter, self).to_int(s)

converter = Base32Converter()
