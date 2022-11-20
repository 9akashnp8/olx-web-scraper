from bs4 import BeautifulSoup

def html_scraper(page_source):

    soup = BeautifulSoup(page_source, 'html.parser')
    car_listings_ul = soup.find("ul", attrs={"data-aut-id": "itemsList"})
    listings = car_listings_ul.find_all("li", attrs={"data-aut-id": "itemBox"})

    data = []
    for listing in listings:
        ad_link = listing.find("a")["href"]
        ad_id = ad_link.split("-")[-1]
        ad_title = listing.find("div", attrs={"data-aut-id":"itemTitle"}).string
        ad_price = listing.find("span", attrs={"data-aut-id":"itemPrice"}).string.split()[1].replace(",", "")
        kms_year = listing.find("div", attrs={"data-aut-id": "itemSubTitle"}).string.split(" - ")
        model_year = kms_year[0]
        try:
            kms_driven = kms_year[1].split()[0].replace(",", "")
        except IndexError:
            kms_driven = ""
        ad_location = listing.find("div", attrs={"data-aut-id":"itemDetails"}).contents[0]
        data.append([ad_id, ad_price, model_year, kms_driven, ad_title, ad_location, ad_link])
    
    return data