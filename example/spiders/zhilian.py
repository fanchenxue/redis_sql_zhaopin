# -*- coding: utf-8 -*-
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from example.items import ExampleItem
import re
import hashlib
import datetime

from scrapy_redis.spiders import RedisCrawlSpider


class MyCrawler(RedisCrawlSpider):
    """Spider that reads urls from redis queue (myspider:start_urls)."""
    name = 'mycrawler_redis'
    redis_key = 'start_urls'
# class ZhilianSpider(CrawlSpider):
#     name = 'zhilian'
#     allowed_domains = ['zhaopin.com']
#     start_urls = ['https://sou.zhaopin.com']



    rules = [
        #限定在制定位置查找
        Rule(LinkExtractor(allow=r'https://sou\.zhaopin\.com/',restrict_xpaths=('//div[@class="search"]','//div[@class="pagesDown"]')), follow=True),
        Rule(LinkExtractor(allow=r'searchresult'), follow=True),
        Rule(LinkExtractor(allow=r'http://jobs\.zhaopin\.com/\d+\.htm'), callback='parse_directory', follow=False,process_request='pr'),


    ]
    def parse_directory(self, response):
        item = ExampleItem()
        url = response.url.strip()
        jid = self.md5(url)
        location = response.xpath(r'//ul/li[2]/strong/a/text()').extract()[0]
        exp = response.xpath(r'//ul/li[5]/strong/text()').extract()[0].strip('年')
        if '不限' in exp:
            exp = 0
        else:
            exp = exp.strip('-')[0]
        degree = response.xpath(r'//ul/li[6]/strong/text()').extract()[0]
        crawled = datetime.datetime.now().strftime('%Y-%m-%d')
        title = response.xpath(r'//div[@class="inner-left fl"]/h1/text()').extract()[0].strip()
        money = response.xpath(r'//ul/li[1]/strong/text()').extract()[0].strip('元/月\xa0')
        if '以上' in money:
            minmoney = maxmoney = money.strip('元/月以上')
        elif '面议' in money :
            minmoney = maxmoney = 0
        elif '以下' in money :
            minmoney = maxmoney = money.strip('元/月以下')
        else:
            money = money.split('-')
            maxmoney = money[1].strip('元/月')
            minmoney = money[0]

        item['jid'] = jid
        item['title'] = title
        item['maxmoney'] = maxmoney
        item['minmoney'] = minmoney
        item['crawled'] = crawled
        item['location'] = location
        item['exp'] = exp
        item['degree'] = degree
        item['url'] = url

        yield item
    def pr(self,request):
        request.priority = 1
        return request
    def md5(self, value):
        md5 = hashlib.md5()
        md5.update(bytes(value, encoding='utf8'))
        return md5.hexdigest()
