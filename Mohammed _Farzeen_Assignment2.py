import scrapy
import json


class BayutSpiderSpider(scrapy.Spider):
    name = "bayut_spider"
    allowed_domains = ["www.bayut.com"]
    start_urls = ["https://www.bayut.com/to-rent/property/dubai/"]

    def __init__(self):
        self.visited_urls = set()

    def parse(self, response):
        # Extract links and titles from the page using XPath
        links_with_titles = response.xpath('//div/a[starts-with(@href, "/property/details-")]')
        for link in links_with_titles:
            url = link.xpath('./@href').get()

            # Construct absolute URL
            absolute_url = response.urljoin(url)

            # Follow each link if it hasn't been visited already
            if absolute_url not in self.visited_urls:
                self.visited_urls.add(absolute_url)
                yield scrapy.Request(url=absolute_url, callback=self.parse_page)

        # Follow pagination links
        next_page = response.css('a.b7880daf::attr(href)').getall()
        for page_link in next_page:
            if page_link.startswith('/to-rent/property/dubai/page-'):
                yield scrapy.Request(url=response.urljoin(page_link), callback=self.parse)

    def parse_page(self, response):
        # Extract property details
        property_id = response.xpath('//span[contains(text(), "Reference no.")]/following-sibling::span/text()').get()
        property_purpose = response.xpath('//li[span[text()="Purpose"]]/span[@aria-label="Purpose"]/text()').get()
        property_type = response.xpath('//li[span[text()="Type"]]/span[@aria-label="Type"]/text()').get()
        added_on = response.xpath('//span[@aria-label="Reactivated date"]/text()').get()
        furnishing = response.xpath('//span[@aria-label="Furnishing"]/text()').get()
        currency = response.xpath('//span[@aria-label="Currency"]/text()').get()
        amount = response.xpath('//span[@aria-label="Price"]/text()').get()
        location = response.xpath('//div[@aria-label="Property header"]/text()').get()
        bedrooms = response.xpath('//span[@aria-label="Beds"]/span/text()').get()
        bathrooms = response.xpath('//span[@aria-label="Baths"]/span/text()').get()
        size = response.xpath('//span[@aria-label="Area"]/span/span/text()').get()
        agent_name = response.xpath('//span[@class="_63b62ff2"]/a[@aria-label="Agent name"]/text()').get()

        # Extract amenities
        amenities = response.xpath('//span[@class="_005a682a"]/text()').getall()

        # Extract description
        description = response.xpath('string(//span[@class="_2a806e1e"])').get()

        # Extract permit number
        permit_number = response.xpath('//span[@class="_812aa185" and @aria-label="Permit Number"]/text()').get()
        # Extract breadcrumbs
        breadcrumbs = response.xpath('//span[@class="_327a3afc" and @aria-label="Link name"]/text()')

        # Join breadcrumbs into a single string
        breadcrumbs_text = ' > '.join(breadcrumbs.getall())

        # Extract image URL
        image_url = response.xpath(
            '//picture[@class="_219b7e0a"]/img[contains(@src, "https://images.bayut.com/thumbnails/")]/@src').get()

        if property_id:
            property_id = property_id.strip()

            # Construct dictionary for price
            price = {'currency': currency, 'amount': amount}

            # Construct dictionary for bed, bath, and size
            bed_bath_size = {'bedrooms': bedrooms, 'bathrooms': bathrooms, 'size': size}

            # Write data to JSON file if it hasn't been written already
            with open('scraped_data.json', 'a', encoding='utf-8') as jsonfile:
                json.dump({'property_id': property_id, 'purpose': property_purpose, 'type': property_type,
                           'added_on': added_on, 'furnishing': furnishing, 'price': price,
                           'location': location, 'bed_bath_size': bed_bath_size, 'permit_number': permit_number,
                           'agent_name': agent_name, 'image_url': image_url, 'breadcrumbs': breadcrumbs_text,
                           'amenities': amenities, 'description': description}, jsonfile, indent=4)
                jsonfile.write('\n')
