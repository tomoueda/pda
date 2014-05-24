from scrapy.spider import Spider
from scrapy.selector import Selector

from pda.items import DungeonURLItem

class PDASpider(Spider):
	name = "pda"
	allowed_domains = ["http://www.puzzledragonx.com"]
	start_urls = ["http://www.puzzledragonx.com/?dir=1"]

	def parse(self, response):
		sel = Selector(response)
		dungeons = sel.xpath("//td[@class=\"dungeonname\"]")
		items = []
		for dungeon in dungeons:
			item = DungeonURLItem()
			item['name'] = dungeon.xpath('a/text()').extract()
			item['url'] = dungeon.xpath('a/@href').extract()
			items.append(item)
		return items
