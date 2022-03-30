import os

from flask import url_for
from werkzeug.utils import secure_filename

from common import UPLOAD_PATH, ALLOWED_EXTENSIONS_IMAGES, SERVICE_URL


def allowed_file(filename, whitelist):
    return '.' in filename and filename.rsplit('.', 1)[1] in whitelist


def upload_file(file, path, filename=None):
    if not filename:
        filename = file.filename
    if file and allowed_file(filename, ALLOWED_EXTENSIONS_IMAGES):
        filename = secure_filename(filename)
        file.save(os.path.join(path, filename))
        return f'{SERVICE_URL}/{path}/{filename}'
    else:
        return False
