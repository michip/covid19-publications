import json
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup

from data.models import PaperHost, Category, Paper, Author
from scrape.citation_refresher import CitationRefresher
from scrape.pdf_image_scraper import PdfImageScraper


def extract_pdf_url(url: str, host: PaperHost):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    dl_element = soup.find('a', attrs={'class': 'article-dl-pdf-link link-icon'})
    relative_link = dl_element['href']
    complete_url = host.url + relative_link
    return complete_url


def scrape_articles(detailed: bool = True, citations: bool = True, images: bool = True):
    biorxiv_corona_json = 'https://connect.biorxiv.org/relate/collection_json.php?grp=181'

    response = requests.get(biorxiv_corona_json)
    data = json.loads(response.text)['rels']

    for i, item in enumerate(data):
        print(i)

        site = item['rel_site']
        if site == "medrxiv":
            name = "medRxiv"
        elif site == "biorxiv":
            name = "bioRxiv"
        else:
            name = site
        host, created = PaperHost.objects.get_or_create(
            name=name,
            url=f'https://www.{site}.org',
        )
        host.save()

        try:
            paper = Paper.objects.get(
                doi=item['rel_doi']
            )
            if paper.category_id == 'unknown':
                url = item['rel_link']
                authors, category = get_detailed_information(url)

                db_category, created = Category.objects.get_or_create(
                    name=category,
                )
                db_category.save()

                paper.category = db_category
                paper.save()
        except Paper.DoesNotExist:
            paper = Paper(
                doi=item['rel_doi']
            )

            paper.title = item['rel_title']
            paper.url = item['rel_link']
            paper.abstract = item['rel_abs']
            paper.host = host
            paper.published_at = item['rel_date']
            paper.pdf_url = extract_pdf_url(item['rel_link'], host)

            if detailed:
                url = item['rel_link']
                authors, category = get_detailed_information(url)

                db_category, created = Category.objects.get_or_create(
                    name=category,
                )
                db_category.save()

                paper.category = db_category
                paper.save()

                for author in authors:
                    db_author, created = Author.objects.get_or_create(
                        first_name=author[0],
                        last_name=author[1],
                    )
                    db_author.save()
                    paper.authors.add(db_author)

            paper.save()

    print("Scraped new papers successfully")

    if images:
        image_scraper = PdfImageScraper()
        image_scraper.load_images()

    if citations:
        citation_refresher = CitationRefresher()
        if citation_refresher.refresh_citations(only_new=True):
            print("Updates citations succesfully")
        else:
            print("Error while updating citations")


def get_detailed_information(url: str) -> Tuple[List[Tuple[str, str, bool]], str]:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    author_webelements = soup.find(
        'span', attrs={'class': 'highwire-citation-authors'}
    ).find_all('span', recursive=False)

    authors = []
    for author_webelement in author_webelements:
        try:
            firstname = author_webelement.find('span', attrs={'class': 'nlm-given-names'}).text
            name = author_webelement.find('span', attrs={'class': 'nlm-surname'}).text
            first_author = 'first' in author_webelement['class']
            authors.append((firstname, name, first_author))
        except AttributeError:
            print(f"Ignore collaboration group: {author_webelement.text}")

    categories = soup.find_all('span', {'class': 'highwire-article-collection-term'})
    if len(categories) > 1:
        print(f"Found multiple categories")
    if len(categories) == 0:
        category = "unknown"
    else:
        category = categories[0].text.strip()
    return authors, category