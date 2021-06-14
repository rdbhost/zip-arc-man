
import sys
import os.path
import copy

import zipfile
import json
import datetime


def inventories_are_different(backup, zi, blob):

    if zi is None:
        return True
    blob1 = blob.encode()
    inv1 = json.loads(blob1)
    b1 = json.dumps(inv1, sort_keys=True, indent=False)

    blob0 = backup.open(zi).read()
    inv0 = json.loads(blob0)
    b0 = json.dumps(inv0, sort_keys=True, indent=False)
    # print('blob sizes are {} and {}'.format(len(blob0), len(blob1)))
    return b0 != b1

def merge(inv, crcs, other):

    # known files
    kfs = inv['known_files']
    for filename, file_rec in other['known_files'].items():
        kf = inv['known_files'].setdefault(filename, {})
        kf.update(file_rec)

        for src, item in kf.items():
            if item['status'] != 'raw':
                continue
            crc = item['crc']
            if crc in crcs and item['timestamp'] < crcs[crc]['timestamp']:
                continue
            crcs[crc] = {'timestamp': item['timestamp'], 'backup_file': src, 'filename': filename}

def get_filename(itm):
    filename = itm.filename
    cmt = itm.comment.decode()
    if ':' in cmt:
        filename = '/'.join([cmt, filename])
    return filename

def add_backup_file(src, crcs, inv):

    with zipfile.ZipFile(src, mode='r') as bu:

        del_keys = []
        for k, itms in inv['known_files'].items():
            if bu.filename in itms:
                del itms[bu.filename]
            if len(itms) == 0:
                del_keys.append(k)
        for k in del_keys:
            del inv['known_files'][k]

        crc_dupe_count = 0
        for itm in bu.infolist():

            if not itm.filename or itm.is_dir():
                continue

            filename = get_filename(itm)

            fn = inv['known_files'].setdefault(filename, {})
            timestamp = datetime.datetime(*itm.date_time).timestamp()
            fn[bu.filename] = {'timestamp': timestamp}
            f = fn[bu.filename]
            f['status'] = 'raw'
            f['crc'] = itm.CRC
            f['filesize'] = itm.file_size
            assert f.get('status') and f.get('crc') is not None, (filename, itm.CRC)

            if itm.CRC in crcs:
                crc_dupe_count += 1

            crc = itm.CRC
            if crc in crcs and timestamp < crcs[crc]['timestamp']:
                continue
            crcs[crc] = {'timestamp': timestamp, 'backup_file': bu.filename, 'filename': filename}

        if crc_dupe_count > 0:
            print('found duplicate {0} crcs in {1}'.format(crc_dupe_count, bu.filename))


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
    crcs = {}
    for src in srcs:

        print('processing source {}'.format(src))
        add_backup_file(src, crcs, prev_inv)

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

