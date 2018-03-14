import requests
import json
from urllib.parse import urlencode
from config import *
import os
import pickle
from multiprocessing import Process,Pool


def get_form_url(person):
    urls = []
    for i in range(1, 10000):
        person['page'] = i
        url = 'https://m.weibo.cn/api/container/getIndex?' + urlencode(person)
        urls.append(url)
    return urls


def get_pic_url(urls):
    pic_urls = []
    for url in urls:
        try:
            content = requests.get(url).content.decode('utf-8')
            data = json.loads(content)
            cards = data['data']['cards']
            if cards:
                for card in cards:
                    try:
                        pics = card['mblog']['pics']
                        for pic in pics:
                            pic_url = pic['large']['url']
                            if pic_url:
                                pic_urls.append(pic_url)
                                print('获取图片地址：', pic_url)
                    except:
                        continue
            else:
                print('已无更多图片')
                break
        except:
            continue
    return pic_urls


def download_img(url, path):
    file_name = url.split('/')[-1]
    file_path = path + file_name
    content = requests.get(url).content
    try:
        if not os.path.isfile(file_path):
            with open(file_path, 'wb') as f:
                f.write(content)
                print('已保存到:', file_path)
    except:
        print('保存失败')
        raise


def get_pics(pic_urls, person):
    print('start download',person['lfid'])
    path = ABS_PATH + person['lfid'].split('=')[-1] + '/'
    if not os.path.exists(ABS_PATH):
        os.mkdir(ABS_PATH)
    if not os.path.exists(path):
        os.mkdir(path)
    # save_as_pickle(path, pic_urls)
    for pic_url in pic_urls:
        print('now downloading',pic_url)
        download_img(pic_url, path)


def save_as_pickle(path, pic_urls):
    path = path + path.split('/')[-1] + '.pickle'
    if not os.path.isfile(path):
        with open(path, 'wb') as f:
            pickle.dump(pic_urls, f)
    else:
        with open(path, 'wb') as f:
            pic_urls = pickle.load(f)


def downloader(person):
    urls = get_form_url(person)
    pic_urls = get_pic_url(urls)
    print('{0}共获得{1}张照片地址'.format(person['lfid'],len(pic_urls)))
    get_pics(pic_urls, person)


if __name__ == '__main__':
    p=Pool()
    p.apply_async(downloader,args=(YA_TING,))
    p.apply_async(downloader,args=(WU_CHUN_YI,))
    p.close()
    p.join()