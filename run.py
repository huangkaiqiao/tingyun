import json
import logging
import logging.config
import os
import re

from bs4 import BeautifulSoup
import requests

logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)
HOST = 'https://novel18.syosetu.com'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
COOKIE = 'ses=7hjuv130h6drqqp5r8r1u49qq2; over18=yes; ks2=cqqmyc7t51e;'

# AUTHOR = {'id':'x6713d', 'name': 'ulth'}
# AUTHOR = {'id':'x6729d', 'name': '二守透谷'}
# AUTHOR = {'id':'x8657y', 'name': '相原アキラ'}
# AUTHOR = {'id':'x5557p', 'name': 'ジョニー003'}
# AUTHOR = {'id':'x7748p', 'name': '三紋昨夏（サンモン・サッカ）'}
# AUTHOR = {'id':'x8570b', 'name': 'きー子'}
# AUTHOR = {'id':'X2500K', 'name': '裏側ざん'}
# AUTHOR = {'id':'x3274i', 'name': '露鳥下種'}
# AUTHOR = {'id':'x0043r', 'name': 'メガダノン'}
# AUTHOR = {'id':'x8089u', 'name': 'かしわもち'}
# AUTHOR = {'id':'x6723bm', 'name': 'ふわふわらいどう'}
AUTHOR = {'id':'x9541bs', 'name': 'だいこん'}

def write_md(subtitle, body, properties):
    ''' 抓取的小说某一章节保存为 markdown 文件 '''
    p = properties
    author = p['author']
    id = p['id']
    ch = p['index']
    filename = f'./dist/{author}/{id}/{ch}.md'
    if ch == -1:
        filename = f'./dist/{author}/{id}.md'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as out:
        out.write(f'# {subtitle} #\n{body}')

def write_readme_md(title, body, properties):
    ''' 抓取的小说介绍保存为 markdown 文件 '''
    p = properties
    author = p['author']
    id = p['id']
    # ch = p['index']
    filename = f'./dist/{author}/{id}/README.md'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as out:
        out.write(f'# {title} #\n{body}')

def write_collection_data(novel_links, author):
    ''' 获取到的所有小说信息保存为 json 文件 '''
    filename = f'./dist/{author}/collection_data.json'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as out:
        out.write(json.dumps(novel_links))

def get_novel_links(soup):
    ''' 获取某一页面中所有的小说信息 '''
    alist = soup.select('.title a')
    res = []
    for a in alist:
        d = {'url': a['href'], 'title': a.text}
        res.append(d)
    return res

def fetch_novel(url):
    ''' 抓取某一本小说的所有章节信息 '''
    # url = 'https://novel18.syosetu.com/n8731hi/'
    # id = 'n8731hi'
    # url = f'{HOST}/{id}/'
    # cookie = 'ses=7hjuv130h6drqqp5r8r1u49qq2; _ga_CQ4S04X1ZS=GS1.1.1688612610.1.0.1688612613.0.0.0; _ga=GA1.1.429152197.1688612610; over18=yes; ks2=cqqmyc7t51e; sasieno=0; lineheight=0; fontsize=0; novellayout=0; fix_menu_bar=1; _ga_C6X74G3CHV=GS1.1.1688631024.3.1.1688632421.0.0.0; nlist3=zyn0.1'
    logger.info(f'tingyun: current novel url to be fetched is {url}')
    pattern = '(?<=https://novel18.syosetu.com/)\w*(?=/)'
    regex = re.compile(pattern)
    m = regex.search(url)
    id = m.group(0)
    # 跳过已经抓取的小说
    path = f'./dist/{AUTHOR["name"]}/{id}'
    if os.path.exists(path):
        logger.info(f'tingyun: {id} is fetched already, skiping...')
        return
    headers = {'User-Agent': USER_AGENT, 'Cookie': COOKIE}
    r = requests.get(url, headers=headers)
    logger.info(r)
    assert r.status_code == 200
    soup = BeautifulSoup(r.content, 'lxml')
    alist = soup.select('.index_box a')
    # chapter_link_list = [a['href'] for a in alist]
    if not alist:  # 只有一章的情况下
        subtitle = soup.select('p.novel_title')[0]
        body = soup.select('#novel_honbun')[0]
        logger.info(len(body.text.replace('　', '').replace('\n', '')))
        write_md(subtitle=subtitle.text, body=body.text, properties={'author': AUTHOR['name'], 'id': id, 'index': -1})
        return
    # Add README.md file to record novel title
    title = soup.select('p.novel_title')[0]
    body = soup.select('#novel_ex')[0]
    write_readme_md(title=title.text, body=body.text, properties={'author': AUTHOR['name'], 'id': id, 'index': -1})
    # Fetch all chapter of the novel
    for a in alist:
        clink = HOST + a['href']
        logger.info(a['href'])
        # i = a['href'][a['href'].rfind('/', -1):]
        i = a['href'].replace('/', '').replace(id, '')
        r = requests.get(clink, headers=headers)
        soup = BeautifulSoup(r.content, 'lxml')
        subtitle = soup.select('p.novel_subtitle')[0]
        body = soup.select('#novel_honbun')[0]
        logger.info(len(body.text.replace('　', '').replace('\n', '')))
        write_md(subtitle=subtitle.text, body=body.text, properties={'author': AUTHOR['name'], 'id': id, 'index': i})

if __name__ == '__main__':
    logger.info('-------- Tingyun start --------')
    # fetch all novel url to json file
    # author_id = 'x6713d'
    # author_name = 'ulth'
    url = f'https://xmypage.syosetu.com/mypage/novellist/xid/{AUTHOR["id"]}/'
    p = 1
    headers = {'User-Agent': USER_AGENT, 'Cookie': COOKIE}
    r = requests.get(url, headers=headers)
    logger.info(r)
    assert r.status_code == 200
    soup = BeautifulSoup(r.content, 'lxml')
    novel_links = get_novel_links(soup)
    next_page = soup.find_all(title='next page')
    while next_page:
        p = p + 1
        next_url = url + f'?p={p}'
        r = requests.get(next_url, headers=headers)
        logger.info(r)
        assert r.status_code == 200
        soup = BeautifulSoup(r.content, 'lxml')
        novel_links.extend(get_novel_links(soup))
        next_page = soup.find_all(title='next page')
    logger.info(f'len of collection data is {len(novel_links)}')
    write_collection_data(novel_links, AUTHOR['name'])
    for item in novel_links:
        fetch_novel(item['url'])
    # fetch all chapter to markdown file
    logger.info('-------- Tingyun end   --------')