import os
from svoibudjetapi import app
from werkzeug.datastructures import FileStorage

VALID_MIME = [
    'image/jpg',
    'image/jpeg',
    'image/gif',
    'image/png',
    'image/bmp',
]


def get_path(id_: int = None, file_name: str = None) -> str:
    parts = [app.config['MEDIA_DIR'], 'qr_strings_img']
    if id_ is not None:
        parts.append(str(id_))
        if file_name is not None:
            parts.append(file_name)
    return os.path.join(*parts)


def generate_file_name(id_: int, file) -> str:
    next_name = max(int(s.split('.')[0]) for s in get_file_names(id_) or [0]) + 1
    if isinstance(file, FileStorage):
        extension = file.mimetype.split('/').pop()
    else:
        extension = file.split(".").pop()

    return f'{next_name}.{extension}'


def generate_file_path(id_: int, file) -> str:
    return get_path(id_, generate_file_name(id_, file))


def get_file_names(id_: int) -> [str]:
    path = get_path(id_)
    if not os.path.isdir(path):
        return

    for file_name in os.listdir(path):
        if not os.path.isfile(os.path.join(path, file_name)):
            continue
        yield file_name


def get_links(id_: int) -> [str]:
    for file_name in get_file_names(id_):
        yield get_link(id_, file_name)


def get_link(id_: int, file_name: str) -> str:
    return f'v1/qr_strings/{id_}/images/{file_name}'


def is_valid_mime(mime: str) -> bool:
    return mime in VALID_MIME
