import json

import backup_zipfile as buz


def main(db, arc_name):

    with open(db, 'r') as _db:
        jsn = _db.read()
    files = json.loads(jsn)

    crcs = {}

    for data_filename, src_hash in files['known_files'].items():

        if arc_name not in src_hash:
            continue

        for zip_filename, details in src_hash.items():
            # details = src_hash[arc_name]
            print('zipfilename: ', zip_filename, 'data_filename', data_filename, details['crc'])
            src_list_by_crc = crcs.setdefault(details['crc'], [])
            src_list_by_crc.append((zip_filename, data_filename, details['timestamp']))

    for crc, lst in crcs.items():

        #print('zip: ', lst[0])
        if len(lst) < 2:
            continue
        lst.sort(key=lambda x: x[2], reverse=True)
        newest, rest = lst[0], lst[1:]
        if newest[0] == arc_name:
            continue

        def are_equal(newest, item):
            zipnm1, nm1 = newest[0:2]
            zipnm2, nm2 = item[0:2]
            zip1 = buz.BackupFile(zipnm1)
            zip2 = buz.BackupFile(zipnm2)
            f1 = zip1.open(zip1.getinfo(nm1))
            f2 = zip2.open(zip2.getinfo(nm2))
            d1 = 1
            while d1:
                d1 = f1.read(1024)
                d2 = f2.read(1024)
                if d1 != d2:
                    return False
            return True

        for item in rest:
            # print('another item')
            if are_equal(newest, item):
                print("for crc {} newest zip for file {} is {} ".format(crc, newest[1], newest[0]))

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description="duplicate finder")
    parser.add_argument('-d', '--database', dest='db', help="name of json database file")
    parser.add_argument('arc', nargs=1, help="name of archive file")
    arguments = parser.parse_args()
    print('args => {}'.format(arguments))

    assert len(arguments.arc) == 1, len(arguments.arc)
    main(arguments.db, arguments.arc[0])