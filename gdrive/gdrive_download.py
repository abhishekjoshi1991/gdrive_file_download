import os.path
import shutil
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from tqdm import tqdm

gauth = GoogleAuth()
# gauth.CommandLineAuth()

gauth.LoadCredentialsFile("credentials.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
gauth.SaveCredentialsFile("credentials.txt")

drive = GoogleDrive(gauth)

class GDriveFile:

    def __init__(self, parent_folder_id, parent_folder_dir):
        self.parent_folder_id = parent_folder_id
        self.parent_folder_dir = parent_folder_dir

    '''
    Get parent folder name from id and create local directory
    if parent directory is present then create backup of that and then download parent directory
    if backup and parent directory both are present, then delete old backup and create
    backup of previous parent directory and then download parent directory
    '''
    def get_folder_name(self):
        content = drive.ListFile().GetList()
        for rec in content:
            if rec['id'] == self.parent_folder_id:
                self.parent_folder_dir = self.parent_folder_dir + rec['title']
                if os.path.exists(self.parent_folder_dir):
                    renamed_path = self.parent_folder_dir + '_backup'
                    if os.path.exists(renamed_path):
                        shutil.rmtree(renamed_path)
                    os.rename(self.parent_folder_dir, renamed_path)
                    os.mkdir(self.parent_folder_dir)
                else:
                    os.mkdir(self.parent_folder_dir)

    # Get list of dictionary for folders and files in parent folder
    @staticmethod
    def fetch_data(parent_folder_id_outer, parent_folder_dir_outer):
        file_dict = dict()
        if parent_folder_dir_outer[-1] != '/':
            parent_folder_dir_outer = parent_folder_dir_outer + '/'

        folder_queue = [parent_folder_id_outer]
        dir_queue = [parent_folder_dir_outer]

        cnt = 0
        while len(folder_queue) != 0:
            current_folder_id = folder_queue.pop(0)
            file_list = drive.ListFile({'q': "'{}' in parents and trashed=false".format(current_folder_id)}).GetList()

            current_parent = dir_queue.pop(0)
            # print(current_parent, current_folder_id)

            for file1 in file_list:
                file_dict[cnt] = dict()
                file_dict[cnt]['id'] = file1['id']
                file_dict[cnt]['title'] = file1['title']
                file_dict[cnt]['dir'] = current_parent + file1['title']

                if file1['mimeType'] == 'application/vnd.google-apps.folder':
                    file_dict[cnt]['type'] = 'folder'
                    file_dict[cnt]['dir'] += '/'
                    folder_queue.append(file1['id'])
                    dir_queue.append(file_dict[cnt]['dir'])
                    dirname = f"{parent_folder_dir_outer}{file1['title']}"
                    GDriveFile.fetch_data(file1['id'],dirname)
                else:
                    file_dict[cnt]['type'] = 'file'
                cnt += 1
        return file_dict

    # Create folders and files locally
    def create_file_folder(self):
        file_list = GDriveFile.fetch_data(self.parent_folder_id, self.parent_folder_dir)
        with tqdm(range(len((file_list.keys()))), desc="Downloading Files/Folders") as pbar:
            for file_iter in file_list.keys():
                if file_list[file_iter]['type'] == 'folder':
                    try:
                        if not os.path.exists(file_list[file_iter]['dir']):
                            os.mkdir(file_list[file_iter]['dir'])
                            pbar.update(1)
                    except:
                        pass
                else:
                    path_to_save = file_list[file_iter]['dir'].split(file_list[file_iter]['title'])[0]
                    os.chdir(path_to_save)
                    file_to_save = drive.CreateFile({'id': file_list[file_iter]['id']})
                    file_to_save.GetContentFile(file_list[file_iter]['title'])
                    pbar.update(1)


folder_id_to_download = '1jL9KlZleK184Wa9JclTAsVgsXG-llAxb'
local_folder_path = '/home/abhishek/Music/'

g_drive_obj = GDriveFile(folder_id_to_download, local_folder_path)
g_drive_obj.get_folder_name()
g_drive_obj.create_file_folder()
