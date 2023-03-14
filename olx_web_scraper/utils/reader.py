from typing import Optional
from bs4 import BeautifulSoup
from bs4.element import Tag

def extract_string_from_listing(
        listing: Tag,
        html_tag: str,
        html_attribute: str,
        attribute_value: str
    ) -> Optional[str]:
    attribute_value = getattr(
        listing.find(html_tag, attrs={html_attribute: attribute_value}),
        'string',
        None
    )
    return attribute_value

def extract_ad_price(listing):
    price = getattr(
        listing.find("span", attrs={"data-aut-id":"itemPrice"}),
        'string',
        None
    )
    if price:
        return price.split()[1].replace(",", "")
    return price

def extract_kms_year(listing):
    km_year = getattr(
        listing.find("span", attrs={"data-aut-id": "itemDetails"}),
        'string',
        None
    )
    if km_year:
        km_year = km_year.split(" - ")
        model_year = km_year[0]
        kms_driven = km_year[1].split()[0].replace(",", "")
        return kms_driven, model_year
    return "", ""

def html_scraper(page_source):

    soup = BeautifulSoup(page_source, 'html.parser')
    car_listings_ul = soup.find("ul", attrs={"data-aut-id": "itemsList"})
    listings = car_listings_ul.find_all("li", attrs={"data-aut-id": "itemBox"})

    data = []
    for listing in listings:
        ad_link = listing.find("a")["href"]
        ad_id = ad_link.split("-")[-1]
        ad_title = extract_string_from_listing(
            listing=listing, html_tag="span",
            html_attribute="data-aut-id", attribute_value="itemTitle"
        )
        ad_price = extract_ad_price(listing)
        kms_driven, model_year = extract_kms_year(listing)
        ad_location = extract_string_from_listing(
            listing=listing, html_tag="span",
            html_attribute="data-aut-id", attribute_value="item-location"
        )
        data.append([ad_id, ad_price, model_year, kms_driven, ad_title, ad_location, ad_link])
    
    return data