import scrapy
import os
from urllib.parse import urljoin
from ..items import AldoshoesItem
from scrapy.selector import Selector

class AldoSHoes(scrapy.Spider):
    name="aldoshoes"
    allowed_domains=["aldoshoes.com"]
    start_urls=["https://www.aldoshoes.com/us/en_US"]
    status=True
    sub_categories_counter=0
    sub_visit_counter=0
    def parse(self, response):
        produt_urls = set([])
        for anchor in response.css("a::attr(href)").extract():
                if "men" in anchor or "kids" in anchor:
                    #to not show duplicate url on command promt we arte using this if condition
                    if anchor not in produt_urls:
                        produt_urls.add(anchor)
                        print("main href => ", anchor)

                    #yield cannot parse duplicate url
                    yield response.follow(anchor,callback=self.parse_category)


    def parse_category(self,response):
        for href in response.css("a.c-product-tile__link-product::attr(href)").extract():
            self.sub_categories_counter=self.sub_categories_counter+1
            print("sub-category-href => ",self.sub_categories_counter,href)
            yield  response.follow(href,callback=self.parse_category_detail,meta={'href':href})




    #this method extract name, stylenotes,details,materials and measurement they are not changing with different colors so we are extracting them once for each product.
    #extract all the available color href and call other parsing method get_variations
    def parse_category_detail(self,response):
        self.sub_visit_counter=self.sub_visit_counter+1
        print("visiting sub_category no ",self.sub_visit_counter)

        product_name = response.css('header h1.c-heading.c-buy-module__product-title span::text').extract()

        #some products have syle_note under p tag and some have under div
        if response.css('div.c-read-more__inner p'):
            style_notes=response.css('div.c-read-more__inner p::text').extract_first()
        else:
            style_notes=response.css('div.c-read-more__inner::text').extract_first()

        #3 block exists with same content under differen media query. below selector get only first block
        block_3_description=response.css('div.c-product-description__section-container').extract_first()
        #convert the extracted string to selector for further parsing
        block_3_description=Selector(text=block_3_description).css('div.c-product-description__section')

        details = None
        materials = None
        measurements = None

        for detail_block in block_3_description:
            content_list=[]
            heading = detail_block.css('h2::text').extract_first()
            content_list= detail_block.css('ul.u-reset-list li::text').extract()
            if heading == "Details":
                details = content_list
            if heading == "Materials":
                materials = content_list
            if heading == "Measurements":
                measurements = content_list

        colors_block=response.xpath('//*[@id="PdpProductColorSelectorOpts"]')

        for color_href in colors_block.css('li a::attr(href)').extract():
            # scrapy.Request(urljoin(self.start_urls[0],color_href),callback=self.test)
             yield response.follow(color_href,callback=self.get_variations,cb_kwargs ={"product_name":product_name,
                                                                                 "style_notes":style_notes,
                                                                                 "details":details,
                                                                                 "materials":materials,
                                                                                 "measurements":measurements})

    #this mehtod recieve product url with different colors and it extract the price for specific colors.
    def get_variations(self,response,product_name,style_notes,details,materials,measurements):
        item=AldoshoesItem()
        item['product_name']=product_name
        item['style_note']= style_notes
        item['details']= details
        item['materials']= materials
        item['measurements']= measurements
        item['original_price'] = None
        item['reduce_price'] = None
        item['url']=response.request.url
        #if price_desc found it means that product is on sale and we have to get both original and reduce price

        #original_price have different classes if reduced_price exists or if not.
        item['reduce_price']= response.css('span.c-product-price__formatted-price.c-product-price__formatted-price--is-reduced::text').extract_first()
        if item['reduce_price']:
            item['original_price'] = response.css('span.c-product-price__formatted-price.c-product-price__formatted-price--original.u-text-strikethrough::text').extract_first()
        else:
            item['original_price'] = response.css('span.c-product-price__formatted-price::text').extract_first()


        item['color']=response.css('span.c-product-option__label-current-selection::text').extract_first()
        item['size']=response.css('ul#PdpProductSizeSelectorOpts li::text').extract()
        yield item
