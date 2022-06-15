#import library
import numpy as np
import joblib
from flask import Flask, render_template, request, url_for, redirect, session
from flask_admin import BaseView, expose
import pandas as pd
import flask_excel as excel
import matplotlib.pyplot as plt
import joblib
import sqlalchemy 
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'weightknn'
db = SQLAlchemy(app)
admin = Admin(app,name='Prediksi Kelulusan', template_mode='bootstrap4')

#model createds
class kelulusan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama= db.Column(db.String(50))
    umur = db.Column(db.Integer())
    jenis_kelamin = db.Column(db.String(10))
    status_sekolah = db.Column(db.String(10))
    asal_sekolah = db.Column(db.String(10))
    kegiatan_ukm = db.Column(db.String(10))
    penghasilan_ortu= db.Column(db.String(10))
    ips1= db.Column(db.Integer())
    ips2= db.Column(db.Integer())
    ips3= db.Column(db.Integer())
    ips4= db.Column(db.Integer())
    ips5= db.Column(db.Integer())
    ips6= db.Column(db.Integer())
    prediction = db.Column(db.String(100))

# app = Flask(__name__)
class UserView(ModelView):
        can_export = True
class Rekap(BaseView):
    @expose('/')
    def index(self):
        results = kelulusan.query.with_entities(kelulusan.prediction).all()
        df = pd.DataFrame(results)
        df.columns = ['prediction']
        data = df.groupby('prediction').size().reset_index(name='jumlah')
        dat = pd.DataFrame(data.jumlah)
        my_labels = ['Tepat Waktu', 'Terlambat']
        my_color = ['green', 'red']
        dat.plot(kind='pie', labels=my_labels, autopct='%1.1f%%',
                 colors=my_color, subplots=True, stacked=True, legend=False)
        plt.title('Hasil Seluruh Prediksi')
        plt.xlabel('Kelulusan')
        plt.ylabel("")
        plt.savefig('static/img/hasil.png')

        # Rekap = submit()
        return self.render('admin/rekap.html')

#Logout
class Logout(BaseView):
    @expose('/')
    def index(self):
        session.pop('username',None)
        return self.render('index.html')

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route('/prediksi/', methods=['GET', 'POST'])
def prediksi():
    return render_template('form_prediksi.html')
    
@app.route('/predict/', methods=['GET', 'POST'])
def predict():
    if request.method == "POST":
        # get form data
        nama = request.form.get('nama')
        umur = request.form.get('umur')
        jenis_kelamin = request.form.get('jenis_kelamin')
        status_sekolah = request.form.get('status_sekolah')
        asal_sekolah = request.form.get('asal_sekolah')
        kegiatan_ukm = request.form.get('kegiatan_ukm')
        penghasilan_ortu = request.form.get('penghasilan_ortu')
        ips1 = request.form.get('ips1')
        ips2 = request.form.get('ips2')
        ips3 = request.form.get('ips3')
        ips4 = request.form.get('ips4')
        ips5 = request.form.get('ips5')
        ips6 = request.form.get('ips6')

        
      # panggil preprocessDataAndPredict and pass inputs
        try:
            prediction = preprocessDataAndPredict(umur, jenis_kelamin,status_sekolah,asal_sekolah,kegiatan_ukm, penghasilan_ortu, ips1, ips2, ips3, ips4, ips5, ips6)
            # pass prediction to template
            predictiondb = kelulusan(nama=nama, umur=umur, jenis_kelamin=jenis_kelamin,status_sekolah=status_sekolah,asal_sekolah=asal_sekolah, kegiatan_ukm=kegiatan_ukm,penghasilan_ortu=penghasilan_ortu,ips1=ips1, ips2=ips2, ips3=ips3, ips4=ips4, ips5=ips5, ips6=ips6, prediction=int(prediction))
            db.session.add(predictiondb)
            db.session.commit()
            
            return render_template('predict.html',nama=nama, umur=umur, jenis_kelamin=jenis_kelamin,status_sekolah=status_sekolah,asal_sekolah=asal_sekolah, kegiatan_ukm=kegiatan_ukm,
            penghasilan_ortu=penghasilan_ortu,ips1=ips1, ips2=ips2, ips3=ips3, ips4=ips4, ips5=ips5, ips6=ips6, prediction=prediction)

        except ValueError:
            return "Please Enter valid values"

        pass
    pass

 

def preprocessDataAndPredict(umur, jenis_kelamin,status_sekolah ,asal_sekolah, kegiatan_ukm, penghasilan_ortu, ips1, ips2, ips3, ips4, ips5, ips6):
    # keep all inputs in array
    test_data = [umur, jenis_kelamin, status_sekolah ,asal_sekolah, kegiatan_ukm,penghasilan_ortu, ips1, ips2, ips3, ips4, ips5, ips6]
    print(test_data)

    # convert value data into numpy array
    test_data = np.array(test_data)

    # reshape array
    test_data = test_data.reshape(1, -1)
    print(test_data)

    # open file
    file = open("wknn_model.pkl", "rb")

    # load trained model
    trained_model = joblib.load(file)

    # predict
    prediction = trained_model.predict(test_data)

    
    return prediction
    pass

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == 'admin' and request.form['username'] == 'admin':

            session['logged_in'] = True
            return redirect('/admin')
        else:
            return render_template('login.html')

    else:
        return render_template('login.html')

#menu admin
admin.add_view(UserView(kelulusan, db.session))
admin.add_view(Rekap(name='rekap', endpoint='Rekap'))
admin.add_view(Logout(name='logout', endpoint='Logout'))

if __name__ == '__main__':
    app.run(debug=True)