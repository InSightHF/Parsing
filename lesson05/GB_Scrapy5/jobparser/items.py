import scrapy


class JobparserItem(scrapy.Item):

    _id = scrapy.Field()
    name = scrapy.Field()
    company_name = scrapy.Field()
    company_address = scrapy.Field()
    salary = scrapy.Field()
    vacancy_link = scrapy.Field()
    site_scraping = scrapy.Field()
