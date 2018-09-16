from scrapy import cmdline

# cmdline.execute('scrapy crawl tong'.split())
# cmdline.execute('scrapy crawl 51job'.split())
# cmdline.execute('scrapy crawl zhilian'.split())
# cmdline.execute('scrapy crawl lagou'.split())
# cmdline.execute('scrapy crawl chinahr'.split())
# cmdline.execute('scrapy crawl ganji'.split())

import os
os.chdir('example/spiders')
cmdline.execute('scrapy runspider 51job.py'.split())
# cmdline.execute('scrapy runspider tong.py'.split())
