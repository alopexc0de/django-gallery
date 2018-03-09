import logging
from StringIO import StringIO
import zlib
class UnzipRequestMiddleware(object):
    """A middleware that unzips POSTed data.

    For this middleware to kick in, the client must provide a value
    for the ``Content-Encoding`` header. The only accepted value is
    ``gzip``. Any other value is ignored.
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        encoding = environ.get('HTTP_CONTENT_ENCODING')
        if encoding == 'gzip':
            data = environ['wsgi.input'].read()
            try:
                uncompressed = zlib.decompress(data, 31)
                environ['wsgi.input'] = StringIO(uncompressed)
                environ['CONTENT_LENGTH'] = len(uncompressed)
            except zlib.error:
                logging.warning(u"Could not decompress request data.", exc_info=True)
                environ['wsgi.input'] = StringIO(data)
        return self.app(environ, start_response)

