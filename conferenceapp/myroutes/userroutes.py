'''This File is like the controller that determines what happens when a user visits our app'''
import json, requests, random
import urllib3
from flask import make_response, render_template, request, session,redirect, flash, url_for, jsonify
from sqlalchemy import desc

from conferenceapp import app, db
from conferenceapp.mymodels import User,State,Skill,Breakout,Contactus, user_sessions,Posts,Comments, Myorder, Payment, OrderDetails


from conferenceapp.forms import LoginForm, ContactusForm
from conferenceapp import Message,mail


@app.route("/donate", methods=['GET','POST'])
def donation():
    if request.method =="GET":
        return render_template('user/donation.html')
    else:
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        amt = request.form.get('amt') 
        #generate a random number as transaction ref
        ref = int(random.random() * 10000000)
        session['refno'] = ref #keep ref in session
        #insert into the database
        db.session.execute(f"INSERT INTO donation SET fullname='{fullname}',email='{email}',amt='{amt}',status='pending',ref='{ref}'")
        db.session.commit()
        return redirect("/confirmpay")

@app.route('/confirmpay')
def confirmpay():
    ref = session.get('refno')
    #run the query to retieve details of this donation
    qry = db.session.execute(f"SELECT * FROM donation WHERE ref={ref}")
    data = qry.fetchone()
    return render_template("user/payconfirm.html", data=data)

    

@app.route("/")
def home():
    login=LoginForm()
    id = session.get('loggedin')
    userdeets = User.query.get(id)
    b = Breakout.query.all()
    contactform = ContactusForm()  

    #connect to API without authentication
    # response = requests.get('http://127.0.0.1:8082/api/v1.0/listall')

    # #connect if there is authentication
    # response=requests.get('http://127.0.0.1:8082/api/v1.0/listall',auth=('sam', '1234'))
    
    try:
        http = urllib3.PoolManager()
        response = http.request('GET', "http://127.0.0.1:8082/api/v1.0/listall")
        hostel_json = json.loads(response.data)
    except:
        hostel_json = {}
      

    #retrieve the json in the request
    #hostel_json = response.json() #json.loads(response.text)
    # hostel_json=json.dumps(response)
    # status = hostel_json.get('status') #to pick the status  
      
    #pass it to the template as hostel_json=hostel_json
    return render_template("user/index.html",b=b, login=login, userdeets=userdeets, contactform=contactform,hostel_json=hostel_json)



 

@app.route("/user/editprofile")
def editprofile():
    id = session.get('loggedin')
    if id == None:
        return redirect("/")
    else:
        userdeets = User.query.get(id)
        all_levels = Skill.query.all()
        state = State.query.all()
        contactform = ContactusForm()
        return render_template("user/profile.html", userdeets=userdeets,all_levels=all_levels,state=state,contactform=contactform)


@app.route("/user/login", methods=['POST'])
def submit_login():
    login = LoginForm()
    #retrieve form data
    username = request.form.get('username')#method 1
    pwd = login.pwd.data #method 2
    #validate
    if login.validate_on_submit():
        #deets = User.query.filter(User.user_email ==username, User.user_pass==pwd).all()
        deets = User.query.filter(User.user_email ==username).filter(User.user_pass==pwd).first()        
        if deets:            
            #retrieve his user_id and then keep in session
            id = deets.user_id
            session['loggedin']=id
            return redirect('/userhome') #redirect him/her to userhome            
        else:
            #keep a failed message in flash, then redirect him to login again
            flash('Invalid Credentials.. Please try again')
            return redirect('/')
    else:
        return render_template("user/index.html", login=login)

@app.route("/user/update", methods=['POST','GET'])
def user_update():
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect('/')
    if request.method =='GET':
        return(redirect(url_for('home')))
    #get this intance of the User  
    user = User.query.get(loggedin)
    #change the fields
    user.user_fname=request.form.get('fname')
    user.user_lname = request.form.get('lname')
    user.user_phone=request.form.get('phone')
    user.user_address = request.form.get('address')
    user.user_skillid = request.form.get('skill')
    user.user_stateid = request.form.get('state')
    #commit the changes to database
    db.session.commit()
    flash("Details updated..")
    return redirect(url_for('editprofile'))


# @app.route("/user/update/<id>", methods=['POST','GET'])
# def user_update(id):
#     loggedin = session.get('loggedin')

#     if loggedin == None:
#         return redirect('/')
#     if request.method =='GET':
#         return(redirect(url_for('home')))
#     #retrieve form data
#     fname = request.form.get('fname')
#     lname = request.form.get('lname')
#     phone = request.form.get('phone')
#     address = request.form.get('address')
#     skill = request.form.get('skill')
#     state = request.form.get('state')
#     #get this intance of the User
#     if int(loggedin) == int(id):        
#         user = User.query.get(id)
#         #change the fields
#         user.user_fname=fname
#         user.user_lname = lname
#         user.user_phone=phone
#         user.user_address = address
#         user.user_skillid = skill
#         user.user_stateid = state
#         #commit the changes to database
#         db.session.commit()
#         flash("Details updated..")
#     return redirect(url_for('editprofile'))

    


@app.route("/user/regbreakout",methods=['POST'])
def reg_breakout():
    #getlist() to retrieve multiple form elements with same name
    bid = request.form.getlist('bid')  #[1,2,3]
    loggedin = session.get('loggedin')

    user = User.query.get(loggedin)

    db.session.execute(f"DELETE FROM user_breakout WHERE user_id='{loggedin}'") 
    db.session.commit()
    for i in bid:
        #METHOD 1 - SQL Alchemy Core
        # q = user_sessions.insert().values(user_id=loggedin,breakout_id=i)
        # db.session.execute(q)
        # db.session.commit() 
        #METHOD 2 - Using SQLAlchemy ORM
        
        item = Breakout.query.get(i)
        user.mybreakouts.append(item)
        db.session.commit()

    return redirect("/user/breakout")
    
    
@app.route("/user/contact", methods=['POST','GET'])
def contact_submit():
    contactform = ContactusForm()
    #if contactform.validate_on_submit():

    fullname = request.args.get('fullname')
    email = request.args.get('email')
    message = request.args.get('message')


    #insert ino the database
    msg = Contactus(contact_name=fullname,contact_email=email,contact_message=message)
    db.session.add(msg)
    db.session.commit()
    cid = msg.contact_id 

    if cid:
        return jsonify({"id":cid, "msg":"Message sent"})
    else:
        return "Sorry, please try again"        
    # else:
    #     return "Please complete all the fields"


#1. This route displays the breakouts with their prices
@app.route('/user/showbreakout')
def user_showbreakout():
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect("/")
    else:
        userdeets = User.query.get(loggedin)
        userskill= userdeets.user_skillid
        breakouts = db.session.query(Breakout).filter(Breakout.break_skillid==userskill).all()
        contactform = ContactusForm()
        return render_template("user/mybreakout.html",userdeets=userdeets, userskill=userskill,contactform=contactform, breakouts=breakouts)

#2. The user submits selected breakouts to this route
@app.route("/user/sendbreakout", methods=['POST','GET'])
def send_breakout():
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect("/")
    if request.method=='POST':
        #retrieve form data, breakout ids
        bid = request.form.getlist('bid')
        #insert new recd into myorder,
        mo = Myorder(order_userid=loggedin)
        db.session.add(mo)
        db.session.commit()
        orderid = mo.order_id
        #generate a trans ref using random (save in session), insert into payment table
        ref = int(random.random() * 10000000)
        session['refno'] = ref
        #loop over the selected breakout ids and insert into
        #order_details, 
        totalamt = 0
        for b in bid:
            breakdeets = Breakout.query.get(b)
            break_amt = breakdeets.break_amt
            totalamt = totalamt + break_amt
            od = OrderDetails(det_orderid=orderid,det_breakid=b,det_breakamt=break_amt)
            db.session.add(od)

        db.session.commit()
        p = Payment(pay_userid=loggedin,pay_orderid=orderid,pay_ref=ref,pay_amt=totalamt)       
        db.session.add(p) 
        db.session.commit()
        return redirect("/user/confirm_breakout")    
    else:
        return redirect("/user/home")

#3.This route will show all chosen sessions and connect to paystack
@app.route("/user/confirm_breakout", methods=['POST','GET'])
def confirm_break():
    loggedin = session.get('loggedin')
    ref = session.get('refno')
    if loggedin == None or ref == None:
        return redirect("/")
    userdeets = User.query.get(loggedin) 
    deets = Payment.query.filter(Payment.pay_ref==ref).first() 

    if request.method == 'GET':          
        contactform = ContactusForm()                
        return render_template("user/show_breakout_confirm.html",deets = deets,userdeets=userdeets,contactform=contactform)
    else:
        url = "https://api.paystack.co/transaction/initialize"
        
        data = {"email":userdeets.user_email,"amount":deets.pay_amt*100, "reference":deets.pay_ref}

        headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_3c5244cfb8965dd000f07a4cfa97185aab2e88d5"}

        response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, data=json.dumps(data))

        rspjson = json.loads(response.text) 
        if rspjson.get('status') == True:
            authurl = rspjson['data']['authorization_url']
            return redirect(authurl)
        else:
            return "Please try again"

#4. This  is the landing page for paystack, you are to connect to paystack and check the actual details of the transaction, then update yopur database
@app.route("/user/payverify")
def paystack():
    reference = request.args.get('reference')
    ref = session.get('refno')
    #update our database 
    headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_3c5244cfb8965dd000f07a4cfa97185aab2e88d5"}

    response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
    rsp =response.json()#in json format
    if rsp['data']['status'] =='success':
        amt = rsp['data']['amount']
        ipaddress = rsp['data']['ip_address']
        p = Payment.query.filter(Payment.pay_ref==ref).first()
        p.pay_status = 'paid'
        db.session.add(p)
        db.session.commit()
        return "Payment Was Successful"  #update database and redirect them to the feedback page
    else:
        p = Payment.query.filter(Payment.pay_ref==ref).first()
        p.pay_status = 'failed'
        db.session.add(p)
        db.session.commit()
        return "Payment Failed"  
    #return render_template("user/demo.html", response=rsp)


@app.route('/demo/available')
def available():
    return render_template("user/check_availability.html")




@app.route("/check/result")
def check_username_result():
    user = request.args.get('us')
    #query your user table for where user_email == user
    deets = db.session.query(User).filter(User.user_email==user).first()
    if deets:
        return "Username is taken"
    else:
        return "Username is available"
 

@app.route("/check/lga")
def check_lga():
    #fetch the states from State table
    states = State.query.all() #db.session.query(State).all()
    return render_template('user/load_lga.html', states=states)


@app.route('/demo/lga', methods=['POST'])
def show_lga():
    state = request.form.get('stateid')
    #TO DO: write a query that wll fetch from LGA table where state_id =state
    res = db.session.execute(f"SELECT * FROM lga WHERE state_id={state}")
    results = res.fetchmany(20)

    select_html = "<select>"
    for x,y,z in results:
        select_html = select_html + f"<option value='{x}'>{z}</option>"
    
    select_html = select_html + "</select>"

    return select_html


@app.route("/user/breakout")
def user_breakout():
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect("/")
    else:
        userdeets = User.query.get(loggedin)
        userskill= userdeets.user_skillid
        breakouts = db.session.query(Breakout).filter(Breakout.break_skillid==userskill).all()
        contactform = ContactusForm()

        return render_template('user/breakout.html', contactform=contactform,userdeets=userdeets,breakouts=breakouts)




@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='GET':

        skills = db.session.query(Skill).all()
        states = State.query.all()
        id = session.get('loggedin')
        userdeets = User.query.get(id)
        contactform = ContactusForm()
        return render_template('/user/register.html', skills=skills,states=states,userdeets=userdeets,contactform=contactform)
    else:
        #retrieve form data
        email  = request.form.get("email")
        pwd1 = request.form.get('pwd1')
        pwd2 = request.form.get('pwd2')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        state = request.form.get('state')
        skill = request.form.get('skill')
        #validate
        if email =="" or pwd1 =="" or fname=="" or lname=='' or state=='' or skill=='':
            flash("You need to complete all the fields")
            return redirect("/register")
        elif pwd1 != pwd2:
             flash("The two passwords did not match")
             return redirect("/register")
        else:
            u = User(user_email=email,user_pass=pwd1,user_fname=fname,user_lname=lname,user_skillid=skill,user_stateid=state)
            db.session.add(u)
            db.session.commit()
            id = u.user_id
            session['loggedin'] = id
            return redirect("/userhome")


@app.route('/post/details/<int:id>')
def post_details(id):
    contactform = ContactusForm()
    loggedin = session.get('loggedin')
    userdeets = User.query.get(loggedin)
    if loggedin == None:
        return redirect("/")
    else:
        postdeets = Posts.query.get_or_404(id)
        
        commentdeets = db.session.query(Comments).filter(Comments.c_postid==id).order_by(desc(Comments.c_date)).all()

        return render_template('user/postdetails.html', postdeets=postdeets,contactform=contactform,userdeets=userdeets,commentdeets=commentdeets)


@app.route("/post/comment", methods=['POST'])
def post_comment():
    #retrieve data
    loggedin = session.get('loggedin',0)
    postid = request.form.get('postid')
    comment = request.form.get('comment')    
    # c = Comments()
    # db.session.add(c)
    # c.c_userid=loggedin
    # c.c_postid=postid
    # c.c_comment=comment
    # db.session.commit()
    #method2
    c= Comments(c_userid=loggedin,c_postid=postid,c_comment=comment)
    db.session.add(c)
    db.session.commit()
    #method3
    user = User.query.get(loggedin)
    dpost = Posts.query.get(postid)
    c= Comments()
    db.session.add(c)
    user.user_comments.append(c)
    dpost.post_comments.append(c)
    c.c_comment=comment
    db.session.commit()
    #{"comment":comment,"total":6}
    ddate = c.c_date
    return f"{comment} and {ddate}"

@app.route('/user/discussion')
def discussion():
    contactform = ContactusForm()
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect("/")
    else:
        userdeets = User.query.get(loggedin)
        #retrieve all the posts and display in the template
        posts = Posts.query.all()
        return render_template("user/discussions.html",contactform=contactform,userdeets=userdeets,posts=posts)







@app.route("/userhome")
def userhome():
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect("/")
    else:
        userdeets = db.session.query(User).get(loggedin)
        contactform = ContactusForm() 
        return render_template("user/userhome.html", loggedin=loggedin, userdeets=userdeets,contactform=contactform)

@app.route('/logout')
def logout():
    session.pop('loggedin')
    return redirect('/')


@app.route("/sendmail")
def sendmail():
    subject = "Automated Email"
    sender = ("Admin Distrupt","admin@conferencea.com")
    recipient = ["moatacad@gmail.com"] #use an email you have access to
    #instantiate an object of Message..  
    #try:   
    # msg=Message(subject=subject,sender=sender,recipients=recipient,body="<b>This is a sample email sent from Python App</b>")

    #method2
    msg = Message()
    msg.subject = subject
    msg.sender=sender
    msg.body = "Test Message Again"
    msg.recipients=recipient
    
    #Sending HTML
    htmlstr = "<div><h1 style='color:red'>Thank you for signing up!</h1><p>You ahve subscribed...<br>Signed by Admin</p><img src='https://i0.wp.com/images-prod.healthline.com/hlcmsresource/images/AN_images/ways-to-make-coffee-super-healthy-1296x728-feature.jpg?w=1155&h=1528' width='100'></div>"
    
    msg.html = htmlstr
    with app.open_resource("invite.pdf") as fp:
        msg.attach("invite_savedas.pdf", "application/pdf", fp.read())

    mail.send(msg)
    return "Message Sent"
    # except:
    #     return "Connection Refused"