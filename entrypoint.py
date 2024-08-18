import os
import os.path
import re
import json

from factorioModPortal import FactorioModPortal
# ------------------------------------------------------------------------------- #
class factorioModDeploymentError(RuntimeError):
	'''Custom Error representing issues with the mod deployment'''

# ------------------------------------------------------------------------------- #
# 	Set up Env
# ------------------------------------------------------------------------------- #
# Get Various inputs from ENV
GITHUB_REPOSITORY_OWNER = os.environ['GITHUB_REPOSITORY_OWNER']
GITHUB_REPOSITORY = os.environ['GITHUB_REPOSITORY']
print("Starting Deployment for : %s" % (GITHUB_REPOSITORY))
FACTORIO_APIKEY = os.environ['INPUT_MOD_UPLOAD_API_KEY']
if FACTORIO_APIKEY.isspace() or len(FACTORIO_APIKEY) == 0:
	raise factorioModDeploymentError("Factorio API key is required for deployment")
GITHUB_REF = os.environ['GITHUB_REF']
print("Environment set up successfully, running on ref: %s" % GITHUB_REF)
# ------------------------------------------------------------------------------- #
# 	Ensure we are on a tagged push
# ------------------------------------------------------------------------------- #
tag_pattern = re.compile(r"^refs\/tags\/(?P<major>\d+)\.(?P<minor>\d+)\.(?P<build>\d+)$")
tag_match = tag_pattern.match(GITHUB_REF)
if tag_match:
	mod_version = tag_match.groupdict()
else:
	raise factorioModDeploymentError("Invalid tag or not a tagged push")
print("Version tag %d.%d.%d" % (int(mod_version["major"]), int(mod_version["minor"]), int(mod_version["build"])))
# ------------------------------------------------------------------------------- #
# 	Ensure correct package with version and changelog
# ------------------------------------------------------------------------------- #
# check mod json
if not os.path.isfile('./info.json'):
	raise factorioModDeploymentError("info.json missing")
with open('./info.json') as json_file:
	data = json.load(json_file)
	modinfo_name = data["name"]
	modinfo_version = data["version"]
	modinfo_fullname = ("%s_%s" % (modinfo_name, modinfo_version))
	modinfo_filename = ("%s_%s.zip" % (modinfo_name, modinfo_version))
print("Mod info:")
print("  name:     %s" % modinfo_name)
print("  version:  %s" % modinfo_version)
print("  fullname: %s" % modinfo_fullname)
print("  filename: %s" % modinfo_filename)
# check if version matches tag
tag_version = "%d.%d.%d" % (int(mod_version["major"]), int(mod_version["minor"]), int(mod_version["build"]))
if tag_version != modinfo_version:
	raise factorioModDeploymentError("mod version %s does not match tag %s" % (modinfo_version, tag_version))
print("mod version matches release tag")
# check for changelog
file = open('./changelog.txt', 'r')
flines = file.readlines()
str_version = ("Version: %s\n" % modinfo_version)
res = [x for x in flines if x == str_version]
if len(res) != 1:
	raise factorioModDeploymentError("Current version %s not found in 'changelog.txt' or Duplicate entry" % modinfo_version)
# check for mod package
modinfo_filepath = ("./dist/%s" % modinfo_filename)
if not os.path.isfile(modinfo_filepath):
	raise factorioModDeploymentError("%s is missing\nDid you run Roang-zero1/factorio-mod-package@master ?" % modinfo_filepath)
modinfo_filesize = os.path.getsize(modinfo_filepath)
print("%s found, filesize is %d bytes" % (modinfo_filepath, modinfo_filesize))
# ------------------------------------------------------------------------------- #
# 	Access Mod Portal and deploy
# ------------------------------------------------------------------------------- #
portal = FactorioModPortal(FACTORIO_APIKEY)
# Start deployment to mod-portal
portal.upload_mod(modinfo_name, modinfo_filepath)
