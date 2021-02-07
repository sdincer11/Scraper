# Scraper
This repository has some samples of my web scraping Python codes.
Notes:
1) TrueCar.py has all the functions necessary to scrape the website https://www.truecar.com for used cars by "county-state abbreviation".
2) In order to successfully run it successfully, one needs to ensure that
  - the Python.exe is added to the computer's system variables.
  - "Google Chrome" has already been download to the computer the program runs on.
  - download the whole GitHub repository including the files "uszips.csv", "chromedriver.exe", "phantomjs.exe" 
3) Example function call can be found at the bottom of "TrueCar.py" where the searchLocation takes the value of "shelby-ia" to query the 
used car listings located in Shelby-Iowa, and the driverType takes the value of "chrome" so that the user can visually trace the scraping process
on a Google Chrome window. If you want the program to run in the background, please set the "driverType" parameter value to "phantomjs".
4) For now, the scraping does not work with other web browsers other than "Google Chrome".
