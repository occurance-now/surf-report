import urllib
import requests
from lxml import html
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import string
import re
import schedule
import datetime

# use creds to create a client to interact with the Google Drive API

scope =  ['https://spreadsheets.google.com/feeds' + ' ' +'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)
sheet = client.open("Surf Rating").sheet1

row = 2



'''

/////////////////////////////////////
Swell Info taken from NOAA buoy 44097
/////////////////////////////////////

'''


class Swell():

	def __init__(self):

		link = "https://www.ndbc.noaa.gov/data/realtime2/44097.spec"
		f = urllib.request.urlopen("https://www.ndbc.noaa.gov/data/realtime2/44097.spec")

		myfile = f.read()
		contents1 = myfile.split()

		li = []
		for i in contents1:
			li.append(str(i))

		self.swell_height = (li[36]) #meters
		self.average_wave_period = (li[43])#seconds
		self.mean_wave_direction = (li[44])#compass

		self.raw_mean_wave_direction = None
		self.raw_swell_height = None
		self.raw_average_wave_period = None

		return

	def Function1(self):

		mean_wave_direction_str = str(self.mean_wave_direction)
		self.raw_mean_wave_direction = re.sub('[^0-9,.]','', mean_wave_direction_str)

		swell_height_str = str(self.swell_height)
		self.raw_swell_height = re.sub('[^0-9,.]','', swell_height_str)

		average_wave_period_str = str(self.average_wave_period)
		self.raw_average_wave_period = re.sub('[^0-9,.]','', average_wave_period_str)

		#return raw_mean_wave_direction, raw_swell_height, raw_average_wave_period
		return

'''

///////////////////////////////////////////
Wind info (((FILTER)) from NOAA Station BUZM3
///////////////////////////////////////////

'''

class Wind():

	def __init__(self):
		link = "https://www.ndbc.noaa.gov/data/realtime2/BUZM3.txt"
		g = urllib.request.urlopen("https://www.ndbc.noaa.gov/data/realtime2/BUZM3.txt")

		myfile2 = g.read()
		contents2 = myfile2.split()

		li1 = []
		for i in contents2:
			li1.append(str(i))

		self.wind_direction = (li1[43]) #compass
		self.wind_speed = (li1[44]) #m/s
		self.gust_speed = (li1[45]) #m/s
		self.pressure = (li1[50]) #hPa

		self.raw_wind_direction = None
		self.raw_wind_speed = None
		self.raw_gust_speed = None
		self.raw_pressure = None

		return

	def Function2(self):

		wind_direction_str = str(self.wind_direction)
		self.raw_wind_direction = re.sub('[^0-9,.]','', wind_direction_str)

		wind_speed_str = str(self.wind_speed)
		self.raw_wind_speed = re.sub('[^0-9,.]','', wind_speed_str)

		gust_speed_str = str(self.gust_speed)
		self.raw_gust_speed = re.sub('[^0-9,.]','', gust_speed_str)

		pressure_str = str(self.pressure)
		self.raw_pressure = re.sub('[^0-9,.]','', pressure_str)

		return


'''

////////////////////////////////////////////////////
TIDE info ((FILTER)) from NOAA  Station ID: 8452660
///////////////////////////////////////////////////

'''


class Tide():

	def __init__(self):

		driver = webdriver.Chrome('C:/Users/Shane/.wdm/drivers/chromedriver/80.0.3987.106/win32/chromedriver.exe')
		url = 'https://tidesandcurrents.noaa.gov/stationhome.html?id=8452660#photos'
		driver.get('https://tidesandcurrents.noaa.gov/stationhome.html?id=8452660#photos')

		html = driver.page_source
		soup = BeautifulSoup(html, 'lxml')

		primary_detail = soup.find('div', {'id': 'wltext'})
		self.water_level = soup.find('h1').text
		self.raw_water_level = None

		time.sleep(1)
		driver.quit()#closes webpage


	def Function3(self):	

		water_level_str = str(self.water_level)
		self.raw_water_level = re.sub('[^0-9,.]','', water_level_str)

		return



'''	

/////////////
Update GSheet
/////////////

'''	


class Child(Swell):

	def update_GSheet(self):

		global row
	
		self.Function1()
		sheet.update_cell(row, 4, self.raw_mean_wave_direction)
		sheet.update_cell(row, 5, self.raw_swell_height)
		sheet.update_cell(row, 6, self.raw_average_wave_period)


		return



class Child2(Wind):

	def update_GSheet2(self):

		global row
		
		self.Function2()
		sheet.update_cell(row, 7, self.raw_wind_direction)
		sheet.update_cell(row, 8, self.raw_wind_speed)
		sheet.update_cell(row, 9, self.raw_gust_speed)
		sheet.update_cell(row, 10, self.raw_pressure)
		
		return


class Child3(Tide):

	def update_GSheet3(self):

		global row

		self.Function3()
		sheet.update_cell(row, 11, self.raw_water_level)

		return


def master_update():

	global row

	Object1 = Child()
	Object1.update_GSheet()

	Object2 = Child2()
	Object2.update_GSheet2()

	Object3 = Child3()
	Object3.update_GSheet3()

	row += 1

	print('ran master update')
	print((datetime.datetime.now().time()))


if __name__ == '__main__':

	#start_time = time.time()

	while True: 
		'''
		master_update()
		time.sleep(30.0 - ((time.time()-start_time) % 30.0 ))

		'''

		schedule.every().day.at("06:00").do(master_update)
		schedule.every().day.at("10:00").do(master_update)
		schedule.every().day.at("13:00").do(master_update)
		schedule.every().day.at("19:00").do(master_update)

		schedule.run_pending()
		time.sleep(60)
		
