import scrapy


class MinigameSpider(scrapy.Spider):
    name = "minigame"
    allowed_domains = ["4399.com"]
    start_urls = ["https://www.4399.com/flash/"]

    def parse(self, response):
        # 解析数据
        print(response)
        # print(response.text)

        li_list = response.xpath("//ul[@class='n-game cf']/li")
        for li in li_list:
            name = li.xpath("./a/b/text()").extract_first()
            category = li.xpath("./em/a/text()").extract_first()
            date = li.xpath("./em/text()").extract_first()
            # print(name, categroy, date)

            dic = {
                "name":name,
                "category":category,
                "date":date
            }
            yield dic