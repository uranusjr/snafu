import atexit
import pathlib
import shutil
import tempfile

import requests

from . import termui


class DownloadIntegrityError(ValueError):
    pass


def download_file(url, *, filename=None, container=None, check=None):
    response = requests.get(url, stream=True)
    response.raise_for_status()

    if not filename:
        filename = url.rsplit('/', 1)[-1]
    total = response.headers.get('content-length', '')
    chunks = []

    if total.isdigit():
        with termui.progressbar(length=int(total), label=filename) as b:
            for chunk in response.iter_content(chunk_size=4096):
                chunks.append(chunk)
                b.update(len(chunk))
    else:
        chunks.append(response.content)

    data = b''.join(chunks)
    if callable(check):
        try:
            check(data)
        except AssertionError as e:
            raise DownloadIntegrityError(str(e))

    if container is None:
        container = pathlib.Path(tempfile.mkdtemp())
        atexit.register(shutil.rmtree, str(container), ignore_errors=True)
    path = container.joinpath(filename)
    with path.open('wb') as f:
        f.write(data)
    return path
