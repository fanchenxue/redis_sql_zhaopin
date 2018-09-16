from example.items import ExampleItem
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_redis.spiders import RedisCrawlSpider
import hashlib
import datetime



class MyCrawler(RedisCrawlSpider):
    """Spider that reads urls from redis queue (myspider:start_urls)."""
    name = 'mycrawler_redis'
    redis_key = 'start_urls'


    rules = [
        Rule(LinkExtractor(allow=r'http://search\.51job\.com/list',restrict_xpaths=(r'//div[@class="cn hlist"]',r'//div[@class="dw_page"]')),follow=True),
        Rule(LinkExtractor(allow=r'http://jobs\.51job\.com/.*?/\d+\.html'), callback='parse_directory', follow=False),

    ]


    def parse_directory(self, response):
        item = ExampleItem()
        url = response.url
        jid = self.md5(url)

        title = response.xpath(r'//h1/text()').extract()[0]
        location = response.xpath(r'//div/span[@class="lname"]/text()').extract()[0]
        exp = response.xpath(r'//div[@class="t1"]/span[1]/text()').extract()[0].strip('年经验')
        if '无工作' in exp:
            exp = 0
        else:
            exp = exp.strip('-')[0]
        degree = response.xpath(r'//div[@class="t1"]/span[2]/text()').extract()[0]
        crawled = datetime.datetime.now().strftime('%Y-%m-%d')
        money = response.xpath(r'//div[@class="cn"]/strong/text()').extract()
        maxmoney = minmoney = 0
        if money:
            money = money[0]
        else:
            pass
        if  '/月' in money:
            money = money.strip('/月')
            money = money.split('-')
            if 'k' in money[1]:
                maxmoney = float(money[1].strip('k')) * 1000
                minmoney = float(money[0]) * 1000
            elif '千' in money[1]:
                maxmoney = float(money[1].strip('千')) * 1000
                minmoney = float(money[0]) * 1000
            elif '万' in money[1]:
                maxmoney = float(money[1].strip('万')) * 10000
                minmoney = float(money[0]) * 10000
        elif '万/年' in money:
            money = money.strip('/年')
            money = money.split('-')
            if '万' in money[1]:
                maxmoney = float(money[1].strip('万')) * 1000
                minmoney = float(money[0]) * 1000
        elif '以上' in money:
            minmoney = maxmoney = money.strip('元/月以上')
        elif '面议' in money :
            minmoney = maxmoney = 0
        elif '以下' in money :
            minmoney = maxmoney = int(money.strip('元/月以下'))

        item['title'] = title
        item['maxmoney'] = int(maxmoney)
        item['minmoney'] = int(minmoney)
        item['crawled'] = crawled
        item['location'] = location
        item['exp'] = exp
        item['degree'] = degree
        item['url'] = url
        item['jid'] = jid

        print(title,location,exp,degree,url)
        yield item
    def md5(self,value):
        md5 = hashlib.md5()
        md5.update(bytes(value,encoding='utf8'))
        return md5.hexdigest()