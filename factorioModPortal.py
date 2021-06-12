import os
import requests
from lxml import html
import re
import json


class factorioModPortalError(RuntimeError):
	'''Custom Error representing issues with the factorio mod ~api~'''


class factorioModPortal():
	def __init__(self, factorio_user, factorio_password, debug=0):
		self.factorio_user = factorio_user
		self.factorio_password = factorio_password
		self.debug = debug
		print("new factorio mod portal session")
		self.session = requests.Session()

	def check_pattern(self, regex_pattern, text):
		pattern = re.compile(regex_pattern, re.MULTILINE | re.DOTALL)
		match = pattern.match(text)
		if match:
			return match.groupdict()
		else:
			return None

	def save_file(self, file_name, content):
		if self.debug:
			with open(file_name, "w") as f:
				f.write(content)

	def get_csrf_token(self):
		print("get_csrf_token")
		res = self.session.get('https://factorio.com/login?mods=1&next=%2Ftrending')
		if res.status_code != 200:
			print("  http status code:", res.status_code)
		tree = html.fromstring(res.text)
		csrf_token_result = tree.xpath('//*[@id="csrf_token"]/@value')
		if len(csrf_token_result) == 0:
			raise factorioModPortalError("Error obtaining csrf_token")
		else:
			print("  Obtained csrf_token")
		self.csrf_token = csrf_token_result[0]

	def get_auth_token(self):
		print("get_auth_token")
		data = {
			'username': self.factorio_user,
			'password': self.factorio_password
		}
		res = self.session.post('https://auth.factorio.com/api-login', data=data)
		if res.status_code != 200:
			print("  http status code:", res.status_code)
		data = json.loads(res.text)
		if "error" in data:
			# application/json
			# {
			#   "data":{},
			#   "error":"login-failed",
			#   "message":"Given username or email and password do not match any account",
			#   "status":401
			# }
			raise factorioModPortalError("%s, %s" % (data["error"], data["message"]))
		else:
			print("  Auth token obtained")
		self.auth_token = data[0]

	# The login method is very picky at mod-portal side
	# This is very messy HTML parsing, It would be nice if the factorio team added a ~real~ json based API
	def login(self):
		print("login")
		self.get_csrf_token()
		self.session.headers.update({'referer': "https://factorio.com/login"})
		data = {
			'username_or_email': self.factorio_user,
			'password': self.factorio_password,
			'csrf_token': self.csrf_token,
			'next_url': "/profile"
		}
		res = self.session.post('https://factorio.com/login', data=data)
		if res.status_code != 200:
			print("  http status code:", res.status_code)
		self.save_file("loginresult.html", res.text)
		login_success = self.check_pattern(
			r".*(?P<login_success>You\s+have\s+been\s+successfully\s+logged\s+in).*",
			res.text
		)
		if login_success:
			print("  Login success")
			return
		else:
			login_error = self.check_pattern(
				r"<ul class=\"flashes\">[\s\n]*<li>(?P<login_error>.*)<\/li>",
				res.text
			)
			if login_error:
				raise factorioModPortalError("Login Error:%s" % login_error["login_error"])
			captcha_error = self.check_pattern(
				r".*(?P<captcha_error>Please\s+pass\s+the\s+CAPTCHA).*",
				res.text
			)
			if captcha_error:
				raise factorioModPortalError("Captcha error:%s" % captcha_error["captcha_error"])
		raise factorioModPortalError("Login Failed")

	# This is very messy HTML parsing, It would be nice if the factorio team added a ~real~ json based API
	def get_upload_token(self, modName):
		print("get_upload_token")
		url = "https://mods.factorio.com/mod/%s/downloads/edit" % (modName)
		res = self.session.get(url)
		if res.status_code != 200:
			print("  http status code:", res.status_code)
		self.save_file("uploadTokenResult.html", res.text)
		tree = html.fromstring(res.text)
		script_result = tree.xpath('/html/body/script/text()')
		for script in script_result:
			token_match = self.check_pattern(
				r"[\s\r\n]*Factorio\.createEdit\(\s*\{.*token[\s\r\n]*:[\s\r\n]*[\"'](?P<token>[^\"']+)[\"'].*\}\s*\)[\s\r\n]*",
				script
			)
			if token_match:
				print("  obtained upload token")
				self.upload_token = token_match['token']
				return
		raise factorioModPortalError("Failed to obtain upload token")

	# This is very messy HTML parsing, It would be nice if the factorio team added a ~real~ json based API
	def upload_mod(self, modName, fileName):
		print("upload_mod")
		self.get_upload_token(modName)
		url = "https://direct.mods-data.factorio.com/upload/mod/%s" % self.upload_token
		print("  uploading mod")
		with open(fileName, 'rb') as zip_file:
			files = {'file': zip_file}
			res = self.session.post(url, files=files)
		if res.status_code != 200:
			print("  http status code:", res.status_code)
		self.save_file("uploadFileResult.json", res.text)
		data = json.loads(res.text)
		print("  confirming upload")
		url = "https://mods.factorio.com/mod/%s/downloads/edit" % (modName)
		data = {
			"file": None,
			"info_json": data["info"],
			"changelog": data["changelog"],
			"filename": data["filename"],
			"file_size": os.path.getsize(fileName),
			"thumbnail": data["thumbnail"]
		}
		res = self.session.post(url, data=data)
		self.save_file("uploadFileResult2.html", res.text)
		if res.status_code != 200:
			print("  http status code:", res.status_code)
		tree = html.fromstring(res.text)
		success_message = tree.xpath("/html/body//div[contains(@class, 'alert-success')]/*/text()")
		if len(success_message) > 0:
			for message_node in success_message:
				message = str(message_node)
				if not (message + " ").isspace():
					print("  " + message.strip())
			return
		error_match = self.check_pattern(
			r"category:\s*'error',\s*\n\s*message:\s*'(?P<error>[^']*)'",
			res.text
		)
		errorMsg = "Unknown Error"
		if error_match:
			errorMsg = error_match["error"]
		raise factorioModPortalError(errorMsg)
