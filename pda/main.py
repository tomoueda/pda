#This is in order to add the this directory as a path name, in order for pda spider's
#import to work.
import os.path
import sys

parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent)

#Start code:

from twisted.internet import reactor
from scrapy.crawler import Crawler 
from scrapy import log, signals
from spiders.pda_spider import PDASpider
from scrapy.utils.project import get_project_settings
from scrapy.statscol import StatsCollector

spider = PDASpider()
settings = get_project_settings()
crawler = Crawler(settings)
stats = StatsCollector()
stats.open_spider(spider)
crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
crawler.configure()
crawler.crawl(spider)
crawler.start()
log.start()
reactor.run()
print stats.get_stats()