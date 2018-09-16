# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
import scrapy

class ExampleItem(Item):
    title = Field()
    maxmoney = Field()
    minmoney = Field()
    # money =Field()
    location = Field()
    exp = Field()
    degree = Field()
    url = Field()
    crawled = Field()
    jid = Field()
    spider = Field()
class ExampleLoader(ItemLoader):
    default_item_class = ExampleItem
    default_input_processor = MapCompose(lambda s: s.strip())
    default_output_processor = TakeFirst()
    description_out = Join()
