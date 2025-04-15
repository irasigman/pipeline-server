# app/plugins/scrape.py
import asyncio
from datetime import datetime, timedelta

from data.web.model.pages import Page
from data.web.util.scrape import reader_page
from db.pg_base import PGBase


class WebScrape(PGBase):
    def __init__(self):
        super().__init__()

    def retrieve_page_markdown(self, url):
        self.connect()
        page = self.get_recent_page_by_url(url, days=1)
        if page:
            self.disconnect()
            return page.markdown
        else:
            # cache miss, fetch the page
            page = self.fetch_page(url)
            markdown = page.markdown
            self.disconnect()
            return markdown


    def get_recent_page_by_url(self, url, days=365):
        recent_window = datetime.now() - timedelta(days=days)
        result = self.db.session.query(Page).filter(
            Page.url.ilike(url.rstrip('/').lower()),
            Page.fetched_at >= recent_window
        ).order_by(Page.fetched_at.desc()).first()
        return result

    def fetch_page(self, url) -> Page:
        scrape_result = reader_page(url)
        print(scrape_result)
        new_page = Page(
            url=url.rstrip('/'),
            domain=url.split('/')[2],
            fetched_at=datetime.now(),
            html="",
            markdown=scrape_result,
            content_tsv=None,
        )
        self.db.session.add(new_page)
        self.db.session.commit()
        self.db.session.refresh(new_page)
        return new_page


if __name__ == '__main__':
    ws = WebScrape()
    asyncio.run(ws.retrieve_page_markdown("https://graystone.morganstanley.com/the-dobbs-group/articles/graystone/clients-we-serve/healthcare"))
    # ws.process_links(3)
