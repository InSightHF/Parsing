""" Тема: "Парсинг данных. Scrapy. Начало"
Задание 1. Доработать паука в имеющемся проекте, чтобы он формировал item по структуре:
- наименование вакансии;
- зарплата от;
- зарплата до;
- ссылка на саму вакансиию.
И складывал все записи в базу данных (любую). """

import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hh_ru'
    allowed_domains = ['hh.ru']

    def __init__(self, vacancy=None):
        super(HhruSpider, self).__init__()
        self.start_urls = [
            f'https://hh.ru/search/vacancy?area=2019&st=searchVacancy&text={vacancy}'
        ]

    def parse(self, response: HtmlResponse, start=True):
        next_page = response.css('a.HH-Pager-Controls-Next::attr(href)') \
            .extract_first()

        yield response.follow(next_page, callback=self.parse)

        vacancy_items = response.css(
            'div.vacancy-serp \
            div.vacancy-serp-item \
            div.vacancy-serp-item__row_header \
            a.bloko-link::attr(href)'
        ).extract()

        for vacancy_link in vacancy_items:
            yield response.follow(vacancy_link, self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.css('h1.bloko-header-1 ::text').extract()

        company_name = response.css(
            'div.vacancy-company-name-wrapper \
            span.bloko-section-header-2 ::text') \
            .extract()

        company_address = response.css(
            'div.vacancy-company_with-logo \
            p[data-qa="vacancy-view-location"] ::text') \
            .extract()

        salary = response.css('div.vacancy-title p.vacancy-salary ::text').extract()

        vacancy_link = response.url
        site_scraping = self.allowed_domains[0]

        yield JobparserItem(name=name,
                            company_name=company_name,
                            company_address=company_address,
                            vacancy_link=vacancy_link,
                            salary=salary,
                            site_scraping=site_scraping
                            )
