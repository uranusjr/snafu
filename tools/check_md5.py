"""Quick way to verify I provided matching download URL and MD5.
"""

import hashlib
import json
import pathlib
import sys

import requests


def download_data(url):
    print('Downloading', url, '... ', end='', flush=True)
    response = requests.get(url)
    response.raise_for_status()
    print('Done')
    return response.content


def check_download(url, version_info, md5sum):
    prefix = 'https://www.python.org/ftp/python/{v}/python-{v}'.format(
        v='.'.join(str(s) for s in version_info),
    )
    if not url.startswith(prefix):
        raise ValueError('{} is not from version {}'.format(url, version_info))

    checksum = hashlib.md5(download_data(url)).hexdigest()
    if checksum != md5sum:
        raise AssertionError('{} != {} (expected)'.format(checksum, md5sum))


def check_cpython(info):
    check_download(info['url'], info['version_info'], info['md5_sum'])


def check_cpython_msi(info):
    for variant in ['x86', 'amd64']:
        check_download(
            info[variant]['url'],
            info['version_info'],
            info[variant]['md5_sum'],
        )


CHECKERS = {
    'cpython': check_cpython,
    'cpython_msi': check_cpython_msi,
}


def main():
    if len(sys.argv) < 2:
        raise ValueError('no versions provided')
    for v in sys.argv[1:]:
        path = pathlib.Path(__file__).parent.parent.joinpath(
            'snafu', 'versions', '{}.json'.format(v),
        )
        with path.open() as f:
            info = json.load(f)
        CHECKERS[info['type']](info)
        print('Version', v, 'is OK!')


if __name__ == '__main__':
    main()
