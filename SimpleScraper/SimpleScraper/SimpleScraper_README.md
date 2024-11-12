# Quotes Scraping Project

This project involves scraping quotes from the website [quotes.toscrape.com](http://quotes.toscrape.com), with multiple spiders implemented to scrape quotes, author details, and category-based pages.

## Project Overview

The project is divided into several spiders, each designed to handle different aspects of the scraping process:

- **quotes_spider**: Scrapes quotes and their associated data from the homepage.
- **multipage_navigator_spider**: Handles pagination and scrapes quotes from multiple pages.
- **detail_page_spider**: Extracts additional details about each author from their individual pages.
- **category_spider**: Scrapes quotes based on specific categories, following category links and pagination.

---

## Spiders

### 1. Quotes Spider

This spider is the simplest one in the project, focused on scraping quotes from the homepage.

- **Name**: `quotes`
- **Description**: Scrapes quotes along with their author names and tags from the homepage of the website.
- **Key Features**:
    - Scrapes title, author, and tags.
    - Extracts data from the homepage.

#### How to Run:
```bash
scrapy crawl quotes -o quotes.json

```

### 2. Multipage Navigator Spider 

- **Name**: `multipagenavigator`
- **Description**: Scrapes quotes from multiple pages by navigating through pagination links.
- **Key Features**:
    - Automatically follows the "Next" page link.
    - Scrapes quotes from all pages.

#### How to Run:
```bash
scrapy crawl multipagenavigator -o multipage_quotes.json

```

### 3. Detail Page Spider

- **Name**: `detailpagespider`
- **Description**: Scrapes additional details for each author by visiting their respective detail pages.
- **Key Features**:
    - Follows the link to the author page.
    - Scrapes additional author information such as birth date, place, and a description.

#### How to Run:
```bash
scrapy crawl detailpagespider -o author_details.json

```

### 4. Category Spider

- **Name**: `categoryspider`
- **Description**: Scrapes quotes from different categories, following category links and handling pagination.
- **Key Features**:
    - Follows category links and extracts quotes.
    - Handles pagination within each category page.

#### How to Run:
```bash
scrapy crawl categoryspider -o category_quotes.json

```