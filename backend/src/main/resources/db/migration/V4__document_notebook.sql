-- Document notebook: page-preserved text of a learner's own PDFs (the file itself is not kept), and revision cards.
CREATE TABLE notebook_sources (
  id VARCHAR(64) PRIMARY KEY,
  member_id VARCHAR(64) NOT NULL,
  title VARCHAR(200) NOT NULL,
  file_name VARCHAR(255) NOT NULL,
  pages INTEGER NOT NULL,
  bytes INTEGER NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX notebook_sources_member ON notebook_sources(member_id);
CREATE TABLE notebook_pages (
  source_id VARCHAR(64) NOT NULL REFERENCES notebook_sources(id) ON DELETE CASCADE,
  page INTEGER NOT NULL,
  text TEXT NOT NULL,
  PRIMARY KEY(source_id, page)
);
CREATE TABLE notebook_cards (
  id VARCHAR(64) PRIMARY KEY,
  member_id VARCHAR(64) NOT NULL,
  source_id VARCHAR(64),
  page INTEGER,
  front VARCHAR(500) NOT NULL,
  back VARCHAR(2000) NOT NULL,
  drafted_by VARCHAR(20) NOT NULL,
  recall VARCHAR(10),
  recalled_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX notebook_cards_member ON notebook_cards(member_id);
