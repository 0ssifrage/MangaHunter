import json
import os
import urllib
import urllib2

manga_num = {
    'gintama': 505435
}


class MangaHunter():
    def get_chapter_list(self, manga_id):
        url = "http://m.ac.qq.com/GetData/getChapterList?id=%i" % manga_id
        data = urllib2.urlopen(url).read()
        chapter_list = json.loads(data)
        return chapter_list

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
        pic_url = "%s&uin=%i&name=%i.mif2" % (
            url_base, uin, pic_id
        )
        return pic_url

    def download_pics(self, manga_id, chapter_id, base_dir=''):
        pics_list = self.get_pics_list(manga_id, chapter_id)
        url_base = self._get_pics_url_base(manga_id, chapter_id)

        folder = os.path.join(base_dir, '%i' % chapter_id)
        if not os.path.exists(folder):
            os.mkdir(folder)
        for pic in pics_list['pHash'].values():
            filepath = os.path.join(folder, '%02i.jpg' % int(pic['seq']))
            if not os.path.exists(filepath):
                pic_id = int(pic['pid'])
                pic_url = self._get_pic_url(url_base, manga_id, chapter_id,
                                            pic_id)
                f = open(filepath, 'w')
                f.write(urllib2.urlopen(pic_url).read())
                f.close()


def main():
    mh = MangaHunter()
    mh.download_pics(manga_num['gintama'], 481)

if __name__ == "__main__":
    main()
