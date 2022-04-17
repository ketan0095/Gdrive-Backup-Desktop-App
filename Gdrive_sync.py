from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QWidget
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os, json, subprocess

installation_path = os.getcwd().replace("\Gdrive_sync", "")
client_path = os.path.join(installation_path, "client_secret.json")
user_folder = os.path.join(installation_path, "user")
user_data_path = os.path.join(user_folder, "user_data.json")
jobs_path = os.path.join(user_folder, "all_jobs.json")
status_path = os.path.join(user_folder, "status.txt")
jobs_call_path = os.path.join(installation_path, "jobs.py")


timer = QtCore.QTimer()

if os.path.exists(user_folder) == False:
    os.mkdir(user_folder)


def create_(path, dict):
    print("---", dict, path)
    with open(path, "w") as outfile:
        json.dump(dict, outfile, indent=4)


def update_status(path, val_=None, mode=None):
    if mode == "w":
        with open(path, mode) as o:
            o.write(val_)
            return "200"
    if mode == "r":
        with open(path, mode) as o:
            f_ = o.read()
            if f_ == "1":
                return True
            else:
                return False


def read_(path):
    if os.path.exists(path) == False:
        create_(path, {})
    with open(path) as json_file:
        data = json.load(json_file)
    return data


if os.path.exists(user_data_path) == False:
    create_(user_data_path, {})
f_ = read_(user_data_path)

if "drive user" in f_.keys():
    update_status(status_path, mode="w", val_="1")
else:
    update_status(status_path, mode="w", val_="0")


class Ui_Form(QWidget):
    def new_job(self):
        # check if node is online
        # if not send a popup msg
        # else open job frame
        print(update_status(status_path, mode="r"))
        if update_status(status_path, mode="r"):
            self.create_job_frame.show()
        else:
            print("You are offline !")

    def go_back(self):
        self.create_job_frame.hide()

    def try_connecting(self):
        # check if user json is available
        # check if user txt if available for auto login
        user_email_id = self.lineEdit_3.text()
        already_logged_flag = False
        if "@gmail.com" in user_email_id:

            # check for already logged in
            f_ = read_(user_data_path)
            if "drive user" in f_.keys():
                self.lineEdit_3.setText(f_["drive user"])
                if os.path.exists(client_path) and os.path.exits(
                    "{}.txt".format(f_["drive user"].split("@")[0])
                ):
                    # user is already logged in
                    already_logged_flag = True
                    self.status_text.setText(
                        "You are logged in as {} .".format(
                            f_["drive user"].split("@")[0]
                        )
                    )
                    self.label_5.setStyleSheet(
                        "background-color: rgb(0, 170, 0);\n"
                        "\n"
                        "border-radius:6px;\n"
                        "border:none;"
                    )
                    update_status(status_path, mode="w", val_="1")

            if not already_logged_flag:
                user_ = self.lineEdit_3.text().split("@")[0]
                try:
                    print("Trying to login...")
                    gauth = GoogleAuth()
                    # Try to load saved client credentials
                    gauth.LoadCredentialsFile("{}.txt".format(user_))
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
                    gauth.SaveCredentialsFile("{}.txt".format(user_))

                    f_ = read_(user_data_path)
                    f_["drive user"] = self.lineEdit_3.text()
                    create_(user_data_path, f_)

                    drive = GoogleDrive(gauth)

                    self.status_text.setText("You are logged in as {} .".format(user_))
                    self.label_5.setStyleSheet(
                        "background-color: rgb(0, 170, 0);\n"
                        "\n"
                        "border-radius:6px;\n"
                        "border:none;"
                    )
                    update_status(status_path, mode="w", val_="1")

                except Exception as e:
                    print("Connect Exception :", e)

        else:

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)

            # setting message for Message Box
            msg.setText("Please enetr valid Email ID !")

            # setting Message box window title
            msg.setWindowTitle("Error : 404")

            # declaring buttons on Message Box
            msg.setStandardButtons(QMessageBox.Ok)

            # start the app
            retval = msg.exec_()
            self.status_text.setText("Please enetr valid Email ID !")

    def open_explorer(self):
        fileName = QFileDialog.getOpenFileName(
            self, "Open a file", "", "All Files (*.*)"
        )
        self.label_12.setText(fileName[0])
        print(fileName)

    def job_Create(self):
        if (
            self.label_12.text() == ""
            or self.lineEdit.text() == ""
            or self.lineEdit_3.text() == ""
        ):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)

            # setting message for Message Box
            msg.setText("Make sure all fileds are filled !")

            # setting Message box window title
            msg.setWindowTitle("Job")

            # declaring buttons on Message Box
            msg.setStandardButtons(QMessageBox.Ok)

            # start the app
            retval = msg.exec_()

        else:
            filepath = self.label_12.text()
            sch_ = self.comboBox.currentText()
            version_ = self.lineEdit.text()
            space = self.lineEdit_3.text()

            f_ = read_(jobs_path)
            f_[filepath] = [sch_, version_, space, os.path.getmtime(filepath), 1]
            create_(jobs_path, f_)

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)

            # setting message for Message Box
            msg.setText(
                "Job succesfully created for {}".format(os.path.basename(filepath))
            )

            # setting Message box window title
            msg.setWindowTitle("Job")

            # declaring buttons on Message Box
            msg.setStandardButtons(QMessageBox.Ok)

            # start the app
            retval = msg.exec_()
            self.create_job_frame.hide()

    def fill_list(self):
        f_ = read_(jobs_path)

        self.listWidget.clear()
        for c, key_ in enumerate(list(f_.keys())):
            string_ = "{}\t\t{}".format(key_, f_[key_][3])
            item = QtWidgets.QListWidgetItem()
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            brush.setStyle(QtCore.Qt.NoBrush)
            item.setBackground(brush)
            self.listWidget.addItem(item)
            item.setText(string_)

        # -----------------------------
        # call jobs
        # -----------------------------
        subprocess.Popen('python "{}"'.format(jobs_call_path))

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1100, 698)
        Form.setMinimumSize(QtCore.QSize(1100, 698))
        Form.setMaximumSize(QtCore.QSize(1100, 698))
        self.Main__Frame = QtWidgets.QFrame(Form)
        self.Main__Frame.setGeometry(QtCore.QRect(0, 0, 1141, 701))
        self.Main__Frame.setStyleSheet("background-color: rgb(85, 85, 85);")
        self.Main__Frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Main__Frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Main__Frame.setObjectName("Main__Frame")
        self.Upload_Frame = QtWidgets.QFrame(self.Main__Frame)
        self.Upload_Frame.setGeometry(QtCore.QRect(20, 10, 311, 151))
        self.Upload_Frame.setStyleSheet(
            "border:2px dashed orange;\n"
            "background-color: rgb(44, 44, 44);\n"
            "border-radius:5px;\n"
            ""
        )
        self.Upload_Frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Upload_Frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Upload_Frame.setObjectName("Upload_Frame")
        self.create_job = QtWidgets.QPushButton(self.Upload_Frame)
        self.create_job.setGeometry(QtCore.QRect(100, 90, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.create_job.setFont(font)
        self.create_job.setStyleSheet(
            "background-color: rgb(170, 255, 255);\n"
            "border:2px solid black;\n"
            "border-radius:5px;"
        )
        self.create_job.setObjectName("create_job")
        self.create_job.clicked.connect(self.new_job)
        self.label = QtWidgets.QLabel(self.Upload_Frame)
        self.label.setGeometry(QtCore.QRect(20, 10, 271, 61))
        self.label.setStyleSheet("color: rgb(0, 255, 0);\n" "border:none;")
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.Upload_Frame)
        self.label_2.setGeometry(QtCore.QRect(260, 95, 31, 31))
        self.label_2.setStyleSheet("border:none")
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap(""))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName("label_2")
        self.Stat1_Frame = QtWidgets.QFrame(self.Main__Frame)
        self.Stat1_Frame.setGeometry(QtCore.QRect(350, 10, 401, 151))
        self.Stat1_Frame.setStyleSheet(
            "border:1px solid red;\n"
            "border:2px dashed yellow;\n"
            "background-color: rgb(44, 44, 44);"
        )
        self.Stat1_Frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Stat1_Frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Stat1_Frame.setObjectName("Stat1_Frame")
        self.label_3 = QtWidgets.QLabel(self.Stat1_Frame)
        self.label_3.setGeometry(QtCore.QRect(30, 20, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setStyleSheet("color: rgb(255, 255, 127);\n" "border:none;")
        self.label_3.setObjectName("label_3")
        self.connect = QtWidgets.QPushButton(self.Stat1_Frame)
        self.connect.setGeometry(QtCore.QRect(210, 90, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.connect.setFont(font)
        self.connect.setStyleSheet(
            "background-color: rgb(170, 255, 255);\n"
            "border:2px solid black;\n"
            "border-radius:5px;"
        )
        self.connect.setObjectName("connect")
        self.connect.clicked.connect(self.try_connecting)

        if update_status(status_path, mode="r"):
            self.connect.setDisabled(True)
        self.guide = QtWidgets.QPushButton(self.Stat1_Frame)
        self.guide.setGeometry(QtCore.QRect(30, 90, 121, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.guide.setFont(font)
        self.guide.setStyleSheet(
            "background-color: rgb(255, 255, 127);\n"
            "border:2px solid black;\n"
            "border-radius:5px;"
        )
        self.guide.setObjectName("guide")
        self.label_5 = QtWidgets.QLabel(self.Stat1_Frame)
        self.label_5.setGeometry(QtCore.QRect(370, 30, 12, 12))

        if update_status(status_path, mode="r"):
            self.label_5.setStyleSheet(
                "background-color: rgb(0, 170, 0);\n"
                "\n"
                "border-radius:6px;\n"
                "border:none;"
            )
        else:
            self.label_5.setStyleSheet(
                "background-color: rgb(135,135,135);\n"
                "\n"
                "border-radius:6px;\n"
                "border:none;"
            )
        self.label_5.setText("")
        self.label_5.setObjectName("label_5")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.Stat1_Frame)
        self.lineEdit_3.setGeometry(QtCore.QRect(130, 22, 231, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.lineEdit_3.setFont(font)
        self.lineEdit_3.setStyleSheet(
            "border:none;\n" "border-bottom:1px solid white;\n" "color:white;"
        )
        self.lineEdit_3.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_3.setObjectName("lineEdit_3")

        if update_status(status_path, mode="r"):
            self.lineEdit_3.setText(f_["drive user"])

        self.lineEdit_3.setPlaceholderText(r"Enter Gmail ID here..")
        self.Stat2_Frame = QtWidgets.QFrame(self.Main__Frame)
        self.Stat2_Frame.setGeometry(QtCore.QRect(770, 10, 311, 151))
        self.Stat2_Frame.setStyleSheet(
            "border:2px dashed white;\n"
            "background-color: rgb(44, 44, 44);\n"
            "border-radius:5px;\n"
            ""
        )
        self.Stat2_Frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Stat2_Frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Stat2_Frame.setObjectName("Stat2_Frame")
        self.label_6 = QtWidgets.QLabel(self.Stat2_Frame)
        self.label_6.setGeometry(QtCore.QRect(20, 20, 151, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setStyleSheet("color:white;\n" "border:none;")
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.Stat2_Frame)
        self.label_7.setGeometry(QtCore.QRect(20, 60, 171, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setStyleSheet("color:white;\n" "border:none;")
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.Stat2_Frame)
        self.label_8.setGeometry(QtCore.QRect(20, 100, 171, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.label_8.setFont(font)
        self.label_8.setStyleSheet("color:white;\n" "border:none;")
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.Stat2_Frame)
        self.label_9.setGeometry(QtCore.QRect(220, 20, 51, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.label_9.setFont(font)
        self.label_9.setStyleSheet("color:white;\n" "border:none;")
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(self.Stat2_Frame)
        self.label_10.setGeometry(QtCore.QRect(220, 60, 51, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.label_10.setFont(font)
        self.label_10.setStyleSheet("color:white;\n" "border:none;")
        self.label_10.setAlignment(QtCore.Qt.AlignCenter)
        self.label_10.setObjectName("label_10")
        self.label_11 = QtWidgets.QLabel(self.Stat2_Frame)
        self.label_11.setGeometry(QtCore.QRect(210, 100, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.label_11.setFont(font)
        self.label_11.setStyleSheet("color:white;\n" "border:none;")
        self.label_11.setAlignment(QtCore.Qt.AlignCenter)
        self.label_11.setObjectName("label_11")
        self.Table_Frame = QtWidgets.QFrame(self.Main__Frame)
        self.Table_Frame.setGeometry(QtCore.QRect(20, 180, 1061, 451))
        self.Table_Frame.setToolTip("")
        self.Table_Frame.setToolTipDuration(0)
        self.Table_Frame.setStyleSheet("\n" "")
        self.Table_Frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Table_Frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.Table_Frame.setObjectName("Table_Frame")
        self.job_status = QtWidgets.QLabel(self.Table_Frame)
        self.job_status.setGeometry(QtCore.QRect(0, 10, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.job_status.setFont(font)
        self.job_status.setStyleSheet(
            "border:1px solid white;\n"
            "background-color: rgb(44, 44, 44);\n"
            "border-radius:3px;\n"
            "color:magenta;\n"
            ""
        )
        self.job_status.setAlignment(QtCore.Qt.AlignCenter)
        self.job_status.setObjectName("job_status")
        self.listWidget = QtWidgets.QListWidget(self.Table_Frame)
        self.listWidget.setGeometry(QtCore.QRect(0, 60, 1061, 391))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.listWidget.setFont(font)
        self.listWidget.setStyleSheet(
            "border:1px solid white;\n"
            "background-color: rgb(44, 44, 44);\n"
            "border-radius:3px;"
        )
        self.listWidget.setDragEnabled(True)
        self.listWidget.setVerticalScrollMode(
            QtWidgets.QAbstractItemView.ScrollPerPixel
        )
        self.listWidget.setFlow(QtWidgets.QListView.TopToBottom)
        self.listWidget.setProperty("isWrapping", False)
        self.listWidget.setResizeMode(QtWidgets.QListView.Fixed)
        self.listWidget.setLayoutMode(QtWidgets.QListView.SinglePass)
        self.listWidget.setWordWrap(False)
        self.listWidget.setObjectName("listWidget")
        self.fill_list()

        self.create_job_frame = QtWidgets.QFrame(self.Table_Frame)
        self.create_job_frame.setGeometry(QtCore.QRect(310, 10, 431, 421))
        self.create_job_frame.setStyleSheet(
            "border:2px solid white;\n" "border-radius:5px;"
        )
        self.create_job_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.create_job_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.create_job_frame.setObjectName("create_job_frame")
        self.guide_2 = QtWidgets.QPushButton(self.create_job_frame)
        self.guide_2.setGeometry(QtCore.QRect(30, 40, 121, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.guide_2.setFont(font)
        self.guide_2.setStyleSheet(
            "background-color: rgb(170, 255, 255);\n"
            "border:2px solid black;\n"
            "border-radius:5px;"
        )
        self.guide_2.setObjectName("guide_2")
        self.guide_2.clicked.connect(self.open_explorer)
        self.label_12 = QtWidgets.QLabel(self.create_job_frame)
        self.label_12.setGeometry(QtCore.QRect(170, 50, 241, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_12.setFont(font)
        self.label_12.setStyleSheet(
            "border:none;\n" "border-bottom:1px solid white;\n" "color:white;"
        )
        self.label_12.setAlignment(QtCore.Qt.AlignCenter)
        self.label_12.setObjectName("label_12")
        self.label_13 = QtWidgets.QLabel(self.create_job_frame)
        self.label_13.setGeometry(QtCore.QRect(50, 120, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_13.setFont(font)
        self.label_13.setStyleSheet("color: rgb(255, 255, 127);\n" "border:none;")
        self.label_13.setObjectName("label_13")
        self.comboBox = QtWidgets.QComboBox(self.create_job_frame)
        self.comboBox.setGeometry(QtCore.QRect(210, 115, 141, 41))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.comboBox.setFont(font)
        self.comboBox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.comboBox.setStyleSheet("border:none;\n" "color: rgb(255, 255, 255);")
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.label_14 = QtWidgets.QLabel(self.create_job_frame)
        self.label_14.setGeometry(QtCore.QRect(40, 190, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_14.setFont(font)
        self.label_14.setStyleSheet("color: rgb(255, 255, 127);\n" "border:none;")
        self.label_14.setObjectName("label_14")
        self.lineEdit = QtWidgets.QLineEdit(self.create_job_frame)
        self.lineEdit.setGeometry(QtCore.QRect(260, 190, 61, 22))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.lineEdit.setFont(font)
        self.lineEdit.setStyleSheet(
            "border:none;\n" "border-bottom:1px solid white;\n" "color:white;"
        )
        self.lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit.setObjectName("lineEdit")
        self.label_15 = QtWidgets.QLabel(self.create_job_frame)
        self.label_15.setGeometry(QtCore.QRect(20, 250, 201, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_15.setFont(font)
        self.label_15.setStyleSheet("color: rgb(255, 255, 127);\n" "border:none;")
        self.label_15.setObjectName("label_15")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.create_job_frame)
        self.lineEdit_2.setGeometry(QtCore.QRect(240, 250, 111, 22))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.lineEdit_2.setFont(font)
        self.lineEdit_2.setStyleSheet(
            "border:none;\n" "border-bottom:1px solid white;\n" "color:white;"
        )
        self.lineEdit_2.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.create_job_2 = QtWidgets.QPushButton(self.create_job_frame)
        self.create_job_2.setGeometry(QtCore.QRect(130, 340, 151, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.create_job_2.setFont(font)
        self.create_job_2.setStyleSheet(
            "background-color: rgb(170, 255, 255);\n"
            "border:2px solid black;\n"
            "border-radius:5px;"
        )
        self.create_job_2.setObjectName("create_job_2")
        self.create_job_2.clicked.connect(self.job_Create)
        self.label_back = QtWidgets.QPushButton(self.create_job_frame)
        self.label_back.setGeometry(QtCore.QRect(80, 345, 31, 31))
        self.label_back.setStyleSheet("border:none")
        self.label_back.setIcon(QtGui.QIcon(r"C:\Users\Dell\Downloads\back.png"))
        self.label_back.setObjectName("label_back")
        self.label_back.clicked.connect(self.go_back)

        self.create_job_frame.hide()
        self.frame = QtWidgets.QFrame(self.Main__Frame)
        self.frame.setGeometry(QtCore.QRect(20, 650, 1061, 31))
        self.frame.setStyleSheet("")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.status = QtWidgets.QLabel(self.frame)
        self.status.setGeometry(QtCore.QRect(0, 0, 121, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.status.setFont(font)
        self.status.setStyleSheet(
            "border:1px solid white;\n"
            "background-color: rgb(44, 44, 44);\n"
            "border-radius:3px;\n"
            "color:magenta;\n"
            ""
        )
        self.status.setAlignment(QtCore.Qt.AlignCenter)
        self.status.setObjectName("status")
        self.status_text = QtWidgets.QLabel(self.frame)
        self.status_text.setGeometry(QtCore.QRect(120, 0, 941, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.status_text.setFont(font)
        self.status_text.setStyleSheet(
            "border:1px solid white;\n"
            "background-color: rgb(44, 44, 44);\n"
            "border-radius:3px;\n"
            "color:white;\n"
            ""
        )
        self.status_text.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.status_text.setIndent(8)
        self.status_text.setObjectName("status_text")

        timer.timeout.connect(self.fill_list)
        timer.setInterval(3000)
        timer.start()

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Backup"))
        self.create_job.setToolTip(_translate("Form", "Create a Backup Task"))
        self.create_job.setText(_translate("Form", "Create Job"))
        self.label.setText(
            _translate(
                "Form",
                "Create a job for backing a file into Google Drive.Make sure Google drive is coonected before creating job.",
            )
        )
        self.label_3.setText(_translate("Form", "Drive User "))
        self.connect.setToolTip(_translate("Form", "Connect with Google Drive"))
        self.connect.setText(_translate("Form", "Connect"))
        self.guide.setText(_translate("Form", "Guide"))
        self.label_5.setToolTip(_translate("Form", "Shows online status"))
        self.lineEdit_3.setToolTip(_translate("Form", "Input Email ID"))
        self.label_6.setText(_translate("Form", "Total Jobs Created"))
        self.label_7.setText(_translate("Form", "Current Jobs Running "))
        self.label_8.setText(_translate("Form", "Current Drive used"))
        self.label_9.setText(_translate("Form", "15"))
        self.label_10.setText(_translate("Form", "10"))
        self.label_11.setText(_translate("Form", "10 MB"))
        self.job_status.setText(_translate("Form", "Jobs Status :"))
        self.listWidget.setSortingEnabled(True)
        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)

        self.guide_2.setText(_translate("Form", "Select File"))
        self.label_12.setText(_translate("Form", ""))
        self.label_13.setText(_translate("Form", "Scheduler"))
        self.comboBox.setItemText(0, _translate("Form", "Instant"))
        self.comboBox.setItemText(1, _translate("Form", "Every 1 Hr"))
        self.comboBox.setItemText(2, _translate("Form", "Everyday"))
        self.comboBox.setItemText(3, _translate("Form", "Weekly"))
        self.comboBox.setItemText(4, _translate("Form", "Monthly"))
        self.label_14.setText(_translate("Form", "Max. Version"))
        self.lineEdit.setText(_translate("Form", "5"))
        self.label_15.setText(_translate("Form", "Max. Space Reserved"))
        self.lineEdit_2.setText(_translate("Form", "50 MB"))
        self.create_job_2.setToolTip(_translate("Form", "Create a Backup Task"))
        self.create_job_2.setText(_translate("Form", "Start Job"))
        self.status.setText(_translate("Form", "Status :"))
        self.status_text.setText(
            _translate("Form", "Ketan.xlsx Uploaded Successfully !")
        )


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
