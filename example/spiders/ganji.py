import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from example.items import ExampleItem
import hashlib
import datetime
from datetime import timedelta
import re

from scrapy_redis.spiders import RedisCrawlSpider


class MyCrawler(RedisCrawlSpider):
    """Spider that reads urls from redis queue (myspider:start_urls)."""
    name = 'mycrawler_redis'
    redis_key = 'start_urls'
# class GanjiSpider(CrawlSpider):
#     name = 'ganji'
#     allowed_domains = ['ganji.com']
#     start_urls = ['http://bj.ganji.com/zhaopin/']


    rules = [
        Rule(LinkExtractor(allow=r'zp\w+/',restrict_xpaths=('//div[@class="f-hot"]','//div[@class="pageBox"]')), follow=True),
        # 详情页链接规则
        Rule(LinkExtractor(allow=r'\d+x\.htm'), callback='parse_directory', process_request='pf',follow=False),
    ]
    def parse_directory(self, response):
        item = ExampleItem()
        url = response.url
        jid = self.md5(url)
        title = response.xpath('//h1/text()').extract()[0]
        money = response.xpath('//ul[@class="clearfix pos-relat"]/li[2]/em/text()').extract()[0]
        minmoney = maxmoney = 0
        if '-' in money:
            money = money.split('-')
            minmoney = int(money[0])
            maxmoney = int(money[1].strip('元'))
        elif '面议' in money:
            pass
        elif '元以上' in money:
            minmoney = maxmoney = money.strip('元以上')
        elif '元以下' in money:
            minmoney = maxmoney = int(money.strip('元以下'))
        degree = response.xpath('//ul[@class="clearfix pos-relat"]/li[3]/em/text()').extract()[0]
        location = response.xpath('//ul[@class="clearfix pos-relat"]/li[8]/em/text()|//ul[@class="clearfix pos-relat"]/li[7]/em/text()').extract()[0].strip('                ')
        # if location:
        #     location = location
        # else:
        #     location = response.xpath('//ul[@class="clearfix pos-relat"]/li[7]/em/text()').extract()[0]
        crawled = response.xpath('//p[@class="data-sty mb-5"]/span[1]/text()').extract()[0].strip('更新时间：')
        crawled =self.Strfdate(crawled)
        exp = response.xpath('//ul[@class="clearfix pos-relat"]/li[4]/em/text()').extract()[0]
        p = re.compile(r'(\d+)')
        exp = p.search(exp)
        if exp:
            exp = exp.group(1)
        else:
            exp = 0
        # item['item'] =money
        item["title"] = title
        item["maxmoney"] = maxmoney
        item["minmoney"] = minmoney
        item["location"] = location
        item["crawled"] = crawled
        item["exp"] = exp
        item["degree"] = degree
        item["url"] = url
        item["jid"] = jid

        yield item
    def md5(self, value):
        md5 = hashlib.md5()
        md5.update(bytes(value, encoding='utf-8'))
        return md5.hexdigest()

    def pf(self, request):
        request.priority = 1
        return request

    def Strfdate(self, date):
        if ':' or '今' in date:
            strf = datetime.datetime.now().strftime('%Y-%m-%d')
        elif '天' in date:
            n = int(date.strip('天前'))
            days = timedelta(days=n)
            strf = datetime.datetime.now() - days
            strf = strf.strftime('%Y-%m-%d')
        else:
            strf = date
        return strf
