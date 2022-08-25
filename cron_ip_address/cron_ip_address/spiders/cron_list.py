import scrapy

class CronIp(scrapy.Spider):
    """
    class CronIp is used to run spider named cron_job
    to start cron job user need to open terminal and write command "crontab -e",
    if user is using this command for the first time then he/she will get 4 options to select editor
    else one editor will be displayed in the terminal.
    there user needs to set cron schedule expressions for his/her desired time for crawling the data and add absolute path of current file.
    ex:
    ***** <Absolute path of current file> where ***** is cron schedule expression to crawl data at every one minute.
    save the file by pressing ctrl+X key
    """
    name = 'cron_job'
    start_urls = ['https://free-proxy-list.net/']

    def parse(self, response):
        """
        ip address will be crawled form the website mentioned in start_urls
        :param response:collect requested response from the website
        """
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
