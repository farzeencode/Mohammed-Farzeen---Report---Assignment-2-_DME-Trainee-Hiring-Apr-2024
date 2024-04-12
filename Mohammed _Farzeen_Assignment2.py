import scrapy
import json       #importing libraries
import re
import csv

class BayutSpiderSpider(scrapy.Spider):
    name = "bayut_spider"                   #spider name
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
        permit_number = response.xpath(
            '//div[contains(@class, "_1075545d") and contains(text(), "Permit Number")]/following-sibling::div/text()').get()

        # Extract breadcrumbs
        breadcrumbs = response.xpath('//span[@class="_327a3afc" and @aria-label="Link name"]/text()')

        # Join breadcrumbs into a single string
        breadcrumbs_text = ' > '.join(breadcrumbs.getall())

        # Extract image URL
        image_url = response.xpath(
            '//picture[@class="_219b7e0a"]/img[contains(@src, "https://images.bayut.com/thumbnails/")]/@src').get()

        # Extract only the numbers from bedrooms and bathrooms using regular expressions
        if bedrooms:
            if bedrooms.strip().lower() == 'studio':
                print("Property has a Studio")
            else:
                bedrooms = re.findall(r'\d+', bedrooms)[0]
        if bathrooms:
            bathrooms = re.findall(r'\d+', bathrooms)[0]

        if property_id:
            property_id = property_id.strip()

            # Construct dictionary for price
            price = {'currency': currency, 'amount': amount}

            # Construct dictionary for bed, bath, and size
            bed_bath_size = {'bedrooms': bedrooms, 'bathrooms': bathrooms, 'size': size}

            # Write data to JSON file if it hasn't been written already
            with open('Mohammed_Farzeen.json', 'a', encoding='utf-8') as jsonfile:
                json.dump({'property_id': property_id, 'purpose': property_purpose, 'type': property_type,
                           'added_on': added_on, 'furnishing': furnishing, 'price': price,
                           'location': location, 'bed_bath_size': bed_bath_size,'permit_number': permit_number ,'agent_name': agent_name,
                           'image_url': image_url, 'breadcrumbs': breadcrumbs_text, 'amenities': amenities,
                           'description': description, }, jsonfile, indent=4)
                jsonfile.write('\n')

            # Write data to CSV file
            with open('Mohammed_Farzeen.csv', 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Sl. No', 'Field Name', 'Field Type', 'Example']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Write headers if the file is empty
                if csvfile.tell() == 0:
                    writer.writeheader()

                # Write data rows
                writer.writerow({'Sl. No': '1', 'Field Name': 'property_id', 'Field Type': 'string', 'Example': property_id})
                writer.writerow({'Sl. No': '2', 'Field Name': 'purpose', 'Field Type': 'string', 'Example': property_purpose})
                writer.writerow({'Sl. No': '3', 'Field Name': 'type', 'Field Type': 'string', 'Example': property_type})
                writer.writerow({'Sl. No': '4', 'Field Name': 'added_on', 'Field Type': 'string', 'Example': added_on})
                writer.writerow({'Sl. No': '5', 'Field Name': 'furnishing', 'Field Type': 'string', 'Example': furnishing})
                writer.writerow({'Sl. No': '6', 'Field Name': 'price', 'Field Type': 'dict', 'Example': json.dumps(price)})
                writer.writerow({'Sl. No': '7', 'Field Name': 'location', 'Field Type': 'string', 'Example': location})
                writer.writerow({'Sl. No': '8', 'Field Name': 'bed_bath_size', 'Field Type': 'dict', 'Example': json.dumps(bed_bath_size)})
                writer.writerow({'Sl. No': '9', 'Field Name': 'permit_number', 'Field Type': 'string', 'Example': permit_number})
                writer.writerow({'Sl. No': '10', 'Field Name': 'agent_name', 'Field Type': 'string', 'Example': agent_name})
                writer.writerow({'Sl. No': '11', 'Field Name': 'image_url', 'Field Type': 'string', 'Example': image_url})
                writer.writerow({'Sl. No': '12', 'Field Name': 'breadcrumbs', 'Field Type': 'string', 'Example': breadcrumbs_text})
                writer.writerow({'Sl. No': '13', 'Field Name': 'amenities list', 'Field Type': 'list', 'Example': json.dumps(amenities)})
                writer.writerow({'Sl. No': '14', 'Field Name': 'description', 'Field Type': 'string', 'Example': description})

