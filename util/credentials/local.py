import json
import os


class LocalFileCredentials:
    def __init__(self, relative_file_path='~/.GarminDb/GarminConnectConfig.json') -> None:
        self.absolute_path = os.path.expanduser(relative_file_path)

    def get_credentials(self):
        try:
            with open(self.absolute_path, "r+") as credFile:
                creds = json.load(credFile)
                USERNAME = creds["credentials"]["user"]
                PASSWORD = creds["credentials"]["password"]
                return (USERNAME, PASSWORD)
        except Exception as e:
            print(dir(e))
            print(e.msg)
            print("Unable to load credentials")
            exit()
