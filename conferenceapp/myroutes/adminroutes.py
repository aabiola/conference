'''This File is like the controller that determines what happens when a user visits our app'''

import math, random, os
from flask import make_response, render_template, request, session,redirect, flash, url_for
from sqlalchemy  import or_

from werkzeug.security import generate_password_hash, check_password_hash

from conferenceapp import app, db
from conferenceapp.mymodels import User,State,Skill,Breakout, Admin
from conferenceapp.forms import LoginForm


@app.route("/admin/login")
def adminlogin():
    return render_template("admin/login.html")






@app.route("/admin/reg")
def registrations():
    #users = db.session.query(User,State,Skill).join(State).join(Skill).all()
    

    # users = User.query.join(State).join(Skill).add_columns(State,Skill).filter(or_(User.user_skillid==1, User.user_skillid==2)).all()

    users=User.query.outerjoin(State,User.user_stateid==State.state_id).add_columns(State).order_by(User.user_fname).all()


    return render_template("admin/allusers.html", users=users)



@app.route("/admin/signup", methods=['POST','GET'])
def admin_signup():
    if request.method =='GET':
        return render_template("/admin/signup.html")
    else:
        #retrieve the form data
        username = request.form.get('username')
        pwd1 = request.form.get('password')
        pwd2 = request.form.get('password2')        
        if pwd1 == pwd2:
            formated = generate_password_hash(pwd1)
            ad = Admin(admin_username=username,admin_password=formated)
            db.session.add(ad)
            db.session.commit()
            flash("New user signed up")
            return redirect('/admin/login')
        else:
            flash("The two passwords do not match")
            return redirect('/admin/login')




@app.route("/admin/submit/login", methods=['POST'])
def submit_adminlogin():
    username = request.form.get('username')
    adminpass = request.form.get('password')
    if username =='' or adminpass =='':
        flash("Please complete both fields")
        return redirect(url_for('adminlogin'))
    else:
        deets = db.session.query(Admin).filter(Admin.admin_username==username).first()        
        formated_pwd = deets.admin_password
        chk = check_password_hash(formated_pwd,adminpass)

        if chk ==True:
            session['admin'] = deets.admin_id
            return redirect(url_for('adminpage')) 
        else:
            flash("Invalid login credentials")
            return redirect(url_for('adminlogin'))




# @app.route("/admin/submit/login", methods=['POST'])
# def submit_adminlogin():
#     username = request.form.get('username')
#     adminpass = request.form.get('password')
#     if username =='' or adminpass =='':
#         flash("Please complete both fields")
#         return redirect(url_for('adminlogin'))
#     else:
#         deets = db.session.query(Admin).filter(Admin.admin_username==username).filter(Admin.admin_password==adminpass).first()
#         if deets:
#             session['admin'] = deets.admin_id
#             return redirect(url_for('adminpage')) 
#         else:
#             flash("Invalid login credentials")
#             return redirect(url_for('adminlogin'))


@app.route('/admin/home')
def adminpage():
    return render_template('admin/index.html')

@app.route('/admin/breakout/delete/<id>')
def admin_deletebreakout(id):
    b = db.session.query(Breakout).get(id)
    db.session.delete(b)
    db.session.commit()
    flash(f"Breakout session {id} deleted")
    return redirect('/admin/breakout')
    


@app.route('/admin/breakout')
def breakout():
    break_deets= Breakout.query.all() #db.session.query(Breakout).all()
    
    return render_template('admin/breakout.html', break_deets=break_deets)





@app.route('/admin/addbreakout', methods=['GET','POST'])
def addbreakout():
    if request.method =='GET':
        skills = Skill.query.all()
        return render_template('admin/addbreakout.html', skills=skills)
    else:
        #Retrieve form data (request.form....)
        title = request.form.get('title')
        level = request.form.get('level')
        #request file
        pic_object = request.files.get('pic')
        original_file =  pic_object.filename
        if title =='' or level =='':
            flash("Title and Level cannot be empty")
            return redirect('/admin/addbreakout')
        if original_file !='': #check if file is not empty
            extension = os.path.splitext(original_file)
            if extension[1].lower() in ['.jpg','.png']:
                fn = math.ceil(random.random() * 100000000)  
                save_as = str(fn)+extension[1] 
                pic_object.save(f"conferenceapp/static/assets/img/{save_as}")
                #insert other details into db
                b = Breakout(break_title=title,break_picture=save_as,break_skillid=level)
                db.session.add(b)
                db.session.commit()            
                return redirect("/admin/breakout")
            else:
                flash('File Not Allowed')
                return redirect("/admin/addbreakout")

        else:
            save_as =""
            b = Breakout(break_title=title,break_picture=save_as,break_skillid=level)
            db.session.add(b)
            db.session.commit() 
            return redirect("/admin/breakout")  


        
        #if it is not empty, upload it
        #run an insert query --instantiate a class of breakout b-db.session.add(b), db.session.commit() remember to importr Breakout from models
        #if successfully added, redirect to /admin/breakout else show form again

        return 'Form is submitted'






@app.route('/admin/upload', methods=['POST','GET'])
def admin_upload():
    if request.method =='GET':
        return render_template("admin/test.html")
    else:
        data = request.files.get('image')  
        original_name= data.filename
        #task is to generate random string to be used as our filename
        fn = math.ceil(random.random() * 100000000)        
        ext = os.path.splitext(original_name)
        save_as = str(fn)+ext[1] 
        allowed = ['.jpg','.png','.gif']
        if ext[1].lower() in allowed:
            data.save(f'conferenceapp/static/assets/img/{save_as}')        
            return f"Submitted and saved as {save_as}"
        else:
            return "File typoe not allowed"