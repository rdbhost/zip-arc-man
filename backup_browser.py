
#!/usr/bin/env python
import sys
import os
import PySimpleGUI as sg
import json
from datetime import datetime
import arrow
from pathlib import PureWindowsPath

"""

"""

# Base64 versions of images of a folder and a file. PNG files (may not work with PySimpleGUI27, swap with GIFs)

folder_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABnUlEQVQ4y8WSv2rUQRSFv7vZgJFFsQg2EkWb4AvEJ8hqKVilSmFn3iNvIAp21oIW9haihBRKiqwElMVsIJjNrprsOr/5dyzml3UhEQIWHhjmcpn7zblw4B9lJ8Xag9mlmQb3AJzX3tOX8Tngzg349q7t5xcfzpKGhOFHnjx+9qLTzW8wsmFTL2Gzk7Y2O/k9kCbtwUZbV+Zvo8Md3PALrjoiqsKSR9ljpAJpwOsNtlfXfRvoNU8Arr/NsVo0ry5z4dZN5hoGqEzYDChBOoKwS/vSq0XW3y5NAI/uN1cvLqzQur4MCpBGEEd1PQDfQ74HYR+LfeQOAOYAmgAmbly+dgfid5CHPIKqC74L8RDyGPIYy7+QQjFWa7ICsQ8SpB/IfcJSDVMAJUwJkYDMNOEPIBxA/gnuMyYPijXAI3lMse7FGnIKsIuqrxgRSeXOoYZUCI8pIKW/OHA7kD2YYcpAKgM5ABXk4qSsdJaDOMCsgTIYAlL5TQFTyUIZDmev0N/bnwqnylEBQS45UKnHx/lUlFvA3fo+jwR8ALb47/oNma38cuqiJ9AAAAAASUVORK5CYII='
file_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABU0lEQVQ4y52TzStEURiHn/ecc6XG54JSdlMkNhYWsiILS0lsJaUsLW2Mv8CfIDtr2VtbY4GUEvmIZnKbZsY977Uwt2HcyW1+dTZvt6fn9557BGB+aaNQKBR2ifkbgWR+cX13ubO1svz++niVTA1ArDHDg91UahHFsMxbKWycYsjze4muTsP64vT43v7hSf/A0FgdjQPQWAmco68nB+T+SFSqNUQgcIbN1bn8Z3RwvL22MAvcu8TACFgrpMVZ4aUYcn77BMDkxGgemAGOHIBXxRjBWZMKoCPA2h6qEUSRR2MF6GxUUMUaIUgBCNTnAcm3H2G5YQfgvccYIXAtDH7FoKq/AaqKlbrBj2trFVXfBPAea4SOIIsBeN9kkCwxsNkAqRWy7+B7Z00G3xVc2wZeMSI4S7sVYkSk5Z/4PyBWROqvox3A28PN2cjUwinQC9QyckKALxj4kv2auK0xAAAAAElFTkSuQmCC'
vers_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAICSURBVDhPhVNNSBtREP52s5vsJvFfatBcbBBbpILH0pvioQgt/uLdQ/BcSi+BGjwL7akIgbaHnvTQFutBEQQvVnoLFqUICoIasprFJCayu3bm6WrWhHYe376dj5nvzcy+lUA2MDw1k0wm3+KKvXvGETd8end/OzE9PmYYR7suK/MDDhB9UIfSpYVcvoifW5s4Mc5gmHkYuTxOTk2ENRlTw097Zt59XmpujjymLHG4EHBoqYqCxvoQRvt7kXo/iwszg462FoG2lkZIFK4qMuKTA7HE3KfvlBa9E3AcyBTg80nY3D7Eo57eW5+hEDJUSXrvGDsHGfQ96Y5R2jOvAGUoPllA1zRKvH5nBPwqVVePsiWhUKJ6r6hnQOPHrYCPBFQKXv3xFTu/01hd/iZ8P0EPqKgLagINYR22LQSECQHLuq6Ae3w5MoYvC0t49SYhfIXAu4uAXxEHunZXAU2JT+SgkK4JCL8GHMcWyWw3ApZowa9SySQg9n+gqgV3iLVO21hfQ6lY8HA1W3BnUIkXQ4MoFs7R1dnu4W37XgsWz4AE3M/mIpX6iFPDQDw+7eGrK+CvQEPkC1OJWKwTExPjmJ//4OFrtiCRAF+eSoRDQXS0R6DrQQ9fLUCL7zp14UG5XEI2m4Vp5jx8pQC5QFPk4fPWaNdr+kMbyL1k7n/259fKHIDFvzvQuWlZRnVcAAAAAElFTkSuQmCC'

def sizeof_fmt(num, suffix=''):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def burrow_past_singles(pytree):
    pt = pytree
    path_segs = []
    while len(pt) == 1:
        k = list(pt.keys())[0]
        path_segs.append(k)
        pt = pt[k]

    return os.path.join(*path_segs), pt

def create_tree(db):

    def add_to_tree(pytree, filename, src_hash):

        pth = PureWindowsPath(filename)
        parts = list(pth.parts)

        root = pytree
        for p in parts[:-1]:
            if p not in root:
                root[p] = {}
            root = root[p]
        root[pth.name] = []

        for path, itm in src_hash.items():
            itm['path'] = path
            root[pth.name].append(itm)

    def transfer_trees(pytree, treedata):

        def transfer(subtree, td_parent, pth_seg):
            key = os.path.join(td_parent, pth_seg)
            if isinstance(subtree[pth_seg], dict):
                treedata.Insert(td_parent, key, pth_seg, [], icon=folder_icon)
                for nxt_seg in subtree[pth_seg].keys():
                    transfer(subtree[pth_seg], key, nxt_seg)
            elif isinstance(subtree[pth_seg], list):
                treedata.Insert(td_parent, key, pth_seg, [], icon=file_icon)
                srcs = sorted(subtree[pth_seg], key=lambda x: -x['timestamp'])
                for src in srcs:
                    key1 = key+src['path']
                    cols = [sizeof_fmt(src['filesize']),
                            datetime.fromtimestamp(src['timestamp']).strftime("%d %b %y %H:%M")]
                    src_name = 'SRC==> '+arrow.get(src['timestamp']).humanize()+' '+src['path']
                    treedata.Insert(key, key1, src_name, cols, icon=vers_icon)
            else:
                raise Exception(type(subtree[pth_seg]))

        for ptk in pytree.keys():
            transfer(pytree, '', ptk)

    with open(db, 'r') as _db:
        jsn = _db.read()
    files = json.loads(jsn)

    pytree = {}
    for filename, src_hash in files['known_files'].items():
        add_to_tree(pytree, filename, src_hash)

    pth, pytree = burrow_past_singles(pytree)

    treedata = sg.TreeData()
    transfer_trees(pytree, treedata)
    return pth, treedata

def create_window(base_pth, treedata):

    path_label = sg.Text(base_pth)
    layout = [[path_label],
              [sg.Tree(data=treedata,
                       headings=['  Size  ','    Date       '],
                       #auto_size_columns=True,
                       #col_widths=[40,40,40],
                       num_rows=20,
                       col0_width=60,
                       def_col_width=15,
                       key='-TREE-',
                       show_expanded=False,
                       enable_events=True),
               ],
              [sg.Button('Ok'), sg.Button('Cancel')]]

    window = sg.Window('Backup Zip Manager', layout)

    return window

def quit(evt, vals):
    print(evt, vals)
    exit(0)


if __name__ == '__main__':

    from argparse import ArgumentParser
    parser = ArgumentParser(description="inventory updater")
    parser.add_argument('-d', '--database', dest='db', help="name of json database file")
    args = parser.parse_args()
    print('args => {}'.format(args))

    base_pth, treedata = create_tree(args.db)
    window = create_window(base_pth, treedata)

    while True:     # Event Loop
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Cancel'):
            quit(event, values)
            break
        print(event, values)
    window.close()

