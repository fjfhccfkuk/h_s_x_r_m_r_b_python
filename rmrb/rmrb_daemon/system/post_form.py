#!/usr/bin/env python

import mimetools;
import mimetypes;
import itertools;

class multi_part_form:
    def __init__(self):
        self.form_fields = []
        self.files = []
        self.boundary = '####'#mimetools.choose_boundary()

    def add_field(self, name, value):
        self.form_fields.append((name, value))

    def add_file(self, fieldname, filename, file_obj, mimetype=None):
        if not mimetype:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        print("add_file.   fieldname:%s" % fieldname  +  " filename:%s" % filename + " mimetype:%s" % mimetype)
        self.files.append((fieldname, filename, mimetype, file_obj.read()))

    def __str__(self):
        parts = []
        part_boundary = "--%s" % self.boundary

        parts.extend(
            [part_boundary,
             'Content-Disposition: form-data; name="%s"' % name,
             '',
             value, ] for name, value in self.form_fields
        )

        parts.extend(
            [part_boundary,
             'Content-Disposition: form-data; name="%s"; filename="%s"' % (field_name, filename),
             'Content-Type: %s' % content_type,
             '',
             body, ] for field_name, filename, content_type, body in self.files
        )

        flattened = list(itertools.chain(*parts))
        flattened.append('--%s--' % self.boundary)
        flattened.append('')
        return '\n'.join(flattened)


def __get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

def encode_multipart_formdata(files):
    import urllib

    BOUNDARY = '##'
    CRLF = '\r\n'
    L = []

#    L.append('--' + BOUNDARY)
#    L.append('Content-Disposition: form-data; name=txt; filename="/tmp/upload.txt"')
#    L.append('Content-Type: text/plain;charset=UTF-8')
#    L.append('')
#    L.append('Hello,world')

    for (filename) in files:
        print ' -------- filename1:' + filename
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name=file; filename="%s"' % filename)
        L.append('Content-Type: %s' % __get_content_type(filename))
        L.append('')

        content = ""

#        for line in open(filename, 'rb'):
#            content += line
#            L.append(content)
        L.append(filename)
    L.append('--' + BOUNDARY + '--')
    body = CRLF.join(L)
    print body
    print "body length:" + str(len(body))
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body