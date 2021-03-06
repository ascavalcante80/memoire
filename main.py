from crawlers.crawlerCorpus import CrawlerSite1
from crawlers.crawlerDic import CrawlerDic
from time import sleep
import datetime

"""
    This version modifies the xpath for cinema and don`t use user-agent in the classe webCrawler/Crawler.
    This avoid the strang error 404, when trying to create an object user-agent.

"""

__author__ = 'alexandre s. cavalcante'

crawlerFeed = CrawlerSite1()
crawlerDic = CrawlerDic()
while (True):


    crawlerFeed.crawlWithSoup(25, 'http://guia.folha.uol.com.br/busca/cinema/noticias',
                              '//div[@class="card__body"]/a/@href', 'cinema')


    # ----------------- crawler news feed  ------------------------------------------ #
    crawlerFeed.crawlWithSoup(25, 'https://observatoriodocinema.bol.uol.com.br/filmes/page/' + str(index),
                              '//div[@class="item-details"]/h3/a/@href', 'cinema')

    for index in range(2, 756):
        crawlerFeed.crawlWithSoup(25, 'https://observatoriodocinema.bol.uol.com.br/filmes/page/' + str(index),
                                  '//div[@class="item-details"]/h3/a/@href', 'cinema')

    crawlerFeed.crawlWithSoup(25, 'https://observatoriodocinema.bol.uol.com.br/filmes', '//div[@class="item-details"]/h3/a/@href', 'cinema')

    # feed g1 cinema
    crawlerFeed.crawlWithSoup(25, 'http://g1.globo.com/pop-arte/cinema/', '//a[@class="feed-post-link"]/@href',
                             'cinema')

    # # feed g1 sport
    crawlerFeed.crawlWithSoup(25, 'http://globoesporte.globo.com/futebol/',
                              '//a[@class="feed-post-link"]/@href', 'futebol')
    #
    # # feed g1 tech
    crawlerFeed.crawlWithSoup(25, 'http://www.techtudo.com.br/', '//a[@class="feed-post-link"]/@href', 'tech')

    # # feed adoro cinema
    crawlerFeed.crawlWithSoup(25, 'http://www.adorocinema.com/noticias-materias-especiais/',
                              '//a[@class="tt_14 bold no_underline"]/@href', 'cinema', 'http://www.adorocinema.com/')

    # -------------------- crawler dic ------------------------------------------------#

    # new movies g1 cinema
    crawlerDic.crawlOneSectionPage(10, 'http://guia.uol.com.br/sao-paulo/cinema/',
                                   '//a[@class="pg-color4 nome"]/text()', )

    # new movies adoro cinema
    crawlerDic.crawlOneSectionPage(10, 'http://www.adorocinema.com/filmes/numero-cinemas/',
                                   '//h2[@class="tt_18 d_inline"]/a/text()')

    print('sleeping since... ' + str(datetime.datetime.now()))
    sleep(1800)
