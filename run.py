import logging
import logging.config
import os

from bs4 import BeautifulSoup
import requests

logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)
HOST = 'https://novel18.syosetu.com'


def write_md(subtitle, body, properties):
    p = properties
    author = p['author']
    id = p['id']
    ch = p['index']
    filename = f'./dist/{author}/{id}/{ch}.md'
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as out:
        out.write(f'# {subtitle} #\n{body}')

if __name__ == '__main__':
    logger.info('-------- Tingyun start --------')
    # url = 'https://novel18.syosetu.com/n8731hi/'
    id = 'n8731hi'
    url = f'{HOST}/{id}/'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0'
    # cookie = 'ses=7hjuv130h6drqqp5r8r1u49qq2; _ga_CQ4S04X1ZS=GS1.1.1688612610.1.0.1688612613.0.0.0; _ga=GA1.1.429152197.1688612610; over18=yes; ks2=cqqmyc7t51e; sasieno=0; lineheight=0; fontsize=0; novellayout=0; fix_menu_bar=1; _ga_C6X74G3CHV=GS1.1.1688631024.3.1.1688632421.0.0.0; nlist3=zyn0.1'
    cookie = 'ses=7hjuv130h6drqqp5r8r1u49qq2; over18=yes; ks2=cqqmyc7t51e;'
    headers = {'User-Agent': user_agent, 'Cookie': cookie}
    r = requests.get(url, headers=headers)
    logger.info(r)
    assert r.status_code == 200
    soup = BeautifulSoup(r.content, 'lxml')
    alist = soup.select('.index_box a')
    # chapter_link_list = [a['href'] for a in alist]
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
        write_md(subtitle=subtitle.text, body=body.text, properties={'author': 'ulth', 'id': id, 'index': i})
    logger.info('-------- Tingyun end   --------')
