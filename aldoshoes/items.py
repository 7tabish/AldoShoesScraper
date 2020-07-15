# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field


class AldoshoesItem(Item):
    product_name = Field()
    original_price = Field()
    reduce_price = Field()
    color = Field()
    size = Field()
    style_note = Field()
    details = Field()
    materials = Field()
    measurements = Field()
    url = Field()
