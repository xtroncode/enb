import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, send_from_directory
#from contextlib import closing
import os
from werkzeug import secure_filename
from peewee import *
import datetime
import json
try:
  from urllib.request import urlopen
except ImportError:
  from urllib2 import urlopen
# configuration
BASE_DIR = os.getcwd()
DATABASE = os.path.join(BASE_DIR, 'notices.db')
#'/home/meet1995/nb/notices.db'
DEBUG = True
SECRET_KEY = 'devwebdevcode1234'
RECAPTCHA_PUBLIC_KEY = "6LdV9AATAAAAADrgRr_r8N04Ek0FA6Hx6eYIIDrE"
RECAPTCHA_PRIVATE_KEY = "6LdV9AATAAAAAFW4Ejbr65Y3eJW2Pjm3jRpGX-kr"
UPLOAD_FOLDER_POSTER = os.path.join(BASE_DIR, 'media/poster/')
UPLOAD_FOLDER_DOCS = os.path.join(BASE_DIR, 'media/docs/')
ALLOWED_EXTENSIONS_POSTER = set(['png', 'jpg', 'jpeg', 'gif','PNG'])
ALLOWED_EXTENSIONS_FILE = set(['txt','pdf','doc','docx'])
MAX_CONTENT_LENGTH = 5*1024*1024
app = Flask(__name__)
app.config.from_object(__name__)

database = SqliteDatabase(DATABASE,threadlocals=True)
class Notices(Model):
    description = TextField()
    postername = CharField(unique=True,max_length = 100,null=True)
    docname = CharField(unique=True,max_length = 100,null=True)
    pub_date = DateTimeField()
    approval=BooleanField()
    class Meta:
        database = database



def create_tables():
    database.connect()
    database.create_tables([Notices])

def allowed_file_poster(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS_POSTER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS_FILE
def delete_poster(file):
  if file:os.remove(UPLOAD_FOLDER_POSTER+file)
def delete_doc(file):
  if file:os.remove(UPLOAD_FOLDER_DOCS+file)

def captcha_validate(gresponse):
  data=urlopen(' https://www.google.com/recaptcha/api/siteverify?secret='+RECAPTCHA_PRIVATE_KEY+'&response='+gresponse+'&remoteip='+request.remote_addr)
  data=json.loads(data.read().decode())
  return data['success']

@app.before_request
def before_request():
    g.db = database
    g.db.connect()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/uploads/<media>/<filename>')
def uploaded_file(media,filename):
    if media=="poster":
      return send_from_directory(app.config['UPLOAD_FOLDER_POSTER'],filename)
    if media=="docs":
      return send_from_directory(app.config['UPLOAD_FOLDER_DOCS'],filename)

@app.route('/')
@app.route('/<int:page_num>')
def show_entries(page_num=1):
    notices=Notices.select().where(Notices.approval==True).order_by(Notices.id.desc()).paginate(page_num,3)
    if page_num==1:return render_template('home.html',notices=notices,page_num=2 )
    if notices.count()>0:return render_template('scroll.html',notices=notices,page_num=page_num+1 )


@app.route('/add', methods=['GET', 'POST'])
def add_notice():
    if request.method == 'POST':
        if not captcha_validate(request.form['g-recaptcha-response']):return redirect(url_for('show_entries'))
        description = request.form['description']
        if len(description)>1000 or len(description)==0:
          return redirect(url_for('show_entries'))
        poster = request.files['poster']
        if poster and allowed_file_poster(poster.filename):
            photoname = secure_filename(poster.filename)
        else:
            photoname=None
        document = request.files['document']
        if document and allowed_file(document.filename):
            docname = secure_filename(document.filename)
        else:
            docname=None
        with g.db.transaction():
            notice = Notices.create(description=description, postername=None, docname=None, pub_date=datetime.datetime.now().strftime('%m/%d/%Y'),approval=False)
            if photoname:
              photoname="nid"+str(notice.id)+photoname
              notice.postername=photoname
              poster.save(os.path.join(app.config['UPLOAD_FOLDER_POSTER'], photoname))
            if docname:
              docname="nid"+str(notice.id)+docname
              notice.docname=docname
              document.save(os.path.join(app.config['UPLOAD_FOLDER_DOCS'], docname))
            notice.save()
        return redirect(url_for('show_entries'))

    return redirect(url_for('show_entries'))
@app.route('/admin',methods=['GET', 'POST'])
def post_approval():
    if request.method == 'POST':
          adminpass=request.form['password']
          if adminpass=="webdevlabs" and request.form['approval']=='false':
            noticeid=request.form['postid']
            notice=Notices.select().where(Notices.id==noticeid).get()
            postername=notice.postername
            docname=notice.docname
            notice.delete_instance()
            delete_poster(postername)
            delete_doc(docname)
          if adminpass=="webdevlabs" and request.form['approval']=='true':
            noticeid=request.form['postid']
            notice=Notices.select().where(Notices.id==noticeid).get()
            notice.approval=True
            notice.save()
            return redirect(url_for('post_approval'))
    notices=Notices.select().where(Notices.approval==False)
    return render_template('admin.html',notices=notices)

@app.route('/api/<int:page_num>/<int:paginate_by>/',methods=['GET', 'POST'])
def json_api(page_num,paginate_by):
    data=Notices.select().where(Notices.approval==True).order_by(Notices.id.desc()).paginate(page_num,paginate_by).dicts()
    data_list=[]
    for row in data:
      data_list.append(row)
    return app.response_class(json.dumps(data_list,
        indent=None if request.is_xhr else 2), mimetype='application/json')


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080)