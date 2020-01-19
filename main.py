import httplib2
import os, io
import pickle

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive', 
                                                            'https://www.googleapis.com/auth/drive.readonly']
class API():
    def __init__(self, SCOPES):
        # If modifying these scopes, delete your previously saved credentials
        self.SCOPES = SCOPES
        self.creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.path.join(os.getcwd(),'credentials/client_secret.json'), SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('drive', 'v3', credentials=self.creds)


    def listFiles(self, size, display= True):
        results = self.service.files().list(
            pageSize=size,fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        if display:
            if not items:
                print('No files found.')
            else:
                print('Files:')
                for item in items:
                    pass
                    print(u'{0} ({1})'.format(item['name'], item['id']))

        return items


    def uploadFile(self, filename,filepath,mimetype = None):
        file_metadata = {'name': filename}
        media = MediaFileUpload(filepath,
                                mimetype=mimetype)
        file = self.service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id').execute()
        print('File ID: %s' % file.get('id'))


    def downloadFile(self, file_id, file_name ='Untitled'):
        file_path = os.path.join(os.getcwd(), file_name)
        if os.path.isfile(file_path):
            print("Warning. File already exists")
            replace = input("\nTo overwrite enter: n \nTo keep as seprate files: y\n choice: ")
            while replace != 'n' and replace != 'y': 
                replace = input("Enter again\nTo overwrite enter: n \nTo keep as seprate files: y\n choice: ")

            if replace == 'n':
                file_path = file_path[:file_path.find('.')] + f'({1})' + file_path[file_path.find('.'):]
        
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))
        with io.open(file_path,'wb') as f:
            fh.seek(0)
            f.write(fh.read())


    def createFolder(self, name):
        file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
        }
        file = self.service.files().create(body=file_metadata,
                                            fields='id').execute()
        print ('Folder ID: %s' % file.get('id'))

    def searchFile(self, size,query):
        results = self.service.files().list(
        pageSize=size,fields="nextPageToken, files(id, name, kind, mimeType)",q=query).execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print(item)
                print('{0} ({1})'.format(item['name'], item['id']))


if __name__ == '__main__':
    API = API(SCOPES)
    #API.uploadFile('test.txt','/media/kasem/Happy_place/University stuff/PlayGround/Google Drive sync app/test.txt')
    files_list = API.listFiles(4,display= True)
    item_0_ID = files_list[0]['id']
    API.downloadFile(item_0_ID, files_list[0]['name'])
    #uploadFile('unnamed.jpg','unnamed.jpg','image/jpeg')
    #downloadFile('1Knxs5kRAMnoH5fivGeNsdrj_SIgLiqzV','google.jpg')
    #createFolder('Google')