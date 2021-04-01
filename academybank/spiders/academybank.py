import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from academybank.items import Article


class academybankSpider(scrapy.Spider):
    name = 'academybank'
    start_urls = ['https://www.academybank.com/blog']

    def parse(self, response):
        articles = response.xpath('(//div[@class="view-content"])[1]/div')
        for article in articles:
            link = article.xpath('.//h2/a/@href').get()
            date = article.xpath('.//div[@class="views-field views-field-created"]/span/text()').get()[0]
            if date:
                date = date.strip()

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//li[@class="pager-next"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1[@class="page-title"]/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="content"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
