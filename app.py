from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from requests import get
import json
import os
import datetime
import re
import logging
import random

def config_init():
	"""
	Set required variables from config file.
	"""
	try:
		with open('config.json') as f:
			config = json.load(f)
	except Exception as e:
		print(e)
		print('no config found')
		exit
	return config

# Configure app
config = config_init()
secret_key = 'HTTP_{}'.format(config['secret']['key'].upper().replace('-','_').replace(' ', '_')) # Parse secret_key header name to match HTTP standard eg.: please-send-me becomes: HTTP_PLEASE_SEND_ME
secret_value = config['secret']['value']
logfile = config['logfile']
p = re.compile('''\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}''')

def app_init():
	"""
	Set up Flask app
	"""
	app = Flask(__name__)
	api = Api(app)
	app.logger.disabled = True
	log = logging.getLogger('werkzeug')
	log.disabled = False
	return (app, api)

def decoy():
	"""
	Generate fake IP address for unathenticated requests
	"""
	fake_ip = '{}.{}.{}.{}'.format(random.randint(3,254),
		random.randint(3,254),
		random.randint(3,254),
		random.randint(3,254)
		)
	return {'ip': fake_ip }

def write_log(msg, logfile=logfile):
	"""
	Write events to log
	"""
	if os.path.isfile(logfile):
		write_mode = 'a+'
	else:
		write_mode = 'w'
	with open(logfile, write_mode) as f:
		f.write('{} - {}\n'.format(datetime.datetime.now(), msg))

def save_ip(ip):
	"""
	Save IP address to ip.txt
	"""
	with open('ip.txt', 'w') as f:
		f.write(ip)

def read_ip_from_file():
	"""
	Read IP from ip.txt
	"""
	ip = None
	try:
		with open('ip.txt', 'r') as f:
			ip = f.read()
	except: 
		ip = 'NOT SET'
	return ip

def read_ip():
	"""
	Get IP address from os environment information
	"""
	try:
		ip = os.environ['PUBLIC_IP']	
	except Exception as e:
		os.environ['PUBLIC_IP'] = read_ip_from_file()

def header_ok(request, header, value=None):
	"""Check if incoming HTTP header matches config"""
	try:
		if value:
			if request.environ[header] == value:
				return True
			else:
				return False
		else:
			return False
	except:
		return False


class IPApi(Resource):
	"""Main API object"""
	def get(self):
		"""
		Handle GET requests
		If the header has the required information, read public IP and return it
		If the header lacks the required information, generate a random IP and return it
		"""
		try:
			if header_ok(request, secret_key, secret_value):
				read_ip()
				write_log('INFO - IP requested from: {}'.format(request.environ['REMOTE_ADDR']))
				return {'ip': os.environ['PUBLIC_IP']}, 200
			else:
				raise KeyError
		except KeyError:
			write_log('WARN - IP requested without header from: {}'.format(request.environ['REMOTE_ADDR']))
			return decoy()

	def post(self):
		"""
		Parse POST request from client app
		"""
		try:
			data = request.args.get('ip')
			if p.match(data) and header_ok(request, secret_key, secret_value):
				try:
					old_ip = os.environ['PUBLIC_IP']
				except:
					old_ip = 'None'
				os.environ['PUBLIC_IP'] = data  			# Set PUBLIC_IP environ to current public IP
				save_ip(data)
				write_log('INFO - IP updated from {} to {} - from: {}'.format(old_ip, os.environ['PUBLIC_IP'], request.environ['REMOTE_ADDR']))
				return {'msg': 'ok'}, 200
			else:
				write_log('WARN - invalid POST request from: {}'.format(request.environ['REMOTE_ADDR']))
				return 'invalid format', 400
		except Exception as e:
			print(e)
			write_log('WARN - invalid POST request from: {}'.format(request.environ['REMOTE_ADDR']))
			return {'msg': 'no data'}, 400
		

if __name__ == '__main__':
	# Load config
	config_init()
	# Initalise Flask app
	app_data = app_init()
	app = app_data[0]
	api = app_data[1]
	api.add_resource(IPApi, '/')
	app.run(host='0.0.0.0', port=1265)
