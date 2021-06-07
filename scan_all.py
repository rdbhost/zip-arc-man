
import glob
import os.path
import itertools
import subprocess


def main(db, args):

    #assert os.path.isfile(db), 'db {} does not exist'.format(db)
    curpath = os.path.dirname(os.path.abspath(__file__))

    for src in args:
        new_str = '--new' if not os.path.isfile(db) else ''
        update_py = os.path.join(curpath, 'update_inventory_db.py')
        assert os.path.isfile(src), 'source {} does not exist'.format(src)
        
        res = subprocess.run('python {} {} -d {} "{}"'.format(update_py, new_str, db, src), capture_output=True)   
        print(src)
        if res.stderr:
            print(res.stderr.decode())
        res.check_returncode()


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description="inventory updater")
    parser.add_argument('args', nargs='+', help="names of source files")
    parser.add_argument('-d', '--database', dest='db', help="name of json database file")

    arguments = parser.parse_args()
    print('args => {}'.format(arguments))

    args = list(itertools.chain(*[glob.glob(x) for x in arguments.args]))
    args = list(dict.fromkeys(args))
    #print(args)

    main(arguments.db, args)

