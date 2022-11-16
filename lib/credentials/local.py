import json
class LocalFileCredentials:
    def __init__(self, relative_file_path) -> None:
        self.relative_file_path = relative_file_path
    
    def save_updated_credentials(self, response):
        ACCESS_TOKEN = response["access_token"]
        REFRESH_TOKEN = response["refresh_token"]	
        with open(self.relative_file_path, "r+") as credFile:
            cred_dict = json.load(credFile)
            cred_dict["access_token"] = ACCESS_TOKEN
            cred_dict["refresh_token"] = REFRESH_TOKEN
            credFile.seek(0)
            credFile.write(json.dumps(cred_dict))

    def get_credentials(self):
        try: 
            with open(self.relative_file_path, "r+") as credFile:
                cred_dict = json.load(credFile)
                CLIENT_ID = cred_dict["client_id"]
                CLIENT_SECRET = cred_dict["client_secret"]
                ACCESS_TOKEN = cred_dict["access_token"]
                REFRESH_TOKEN = cred_dict["refresh_token"] 
                return (CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN, REFRESH_TOKEN)
        except Exception as e:
            print(dir(e))
            print(e.msg)
            print("Unable to load credentials")
            exit()