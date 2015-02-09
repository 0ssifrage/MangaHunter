import cookielib
import json
import os
import sys
import urllib
import urllib2
import zipfile


class MangaHunter():
    def __init__(self):
        self.manga_id = 0
        self.chapter_list = {'manga_id': 0, 'data': []}

    def select_manga(self, cid=4, page=1):
        url = 'http://m.ac.qq.com/GetData/getCategoryOpus'
        url = '%s?ver=1&cid=%i&page=%i' % (url, cid, page)
        data = urllib2.urlopen(url).read()
        manga_list = json.loads(data)
        idx = 0
        for m in manga_list:
            idx += 1
            print idx, m['title']
        opt = input('Select: ')
        self.manga_id = int(manga_list[opt-1]['id'])

    def get_chapter_list(self, manga_id=-1):
        def cmp_func(x, y):
            if not x.isdecimal():
                return 1
            if not y.isdecimal():
                return -1
            return cmp(int(x), int(y))

        if manga_id == -1:
            manga_id = self.manga_id
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

    def get_pics_list(self, chapter_id, manga_id=-1):
        if manga_id == -1:
            manga_id = self.manga_id
        url = "http://m.ac.qq.com/View/mGetPicHash?id=%i&cid=%i" % (
            manga_id, chapter_id
        )
        rurl = "http://m.ac.qq.com/Comic/view/id/%i/cid/%i" % (
            manga_id, chapter_id
        )
        req = urllib2.Request(url)
        req.add_header("Cookie", "ac_refer=%s; ac_random_token_view=%s;" % (
            "http%3A%2F%2Fm.ac.qq.com%2F",
            "a621eaf4250d9fd3f8578bf116ba8358"
        ))
        req.add_header("Referer", rurl)
        data = urllib2.urlopen(req).read()
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

    def download_pics(self, chapter, display=False, base_dir='manga/',
                      manga_id=-1):
        if manga_id == -1:
            manga_id = self.manga_id
        if (manga_id != self.chapter_list['manga_id']):
            self.get_chapter_list(manga_id)
        chapter_id = self.chapter_list['data'][chapter][0]
        pics_list = self.get_pics_list(chapter_id, manga_id)
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

    def download_pics_zip(self, chapter, display=False,
                          base_dir='manga/', manga_id=-1):
        if manga_id == -1:
            manga_id = self.manga_id
        if (manga_id != self.chapter_list['manga_id']):
            self.get_chapter_list(manga_id)
        chapter_id = self.chapter_list['data'][chapter][0]
        pics_list = self.get_pics_list(chapter_id, manga_id)
        url_base = self._get_pics_url_base(manga_id, chapter_id)

        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
        zipfile_path = os.path.join(base_dir, '%03i.zip' % chapter)
        f = zipfile.ZipFile(zipfile_path, 'w')
        p_sum = len(pics_list['pHash'])
        idx = 0
        for pic in pics_list['pHash'].values():
            idx += 1
            pic_name = '%03i/%03i.jpg' % (chapter, int(pic['seq']))
            pic_id = int(pic['pid'])
            pic_url = self._get_pic_url(url_base, manga_id, chapter_id,
                                        pic_id)
            if display:
                sys.stdout.write('\r    (%i/%i) Downloading %s...' % (
                    idx, p_sum, pic_name))
                sys.stdout.flush()

            f.writestr(pic_name, urllib2.urlopen(pic_url).read())
        f.close()
        if display:
            sys.stdout.write('\r\n')
            sys.stdout.flush()

    def print_chapter_name(self, start=1, end=99999, manga_id=-1):
        if manga_id == -1:
            manga_id = self.manga_id
        self.get_chapter_list(manga_id)
        start = max(1, start)
        end = min(end, len(self.chapter_list['data']))
        for i in range(start, end + 1):
            print "[%03i] %s" % (i, chapter_list[i][1])

    def download_batch(self, start=1, end=99999, zip=True, display=False,
                       base_dir='manga/', manga_id=-1):
        if manga_id == -1:
            manga_id = self.manga_id
        self.get_chapter_list(manga_id)
        start = max(1, start)
        end = min(end, len(self.chapter_list['data']))
        ch_sum = end + 1 - start
        for i in range(start, end + 1):
            if display:
                print '[%i/%i] Downloading %3i...' % (i-start+1, ch_sum, i)
            if zip:
                self.download_pics_zip(i, display, base_dir, manga_id)
            else:
                self.download_pics(i, display, base_dir, manga_id)


def test():
    mh = MangaHunter()
    mh.select_manga()
    mh.download_batch(400, 401, display=True)

if __name__ == "__main__":
    test()
