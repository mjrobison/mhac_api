CREATE SCHEMA web_config;

CREATE TABLE web_config.pages
(
    id SERIAL,
    title text,
    slug text,
    active boolean,
    last_edit timestamp,
    page_display_date timestamp
);

CREATE TABLE web_config.page_content
(    
    page_id INTEGER,
    section integer, 
    content text
);
