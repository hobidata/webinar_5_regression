import scrapy
from scrapy.loader import ItemLoader

class MobilItem(scrapy.Item):
    nama_product = scrapy.Field()
    nama_mobil = scrapy.Field()
    link_product = scrapy.Field()
    km = scrapy.Field()
    transmisi = scrapy.Field()
    lokasi = scrapy.Field()
    penjual = scrapy.Field()
    harga = scrapy.Field()

class MobilSpider(scrapy.Spider):
    name = 'mobil123scraper'
    allowed_domains = ['mobil123.com']
    start_urls = ['https://www.mobil123.com/mobil-dijual/indonesia?type=used&page_number=1&page_size=25']
    max_pages = 500

    def parse(self, response):
        # Ambil nomor halaman saat ini dari URL
        current_page = int(response.url.split('page_number=')[-1].split('&')[0])

        for car in response.css('article.listing--card'):
            l = ItemLoader(item=MobilItem(), selector=car)

            # Nama Produk dan Link
            l.add_css('nama_product', 'h2.listing__title a::text')
            l.add_css('link_product', 'h2.listing__title a::attr(href)')

            # Nama Mobil
            l.add_css('nama_mobil', 'div.listing__rating-model::text')

            # Harga
            raw_price = car.css('div.listing__price::text').get()
            if raw_price:
                price_clean = (
                    raw_price.replace('Rp', '')
                    .replace('.', '')
                    .replace(',', '')
                    .strip()
                )
                try:
                    l.add_value('harga', int(price_clean))
                except ValueError:
                    l.add_value('harga', None)

            # Spesifikasi
            specs = car.css('div.listing__specs div.item::text').getall()
            specs = [s.strip() for s in specs if s.strip()]
            if len(specs) >= 4:
                l.add_value('km', specs[0])
                l.add_value('transmisi', specs[1])
                l.add_value('lokasi', specs[2])
                l.add_value('penjual', specs[3])

            yield l.load_item()

        # Pagination manual hingga 100 halaman
        if current_page < self.max_pages:
            next_page = f'https://www.mobil123.com/mobil-dijual/indonesia?type=used&page_number={current_page + 1}&page_size=25'
            yield response.follow(next_page, callback=self.parse)
