import re

import asyncio
import requests
from bs4 import BeautifulSoup


class Deputat(object):
    def __init__(self, url, name, kpd=None):
        self.url = url
        self.name = name
        self.kpd = kpd

    def __unicode__(self):
        return '%s - %s' % (self.name, self.kpd)

    def __str__(self):
        return '%s - %s' % (self.name, self.kpd)


class DeputatClubParser(object):
    def __init__(self):
        self._url = 'http://www.deputat.club'

    def get_deputates(self):
        page = requests.get(self._url + '/deputies')
        soup = BeautifulSoup(page.text, 'html.parser')
        deputates_divs = soup.findAll("div", {"class": "view-content"})

        urls = []
        for div in deputates_divs:
            for link in div.find_all('a'):
                url = link['href']
                if re.match(r'/deputies/[0-9]+$', url):
                    urls.append(self._url + url)

        loop = asyncio.get_event_loop()
        tasks = []
        for url in urls:
            tasks.append(self.parse_depute_page(url))

        all_data = loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()
        return all_data

    async def parse_depute_page(self, url):
        page = requests.get(url)
        deputy_soup = BeautifulSoup(page.text, 'html.parser')
        name = deputy_soup.findAll('h1', attrs={'class': 'page-title'})[0].text
        kpds = deputy_soup.findAll('div', attrs={'class': 'kpd-score'})
        if kpds:
            kpd = kpds[0].text
        else:
            kpd = None
        return Deputat(url=url, name=name, kpd=kpd)


if __name__ == '__main__':
    print(DeputatClubParser().get_deputates()[0])
