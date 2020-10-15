from requests import post, get
import json
import time

pub_ip_api_address = 'https://ip4.seeip.org/json'
update_interval = 3600
server_address = ''
secret = {'SECRET': 'SECRET_KEY_CHANGE_ME_IN_CONFIG'}

def init():
	"""
	Set required variables from config file.
	"""
	try:
		with open('config.json') as f:
			config_file = json.load(f)
			config = {
				'pub_ip_api_address': config_file['urls'][config_file['protocol']],
				'update_interval': config_file['update_interval'],
				'server_address': config_file['urls']['server_address'],
				'secret': {config_file['secret']['key']: config_file['secret']['value']}
			}
			return config
	except: 
		exit

def get_public_ip(url):
	"""
	Pull public ip from provider. Response must be JSON
	"""
	try:
		r = get(url)
		data = r.json()
		print(data)
		return data['ip']
	except:
		pass

def get_stored_ip(url):
	"""
	Get IP stored in our server
	"""
	try:
		r = get(url, headers=config['secret'])
		data = r.json()
		return data['ip']
	except:
		pass

def post_ip(url, payload):
	try:
		r = post('{}?ip={}'.format(url, payload['ip']), config['secret'])
	except:
		r = None
	return r

def main():
	while True:
		pub_ip = get_public_ip(config['pub_ip_api_address'])
		stored_ip = get_stored_ip(config['server_address'])
		if pub_ip != stored_ip:
			payload = {'ip': pub_ip}
			post_ip(config['server_address'], payload)
		time.sleep(3600)

if __name__ == '__main__':
	config = init()
	main()
