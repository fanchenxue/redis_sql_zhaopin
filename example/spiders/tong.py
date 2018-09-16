# -*- coding: utf-8 -*-
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

# class YingcaiSpider(CrawlSpider):
#     name = 'tong'
#     allowed_domains = ['58.com']
#     start_urls = ['http://bj.58.com/job.shtml']
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'User-Agent': 'Baiduspider'
        },
        'COOKIES_ENABLED': False,

        'LOG_LEVEL ': 'DEBUG',

    }
    rules = [
        Rule(LinkExtractor(allow=(r'/\w+/'), restrict_css=(r'div.allPos', r'div.pagesout')), follow=True),

        # 详情页链接规则
        Rule(LinkExtractor(allow=r'http://bj\.58\.com/.*?/\d+x\.shtml'), callback='parse_directory', process_request='pf',follow=False),
    ]
    def parse_directory(self, response):
        item = ExampleItem()
        url = response.url
        jid = self.md5(url)

        location = response.xpath('//div[@class="pos-area"]/span/span[1]/text()').extract()[0]
        exp = response.xpath('//div[@class="pos_base_condition"]/span[3]/text()').extract()[0]
        p = re.compile(r'(\d+)')
        exp = p.search(exp)
        if exp:
            exp = exp.group(1)
        else:
            exp = 0
        date_pub = response.xpath('//span[@class="pos_base_num pos_base_update"]/span/text()').extract()[0]
        crawled = self.Strfdate(date_pub)

        degree = response.xpath('//span[@class="item_condition"]/text()').extract()[0]
        title = response.xpath('//div[@class="pos_base_info"]/span[1]/text()').extract()[0]
        money = response.xpath('//div[@class="pos_base_info"]/span[2]/text()').extract()[0].strip('元/月\xa0')
        minmoney = maxmoney = 0
        if '-' in money:
            money = money.split('-')
            minmoney = int(money[0])
            maxmoney = int(money[1])
        elif  '面议' in money:
            pass
        elif '以上' in money:
            minmoney = maxmoney = money.strip('元/月以上')
        elif '以下' in money:
            minmoney = maxmoney = int(money.strip('元/月以下'))

        item['url'] = url
        item['jid'] = jid
        item['title'] = title
        item['location'] = location
        item['exp'] = exp
        item['degree'] = degree
        item['maxmoney'] = maxmoney
        item['minmoney'] = minmoney
        item['crawled'] = crawled
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





