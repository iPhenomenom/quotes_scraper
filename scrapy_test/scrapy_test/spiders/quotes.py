import scrapy
from scrapy.crawler import CrawlerProcess
import json


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = ['http://quotes.toscrape.com']
    quotes_list = []
    authors_set = set()

    def parse(self, response):
        self.log('Visited %s' % response.url)

        # Обработка страницы с цитатами
        quotes = response.css('div.quote')
        for quote in quotes:
            item = {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('span small::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }
            self.quotes_list.append(item)
            self.authors_set.add(item['author'])

        # Переход на следующую страницу
        next_page_url = response.css('li.next > a::attr(href)').get()
        if next_page_url is not None:
            yield response.follow(next_page_url, self.parse)

    def closed(self, reason):
        # Запись цитат в файл при завершении работы паука
        with open('quotes.json', 'w') as f:
            json.dump(self.quotes_list, f, ensure_ascii=False)

        # Запись списка авторов в файл при завершении работы паука
        with open('authors.json', 'w') as f:
            json.dump(list(self.authors_set), f, ensure_ascii=False)


process = CrawlerProcess()
process.crawl(QuotesSpider)
process.start()
