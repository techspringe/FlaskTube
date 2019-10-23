from flask import Blueprint,render_template

main  = Blueprint('main',__name__,template_folder='templates',url_prefix='/')

@main.route('/',methods=['GET'])
def method_name():
    return render_template('main/index.html')
   

@main.route('/',methods=['GET'])
def info():
    return render_template('main/info.html')