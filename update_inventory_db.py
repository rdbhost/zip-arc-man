
import sys
import os.path
import copy

import json
import datetime

import backup_zipfile


def get_filename(itm):
    filename = itm.filename
    cmt = itm.comment.decode()
    if ':' in cmt:
        filename = '/'.join([cmt, filename])
    return filename

def add_backup_file(src, inv):

    del_keys = []
    for k, itms in inv['known_files'].items():
        if src in itms:
            del itms[src]
        if len(itms) == 0:
            del_keys.append(k)
    for k in del_keys:
        del inv['known_files'][k]

    if not os.path.exists(src):
        print('file {} was not found'.format(src))
        return

    with backup_zipfile.BackupFile(src, mode='r') as bu:

        for itm in bu.infolist():

            if not itm.filename or itm.is_dir():
                continue

            filename = get_filename(itm)

            fn = inv['known_files'].setdefault(filename, {})
            timestamp = bu.time_stamp.timestamp() # itm.date_time.timestamp()
            fn[bu.filename] = {'timestamp': timestamp}
            f = fn[bu.filename]
            f['status'] = 'raw'
            f['crc'] = itm.CRC
            f['filesize'] = itm.file_size
            assert f.get('status') and f.get('crc') is not None, (filename, itm.CRC)

def main(db, srcs, new=False):

    assert len(srcs) > 0
    try:
        if new:
            # check that db does not exist.
            jsn = '{"known_files": {}}'
            with open(db, 'x') as _db:
                _db.write(jsn)
        else:
            with open(db, 'r') as _db:
                jsn = _db.read()
    except OSError as e:
        print (e)
        return

    prev_inv = json.loads(jsn)
    for src in srcs:

        print('processing source {}'.format(src))
        add_backup_file(src, prev_inv)

    blob = json.dumps(prev_inv, indent=2)
    print('writing new/changed inventory of length {}'.format(len(blob)))
    with open(db, 'w') as bu:
        bu.write(blob)


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description="inventory updater")
    parser.add_argument('args', nargs='+', help="names of source files")
    parser.add_argument('-d', '--database', dest='db', help="name of json database file", 
                         required=True)

    parser.add_argument('--new', dest='mustcreate', action='store_true',
                        help="if json database does not exist")
    args = parser.parse_args()
    print('args => {}'.format(args))

    main(args.db, args.args, args.mustcreate)

