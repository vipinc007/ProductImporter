from flask import Flask, Response, flash, render_template, request, redirect, url_for
from Entity.Database.DBHelper import DBHelper
from Entity import CommonFunctions
from werkzeug.utils import secure_filename
import time
import os
import csv
from flask_paginate import Pagination, get_page_args


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 20000 * 1024 * 1024
app.secret_key = "thisisfullfilltest"


def allowed_file_extensions(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    #print("here 1")
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'err'
        file = request.files['file']
        if file.filename == '':
            return "err"
        if file and allowed_file_extensions(file.filename):
            try:
                filename = secure_filename(file.filename)
                fileext = filename.split('.')[1]
                fname = CommonFunctions.generate_random_number()
                filename = fname+"."+fileext
                fn = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(fn)
                num_lines = sum(1 for line in open(fn))
                CommonFunctions.register_session('TotalRecords', num_lines)
                CommonFunctions.register_session('TotalRecordsImported', 0)
                CommonFunctions.register_session('UploadedFile', fn)
                return "ok"
            except Exception as e:
                return (str(e))
    else:
        return "err"

    return "err"

@app.route('/deleteuploadfile', methods=['GET', 'POST'])
def delete_uploaded_file():
    os.remove(CommonFunctions.get_session_value('UploadedFile'))
    return "ok"

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/import")
def importer():
    return render_template('importer.html')


@app.route("/add_edit_product",methods=['GET', 'POST'])
def add_edit_product():
    db = DBHelper()
    if request.method == 'POST':
        if request.form.get('doaction')=='add':
            name = request.form.get('pname')
            sku = request.form.get('psku')
            description = request.form.get('pdescription')
            sql= "Insert into products (name,sku, description) values ('{0}','{1}','{2}')".format(name, sku, description)
            print(sql)
            db.execute(sql)
            return "ok"
        if request.form.get('doaction')=='edit':
            name = request.form.get('pname')
            sku = request.form.get('psku')
            description = request.form.get('pdescription')
            sql= "UPDATE products SET NAME='{0}' , description='{1}' where sku='{2}'".format(name,  description, sku)
            print(sql)
            db.execute(sql)
            return "ok"
    return "err"

@app.route("/del_product/<string:sku>",methods=['GET', 'POST'])
def delete_product(sku):
    db = DBHelper()
    if request.method == 'POST':
            sql= "delete from products where sku='{0}'".format(sku,)
            db.execute(sql)
            return "ok"

    return "err"


@app.route("/products",methods=['GET', 'POST'])
def products():
    db = DBHelper()
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    sql = "select * from products limit {0} offset {1}".format(per_page,offset)
    df = db.executetodataframe(sql)
    tot = db.fetch("select count(*) cnt from products")
    totrecords = 0
    for row in tot:
        totrecords = row[0]
    total = int(totrecords/per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template('products.html',table=df,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,)


@app.route("/product/<string:sku>",methods=['GET', 'POST'])
def product(sku):
    db = DBHelper()
    if request.method == 'POST':
        if request.form.get('doaction')=='add':
            name = request.form.get('pname')
            sku = request.form.get('psku')
            description = request.form.get('pdescription')
            sql= "Insert into products (name,sku, description) values ('{0}','{1}','{2}')".format(name, sku, description)
            print(sql)
            db.execute(sql)
            #return redirect(request.host_url)

    doaction = 'edit'
    if sku=='0':
        doaction = 'add'

    sql = "select * from products where sku like '{0}'".format(sku)
    res = db.fetch(sql)
    therow = None
    for row in res:
        therow = row
    return render_template('product.html',item=therow,doaction=doaction)


@app.route("/importdata", methods=['POST'])
def import_data():
    db = DBHelper()
    filetoread = CommonFunctions.get_session_value('UploadedFile')
    db.import_csv_to_db(filetoread, "products")
    CommonFunctions.register_session('TotalRecordsImported', CommonFunctions.get_session_value('TotalRecords'))
    return "ok"


@app.route("/stream")
def stream():
    nofrecords = CommonFunctions.get_session_value('TotalRecords')
    increment = nofrecords/100
    cnt=0
    def eventStream(n,c,i):
        while True:
            time.sleep(2)
            c+=i
            yield "data:{0},{1}\n\n".format(n,c)

    return Response(eventStream(nofrecords, cnt,increment), mimetype="text/event-stream")


if __name__ == '__main__':
   app.run()