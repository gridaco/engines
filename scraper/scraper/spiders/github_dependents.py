#
# How to use
# scrapy crawl github.com/network/dependents -a repo=<org/repo> -a dependents_after=<id> -o <out>.json
#

import scrapy


def url(repo, dependents_after=None):
    if dependents_after is not None:
        return f'https://github.com/{repo}/network/dependents?dependents_after={dependents_after}'
    else:
        return f'https://github.com/{repo}/network/dependents'


class GithubNetworkDependentsSpider(scrapy.Spider):
    name = "github.com/network/dependents"

    def start_requests(self):
        yield scrapy.Request(url=url(repo=self.repo, dependents_after=self.dependents_after), callback=self.parse)

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
