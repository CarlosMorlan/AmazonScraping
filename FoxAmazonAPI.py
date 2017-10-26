#This is a new change to test Sourcetree
# coding: utf-8

# In[ ]:

# ***********************************************
# Libraries used to get Rating and Reviews
import urllib
import requests
import json
import re

from lxml import html  
from bs4 import BeautifulSoup
# ***********************************************

# ***********************************************
def get_credentials(p_region='US', p_debug=0):
	if p_region == 'UK':
		credentials = ('AKIAJE3VDQXKG7E556KA', 'I2OqtNPaMlRIzPO89HsXsljmjFgiu7JNJQ8oRZTl', 'foxinsights-20')
	else:
		credentials = ('AKIAJE3VDQXKG7E556KA', 'I2OqtNPaMlRIzPO89HsXsljmjFgiu7JNJQ8oRZTl', 'foxinsights-20')
	return credentials

# ***********************************************
def get_rating_and_reviews_count(p_asin, p_region, p_delimiter, p_debug=0):

	# ***********************************************
	# Libraries to get Amazon products
	from amazon.api import AmazonAPI
	# ***********************************************

	access_key, secret_key, associate_tag = get_credentials(p_debug)
	amazon = AmazonAPI(access_key, secret_key, associate_tag, Region = p_region)

	# Constants declaration
	cc_rating_text = 'out of 5 stars'		# Rating tag to search
	cc_reviews_text = 'customer reviews'	# Reviews tag to search
	cc_response_group = 'Reviews'			# Search Response Group
	cc_html_tag_to_search = 'span'			# HTML Tag where the parse will happen

	# Variables declaration
	i = 0				# Line number
	tag_found = 0		# Tag found in html text
	tags_found = 0		# Number of tags found
	rating = ' '		# Rating to return
	reviews_count = ' '	# Reviews count to return

	try:
		# Item without reviews results = amazon_api.lookup(ItemId='B00566HTI4', ResponseGroup='Reviews')
		results = amazon.lookup(ItemId=p_asin,  ResponseGroup=cc_response_group)
		reviews_page = results.offer_url
		if p_debug == 1:
			print ('Reviews page: ' + reviews_page + '#customerReviews')

		reviews=requests.get(reviews_page)
		soup = BeautifulSoup(reviews.text, 'html.parser')
		if p_debug == 10:
			print (soup)

		tags = soup(cc_html_tag_to_search)
		for tag in tags:
			line = tag.text.strip()
			i = i + 1
			if p_debug == 10:
				print(str(i) + '.' + line)

			# Assumption: Rating will appear first in the page than the customer reviews count
			tag_found = line.find(cc_rating_text)
			if 0 < tag_found and rating == ' ':
				if p_debug == 1:
					print ('Rating found in line ' + str(i) + ': ' + line)
				rating = line[:line.find(' ')]
				tags_found = tags_found + 1

			tag_found = line.find(cc_reviews_text)
			if 0 < tag_found and reviews_count == ' ':
				if p_debug == 1:
					print (line + ' found in line ' + str(i))
				reviews_count = line[:line.find(' ')]
				tags_found = tags_found + 1

			if tags_found == 2:
				break
		
		rating_and_reviews = reviews_count + p_delimiter + rating
	except Exception as e:
		#print(e.reason)
		rating_and_reviews = 'Unexpected error in get_rating_and_reviews_count: ' + e.reason + ' error code ' + str(e.code) + '\n'
#	finally:
#		pass
	return rating_and_reviews
# ***********************************************

# ***********************************************
def search_by_keywords(p_keywords, p_search_indexes, p_region, p_debug=0):

	# ***********************************************
	# Libraries to get Amazon products
	from amazon.api import AmazonAPI
	# ***********************************************

	access_key, secret_key, associate_tag = get_credentials(p_debug)
	amazon = AmazonAPI(access_key, secret_key, associate_tag, Region = p_region)

	try:
		products = amazon.search( Keywords = p_keywords, SearchIndex=p_search_indexes )
	except SearchException as e:
		products = 'No data found'
		print(type(e))
	except Exception as e:
		#print(e.reason)
		products = 'Unexpected error in search_by_keywords: ' + e.reason + ' error code ' + str(e.code) + '\n'
#	finally:
#		pass
	return products
	
# ***********************************************
def get_total_elements(p_iterable, p_debug=0):
	v_iterable = p_iterable
	total = 0
	for i in v_iterable:
		if not i:
			total = 0
		else:
			total = total + 1
	if p_debug == 1:
		print ('Inside ' + str(total))
	return total

# ***********************************************
def get_report_data(p_report, p_region, p_wpr, p_title_name, p_film_year, p_director_name, p_products, p_products_tmp, p_max_urls_by_title, p_delimiter, p_debug=0):
	# Variables declaration
	if p_report == 'Scrape':
		# Variables declaration
		release_year = ' '	# Release year from Amazon Product Release Date
		title_found = 0		# Found: 1 / Not found: 0
		director_found = 1	# Found: 1 / Not found: 0
		film_year_found = 1	# Found: 1 / Not found: 0
		line = ''			# Data line
		total_products = get_total_elements(p_products_tmp)
		if total_products > 0:
			#print('Products found: ' + str(total_products))
			for j, product in enumerate(p_products): # Find data from Amazon response
				asin = product.asin
				title = product.title
				url = product.offer_url
				directors = ', '.join(product.directors)
				# To be discussed with Christopher and Natasha
				#if product.release_date is None:
				#	release_year = '0'
				#else:
				#	release_year = product.release_date.strftime('%Y')
				#print(url + ' ' + release_year)
				#director_found = directors.find(p_director_name)
				#film_year_found = release_year.find(p_film_year)
				if director_found == 1 and film_year_found == 1:
					title_found = title_found + 1
					# Getting Rating and Reviews Count
					string_item = get_rating_and_reviews_count(asin, p_region, p_delimiter)
					tmp_num = string_item.find(p_delimiter)
					reviews_count = string_item[:tmp_num]
					rating = string_item[tmp_num + 1:]
					line = line + p_wpr + '\t' + asin + '\t' + url + '\t' + p_title_name + '\t' + title + '\t' + p_film_year + '\t' + p_director_name + '\t' + rating + '\t' + reviews_count + '\n'
					if reviews_count == ' ' or rating == ' ':
						line = line + 'Error: Could not find reviews count or rating\n'
				if p_max_urls_by_title <= title_found:
					break
	return line
