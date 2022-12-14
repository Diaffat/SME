from PyQt5 import QtCore, QtGui, QtWidgets,uic
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import* 
import cv2
import smtplib, ssl    
import threading  
import os  
import playsound    
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import smtplib   
import common
import pandas as pd  

from codecarbon import EmissionsTracker

class UI(QMainWindow):
    def __init__(self):
        super(UI,self).__init__()
        uic.loadUi("ui_files/acceuil.ui",self)
        self.st=0
        self.start_btn=self.findChild(QPushButton,"start_btn")
        self.stop_btn=self.findChild(QPushButton,"stop_btn")
        self.codecarb_btn=self.findChild(QPushButton,"codecarb_btn")
        self.video_label=self.findChild(QLabel,"video_label")
        self.camera_ip=self.findChild(QLineEdit,"lineEdit")
         
        
        self.stop_btn.clicked.connect(self.cancel)
        self.start_btn.clicked.connect(self.start_video)
        self.codecarb_btn.clicked.connect(self.show_co2)


    def start_video(self):
        if str(self.camera_ip.text())!="":
            self.Work = Work()
            self.Work.ip=str(self.camera_ip.text())
            if self.Work.ip=="0":
                self.Work.ip=0
            self.Work.start()
            self.Work.Imageupd.connect(self.Imageupd_slot)
            self.st=1
        else:
            pass 

    def Imageupd_slot(self, Image):
        self.video_label.setPixmap(QPixmap.fromImage(Image))

    def cancel(self):
        if self.st==0:
            pass 
        else:
            self.Work.stop()
            self.video_label.clear()

    def salir(self):
        sys.exit()
    
    def show_co2(self):
        stat=common.stat
        if stat==False:
            pass
        else: 
            self.win=CO2()
            _=self.win.get_outputs()
            self.win.show() 

     
class Work(QThread):
    Imageupd = pyqtSignal(QImage)
    ip=0
    tracker=EmissionsTracker()
    tracker.start()
    def run(self):
          
        fire_cascade = cv2.CascadeClassifier('cascade.xml') 
        self.statut= True
        cap = cv2.VideoCapture(self.ip)
        while self.statut:
            Alarm_Status = False
            ret, frame = cap.read() 
            if ret:
                fire = fire_cascade.detectMultiScale(frame, 12, 5)  
                for (x,y,w,h) in fire:
                    cv2.rectangle(frame,(x,y),(x+w,y+h),(0,128,0),2)
                    cv2.putText(frame,"FIRE",(x,y-10),cv2.FONT_HERSHEY_PLAIN,3,color=(0, 0, 255),thickness=2)
                    cv2.imwrite('Fire_started.png',frame)
                    threading.Thread(target=self.play_alarm_sound_function).start()  
                     
                    threading.Thread(target=self.send_mail_function).start()   
                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                flip = cv2.flip(Image, 1)
                convertir_QT = QImage(flip.data, flip.shape[1], flip.shape[0], QImage.Format_RGB888)
                self.Imageupd.emit(convertir_QT)
                #########################################################
    def stop(self):
        self.statut= False
        self.disconnect()
        self.tracker.stop()
        common.stat=True
    
    def play_alarm_sound_function(self): 
        playsound.playsound('alerte.mp3',True) 
    def send_mail_function(self):  
        try:
            ImgFileName="Fire_started.png"
 
            with open(ImgFileName, 'rb') as f:
                img_data = f.read()

            port = 465  
            smtp_server = "smtp.gmail.com"
            sender_email = "salifousaouadogo@gmail.com"  

            receiver_email = "fatoumatasoukouradiassana18@gmail.com"  

            password = "joae wsca vnft zxpa"

            message = "python_grey.png"

            msg = MIMEMultipart()

            msg['Subject'] = 'Feu detecté'

            msg['From'] = 'salifousaouadogo@gmail.com'

            msg['To'] = 'fatoumatasoukouradiassana18@gmail.com'
            text = MIMEText("latitude:  33.873016----------longitude: -5.540730")
            msg.attach(text)
            image = MIMEImage(img_data, name=os.path.basename(ImgFileName))
            msg.attach(image)
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login("salifousaouadogo@gmail.com", password)
                server.sendmail(sender_email, receiver_email,  msg.as_string())
        except Exception as e:
            pass 


class CO2(QDialog):
    def __init__(self):
        super(CO2,self).__init__()
        uic.loadUi("ui_files/dialog.ui",self)
        self.oss=self.findChild(QLabel,"oss")
        self.cpum=self.findChild(QLabel,"cpum")
        self.tt=self.findChild(QLabel,'tt')
        self.dd=self.findChild(QLabel,'dd')
        self.em=self.findChild(QLabel,'em')
        self.cpup=self.findChild(QLabel,'cpup')
        self.cpue=self.findChild(QLabel,'cpue')
        self.ramp=self.findChild(QLabel,'ramp')
        self.rame=self.findChild(QLabel,'rame')
        self.cc=self.findChild(QLabel,'cc')
        self.ec=self.findChild(QLabel,'ec')
        self.lg=self.findChild(QLabel,'lg')
        self.lt=self.findChild(QLabel,'lt')
        self.pythonv=self.findChild(QLabel,'python')
    
        df=pd.read_csv("emissions.csv").tail(1)
        
        self.oss.setText(str(df.os.values[0]))
        self.cpum.setText(str(df.cpu_model.values[0]))
        self.tt.setText(str(df.timestamp.values[0]))
        self.dd.setText(str(df.duration.values[0])+" seconds")
        self.em.setText(str(df.emissions.values[0])+" [CO₂eq], in kg")
        self.cpup.setText(str(df.cpu_power.values[0])+" W")
        self.cpue.setText(str(df.cpu_energy.values[0])+" kWh")
        self.ramp.setText(str(df.ram_power.values[0])+" W")
        self.rame.setText(str(df.ram_energy.values[0])+" kWh")
        self.cc.setText(str(df.country_name.values[0]))
        self.ec.setText(str(df.energy_consumed.values[0])+" kWh")
        self.lg.setText(str(df.longitude.values[0]))
        self.lt.setText(str(df.latitude.values[0]))
        self.pythonv.setText(str(df.python_version.values[0]))

    def get_outputs(self):
        if self.exec_()==QDialog.Accepted:
            return 1
        else:
            return 0







if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = UI()
    ui.show()
    sys.exit(app.exec_())
