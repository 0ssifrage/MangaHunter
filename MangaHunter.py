import json
import os
import urllib
import urllib2
import zipfile

manga_num = {
    'gintama': 505435
}


class MangaHunter():
    def __init__(self):
        self.manga_id = 0
        self.chapter_list = {'manga_id': 0, 'data': []}

    def get_chapter_list(self, manga_id):
        def cmp_func(x, y):
            if not x.isdecimal():
                return 1
            if not y.isdecimal():
                return -1
            return cmp(int(x), int(y))

        url = "http://m.ac.qq.com/GetData/getChapterList?id=%i" % manga_id
        data = urllib2.urlopen(url).read()
        clist = json.loads(data)
        k = clist.keys()
        k.sort(cmp=cmp_func)

        chapter_list = {}
        for ch in k:
            if ch.isdecimal():
                chapter_list[clist[ch]['seq']+1] = [int(ch), clist[ch]['t']]

        self.chapter_list['manga_id'] = manga_id
        self.chapter_list['data'] = chapter_list

    def get_pics_list(self, manga_id, chapter_id):
        url = "http://m.ac.qq.com/view/mGetPicHash?id=%i&cid=%i" % (
            manga_id, chapter_id
        )
        data = urllib2.urlopen(url).read()
        pics_list = json.loads(data)
        return pics_list

    def _get_pics_url_base(self, manga_id, chapter_id):
        dir_path = '/mif800/%i/%i/%i/%i/' % (
            manga_id % 1000 / 100,
            manga_id % 100,
            manga_id,
            chapter_id
        )
        build = 15017
        data = urllib.urlencode({
            'dir_path': dir_path,
            'buid': '15017'
        })
        res = 'http://ac.tc.qq.com/store_file_download?%s' % data
        return res

    def _get_pic_url(self, url_base, manga_id, chapter_id, pic_id):
        uin = max(manga_id + chapter_id + pic_id, 10001)
        pic_url = "%s&uin=%i&name=%i.mif2" % (url_base, uin, pic_id)
        return pic_url

    def download_pics(self, manga_id, chapter, base_dir='manga/'):
        if (manga_id != self.chapter_list['manga_id']):
            self.get_chapter_list(manga_id)
        chapter_id = self.chapter_list['data'][chapter][0]
        pics_list = self.get_pics_list(manga_id, chapter_id)
        url_base = self._get_pics_url_base(manga_id, chapter_id)

        folder = os.path.join(base_dir, '%03i' % chapter)
        if not os.path.exists(folder):
            os.mkdir(folder)
        for pic in pics_list['pHash'].values():
            filepath = os.path.join(folder, '%03i.jpg' % int(pic['seq']))
            if not os.path.exists(filepath):
                pic_id = int(pic['pid'])
                pic_url = self._get_pic_url(url_base, manga_id, chapter_id,
                                            pic_id)
                f = open(filepath, 'wb')
                f.write(urllib2.urlopen(pic_url).read())
                f.close()

    def download_pics_zip(self, manga_id, chapter, base_dir='manga/'):
        if (manga_id != self.chapter_list['manga_id']):
            self.get_chapter_list(manga_id)
        chapter_id = self.chapter_list['data'][chapter][0]
        pics_list = self.get_pics_list(manga_id, chapter_id)
        url_base = self._get_pics_url_base(manga_id, chapter_id)

        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
        zipfile_path = os.path.join(base_dir, '%03i.zip' % chapter)
        f = zipfile.ZipFile(zipfile_path, 'w')
        for pic in pics_list['pHash'].values():
            pic_name = '%03i/%03i.jpg' % (chapter, int(pic['seq']))
            pic_id = int(pic['pid'])
            pic_url = self._get_pic_url(url_base, manga_id, chapter_id,
                                        pic_id)
            f.writestr(pic_name, urllib2.urlopen(pic_url).read())
        f.close()

    def print_chapter_name(self, manga_id, start=1, end=99999):
        self.get_chapter_list(manga_id)
        start = max(1, start)
        end = min(end, len(self.chapter_list['data']))
        for i in range(start, end + 1):
            print "[%03i] %s" % (i, chapter_list[i][1])

    def download_batch(self, manga_id, start=1, end=99999, zip=True,
                       base_dir='manga/'):
        self.get_chapter_list(manga_id)
        start = max(1, start)
        end = min(end, len(self.chapter_list['data']))
        for i in range(start, end + 1):
            if zip:
                self.download_pics_zip(manga_id, i, base_dir)
            else:
                self.download_pics(manga_id, i, base_dir)


def test():
    mh = MangaHunter()
    # mh.download_pics_zip(manga_num['gintama'], 509)
    mh.download_batch(manga_num['gintama'], 470, 472)

if __name__ == "__main__":
    test()
