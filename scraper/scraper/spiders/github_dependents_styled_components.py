#
# How to use
# scrapy crawl network/dependents -a repo=<org/repo> -o <out>.json
#

import scrapy


def url(repo): return 'https://github.com/{}/network/dependents'.format(repo)


class GithubNetworkDependentsSpider(scrapy.Spider):
    name = "network/dependents"

    def start_requests(self):
        yield scrapy.Request(url=url(repo=self.repo), callback=self.parse)

    def parse(self, response):

        items = response.xpath(
            "//*[@id='dependents']//div[contains(@class, 'Box-row')]")

        for item in items:
            path = item.xpath('./span/a[2]/@href').get()
            repo = "https://github.com" + path
            yield {
                # remove prefix "/"
                "id": path[1:],
                "url": repo,
            }

        next_page = response.xpath(
            '//div[@class="paginate-container"]/div/a[last()]/@href').get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)
