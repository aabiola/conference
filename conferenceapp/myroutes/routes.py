import json, requests, random
import urllib3
from flask import make_response, render_template, request, session,redirect, flash, url_for, jsonify
from sqlalchemy import desc

from conferenceapp import app, db
from conferenceapp.mymodels import User,State,Skill,Breakout,Contactus, user_sessions,Posts,Comments, Myorder, Payment, OrderDetails


from conferenceapp.forms import LoginForm, ContactusForm

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
         
        data = {"email":userdeets.user_email,"amount":deets.pay_amt*100, "reference":deets.pay_ref}

        headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_here"}

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
    headers = {"Content-Type": "application/json","Authorization":"Bearer sk_test_here"}

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
