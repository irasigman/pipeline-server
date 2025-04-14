DROP INDEX IF EXISTS idx_links_from_url;
DROP INDEX IF EXISTS idx_links_destination_page_id;
DROP INDEX IF EXISTS idx_links_source_page_id;

DROP TABLE IF EXISTS links;
DROP TABLE IF EXISTS pages;



CREATE TABLE pages (
    id                  BIGSERIAL PRIMARY KEY,
    url                 TEXT NOT NULL,
    domain              TEXT NOT NULL,
    fetched_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    html                TEXT,
    markdown            TEXT,
    content_tsv         tsvector,
    UNIQUE (url)
);

CREATE TABLE links (
    id                   BIGSERIAL PRIMARY KEY,
    from_page            INT NOT NULL REFERENCES pages (id) ON DELETE CASCADE,
    to_page              INT NULL REFERENCES pages (id) ON DELETE CASCADE,
    link_text            TEXT,
    url                  TEXT NOT NULL
);

-- Indexes for faster lookups and joins:
CREATE INDEX idx_links_source_page_id
  ON links (from_page);

CREATE INDEX idx_links_destination_page_id
  ON links (to_page);

CREATE INDEX idx_links_from_url
  ON links (from_page);


