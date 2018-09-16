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
# class DmozSpider(CrawlSpider):
#     """Follow categories and extract links."""
#     name = 'lagou'
#     allowed_domains = ['lagou.com']
#     start_urls = ['https://www.lagou.com/']

    custom_settings = {
        'COOKIES_ENABLED': False,
        # 'DOWNLOAD_DELAY': 1,
        'DEFAULT_REQUEST_HEADERS': {
            "Host": "www.lagou.com",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cookie": "user_trace_token=20171224205240-10b81281-b8a5-4f27-92e5-b241dbe6f20a; _ga=GA1.2.1770214120.1514119962; LGUID=20171224205240-539aa732-e8a9-11e7-9e3b-5254005c3644; index_location_city=%E5%8C%97%E4%BA%AC; JSESSIONID=ABAAABAACDBABJB9171B4D7DA62313FD1020111A2E14D74; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1515545537,1515999652,1516245140,1516588707; _gid=GA1.2.2095905795.1516588707; LGSID=20180122140047-9795d0a6-ff39-11e7-b3ec-525400f775ce; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; TG-TRACK-CODE=index_navigation; SEARCH_ID=aa7c547d647546f49cb6ab7531fdc9d3; X_HTTP_TOKEN=9de4c1038ca39d713c95b6dae72f4944; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1516602112; _gat=1; LGRID=20180122142151-8903a83c-ff3c-11e7-b407-525400f775ce",
        },
        # 'ITEM_PIPELINES': {
        #     'example.pipelines.ExamplePipeline': 1,
        # }
    }

    rules = (
        Rule(LinkExtractor(allow=r'zhaopin/.*'),follow=True),
        Rule(LinkExtractor(allow=r'gongsi/'), follow=True),
        Rule(LinkExtractor(allow=r'gongsi/j\d+'), follow=True),
        Rule(LinkExtractor(allow=r'gongsi/j\d+'), follow=True),
        Rule(LinkExtractor(allow=r'xiaoyuan\.lagou\.com'), follow=True),
        # Rule(LinkExtractor(allow=r'jobs/list'),follow=True),
        # 详情页链接规则
        Rule(LinkExtractor(allow=r'jobs/\d+\.html'), follow=False, callback='parse_directory',process_request='pf'),
    )
    def parse_directory(self,response):
        item = ExampleItem()
        url = response.url
        jid = self.md5(url)
        # jid = re.compile(r'https://www.lagou.com/jobs/(\d+)')
        # jid = jid.search(url)
        # if jid :
        #     jid = jid.group(1)
        location = response.xpath('//dd[@class="job_request"]/p/span[2]/text()').extract()[0].strip('/').strip(' /')
        exp = response.xpath('//dd[@class="job_request"]/p/span[3]/text()').extract()[0].strip(' /').strip('经验')
        if '年' in exp:
            exp = exp.strip('年').strip('-')[0]

        else:
            exp = 0

        degree = response.xpath('//dd[@class="job_request"]/p/span[4]/text()').extract()[0].strip(' /')
        crawled = datetime.datetime.now().strftime('%Y-%m-%d')
        title = response.xpath('//span[@class="name"]/text()').extract()[0]
        money = response.xpath('//dd[@class="job_request"]/p/span[1]/text()').extract()[0].split('-')
        maxmoney = minmoney = 0
        if money:
            money = money
        else:
            pass
        if 'k'in money[0]:
            minmoney = int(money[0].strip('k'))*1000
            maxmoney = int(money[1].strip('k '))*1000



        # 加载数据
        item['url'] = url
        item['jid'] = jid
        item['title'] = title
        item['location'] = location
        item['exp'] = exp
        item['degree'] = degree
        item['maxmoney'] = maxmoney
        item['minmoney'] = minmoney
        # item['money'] = money
        item['crawled'] = crawled
        yield item
    def md5(self,value):
        md5 = hashlib.md5()
        md5.update(bytes(value,encoding='utf-8'))
        return md5.hexdigest()
    def pf(self,request):
        request.priority = 1
        return request