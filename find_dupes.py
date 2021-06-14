import json


def main(db, arc_name):

    with open(db, 'r') as _db:
        jsn = _db.read()
    files = json.loads(jsn)

    crcs = {}

    for data_filename, src_hash in files['known_files'].items():

        if arc_name in src_hash:
            for zip_filename, details in src_hash.items():
                # details = src_hash[arc_name]
                print('zipfilename: ', arc_name, 'data_filename', data_filename, details['crc'])
                src_list_by_crc = crcs.setdefault(details['crc'], [])
                src_list_by_crc.append((zip_filename, data_filename, details['timestamp']))

    for crc, lst in crcs.items():

        print('zip: ', lst[0])
        if len(lst) < 2:
            continue
        lst.sort(key=lambda x: x[2], reverse=True)
        newest, rest = lst[0], lst[1:]
        if newest[0] == arc_name:
            continue

        def are_equal(newest, item):
            return True
            # open filehandles from each source, and compare whole files

        for item in rest:
            # print('another item')
            if are_equal(newest, item):
                print(newest[0], item[0])

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description="duplicate finder")
    parser.add_argument('-d', '--database', dest='db', help="name of json database file")
    parser.add_argument('arc', nargs=1, help="name of archive file")
    arguments = parser.parse_args()
    print('args => {}'.format(arguments))

    assert len(arguments.arc) == 1, len(arguments.arc)
    main(arguments.db, arguments.arc[0])