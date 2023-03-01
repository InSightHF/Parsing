from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from shopparser import settings
from shopparser.spiders.leroymerlinru import LeroymerlinruSpider
# from leroymerlinparser import settings
# from leroymerlinparser.spiders.leroymerlinru import LeroymerlinruSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroymerlinruSpider, search='ламинат')

    process.start()

