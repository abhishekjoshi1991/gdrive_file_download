from __future__ import print_function

import os.path
import io

from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


class GDriveFiles:
    @staticmethod
    def main():
        """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds

    @staticmethod
    def download_file(real_file_id):
        import pdb; pdb.set_trace()
        creds = GDriveFiles.main()
        try:
            # create drive api client
            service = build('drive', 'v3', credentials=creds)

            file_id = real_file_id

            request = service.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(F'Download {int(status.progress() * 100)}.')

            file.seek(0)
            path = os.getcwd() + '/' + file_id
            with open(path, 'wb') as f:
                f.write(file.read())
                f.close()

        except HttpError as error:
            print(F'An error occurred: {error}')
            file = None

        return file.getvalue()

if __name__ == '__main__':
    # pass id of file to be downloaded
    file_id_to_dwnld = '1jL9KlZleK184Wa9JclTAsVgsXG-llAxb'
    GDriveFiles.download_file(file_id_to_dwnld)
