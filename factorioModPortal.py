import requests


class FactorioModPortalError(RuntimeError):
    """Custom Error representing issues with the Factorio mod portal API."""


class FactorioModPortal:
    MOD_PORTAL_URL = "https://mods.factorio.com"
    INIT_UPLOAD_URL = f"{MOD_PORTAL_URL}/api/v2/mods/releases/init_upload"

    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    def init_upload(self, mod_name):
        response = self.session.post(
            self.INIT_UPLOAD_URL,
            data={"mod": mod_name}
        )
        if not response.ok:
            raise FactorioModPortalError(f"init_upload failed: {response.text}")
        upload_url = response.json().get("upload_url")
        if not upload_url:
            raise FactorioModPortalError("Failed to obtain upload URL")
        return upload_url

    def upload_mod(self, mod_name, file_path):
        upload_url = self.init_upload(mod_name)

        with open(file_path, "rb") as file:
            response = self.session.post(upload_url, files={"file": file})
            if not response.ok:
                raise FactorioModPortalError(f"upload failed: {response.text}")

        print(f"Upload successful: {response.text}")
