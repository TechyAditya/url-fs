from fuse import FUSE, FuseOSError, Operations, LoggingMixIn
import requests
import stat

class HttpFs(LoggingMixIn, Operations):
    def __init__(self, url_dict):
        self.url_dict = url_dict
        self.file_attrs = {}
        for filename, url in url_dict.items():
            self.file_attrs[filename] = {
                'st_mode': (stat.S_IFREG | 0o444),
                'st_nlink': 1,
                'st_size': self.get_size(url),
                'st_ctime': 0,
                'st_mtime': 0,
                'st_atime': 0
            }

    def get_size(self, url):
        response = requests.head(url)
        return int(response.headers['content-length'])

    def getattr(self, path, fh=None):
        if path == '/':
            return {'st_mode': (stat.S_IFDIR | 0o555), 'st_nlink': 2}
        elif path.lstrip('/') in self.file_attrs:
            return self.file_attrs[path.lstrip('/')]
        else:
            raise FuseOSError(2)  # No such file or directory

    def read(self, path, size, offset, fh):
        url = self.url_dict.get(path.lstrip('/'))
        if url:
            headers = {'Range': f"bytes={offset}-{offset + size - 1}"}
            response = requests.get(url, headers=headers)
            return response.content

    def readdir(self, path, fh):
        return ['.', '..'] + list(self.file_attrs.keys())

if __name__ == '__main__':
    # Replace this dictionary with your filenames and URLs
    url_dict = {
        'file1.exe': 'https://dl.google.com/drive-file-stream/GoogleDriveSetup.exe',
        'file2.exe': 'https://dl.google.com/tag/s/appguid%3D%7B8A69D345-D564-463C-AFF1-A69D9E530F96%7D%26iid%3D%7B776A2EA1-96A7-E95F-F377-1401C9096D47%7D%26lang%3Den%26browser%3D5%26usagestats%3D1%26appname%3DGoogle%2520Chrome%26needsadmin%3Dprefers%26ap%3Dx64-stable-statsdef_1%26installdataindex%3Dempty/chrome/install/ChromeStandaloneSetup64.exe',
        # Add more files as needed
    }

    # Replace the mount point with your desired local mount path
    mount_point = '/home/aditya/httpfslink/1'

    FUSE(HttpFs(url_dict), mount_point, nothreads=True, foreground=True)
