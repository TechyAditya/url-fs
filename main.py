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
        'file1.txt': 'https://example.com/file1.txt',
        'file2.txt': 'https://example.com/file2.txt',
        # Add more files as needed
    }

    # Replace the mount point with your desired local mount path
    mount_point = '/path/to/mount'

    FUSE(HttpFs(url_dict), mount_point, nothreads=True, foreground=True)
