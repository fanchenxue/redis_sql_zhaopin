# -*- coding: utf-8 -*-
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from example.items import ExampleItem
import hashlib
import datetime


from scrapy_redis.spiders import RedisCrawlSpider


class MyCrawler(RedisCrawlSpider):
    """Spider that reads urls from redis queue (myspider:start_urls)."""
    name = 'mycrawler_redis'
    redis_key = 'start_urls'
# class YingcaiSpider(CrawlSpider):
#     name = 'chinahr'
#     allowed_domains = ['chinahr.com']
#     start_urls = ['http://www.chinahr.com/']
    custom_settings = {
        'COOKIES_ENABLED': False,
        # 'DOWNLOAD_DELAY': 1,
        'DEFAULT_REQUEST_HEADERS': {
            "Host": "www.chinahr.com",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.90 Safari/537.36 2345Explorer/9.1.1.16851",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Cookie": "chrId=6165eb8a69654d559213daf4a6666e07; gr_user_id=d56850a0-eca8-4d20-b3a9-08fd530374b1; wmda_uuid=e35739211d0e695e0038c8334ec2171e; wmda_new_uuid=1; wmda_visited_projects=%3B1732047435009; als=0; uniq=05c8d15df5c949739379413dd08fc7e9; gr_session_id_b64eaae9599f79bd=d223306a-88cc-4b1b-a017-3241ae912039; _ga=GA1.2.916274688.1517043345; _gid=GA1.2.1200532926.1517043345; gtid=bf1ddccbd4c94da78bb50e1cafc33418; gr_session_id_be17cdb1115be298=1b7daf11-acd6-409f-a165-12fb68bdaf50; 58tj_uuid=bffecd28-b447-49a0-be55-02ba2b9aad99; channel=social; new_session=0; new_uv=2; utm_source=; spm=; init_refer=; wmda_session_id_1732047435009=1517052077445-a169135e-8d83-e85c; RecentVisitCity=398_beijing; RecentVisitCityFullpathPc='34,398'",
        },

    }
    rules = [
        Rule(LinkExtractor(allow=r'http://www\.chinahr\.com/\.*?jobs/'), follow=True),

        # 详情页链接规则
        Rule(LinkExtractor(allow=r'http://www\.chinahr\.com/job/\d+\.html'), follow=False, callback='parse_directory', process_request='pf'),
    ]
    def parse_directory(self, response):
        item = ExampleItem()
        url = response.url
        jid = self.md5(url)
        # jid = re.compile(r'https://www.lagou.com/jobs/(\d+)')
        # jid = jid.search(url)
        # if jid :
        #     jid = jid.group(1)
        location = response.xpath('//div[@class="job_require"]/span[2]/text()').extract()[0]
        exp = response.xpath('//div[@class="job_require"]/span[5]/text()').extract()[0].strip('经验')
        if '年' in exp:
            exp = exp.strip('年').strip('-')[0]
        else:
            exp = 0

        degree = response.xpath('//div[@class="job_require"]/span[4]/text()').extract()[0]
        crawled = datetime.datetime.now().strftime('%Y-%m-%d')
        title = response.xpath('//span[@class="job_name"]/text()').extract()[0]
        money = response.xpath('//span[@class="job_price"]/text()').extract()[0]
        minmoney = maxmoney = 0
        if '-' in money:
            money = money.split('-')
            minmoney = int(money[0])
            maxmoney = int(money[1])
        elif  '面议' in money:
            pass

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
