import json


def main(db):

    with open(db, 'r') as _db:
        jsn = _db.read()
    files = json.loads(jsn)

    crcs = {}

    for data_filename, src_hash in files['known_files'].items():

        for zip_filename, details in src_hash.items():
            #print('zipfilename: ', zip_filename, 'data_filename', data_filename, details['crc'])
            src_list_by_crc = crcs.setdefault(details['crc'], [])
            src_list_by_crc.append((zip_filename, data_filename, details['timestamp']))


    for crc, lst in crcs.items():
        if len(lst) < 2:
            continue
        lst.sort(key=lambda x: x[2], reverse=True)
        newest, rest = lst[0], lst[1:]

        def are_equal(newest, item):
            pass
            # open filehandles from each source, and compare whole files

        for item in rest:
            if are_equal(newest, item):
                print(newest[0], item[0])

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description="duplicate finder")
    parser.add_argument('-d', '--database', dest='db', help="name of json database file")
    arguments = parser.parse_args()
    print('args => {}'.format(arguments))

    main(arguments.db)