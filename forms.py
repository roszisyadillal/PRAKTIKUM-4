from wtforms import Form, StringField, validators, SubmitField, IntegerField, FloatField

class NewPenyakitForm(Form):
    nama_penyakit = StringField('Nama Penyakit', [validators.DataRequired()])
    submit = SubmitField("Submit")

class NewGejalaForm(Form):
    gejala = StringField('Gejala',[validators.DataRequired()])
    submit = SubmitField("Submit")

class NewAturanForm(Form):
    kd_penyakit = IntegerField('Kode Penyakit',[validators.DataRequired()])
    kd_gejala = IntegerField('Kode Penyakit',[validators.DataRequired()])
    probabilitas = FloatField('Probabilitas', [validators.DataRequired()])
    submit = SubmitField("Submit")


