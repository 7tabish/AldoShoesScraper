import scrapy
import os
from urllib.parse import urljoin
from ..items import AldoshoesItem


class AldoSoes(scrapy.Spider):
    name="aldoshoes"
    allowed_domains=["aldoshoes.com"]
    start_urls=["https://www.aldoshoes.com/us/en_US"]
    status=True
    sub_categories_counter=0
    sub_visit_counter=0
    def parse(self, response):
        produt_urls = set([])
        for anchor in response.css("a::attr(href)").extract():
                #get href with men, kid or women in it. men also allow women href to accepted list
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
        style_notes=response.xpath('//*[@id="root"]/div/div[2]/main/div[2]/section/div/div[2]/div[3]/div[2]/div/div[1]/div/div/div/text()').extract()
        details = None
        measurements = None
        materials = None
        for div_counter in range(1, 4):
            css_selector = "#root > div > div:nth-child(2) > main > div.c-product-detail-page > section > div > div.o-grid-vertical\@under-medium-mid-only.o-grid-no-gutters > div.o-box-12.o-box-8\@md-high.o-box-7\@lg.o-box-bleed\@under-medium-mid-only.u-flex-first > div.c-product-detail__info.c-product-detail__info-description.u-hide\@under-lg-only > div > div.c-product-description__section-container > div:nth-child({})".format(
                div_counter)

            #extrct the block style_notes section
            #some products have all these 3 headings and some have 2 or 1 that's why i am usign if condition on heading to match it with exactly according to web content
            block = response.css(css_selector)
            if block:
                heading = block.css("h2::text").extract_first()
                content_list = block.css("li::text").extract()
                if heading == "Details":
                    details = content_list
                elif heading == "Materials":
                    materials = content_list
                elif heading == "Measurements":
                    measurements = content_list
        colors_block=response.xpath('//*[@id="PdpProductColorSelectorOpts"]')
        product_name = response.xpath(
            '//*[@id="c-product-detail__parallax"]/div/div[1]/div/header/h1/span/text()').extract()
        for color_href in colors_block.css('li a::attr(href)').extract():
            # scrapy.Request(urljoin(self.start_urls[0],color_href),callback=self.test)
             yield response.follow(color_href,callback=self.get_variations,meta={"name":product_name,
                                                                                 "style_note":style_notes,
                                                                                 "details":details,
                                                                                 "materials":materials,
                                                                                 "measurements":measurements})

    #this mehtod recieve product url with different colors and it extract the price for specific colors.
    def get_variations(self,response):
        item=AldoshoesItem()
        item['product_name']=response.meta['name']
        item['style_note']= response.meta['style_note']
        item['details']= response.meta['details']
        item['materials']= response.meta['materials']
        item['measurements']= response.meta['measurements']
        item['original_price'] = None
        item['reduce_price'] = None
        item['url']=response.request.url
        #if price_desc found it means that product is on sale and we have to get both original and reduce price
        price_desc = response.css('div.c-buy-module__price-review-wrap span.u-visually-hidden').extract_first()
        if price_desc:
            item['original_price'] = response.xpath(
                '//*[@id="c-product-detail__parallax"]/div/div[1]/div/header/div/div/span[2]/text()').extract_first()
            item['reduce_price'] = response.xpath(
                '//*[@id="c-product-detail__parallax"]/div/div[1]/div/header/div/div/span[3]/text()').extract_first()
        #product is not on sale only need to get the original price
        else:
            item['original_price'] = response.xpath(
                '//*[@id="c-product-detail__parallax"]/div/div[1]/div/header/div/div/span[1]/text()').extract_first()

        item['color']=response.xpath('//*[@id="PdpProductColorSelectorOptsLabel"]/span[2]/text()').extract_first()
        item['size']=response.css('ul#PdpProductSizeSelectorOpts li::text').extract()
        yield item
        # yield {"name":product_name,
        #         "original_price": original_price,
        #         "reduce_price": reduce_price,
        #         "color": color,
        #         "size": all_size,
        #        "style_note":style_note,
        #        "details":details,
        #        "materials":materials,
        #        "measurements":measurements,
        #        }

