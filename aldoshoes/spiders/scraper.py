import scrapy
from bs4 import BeautifulSoup as BS
import os
from urllib.parse import urljoin
from ..items import AldoshoesItem


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

        response_bs=BS(response.text,'html.parser')

        style_notes = response.css('div.c-read-more__inner::text').extract_first()
        response_bs = BS(response.text, "html.parser")
        description_3_blocks = response_bs.find('div', {'class': 'c-product-description__section-container'})
        details = None
        materials = None
        measurements = None

        for block in description_3_blocks:
            content_list = []
            heading = block.find('h2').get_text()
            for list_items in block.find_all('ul', {'class': 'u-reset-list'}, role='presentation'):
                #list_items give us more than one name from ul at a time, to seperate name we are using anothe loop
                for item in list_items:
                    content_list.append(item.text)
            if heading == "Details":
                details = content_list
            if heading == "Materials":
                materials = content_list
            if heading == "Measurements":
                measurements = content_list

        colors_block=response.xpath('//*[@id="PdpProductColorSelectorOpts"]')
        product_name = response.css('header h1.c-heading.c-buy-module__product-title span::text').extract()
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


        item['color']=response.xpath('//*[@id="PdpProductColorSelectorOptsLabel"]/span[2]/text()').extract_first()
        item['size']=response.css('ul#PdpProductSizeSelectorOpts li::text').extract()
        yield item
