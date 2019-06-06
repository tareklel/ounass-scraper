from bs4 import BeautifulSoup as BS
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import requests
import selenium
import re
import pandas as pd
import time
import datetime

def longscraper(url):
    driver=selenium.webdriver.Firefox(executable_path=r'/Users/tarek.lel/Documents/geckodriver')
    driver.get(url)
    driver.implicitly_wait(5)
    while True:
        try:
            driver.find_element_by_xpath("/html/body/div[9]/div/div/div/div[2]/div/div[2]/div/form/a")
            break
        except:
            pass
    try:
        python_button=driver.find_element_by_id("onesignal-popover-cancel-button")
        python_button.click()
    except:
        pass
    try:
        python_button2=driver.find_element_by_xpath("/html/body/div[9]/div/div/div/div[2]/div/div[2]/div/form/a")
        python_button2.click()
    except:
        pass
    SCROLL_PAUSE_TIME = 1
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    driver.implicitly_wait(10)
    try:
        python_button3=driver.find_element_by_xpath("/html/body/div[2]/div[3]/div/section/div/div[4]/div[1]/a")
        python_button3.click()
        x=0
        while x<11:
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)
            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            x+=1
    except:
        pass
    soup=BS(driver.page_source, 'lxml')
    #soup.prettify()
    listurls=[]
    for box in soup("a",{"class":"product-item"}):
        listurls.append(box["href"])
    urls=pd.Series(listurls).astype(str)
    print(urls)
    driver.quit()
    return(re.compile(r"^http.+\.+[^/]*/").search(url).group()[:-1]+urls)

def shortscraper(url):
    soup=BS(requests.get(url).content, 'lxml')
    #soup.prettify()
    listurls=[]
    for box in soup("a",{"class":"product-item"}):
        listurls.append(box["href"])
    urls=pd.Series(listurls).astype(str)
    return(re.compile(r"^http.+\.+[^/]*/").search(url).group()[:-1]+urls)

def crawlpages(listofurls):
    index=['url','product_name','brand','category','color','ISout_of_stock','price','sale','First_Date_Crawled','Last_Crawled',	'Total_out_of_stock','Last Out of Stock']
    plp=pd.DataFrame(columns=index)
    counter=1
    for url in listofurls:
        r = requests.get(url)
        soup=BS(r.content, 'lxml')
        list=[url]
        #ISout_of_stock
        try:
            Out_of_stock="OUT OF STOCK" in soup('span',{"class":"product-badge"})[0].text
        except IndexError as error:
            Out_of_stock=False
        #price
        try:
            price=re.compile("\d+").search(soup("em",{"class":"w-product-price-price"})[0].text).group()
        except:
            price=0
            print("product price blank "+url)
        #brand
        brand=soup("h1")[0].text
        #color
        try:
            color=re.compile("(\S+)\s").search(soup("h2")[0].text).group()
        except IndexError as error:
            color=""
            print("product color blank "+url)
            pass
        #product_name
        try:
            product_name=" ".join([brand,soup("h2")[0].text])
        except IndexError as error:
            product_name=""
            print("product name blank "+url)
            pass
        #category
        try:
            category=soup("span",{"itemprop":"name"})[2].text
        except IndexError as error:
            category=soup("span",{"itemprop":"name"})[1].text
        #sale
        try:
            sale=re.compile("\d+%").search(soup("span",{"class":"w-product-price-discount text-upp"})[0].text).group()
        except:
            sale=""
        [list.append(x) for x in [product_name,brand,category,color,Out_of_stock,price,sale,datetime.datetime.now().date(),"",0,""]]
        plp=plp.append(pd.Series(list,index=index),ignore_index=True)
        print(counter,"/",len(listofurls))
        counter+=1
    return(plp)

def sitemapscraper(url):
    r = requests.get(url)
    soup=BS(r.text,'lxml')
    plps=[]
    for anchor in soup.findAll('loc'):
        plps.append(anchor.text)
    return(pd.Series(plps))

def bulkscraper(listofurls):
    df=shortscraper(listofurls[0])
    for url in listofurls[1:]:
        df=pd.concat([df,shortscraper(url)])
    df=df.reset_index(drop=True).drop_duplicates("first")
    return crawlpages(df)

def longbulkscraper(listofurls):
    df=longscraper(listofurls[0])
    for url in listofurls[1:]:
        df=pd.concat([df,longscraper(url)])
    df=df.reset_index(drop=True).drop_duplicates("first")
    return crawlpages(df)
