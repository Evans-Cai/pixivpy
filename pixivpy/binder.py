# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Pixiv API
# modify from tweepy (https://github.com/tweepy/tweepy/)

import gzip
from .compat import *


def bind_api(**config):
	class APIMethod(object):
		path = config['path']
		method = config.get('method', 'GET')
		allowed_param = config.get('allowed_param', [])
		parser = config.get('parser', None)
		require_auth = config.get('require_auth', False)
		save_session = config.get('save_session', False)
		payload_list = config.get('payload_list', False)

		def __init__(self, api, args, kargs):
			if self.require_auth and not api.session:
				raise Exception('Authentication required!')

			self.api = api
			self.api_root = api.api_root
			self.headers = kargs.pop('headers', {
					'Referer': 'http://spapi.pixiv.net/',
					'User-Agent': 'pixiv-ios-app(ver4.0.0)',
				})
			self.post_data = kargs.pop('post_data', None)
			self.build_parameters(args)

			self.headers['Host'] = api.host

		def build_parameters(self, args):
			self.parameters = []
			self.parameters.extend(zip(self.allowed_param, args))
			if (self.require_auth):
				self.parameters.append(("PHPSESSID", self.api.session))

		def execute(self):
			# Build the request URL
			url = self.api_root + self.path
			host, port = self.api.host, self.api.port
			conn = HTTPConnection(host, port, timeout=self.api.timeout)

			if len(self.parameters):
				url = '?'.join((url, urlencode(self.parameters)))

			# Request compression if configured
			if self.api.compression:
				self.headers['Accept-encoding'] = 'gzip'

			# Execute request
			try:
				conn.request(self.method, url, self.post_data, self.headers)
				resp = conn.getresponse()
			except Exception as e:
				raise Exception('Failed to send request: %s' % e)
			else:
				body = resp.read()
			finally:
				conn.close()

			# handle redirect
			if resp.status in (301, 302) and self.save_session:
				redirect_url = resp.getheader('location', '')
				if resp.getheader('Set-Cookie'):
					session_string = resp.getheader('Set-Cookie').split(';')[0]
					self.api.session = session_string.split('=')[1].strip()
				else:
					sid_key = "PHPSESSID"
					idx = redirect_url.rfind(sid_key) + len(sid_key) + 1
					self.api.session = redirect_url[idx:]
				return self.api.session

			if not (200 <= resp.status < 400):
				raise Exception("Bad response status: %s" % resp.status)

			# Parse the response payload

			if resp.getheader('Content-Encoding', '') == 'gzip':
				try:
					zipper = gzip.GzipFile(fileobj=BytesIO(body))
					body = zipper.read()
				except Exception as e:
					raise Exception('Failed to decompress data: %s' % e)

			if not py2:
				body = body.decode('utf-8')

			if (self.parser):
				result = self.parser(body)

				if not self.payload_list:
					result = result[0] if len(result) else None
			else:
				result = body		# parser not define, return raw string

			return result

	def _call(api, *args, **kargs):
		method = APIMethod(api, args, kargs)
		return method.execute()

	return _call