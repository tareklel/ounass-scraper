from bs4 import BeautifulSoup as BS
import requests
import pandas as pd
import re
import datetime


#Create list of all category URLs from sitemap, limited by maxurls variable
def categorysitemapscraper(url,maxurls=None):
    if re.match(r'.*ounass.*ategor.',url):
        r = requests.get(url)
        soup=BS(r.text,'lxml')
        plps=[]
        for anchor in soup.findAll('loc'):
            plps.append(anchor.text)
        if maxurls is None:
            return(pd.Series(plps))
        else:
            return(pd.Series(plps)[:maxurls])
    else:
        print('This is not a category sitemap, please select one from /sitemap.xml')

#Scrapes all product URLs on product listing page that are loaded when page is called
def shortscraper(url):
    soup=BS(requests.get(url).content, 'lxml')
    listurls=[]
    for box in soup("a",{"class":"Product-details Product-detailsHover"}):
        listurls.append(box["href"])
    urls=pd.Series(listurls).astype(str)
    return(re.compile(r"^http.+\.+[^/]*/").search(url).group()[:-1]+urls)

#Scrapes product information price from a list of product listing pages
def productinfoscraper(listofurls):
    index=['url','product name','brand','ISout_of_stock','price','Date_Crawled']
    plp=pd.DataFrame(columns=index)
    counter=1
    for url in listofurls:
        if url not in plp['url'].unique():
            r = requests.get(url)
            soup=BS(r.content, 'lxml')
            list=[url]
            brand=soup("a",{"class":"Brief-brand"})[0].text
            product_name=soup("div",{"class":"Brief-title"})[0].text
            try:
                out_of_stock="OUT OF STOCK" in soup('span',{"class":"product-badge"})[0].text
            except IndexError as error:
                out_of_stock=False
            try:
                price=soup("span",{"class":"Brief-minPrice"})[0].text
            except:
                price=0
            [list.append(x) for x in [product_name,brand,out_of_stock,price,datetime.datetime.now().date()]]
            plp=plp.append(pd.Series(list,index=index),ignore_index=True)
            print(counter,"/",len(listofurls))
            counter+=1
    return(plp)

#Scrapes a list of product listing pages
def bulkscraper(listofurls):
    series=pd.Series([])
    for url in listofurls:
        series=pd.concat([series,shortscraper(url)])
    series=series.reset_index(drop=True).drop_duplicates("first")
    return productinfoscraper(series)

#Scrapes products starting from crawling sitemap product category pages
def scrapeallsitemap(url, max=None):
        return bulkscraper(categorysitemapscraper(url,max))
