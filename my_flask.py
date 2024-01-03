from flask import Flask, request, flash, render_template, url_for
from forms import NewGejalaForm, NewPenyakitForm, NewAturanForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from flask_wtf import FlaskForm
from wtforms_alchemy import QuerySelectMultipleField
from wtforms import widgets
import os
import numpy as np

app = Flask(__name__)

#koneksi ke database
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:''@localhost/stunting'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY']=SECRET_KEY

db = SQLAlchemy(app)

app.app_context().push()

class Penyakit(db.Model):
    kd_penyakit = db.Column(db.Integer, primary_key=True)
    nama_penyakit = db.Column(db.String(80), unique=True)

    def __init__(self, nama_penyakit):
        self.nama_penyakit=nama_penyakit

    def __repr__(self):
        return self.nama_penyakit

class Gejala(db.Model):
    kd_gejala = db.Column(db.Integer, primary_key=True)
    gejala = db.Column(db.String(80), unique=True)

    def __init__(self, gejala):
        self.gejala=gejala
    
    def __repr__(self):
        return self.gejala

class Aturan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kd_penyakit = db.Column(db.Integer, db.ForeignKey(Penyakit.kd_penyakit))
    kd_gejala = db.Column(db.Integer, db.ForeignKey(Gejala.kd_gejala))
    probabilitas = db.Column(db.Float)

    def __repr__(self):
        return f"{self.kd_gejala} {self.kd_penyakit} {self.probabilitas}"

class QuerySelectMultipleFieldCheckBox(QuerySelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class CheckForm(FlaskForm):
    pilih = QuerySelectMultipleFieldCheckBox("Gejala")

def bayes(data_gejala):
    daftar = []
    for i in data_gejala:
        row = db.session.execute(select(Aturan.kd_gejala, Aturan.kd_penyakit, Aturan.probabilitas).where(Aturan.kd_gejala==i)).all()
        for x in range(len(row)):
            c = row[x]
            daftar.append(c)
    print(f'Query db: {daftar}')
    print(f'Banyak data query: {len(daftar)}')

    #Hitung Unique Value Penyakit
    pen=[]
    for a in range(len(daftar)):
        for b in range(1):
            pen.append(daftar[a][b+1])
    
    array_pen = np.array(pen)
    unique_pen = np.unique(array_pen)
    unique_pen = unique_pen.tolist()
    print(f'Jenis penyakit: {unique_pen}')
    print(f'Jumlah penyakit: {len(unique_pen)}')

    #Hitung total P gejala tiap penyakit
    jumlah = []
    for x in range(len(unique_pen)):
        temp = 1
        for y in range(len(daftar)):
            for z in range(1):
                if unique_pen[x] == daftar[y][z+1]:
                    temp *= daftar[y][z+2]
        jumlah.append(temp)
    print(f'Jumlah prob: {jumlah}')

    #Hitung P|H
    prob = []
    ph = []
    for x in range(len(unique_pen)):
        dataph = []
        dataprob = []
        for y in range(len(daftar)):
            for z in range(1):
                if unique_pen[x] == daftar[y][z+1]:
                    temp = daftar[y][z+2]/jumlah[x]
                    dataph.append(temp)
                    dataprob.append(daftar[y][z+2])
        ph.append(dataph)
        prob.append(dataprob)
    print(f'Prob: {prob}')
    print(f'P|H: {ph}')

    #Hitung P(E|Hk) x P(Hk)
    PHk = []
    for x in range(len(prob)):
        temp = 0
        for y in range(len(prob[x])):
            temp = temp + (prob[x][y]*ph[x][y])
        PHk.append(temp)
    print(f'P x Hk: {PHk}')

    #Hitung P(H|E)
    PHE = []
    for x in range(len(prob)):
        temp = []
        for y in range(len(prob[x])):
            hitung = (prob[x][y]*ph[x][y])/PHk[x]
            temp.append(hitung)
        PHE.append(temp)
    print(f'P(H|E): {PHE}')

    #Hitung Total Bayes
    total_bayes = []
    for x in range(len(prob)):
        temp = 0
        for y in range(len(prob[x])):
            temp = temp + (prob[x][y]*PHE[x][y])
        total_bayes.append(temp)
    print(f'Total Bayes: {total_bayes}')

    #Hitung nilai semesta dengan fungsi SUM(jumlah)
    #hitung P(H1|E)
    hasil = []
    for i in jumlah:
        hasil.append(i/sum(jumlah))

    #Cari nilai max
    for x in range(len(unique_pen)):
        maksi = hasil[0]
        hasil_penyakit = unique_pen[0]
        if hasil[x] > maksi:
            maksi = hasil[x]
            hasil_penyakit = unique_pen[x]
    print(f'Hasil: {hasil_penyakit} peluang: {maksi*100}%')
    return hasil_penyakit, maksi


@app.route("/")
@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/penyakit")
def penyakit():
    data = Penyakit.query.order_by(Penyakit.kd_penyakit)
    return render_template('penyakit.html', data=data)

@app.route("/insertPenyakit", methods=['POST'])
def insertPenyakit():
    form = NewPenyakitForm()
    return render_template('formPenyakit.html', form=form)

@app.route("/gejala")
def gejala():
    data = Gejala.query.order_by(Gejala.kd_gejala)
    return render_template('gejala.html', data=data)

@app.route("/insertGejala", methods=['POST'])
def insertGejala():
    form = NewGejalaForm()
    return render_template('formGejala.html', form=form)

@app.route("/aturan")
def aturan():
    data = Aturan.query.order_by(Aturan.id)
    return render_template('aturan.html', data=data)

@app.route("/insertAturan", methods=['POST'])
def insertAturan():
    form = NewAturanForm()
    return render_template('formAturan.html', form=form)

@app.route("/prediksi", methods = ['GET','POST'])
def prediksi():
    form = CheckForm()
    form.pilih.query = Gejala.query.order_by(Gejala.kd_gejala)
    indeks = []
    if form.validate_on_submit():
        data=form.pilih.data
        for i in data:
            indeks.append(i.kd_gejala)
        print(indeks)
        hasil=bayes(indeks)
        hasil_penyakit = Penyakit.query.filter_by(kd_penyakit=hasil[0]).first()
        peluang = hasil[1]*100
        return render_template('prediksi.html', form=form, data=data, hasil=hasil_penyakit, peluang=peluang)
    else:          
        return render_template('prediksi.html', form=form)


@app.route("/submitPen", methods=['POST','GET'])
def submitPen():
    form = NewPenyakitForm(request.form)
    if form.validate():
        pen = Penyakit(request.form['nama_penyakit'])
        db.session.add(pen)
        try:
            db.session.commit()
            flash(f"Penyakit {pen.nama_penyakit} berhasil ditambahkan")
            return render_template ('formPenyakit.html', penyakit=pen.nama_penyakit)  
        except Exception as e:
            db.session.rollback()
            flash(f"Penyakit {pen.nama_penyakit} gagal ditambahkan. Error {e}")
            return render_template  ('formPenyakit.html', penyakit=pen.nama_penyakit)
    else:
        return "Invalidate form"

@app.route("/updatePenyakit/<int:id>", methods=['POST','GET'])
def updatePenyakit(id):
    form = NewPenyakitForm()
    data_update = Penyakit.query.get_or_404(id)
    if request.method == "POST":
        data_update.nama_penyakit = request.form['nama_penyakit']
        try:
            db.session.commit()
            flash(f"Update penyakit berhasil!")
            return render_template('editPenyakit.html', form=form, data_update=data_update)
        except Exception as e:
            db.session.rollback()
            flash(f"Update gagal! Error {e}")
            return render_template ('editPenyakit.html', form=form, data_update=data_update)
    else:
        return render_template ('editPenyakit.html', form=form, data_update=data_update)


@app.route("/deletePen/<int:id>", methods=['POST','GET'])
def deletePen(id):
    data_delete = Penyakit.query.get_or_404(id)
    try:
        db.session.delete(data_delete)
        db.session.commit()

        #pesan notifikasi
        flash("Data penyakit berhasil dihapus!")

        #menampilkan sisa data
        penyakit = Penyakit.query.order_by(Penyakit.kd_penyakit)
        return render_template('penyakit.html', data=penyakit)
    except Exception as e:
        flash(f"Penghapusan data gagal! Error {e}")

        #menampilkan sisa data
        penyakit = Penyakit.query.order_by(Penyakit.kd_penyakit)
        return render_template('penyakit.html', data=penyakit)



@app.route("/submitGejala", methods=['POST','GET'])
def submitGejala():
    form = NewGejalaForm(request.form)
    if form.validate():
        gej = Gejala(request.form['gejala'])
        db.session.add(gej)
        try:
            db.session.commit()
            flash(f"Gejala {gej.kd_gejala} berhasil ditambahkan")
            return render_template ('gejala.html', gejala=gej.kd_gejala)  
        except Exception as e:
            db.session.rollback()
            flash(f"Gejala {gej.kd_gejala} gagal ditambahkan. Error {e}")
            return render_template  ('gejala.html', gejala=gej.kd_gejala)
    else:
        return "Invalidate form"


@app.route("/updateGejala/<int:id>", methods=['POST','GET'])
def updateGejala(id):
    form = NewGejalaForm()
    data_update = Gejala.query.get_or_404(id)
    if request.method == 'POST':
        data_update.gejala = request.form['gejala']
        try:
            db.session.commit()
            flash(f"Update gejala berhasil!")
            return render_template('editGejala.html', form=form, data_update=data_update)
        except Exception as e:
            db.session.rollback()
            flash(f"Update gagal! Error {e}")
            return render_template ('editGejala.html', form=form, data_update=data_update)
    else:
        return render_template ('editGejala.html', form=form, data_update=data_update)

@app.route("/deleteGejala/<int:id>", methods=['POST','GET'])
def deleteGejala(id):
    data_delete = Gejala.query.get_or_404(id)
    try:
        db.session.delete(data_delete)
        db.session.commit()

        #pesan notifikasi
        flash("Data gejala berhasil dihapus!")

        #menampilkan sisa data
        gejala = Gejala.query.order_by(Penyakit.kd_penyakit)
        return render_template('gejala.html', data=gejala)
    except Exception as e:
        flash(f"Penghapusan data gagal! Error {e}")

        #menampilkan sisa data
        gejala = Gejala.query.order_by(Gejala.kd_gejala)
        return render_template('gejala.html', data=gejala)

@app.route("/submitAturan", methods=['POST','GET'])
def submitAturan():
    form = NewAturanForm(request.form)
    if form.validate():
        pen = Aturan(kd_penyakit=request.form['kd_penyakit'], kd_gejala=request.form['kd_gejala'], probabilitas=request.form['probabilitas'])
        db.session.add(pen)
        try:
            db.session.commit()
            flash(f"Aturan {pen.id} berhasil ditambahkan")
            return render_template ('formAturan.html', penyakit=pen.id)  
        except Exception as e:
            db.session.rollback()
            flash(f"Aturan {pen.id} gagal ditambahkan. Error {e}")
            return render_template  ('formAturan.html', penyakit=pen.id)
    else:
        return "Invalidate form"


@app.route("/updateAturan/<int:id>", methods=['POST','GET'])
def updateAturan(id):
    form = NewAturanForm()
    data_update = Aturan.query.get_or_404(id)
    if request.method == "POST":
        data_update.kd_penyakit = request.form['kd_penyakit']
        data_update.kd_gejala = request.form['kd_gejala']
        data_update.probabilitas = request.form['probabilitas']
        try:
            db.session.commit()
            flash(f"Update aturan berhasil!")
            return render_template('editAturan.html', form=form, data_update=data_update)
        except Exception as e:
            db.session.rollback()
            flash(f"Update gagal! Error {e}")
            return render_template ('editAturan.html', form=form, data_update=data_update)
    else:
        return render_template ('editAturan.html', form=form, data_update=data_update)


@app.route("/deleteAturan/<int:id>", methods=['POST','GET'])
def deleteAturan(id):
    data_delete = Aturan.query.get_or_404(id)
    try:
        db.session.delete(data_delete)
        db.session.commit()

        #pesan notifikasi
        flash("Data aturan berhasil dihapus!")

        #menampilkan sisa data
        aturan = Aturan.query.order_by(Aturan.id)
        return render_template('aturan.html', data=aturan)
    except Exception as e:
        flash(f"Penghapusan data gagal! Error {e}")

        #menampilkan sisa data
        aturan = Aturan.query.order_by(Aturan.id)
        return render_template('aturan.html', data=aturan)
    

if __name__ == '__main__':
    app.run(debug=True)
