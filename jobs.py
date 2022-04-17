from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os, json, sys
from datetime import datetime
import pathlib

installation_path = os.getcwd()
user_folder = os.path.join(installation_path, "user")
user_data_path = os.path.join(user_folder, "user_data.json")
jobs_path = os.path.join(user_folder, "all_jobs.json")
status_path = os.path.join(user_folder, "status.txt")


def read_text(path):
    with open(path, "r") as o:
        return o.read().strip()


# ----------------------------------
# check for online status
# ----------------------------------
online_flag = read_text(status_path)
if online_flag != "1":
    print("Not logged in !!")
    sys.exit(0)


def create_(path, dict):
    with open(path, "w") as outfile:
        json.dump(dict, outfile, indent=4)


def read_(path):
    with open(path) as json_file:
        data = json.load(json_file)
    return data


u_data = read_(user_data_path)

if "drive user" not in u_data.keys():
    print("Not logged in yet")
    sys.exit(0)
user = ""
if "drive user" in u_data.keys():
    user = u_data["drive user"].split("@")[0]

gauth = GoogleAuth()
# Try to load saved client credentials
gauth.LoadCredentialsFile(f"{user}.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile(f"{user}.txt")

drive = GoogleDrive(gauth)


def create_file_on_drive(title, filename, folder_id):

    try:
        file_to_create = drive.CreateFile(
            {"title": title, "parents": [{"kind": "drive#fileLink", "id": folder_id}]}
        )
        file_to_create.SetContentFile(filename)
        file_to_create.Upload()
    except Exception as e:
        print("create_file_on_drive Exception :", e)


if os.path.exists(user_data_path) == False:
    user_data = {}
    create_(user_data_path, user_data)

if os.path.exists(jobs_path) == False:
    jobs_ = {}
    create_(jobs_path, jobs_)

# -----------------------------------
# Create Backup folder
# -----------------------------------
root_flag = False
foldername = "Backup_____________"


file_list = drive.ListFile({"q": "'root' in parents and trashed=false"}).GetList()
for file_ in file_list:
    if file_["title"] == foldername:
        root_flag = True

if root_flag == False:
    file_metadata = {
        "title": foldername,
        "name": foldername,
        "mimeType": "application/vnd.google-apps.folder",
    }
    folder = drive.CreateFile(file_metadata)
    folder.Upload()

file_list = drive.ListFile({"q": "'root' in parents and trashed=false"}).GetList()

root_folder_id = ""
for file_ in file_list:
    if file_["title"] == foldername:
        root_folder_id = file_["id"]
f_ = read_(user_data_path)
f_["root_folder_id"] = root_folder_id
create_(user_data_path, f_)


# ------------------------
# Complete jobs
# ------------------------
all_jobs_ = read_(jobs_path)

for file_ in all_jobs_.keys():

    if (
        all_jobs_[file_][0] == "Instant" and all_jobs_[file_][4] == 1
    ):  # backup type & job status
        ts1 = int(float(all_jobs_[file_][3]))
        ct = int(os.path.getmtime(file_))

        if ct > ts1:  # file changed recently
            # upload the file to gdrive
            time_c = datetime.utcfromtimestamp(ct).strftime(
                "Date(%Y-%m-%d)Time(%H-%M-%S)"
            )
            filename = os.path.basename(file_)
            file_ext = pathlib.Path(filename).suffix

            string_ = "{}___{}".format(filename.replace(file_ext, ""), time_c)
            title_ = "{}{}".format(string_, file_ext)
            print("Uploading :", title_)

            # -----------------------------------
            # check for version on drive
            # -----------------------------------
            files = drive.ListFile(
                {"q": "'{}' in parents and trashed=false".format(root_folder_id)}
            ).GetList()

            version_count = 0
            for file___ in files:
                if filename.replace(file_ext, "") in file___["title"]:
                    version_count += 1
                    if version_count >= int(all_jobs_[file_][1]):
                        # version limit exceeded
                        file___.Trash()
                        print("Deleting {}".format(file___["title"]))
            print("Total version :", version_count)

            create_file_on_drive(
                title_,
                file_,
                root_folder_id,
            )
            all_jobs_[file_][3] = ct

            create_(jobs_path, all_jobs_)
            print("Updated in jobs.")
