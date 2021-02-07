import os
os.system('python -m venv venv && venv\\Scripts\\activate.bat && pip install pipreqs && pipreqs "' + os.getcwd() +'" && pip install -r requirements.txt')
import pandas as pd
from math import ceil
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
import time
from random import random

class Car:
    def __init__(self, vin, browser, brands):
        self.vin = vin
        self.browser = browser
        self.brands = brands
        self.propertyList = self.vehicleOverview()
        self.generalCarInfo = self.getLocationBrandModelYear()
        self.features = self.getFeatures()
        self.autoReport = self.getAutoHistory()
        self.summary = self.mergeAllInfo()
        k=2
    def vehicleOverview(self):
        propertyList = {}
        vehicleProperties = self.browser.find_elements_by_xpath('//div[@data-qa="vehicle-overview"]/div[2]/*')
        for property in vehicleProperties:
            splitted = property.text.split("\n")
            if len(splitted) == 2:
                propertyList.update({splitted[0]: splitted[1]})
            else:
                propertyList.update({splitted[0]: ''})
        try:
            price = self.browser.find_element_by_xpath('//div[@data-qa="PricingBlock"]/div[3]').text
            price = float(price.replace('$','').replace(',',''))
        except:
            price = 'N/A'
        try:
            otherPriceInfo = self.browser.find_element_by_xpath('//div[@data-qa="PricingBlock"]/div[4]').text
            relativePrice = otherPriceInfo.split('\n')[0]
            relativePriceExplanation = otherPriceInfo.split('\n')[-1]
        except:
            relativePrice = 'N/A'
            relativePriceExplanation = 'N/A'
        propertyList.update({'Price': price})
        propertyList.update({'Relative Price':relativePrice})
        propertyList.update({'Relative Price Explanation':relativePriceExplanation})
        return propertyList

    def getLocationBrandModelYear(self):
        dictToReturn = {
            'Year': 'N/A',
            'Brand': 'N/A',
            'Model': 'N/A',
            'Type': 'N/A',
            'Miles': 'N/A',
            'City': 'N/A',
            'State': 'N/A'
        }
        try:
            year_brand_model = self.browser.find_element_by_xpath('//h1[@data-qa="Heading"]/div[1]/div').text.split(' ')
            dictToReturn['Year'] = year_brand_model[0]
            brand = [ brand for brand in self.brands if year_brand_model[1] in brand]
            dictToReturn['Brand'] = brand[0] if len(brand)>0 else 'N/A'
            year_brand_model = ' '.join(year_brand_model)
            dictToReturn['Model'] = year_brand_model.replace(dictToReturn['Year'],'').replace(dictToReturn['Brand'],'').strip()
        except:
            pass
        try:
            dictToReturn['Type'] =self.browser.find_element_by_xpath('//h1[@data-qa="Heading"]/div[2]').text
        except:
            pass
        try:
            location = self.browser.find_element_by_xpath('//span[@data-qa="used-vdp-header-location"]').text.split(',')
            dictToReturn['City'] = location[0].strip()
            dictToReturn['State'] = location[1].strip()
        except:
            pass
        try:
            miles = self.browser.find_element_by_xpath('//span[@data-qa="used-vdp-header-miles"]').text
            dictToReturn['Miles'] = float(miles.replace(',','').replace('Miles','').strip())
        except:
            pass
        return dictToReturn


    def getFeatures(self):
        features = {'Features': []}
        try:
            self.browser.find_element_by_xpath('//button[@data-qa="SeeMore-button"]').click()
        except:
            pass
        try:
            featuresContent = self.browser.find_elements_by_xpath('//div[@class="see-more-body"]/div/*')
            featuresList = []
            for featuresContentElement in featuresContent:
                featuresList.extend(featuresContentElement.text.split('\n'))
            features = {'Features': featuresList}
        except:
            pass

        return features
    def mergeAllInfo(self):
        infoDict = dict()
        for attribute in ['generalCarInfo','propertyList','features','autoReport']:
            for key,value in self.__getattribute__(attribute).items():
                infoDict[key] = value
        infoDict['vin'] = self.vin
        return infoDict
    def getAutoHistory(self):
        report = {
            'Accident Number':'N/A',
            'Usage': 'N/A',
            'Accident Title': 'N/A',
            'Number of Owners': 'N/A',
            'Accident Report Date': 'N/A'
        }
        try:
            cells = self.browser.find_elements_by_xpath('//div[@data-qa="ConditionHistory"]/*')
        except:
            pass
        try:
            reportDataCell = [cell for cell in cells if cell.text.startswith('Condition data as of:')]
            report['Accident Report Date'] = reportDataCell[0].text.replace('Condition data as of:','').strip()
        except:
            pass
        try:
            reportDetailCell = [cell for cell in cells if 'Accident Check' in cell.text]
            reportDetails = reportDetailCell[0].text.split('\n') if len(reportDetailCell)>0 else []
            for detail_idx, detail in enumerate(reportDetails):
                try:
                    if detail =='Accident Check':
                        report['Accident Number'] = float(reportDetails[detail_idx+1].replace('reported accidents','').strip())
                    elif detail == 'Usage':
                        report['Usage'] = reportDetails[detail_idx+1].strip()
                    elif detail == 'Title':
                        report['Accident Title'] = reportDetails[detail_idx + 1].strip()
                    elif detail == 'Number of Owners':
                        report['Number of Owners'] = float(reportDetails[detail_idx+1].strip())
                except:
                    pass
        except:
            pass
        return report
class TrueCarScraper:
    def __init__(self,driverType='chrome',searchLocation='all'):
        self.cwd = os.getcwd()+'\\'
        self.driverType=driverType
        self.links = []
        self.url = 'https://www.truecar.com/used-cars-for-sale/listings/'
        self.url2 = 'https://www.truecar.com/used-cars-for-sale/listing/'
        self.usPostalCodesFile = self.cwd + 'uszips.csv'
        self.usPostalCodes = self.getStatesDict()
        self.driverFile = self.cwd + 'chromedriver.exe' if self.driverType=='chrome' else self.cwd+'phantomjs.exe'
        self.outputFile = self.cwd + 'CARS.csv'
        self.priceRangeDict = {0: 'price-below-10000/', 1: 'price-10000-20000/', 2: 'price-20000-30000/', 3: 'price-30000-40000/',4: 'price-above-40000/'}
        self.browser = self.getBrowser()
        self.cars = []
        self.brands = []
        self.searchLocation = searchLocation
    def getLinks(self,searchURL):
        waitTime1 = 0.5 + random()
        time.sleep(waitTime1)
        txt = self.browser.find_element_by_xpath('/html/body/div[2]/div[3]/main/div/div[3]/div/div[2]/div/div[1]/div/h2/span[1]').text
        if txt.startswith('Showing') and txt.endswith('Listings'):
            txt = txt.replace('Showing','').replace('Listings','')
            matchedItems = txt.split(" of ")
            pageInfoItems = matchedItems[0].split('–')
            numberOfPosts = int(matchedItems[-1].replace(',', '').strip())
            recordsPerPage = int(pageInfoItems[-1].replace(',', '').strip())
            numberOfPages = ceil(numberOfPosts / recordsPerPage)
            for i in range(1, numberOfPages):
                self.browser.get(searchURL + '?page=' + str(i))
                waitTime2 = random()
                time.sleep(waitTime2)
                linkNodes = self.browser.find_elements_by_xpath('//div[@data-qa="Listings"]')
                self.links.extend([node.find_element_by_xpath('./div/a').get_attribute('href')[51:] for node in linkNodes])
    def getStatesDict(self):
        data = pd.read_csv(self.usPostalCodesFile)[['county_name', 'state_name', 'state_id']]
        uniquePlaces = list(set(iter(zip(data['county_name'].tolist(), data['state_name'].tolist()))))

        names = ['Wyoming', 'Wisconsin', 'West Virginia', 'Washington', 'Virginia', 'Vermont', 'Utah', 'Texas', 'Tennessee',
             'South Carolina', 'Rhode Island', 'Pennsylvania', 'Oregon', 'Oklahoma', 'Ohio', 'North Carolina',
             'New York', 'New Mexico',
             'New Jersey', 'New Hampshire', 'Nevada', 'Nebraska', 'Montana', 'Missouri', 'Mississippi', 'Minnesota',
             'Michigan', 'Massachusetts', 'Maryland', 'Maine', 'Louisiana', 'Kentucky', 'Kansas', 'Iowa', 'Illinois',
             'Idaho',
             'Hawaii', 'Georgia', 'Florida', 'Delaware', 'Connecticut', 'California', 'Arkansas', 'Arizona', 'Alaska',
             'Alabama', 'North Dakota', 'South Dakota', 'Colorado', 'District of Columbia', 'Indiana']
        abbrevs = ['WY', 'WI', 'WV', 'WA', 'VA', 'VT', 'UT', 'TX', 'TN', 'SC', 'RI', 'PA', 'OR', 'OK', 'OH', 'NC', 'NY',
               'NM',
               'NJ', 'NH', 'NV', 'NE', 'MT', 'MO', 'MS', 'MN', 'MI', 'MA', 'MD', 'ME', 'LA', 'KY', 'KS', 'IA', 'IL',
               'ID',
               'HI', 'GA', 'FL', 'DE', 'CT', 'CA', 'AR', 'AZ', 'AK', 'AL', 'ND', 'SD', 'CO', 'DC', 'IN']
        states = dict(zip(names, abbrevs))
        places = [(x.lower() + ' ' + states.get(y).lower()).replace(' ', '-') if states.get(y) is not None else '' for (x, y) in uniquePlaces]
        return places
    def getBrowser(self):
        if self.driverType=='phantomjs':
            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap["phantomjs.page.settings.userAgent"] = ( "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36")
            browser = webdriver.PhantomJS(executable_path=self.driverFile, desired_capabilities=dcap)
            browser.set_window_size(1400, 1000)
        else:
            browser = webdriver.Chrome(self.driverFile)
        return browser


    def processLinks(self):
        browser = self.getBrowser()
        for link in self.links:
            splitted = link.split('/')
            vin = splitted[0] if len(splitted)>0 else 'N/A'
            waitTime = 0 + random()
            time.sleep(waitTime)
            browser.get(self.url2 + link)
            car = Car(vin, browser, self.brands)
            self.cars.append(car.summary)

    def scrape(self):
        for i, priceRange in self.priceRangeDict.items():
            if self.searchLocation=='all':
                for location in self.usPostalCodes:
                    searchURL = self.url + priceRange + 'location-' + location
                    try:
                        self.browser.get(searchURL)
                        self.getLinks(searchURL)
                        if len(self.brands) == 0:
                            self.brands = self.browser.find_elements_by_xpath('//select[@data-qa="MakeFilter"]/option')
                            self.brands = set([brand.text for brand in self.brands if brand.text!='All'])

                    except Exception as e:
                        print(e)
                        continue
            else:
                searchURL = self.url + priceRange + 'location-' + self.searchLocation
                try:
                    self.browser.get(searchURL)
                    self.getLinks(searchURL)
                    if len(self.brands) == 0:
                        self.brands = self.browser.find_elements_by_xpath('//select[@data-qa="MakeFilter"]/option')
                        self.brands = set([brand.text for brand in self.brands if brand.text != 'All'])
                except Exception as e:
                    print(e)
                    continue
            break

        self.processLinks()
        self.browser.quit()

    def exportOutput(self):
        carsDF = pd.DataFrame(self.cars)
        if os.path.isfile(self.outputFile):
            carsDF.to_csv(self.outputFile, mode='a', header=None)
        else:
            carsDF.to_csv(self.outputFile)


# run the scraper with "driverType='phantomjs'" if you want the scraper to run in the background
# otherwise run it with "driverType='chrome'"
scraper = TrueCarScraper(driverType='chrome',searchLocation='shelby-ia')
scraper.scrape()
scraper.exportOutput()

