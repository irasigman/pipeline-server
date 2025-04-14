from sqlalchemy import (Column, Integer, Text, text)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import (declarative_base)
from sqlalchemy.types import TIMESTAMP

Base = declarative_base()


class Page(Base):
    __tablename__ = 'pages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text, nullable=False, unique=True)
    domain = Column(Text, nullable=False)
    fetched_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('NOW()'))
    html = Column(Text)
    markdown = Column(Text)
    content_tsv = Column(TSVECTOR)

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'domain': self.domain,
            'fetched_at': str(self.fetched_at),
            'html': self.html,
            'markdown': self.markdown,
            'content_tsv': self.content_tsv,
        }

