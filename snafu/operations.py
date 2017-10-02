import atexit
import pathlib
import shutil
import tempfile

import click
import requests


def download_installer(version):
    response = requests.get(version.url, stream=True)

    installer_name = version.url.rsplit('/', 1)[-1]
    total = response.headers.get('content-length', '')
    chunks = []

    if total.isdigit():
        length = int(total)
    else:
        length = None
    with click.progressbar(length=length, label=installer_name) as b:
        for chunk in response.iter_content(chunk_size=4096):
            chunks.append(chunk)
            if length is not None:
                b.update(len(chunk))

    data = b''.join(chunks)

    # TODO: Maybe we should cache the installer to a consistent location
    # instead, so we don't need to download again when uninstalling?
    tempdir_path = pathlib.Path(tempfile.mkdtemp())
    atexit.register(shutil.rmtree, str(tempdir_path), ignore_errors=True)

    installer_path = tempdir_path.joinpath(installer_name)
    version.save_installer(data, installer_path)

    return installer_path
