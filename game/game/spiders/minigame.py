import scrapy
from game.items import GameItem

class MinigameSpider(scrapy.Spider):
    name = "minigame"
    allowed_domains = ["4399.com"]
    start_urls = ["https://www.4399.com/flash/"]

    def parse(self, response):
        # 解析数据
        # print(response)
        # print(response.text)
        li_list = response.xpath("//ul[@class='n-game cf']/li")
        for li in li_list:
            name = li.xpath("./a/b/text()").get()
            category = li.xpath("./em/a/text()").get()
            date = li.xpath("./em/text()").get()
            # print(name, category, date)
            items = GameItem()
            items["name"] = name
            items["category"] = category
            items["date"] = date
            yield items