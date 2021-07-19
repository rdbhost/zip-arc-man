
import os.path
import zipfile
import datetime

class FileInfo:

    def __init__(self, _='Nope', date_time=datetime.datetime.now(), status='raw', filesize=0):
        if isinstance(_, zipfile.ZipInfo):
            if _.filename[1] != ':':
                self.filename = os.path.join(_.comment.decode(), "/", _.filename)
            else:
                self.filename = _.filename
            self.date_time = datetime.datetime(*_.date_time)
            self.comment = _.comment
            self.CRC = _.CRC
            self.file_size = _.file_size

        else:
            self.filename = _
            self.date_time = date_time
            self.comment = b''
            self.CRC = ''
            self.file_size = filesize

        self.status = status

    def is_dir(self):
        return False


class BackupFile:

    SPECIAL_FILENAMES = []

    def __init__(self, src, mode='r'):
        self.filename = src
        self._mode = mode
        self._dirty = False
        self.special = {}

        t = os.path.getctime(self.filename)
        self.time_stamp = datetime.datetime.fromtimestamp(t)
        self._zip = zipfile.ZipFile(self.filename, mode=self._mode)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._zip.close()

    def _handle_special(self, itm):
        # add to contents of self.special[name]
        raise Exception('special filename {} not handled'.format(itm.filename))

    def infolist(self):
        il = []
        for itm in self._zip.infolist():
            if itm.is_dir():
                continue
            if itm.filename in self.SPECIAL_FILENAMES:
                self._handle_special(itm)
            else:
                fi = FileInfo(itm)
                il.append(fi)
        # add special file-info here
        return il

    def close(self):
        self._zip.close()

    def getinfo(self, filenm):
        t = self.infolist()
        for itm in t:
            if itm.filename == filenm:
                return itm
        raise KeyError('{} not found in {}'.format(filenm, self.filename))

    def open(self, bui, mode='r'):
        assert bui.status == 'raw'
        fname = bui.filename
        if fname[1] == ':':
            fname = fname[3:]
        return self._zip.open(fname, mode)