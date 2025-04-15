create table public.pages (
  id integer primary key not null default nextval('pages_id_seq'::regclass),
  url text not null,
  domain text not null,
  fetched_at timestamp with time zone not null default now(),
  html text,
  markdown text,
  content_tsv tsvector
);

