import scrapy

class CronIp(scrapy.Spider):
    name = 'cron_job'
    start_urls = ['https://free-proxy-list.net/']

    def parse(self, response):
        for products in response.css('body section div.table-responsive div.fpl-list table.table tbody tr'):

            yield {
                'ip': products.css('td')[0].extract().strip('<td>,</td>'),
                'port': products.css('td')[1].extract().strip('<td>,</td>')
                }
            ip=products.css('td')[0].extract().strip('<td>,</td>')
            port=products.css('td')[1].extract().strip('<td>,</td>')
            ip_add='http://'+ip+':'+port+'\n'
            file = open("../../../stackoverflow/stackoverflow/spiders/list.txt", "a")
            file.write(str(ip_add))
            file.close()
