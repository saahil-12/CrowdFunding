from flask import *
from DBConnection import Db

app = Flask(__name__)
app.secret_key="haiii"

import web3


from web3 import Web3, HTTPProvider

blockchain_address = "http://127.0.0.1:7545"
web3 = Web3(HTTPProvider(blockchain_address))
web3.eth.defaultAccount = web3.eth.accounts[0]

compiled_contract_path = 'C:\\myblocknode\\build\\contracts\\Crowdfunding.json'
deployed_contract_address = '0xF31f0b495ecB28A0Cd30E80FbEd835073eE37F0C'
deployed_contract_addressa = web3.eth.accounts[0]





@app.route('/')
def login():
    return render_template('index.html')

@app.route('/login_post', methods=['POST'])
def login_post():
    username=request.form['textfield']
    password=request.form['textfield2']
    qry="SELECT * FROM `login` WHERE `User_Name`='"+username+"' AND `Password`='"+password+"'"
    db=Db()
    res=db.selectOne(qry)
    if res  !=None :
                #return "<script>alert('Invalid user name or password');window.location='/'</script>"
        session['lid']= res['Lid']
        if res['Type']=="admin":
            return redirect('/Admin_Home')
        elif res['Type']=="organization":
            return redirect('/Org_Home')
        elif res['Type']=="user":
            return redirect('/User_home')
        else:
            return "<script>alert('Invalid user name or password');window.location='/'</script>"

    else:
        return "<script>alert('Invalid user name or password');window.location='/'</script>"






#===========Admin=====================
@app.route('/Admin_Home')
def Admin_Home():
    return render_template('admin/home_index.html')


@app.route('/change_password')
def change_password():
    return render_template('admin/Change password.html')

@app.route('/Change_password_post', methods=['POST'])
def Change_password_post():
    db=Db()
    currentpassword=request.form['textfield3']
    newpassword=request.form['textfield4']
    confirmpassword=request.form['textfield5']
    qry="SELECT * FROM `login` WHERE `Lid`='"+str(session['lid'])+"' AND `Password`='"+currentpassword+"'"
    res=db.selectOne(qry)
    if res is not None:
        if newpassword==confirmpassword:
            qry1="UPDATE `login` SET `Password`='"+confirmpassword+"' WHERE `Lid`='"+str(session['lid'])+"'"
            res1=db.update(qry1)
            return "<script>alert('Password Changed');window.location='/'</script>"
        else :
            return "<script>alert('Confirm password doesnot match');window.location='/change_password'</script>"
    else:
        return "<script>alert('Current Password Doesnot match');window.location='/change_password'</script>"

    return "ok"







@app.route('/generate_donation_recipt/')
def generate_donation_recipt():
    return render_template('admin/Generate Donation Recipt.html')


@app.route('/send_reply/<cid>')
def send_reply(cid):
    return render_template('admin/send reply.html',cid=cid)

@app.route('/send_reply_post', methods=['POST'])
def send_reply_post():
    reply=request.form['textarea']
    cid=request.form['cmpid']
    db=Db()
    qry="UPDATE `complaint` SET `Reply`='"+reply+"',`Status`='Replied' WHERE `Complaint_Id`='"+cid+"'"
    res=db.update(qry)
    return "<script>alert('Replied Successfully');window.location='/view_complaint_send_reply'</script>"

@app.route('/status_of_fund')
def status_of_fund():


    qry="SELECT * FROM `organization` JOIN `request` ON `request`.`Org_lid`=`organization`.`Org_lid` "
    db=Db()
    res=db.select(qry)

    return render_template('admin/status of fund.html',data=res)



@app.route('/view_donations/<rid>')
def view_donations(rid):
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    blocknumber = web3.eth.get_block_number()
    print(blocknumber)
    lq = []
    for i in range(blocknumber, 5, -1):
        a = web3.eth.get_transaction_by_block(i, 0)
        try:
            decoded_input = contract.decode_function_input(a['input'])
            print(decoded_input)
            print("ku")
            print(decoded_input)
            lq.append(decoded_input[1])
        except Exception as a:
            pass

    print(lq)
    tot = 0
    ls = []

    for i in lq:
        print(i["policyida"])
        if str(i["policyida"]) == str(rid):
        #     # ls.append(i)
        #     print(i['userida'], "aaaaaaaaaaaaaaaaa")
            qry = "SELECT * FROM `user` WHERE `u_lid`='"+str(i['userida'])+"'"
            db = Db()
            res = db.selectOne(qry)
            if res is not None:
                a = {'reqida': i['reqida'],'policyida':i['policyida'],'userida':i['userida'],'amounta':i['amounta'],'datea':i['datea'],'name':res['User_Name'],'mail':res['Mail_Id'] }
                ls.append(a)
            tot += i["amounta"]

        print("final results")
        print(ls,"=======================================")

    return render_template("admin/view_donations.html",data=ls)




@app.route('/verify_user')
def verify_user():
    db=Db()
    qry="SELECT * FROM `user`  "
    res=db.select(qry)
    return render_template('admin/Verify_user.html',data=res)

@app.route('/verify_user_post', methods=['POST'])
def verify_user_post():
    db=Db()
    nm = request.form['textfield']
    qry = "SELECT * FROM `user` WHERE `User_Name` LIKE '%" + nm + "%' "
    res = db.select(qry)
    return render_template('admin/Verify_user.html', data=res)



@app.route('/view_and_verify_org')
def view_and_verify_org():
    db=Db()
    qry1="SELECT * FROM `organization` WHERE `Status`='pending'"
    res1=db.select(qry1)
    return render_template('admin/View nd verify org.html',data=res1)

@app.route('/admin_approve_org/<id>')
def admin_approve_org(id):
    db=Db()
    qry="UPDATE `organization` SET `Status`='approved' WHERE `Org_id`='"+id+"'"
    res=db.update(qry)
    return redirect('/view_and_verify_org')

@app.route('/admin_reject_org/<id>')
def admin_reject_org(id):
    db=Db()
    qry="UPDATE `organization` SET `Status`='rejected' WHERE `Org_id`='"+id+"'"
    res=db.update(qry)
    return redirect('/view_and_verify_org')

@app.route('/approved_org')
def approved_org():
    db=Db()
    qry="SELECT * FROM `organization` WHERE `Status`='approved'"
    res=db.select(qry)
    return render_template('admin/View_approved_org.html',data=res)



@app.route('/approved_orgpost',methods=['POST'])
def approved_orgpost():
    nm=request.form['textfield']
    db=Db()
    qry="SELECT * FROM `organization` WHERE `Status`='approved' and Org_Name like '%"+nm+"%' "
    res=db.select(qry)
    return render_template('admin/View_approved_org.html',data=res)

@app.route('/rejected_org')
def rejected_org():
    db=Db()
    qry="SELECT * FROM `organization` WHERE `Status`='rejected'"
    res=db.select(qry)
    return render_template('admin/View_rejected_org.html',data=res)

@app.route('/rejected_org_post',methods=['POST'])
def rejected_org_post():
    nm=request.form['textfield']
    db=Db()
    qry="SELECT * FROM `organization` WHERE `Status`='rejected' and Org_Name like '%"+nm+"%'"
    res=db.select(qry)
    return render_template('admin/View_rejected_org.html',data=res)


@app.route('/view_and_verify_org_post', methods=['POST'])
def view_and_verify_org_post():
    vieworg=request.form['textfield']
    return "ok"


@app.route('/view_complaint_send_reply')
def view_complaint_send_reply():
    db = Db()
    qry2= "SELECT * FROM `complaint` INNER JOIN `user` ON `complaint`.`User_lid`=`user`.`u_lid`"
    res2 = db.select(qry2)
    return render_template('admin/View_Complaint_send_Reply.html',data=res2)

@app.route('/view_complaint_send_reply_post', methods=['POST'])
def view_complaint_send_reply_post():
    from1=request.form['textfield']
    to=request.form['textfield2']
    db = Db()
    qry2= "SELECT * FROM `complaint` INNER JOIN `user` ON `complaint`.`User_lid`=`user`.`u_lid` where complaint.Date between '"+from1+"' and '"+to+"'"
    res2 = db.select(qry2)
    return render_template('admin/View_Complaint_send_Reply.html',data=res2)



#==================Organization===========================

@app.route('/Register_Org')
def Register_Org():
    return render_template('Organization/Signup_index.html')

@app.route('/Register_Org_post', methods=['POST'])
def Register_Org_post():
    db=Db()
    Name=request.form['textfield12']
    place=request.form['textfield2']
    post=request.form['textfield5']
    district=request.form['textfield3']
    pin=request.form['textfield4']
    state=request.form['textfield6']
    phone=request.form['textfield7']
    email=request.form['textfield8']
    password=request.form['textfield10']
    confirm_pass=request.form['textfield11']
    qry="INSERT INTO `login`(`User_Name`,`Password`,`Type`)VALUES('"+email+"','"+confirm_pass+"','organization') "
    res=db.insert(qry)
    qry1="INSERT INTO`organization`(`Org_Name`,`Mail_Id`,`Contact_No`,`Place`,`Post`,`District`,`Pincode`,`State`,`Status`,`Org_lid`)VALUES('"+Name+"','"+email+"','"+phone+"','"+place+"','"+post+"','"+district+"','"+pin+"','"+state+"','pending','"+str(res)+"')"
    res1=db.insert(qry1)
    return '''<script>alert('Registered successfully');window.location='/'</script>'''

@app.route('/Org_Home')
def Org_Home():
    return render_template('Organization/home_index.html')


@app.route('/org_view_donations/<rid>')
def org_view_donations(rid):

    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions

    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)

    blocknumber = web3.eth.get_block_number()
    print(blocknumber)
    lq = []
    for i in range(blocknumber, 5, -1):
        a = web3.eth.get_transaction_by_block(i, 0)
        try:
            decoded_input = contract.decode_function_input(a['input'])
            print(decoded_input)
            print("ku")
            print(decoded_input)
            lq.append(decoded_input[1])
        except Exception as a:
            pass

    print(lq)
    tot = 0
    ls = []

    for i in lq:
        print(i["policyida"])
        if str(i["policyida"]) == str(rid):
        #     # ls.append(i)
        #     print(i['userida'], "aaaaaaaaaaaaaaaaa")
            qry = "SELECT * FROM `user` WHERE `u_lid`='"+str(i['userida'])+"'"
            db = Db()
            res = db.selectOne(qry)
            if res is not None:
                a = {'reqida': i['reqida'],'policyida':i['policyida'],'userida':i['userida'],'amounta':i['amounta'],'datea':i['datea'],'name':res['User_Name'],'mail':res['Mail_Id'] }
                ls.append(a)
            tot += i["amounta"]

        print("final results")
        print(ls,"=======================================")



    return render_template("Organization/view_donations.html",data=ls)









@app.route('/org_view_profile')
def org_view_profile():
    db=Db()
    qry="SELECT * FROM `organization` WHERE `Org_lid`='"+str(session['lid'])+"'"
    res=db.selectOne(qry)
    return render_template('Organization/view_profile.html',data=res)


@app.route('/org_edit_profile')
def org_edit_profile():
    db = Db()
    qry = "SELECT * FROM `organization` WHERE `Org_lid`='" + str(session['lid']) + "'"
    res = db.selectOne(qry)
    return render_template('Organization/org_edit_profile.html', data=res)


@app.route('/org_edit_profile_post', methods=['POST'])
def org_edit_profile_post():
    db=Db()
    name=request.form['textfield12']
    place=request.form['textfield2']
    post=request.form['textfield5']
    district=request.form['textfield3']
    pin=request.form['textfield4']
    state=request.form['textfield6']
    phone=request.form['textfield7']
    email=request.form['textfield8']
    qry="UPDATE `organization` SET `Org_Name`='"+name+"' , `Mail_Id`='"+email+"' ,`Contact_No`='"+phone+"', `Place`='"+place+"' ,`Post`='"+post+"',`District`='"+district+"', `Pincode`='"+pin+"', `State`='"+state+"' ,`Status`='pending' WHERE `Org_lid`='"+str(session['lid'])+"'"
    res=db.update(qry)
    return "<script>alert('Updated Successfully');window.location='/org_view_profile'</script>"


@app.route('/org_change_password')
def org_change_password():
    return render_template('Organization/Change password.html')

@app.route('/org_Change_password_post', methods=['POST'])
def org_Change_password_post():
    db=Db()
    currentpassword=request.form['textfield3']
    newpassword=request.form['textfield4']
    confirmpassword=request.form['textfield5']
    qry="SELECT * FROM `login` WHERE `Lid`='"+str(session['lid'])+"' AND `Password`='"+currentpassword+"'"
    res=db.selectOne(qry)
    if res is not None:
        if newpassword==confirmpassword:
            qry1="UPDATE `login` SET `Password`='"+confirmpassword+"' WHERE `Lid`='"+str(session['lid'])+"'"
            res1=db.update(qry1)
            return "<script>alert('Password Changed');window.location='/'</script>"
        else :
            return "<script>alert('Confirm password doesnot match');window.location='/org_change_password'</script>"
    else:
        return "<script>alert('Current Password Doesnot match');window.location='/org_change_password'</script>"



@app.route('/manage_post')
def manage_post():
    db=Db()
    qry="select * from `organization`"
    res=db.select(qry)
    return render_template('Organization/Request.html',data=res)
@app.route('/manage_post_post', methods=['POST'])
def manage_post_post():
    db=Db()
    organization=request.form['select']
    purpose=request.form['textfield']
    amount=request.form['textfield2']
    lastdate=request.form['textfield7']
    name=request.form['textfield3']
    address1=request.form['textfield4']
    address2=request.form['textfield5']
    address3=request.form['textfield6']
    qry="INSERT INTO `request` (`Org_lid`,`Name`,`Amount`,`Address1`,`Address2`,`Address3`,`Purpose`,`Date`,`Status`)VALUES('"+str(session['lid'])+"','"+name+"','"+amount+"','"+address1+"','"+address2+"','"+address3+"','"+purpose+"','"+lastdate+"','pending')"
    res=db.insert(qry)
    return "<script>alert('Request send');window.location='/manage_post'</script>"



@app.route('/org_view_post')
def org_view_post():
    db=Db()
    qry="SELECT * FROM `request`JOIN`organization` ON `request`.`Org_lid`=`organization`.`Org_lid` WHERE `request`.`Org_lid`='"+str(session['lid'])+"'"
    res=db.select(qry)
    return render_template('Organization/view_post.html',data=res)


@app.route('/org_edit_post/<id>')
def org_edit_post(id):
    db=Db()
    qry1= "select * from `organization` where `Org_lid`='"+str(session['lid'])+"'  "
    res1=db.select(qry1)
    qry="SELECT * FROM `request` WHERE `R_id`='"+id+"'"
    res = db.selectOne(qry)
    return render_template('Organization/edit_post.html',data=res,data1=res1)


@app.route('/org_edit_post_post', methods=['POST'])
def org_edit_post_post():
    db=Db()
    id=request.form['id']
    organization = request.form['select']
    purpose = request.form['textfield']
    amount = request.form['textfield2']
    lastdate = request.form['textfield7']
    name = request.form['textfield3']
    address1 = request.form['textfield4']
    address2 = request.form['textfield5']
    address3 = request.form['textfield6']
    qry="update `request` set `Org_lid`='"+organization+"',`Name`='"+name+"',`Amount`='"+amount+"',`Address1`='"+address1+"',`Address2`='"+address2+"',`Address3`='"+address3+"',`Purpose`='"+purpose+"',`Date`='"+lastdate+"',`Status`='pending' where R_id='"+id+"'"
    res=db.update(qry)
    return '''<script>alert('updated');window.location='/org_view_post'</script>'''

@app.route('/org_delete_post/<id>')
def org_delete_post(id):
    db=Db()
    qry="DELETE FROM `request` WHERE `R_id`='"+id+"'"
    res=db.delete(qry)
    return "<script>alert('Deleted');window.location='/org_view_post'</script>"



#==========User=========

@app.route('/User_Register')
def User_Register():
    return render_template('User/Signup_index.html')

@app.route('/User_Register_Post', methods=['POST'])
def User_Register_Post():
    db=Db()
    name=request.form['textfield']
    gender=request.form['RadioGroup1']
    place=request.form['textfield2']
    post=request.form['textfield3']
    district=request.form['textfield4']
    pin=request.form['textfield5']
    from datetime import datetime
    photo = request.files['fileField']
    date=datetime.now().strftime("%Y%m%d-%H%M%S")
    photo.save("C:\\Users\\91759\\PycharmProjects\\crowdfunding\\static\\user_photo\\"+date+".jpg")
    path="/static/user_photo/"+date+".jpg"

    email=request.form['textfield6']
    phone=request.form['textfield7']
    password=request.form['textfield8']
    confirmpass=request.form['textfield9']
    qry="INSERT INTO `login`(`User_Name`,`Password`,`Type`) VALUES ('"+email+"','"+confirmpass+"','user')"
    res=db.insert(qry)
    qry1="INSERT INTO `user`(`User_Name`,`Mail_Id`,`Contact`,`Gender`,`Photo`,`Place`,`Post`,`District`,`Pin`,`u_lid`) VALUES ('"+name+"','"+email+"','"+phone+"','"+gender+"','"+path+"','"+place+"','"+post+"','"+district+"','"+pin+"','"+str(res)+"')"
    res1=db.insert(qry1)
    return "<script>alert('Registered Successfully');window.location='/'</script>"


@app.route('/User_home')
def User_home():
    return render_template('User/User_Home.html')

@app.route('/view_user_profile')
def view_user_profile():
    db=Db()
    qry="SELECT * FROM `user` WHERE `u_lid`='"+str(session['lid'])+"'"
    res=db.selectOne(qry)
    return render_template('User/view_user_profile.html',data=res)

@app.route('/user_edit_profile')
def user_edit_profile():
    db=Db()
    qry = "SELECT * FROM `user` WHERE `u_lid`='" + str(session['lid']) + "'"
    res = db.selectOne(qry)
    return render_template('User/edit_profile.html', data=res)


@app.route('/user_edit_profile_post', methods=['POST'])
def user_edit_profile_post():
    db=Db()
    name=request.form['textfield']
    gender=request.form['RadioGroup1']
    place=request.form['textfield2']
    post=request.form['textfield3']
    district=request.form['textfield4']
    pin=request.form['textfield5']
    email = request.form['textfield6']
    phone = request.form['textfield7']
    if "fileField" in request.files:
        photo=request.files['fileField']
        if photo.filename!="":
            from datetime import datetime
            date = datetime.now().strftime("%Y%m%d-%H%M%S")
            photo.save("C:\\Users\\91759\\PycharmProjects\\crowdfunding\\static\\user_photo\\" + date + ".jpg")
            path = "/static/user_photo/" + date + ".jpg"


            qry="UPDATE `user`SET `User_Name`='"+name+"',`Mail_Id`='"+email+"',`Contact`='"+phone+"',`Gender`='"+gender+"',`Photo`='"+path+"',`Place`='"+place+"',`Post`='"+post+"',`District`='"+district+"',`Pin`='"+pin+"' WHERE`u_lid`='"+str(session['lid'])+"'"
            res=db.update(qry)
            return '''<script>alert('Updated Successfully');window.location='/view_user_profile'</script>'''
        else :
            qry = "UPDATE `user`SET `User_Name`='" + name + "',`Mail_Id`='" + email + "',`Contact`='" + phone + "',`Gender`='" + gender + "',`Place`='" + place + "',`Post`='" + post + "',`District`='" + district + "',`Pin`='" + pin + "' WHERE`u_lid`='" + str(
                session['lid']) + "'"
            res = db.update(qry)
            return '''<script>alert('Updated Successfully');window.location='/view_user_profile'</script>'''
    else :
        qry = "UPDATE `user`SET `User_Name`='" + name + "',`Mail_Id`='" + email + "',`Contact`='" + phone + "',`Gender`='" + gender + "',`Place`='" + place + "',`Post`='" + post + "',`District`='" + district + "',`Pin`='" + pin + "' WHERE`u_lid`='" + str(
            session['lid']) + "'"
        res = db.update(qry)
        return '''<script>alert('Updated Successfully');window.location='/view_user_profile'</script>'''


@app.route('/user_change_password')
def user_change_password():
    return render_template('User/Change password.html')

@app.route('/user_Change_password_post', methods=['POST'])
def user_Change_password_post():
    db=Db()
    currentpassword=request.form['textfield3']
    newpassword=request.form['textfield4']
    confirmpassword=request.form['textfield5']
    qry="SELECT * FROM `login` WHERE `Lid`='"+str(session['lid'])+"' AND `Password`='"+currentpassword+"'"
    res=db.selectOne(qry)
    if res is not None:
        if newpassword==confirmpassword:
            qry1="UPDATE `login` SET `Password`='"+confirmpassword+"' WHERE `Lid`='"+str(session['lid'])+"'"
            res1=db.update(qry1)
            return "<script>alert('Password Changed');window.location='/'</script>"
        else :
            return "<script>alert('Confirm password doesnot match');window.location='/user_change_password'</script>"
    else:
        return "<script>alert('Current Password Doesnot match');window.location='/user_change_password'</script>"



@app.route('/user_send_complaint')
def user_send_complaint():
    return render_template('User/send_complaint.html')
@app.route('/user_send_complaint_post', methods=['POST'])
def user_send_complaint_post():
    complaint=request.form['textarea']
    db=Db()
    qry="INSERT INTO `complaint` (`User_lid`,`Date`,`Reply`,`Status`,`Complaint`)VALUES('"+str(session['lid'])+"',CURDATE(),'pending','pending','"+complaint+"')"
    res=db.insert(qry)
    return "<script>alert('Send');window.location='/user_send_complaint'</script>"


@app.route('/user_view_reply')
def user_view_reply():
    db=Db()
    qry="SELECT * FROM `complaint` WHERE `User_lid`='"+str(session['lid'])+"'"
    res=db.select(qry)
    return render_template('User/View_reply.html',data=res)



@app.route('/user_view_fund_requirements')
def user_view_fund_requirements():
    db=Db()
    qry="SELECT * FROM `fund` "
    res=db.select(qry)
    return render_template('User/view_fund_requirements.html',data=res)


@app.route('/user_fund_transfer')
def user_fund_transfer():
    return render_template('User/')

@app.route('/user_view_transaction_details')
def user_view_transaction_details():
    return render_template('User/')






#########ANDROID USER##########

@app.route('/and_user_login', methods=['POST'])
def and_user_login():
    username=request.form['username']
    password=request.form['password']
    db=Db()
    qry="SELECT * FROM `login` WHERE `User_Name`='"+username+"' AND `Password`='"+password+"'"
    res=db.selectOne(qry)
    if res is not None:
         return jsonify(status="ok",lid=res['Lid'],type=res['Type'])
    else:
        return jsonify(status="not ok")

@app.route('/and_user_signup', methods=['POST'])
def and_user_signup():
    db=Db()
    username=request.form['User_Name']
    mailid=request.form['Mail_Id']
    contact=request.form['Contact']
    gender=request.form['Gender']
    photo=request.form['Photo']
    place=request.form['Place']
    district=request.form['District']
    post=request.form['Post']
    pin=request.form['Pin']
    password=request.form['Password']
    import time, datetime

    import base64
    try:
        timestr = time.strftime("%Y%m%d-%H%M%S")

        a = base64.b64decode(photo)

        fh = open("C:\\Users\\91759\\PycharmProjects\\crowdfunding\\static\\user_photo\\" + timestr + ".jpg", "wb")
        path = "/static/user_photo/" + timestr + ".jpg"
        fh.write(a)
        fh.close()
        qry="INSERT INTO `login`(`User_Name`,`Password`,`Type`)VALUES('" +mailid+"','" +password+"','user')"
        res=db.insert(qry)
        qry1="INSERT INTO `user`(`User_Name`,`Mail_Id`,`Contact`,`Gender`,`Photo`,`Place`,`Post`,`District`,`Pin`,`u_lid`)VALUES('"+username+"','"+mailid+"','"+contact+"','"+gender+"','"+path+"','"+place+"','"+post+"','"+district+"','"+pin+"','"+str(res)+"')"
        res1=db.insert(qry1)
    except Exception as ex:
        print(ex)
    return jsonify(status="ok")

@app.route('/and_user_change_password', methods=['POST'])
def and_user_change_password():
    db=Db()
    currentpassword = request.form['Current']
    newpassword = request.form['New']
    confirmpassword = request.form['Confirm']
    lid=request.form['lid']
    qry = "SELECT * FROM `login` WHERE `Lid`='" +lid+ "' AND `Password`='" + currentpassword+ "'"
    res = db.selectOne(qry)

    if res is not None:
        if newpassword == confirmpassword:
            qry1 = "UPDATE `login` SET `Password`='" +confirmpassword+ "' WHERE `Lid`='" + lid + "'"
            res1 = db.update(qry1)
            return jsonify(status="ok")
        else:
            return jsonify(status="Not ok")
    else:
        return jsonify(status="not ok")

@app.route('/and_user_view_profile', methods=['POST'])
def and_user_view_profile():
    db=Db()
    lid=request.form['lid']
    qry="SELECT * FROM `user` WHERE u_lid='"+lid+"'"
    res=db.selectOne(qry)
    print(res)
    return jsonify(status="ok",data=res)

@app.route('/and_user_edit_profile', methods=['POST'])
def and_user_edit_profile():
    db = Db()
    username = request.form['User_Name']
    mailid = request.form['Mail_Id']
    contact = request.form['Contact']
    gender = request.form['Gender']
    photo = request.form['Photo']
    place = request.form['Place']
    district = request.form['District']
    post = request.form['Post']
    pin = request.form['Pin']
    lid=request.form['lid']
    if photo!='':
        import time, datetime
        from encodings.base64_codec import base64_decode
        import base64

        timestr = time.strftime("%Y%m%d-%H%M%S")
        print(timestr)
        a = base64.b64decode(photo)
        fh = open("C:\\Users\\91759\\PycharmProjects\\crowdfunding\\static\\user_photo\\" + timestr + ".jpg", "wb")
        path = "/static/user_photo/" + timestr + ".jpg"
        fh.write(a)
        fh.close()
        qry="update `USER` set `User_Name`='"+username+"',`Mail_Id`='"+mailid+"',`Contact`='"+contact+"',`Gender`='"+gender+"',`Photo`='"+path+"',`Place`='"+place+"',`Post`='"+post+"',`District`='"+district+"',`Pin`='"+pin+"' where `u_lid`='"+lid+"'"
        res=db.update(qry)
        return jsonify(status="ok")
    else:
        qry = "update `USER` set `User_Name`='" + username + "',`Mail_Id`='" + mailid + "',`Contact`='" + contact + "',`Gender`='" + gender + "',`Place`='" + place + "',`Post`='" + post + "',`District`='" + district + "',`Pin`='" + pin + "' where `u_lid`='" + lid + "'"
        res = db.update(qry)
        return jsonify(status="ok")

@app.route('/and_user_send_complaint', methods=['POST'])
def and_user_send_complaint():
    db=Db()
    complaint=request.form['Complaint']
    lid=request.form['lid']
    qry="Insert into `complaint`(`User_lid`,`DATE`,`Reply`,`STATUS`,`Complaint`)values('"+lid+"',curdate(),'pending','pending','"+complaint+"')"
    res=db.insert(qry)
    return jsonify(status="ok")






def checkdonst(reqid):
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions

    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    blocknumber = web3.eth.get_block_number()
    lq=[]
    for i in range(blocknumber,4, -1):
        a = web3.eth.get_transaction_by_block(i, 0)
        try:
            decoded_input = contract.decode_function_input(a['input'])
            lq.append(decoded_input[1])
        except Exception as a:
            pass

    print(lq)
    tot=0
    ls=[]
    for i in lq:
        print(i["policyida"])
        if i["policyida"]==int(reqid):
            # ls.append(i)

            qry="SELECT * FROM `request` WHERE `R_id`='"+str(i['policyida'])+"'"
            db=Db()
            res=db.selectOne(qry)
            if res is not None:
                a={'reqida':i['reqida'],'policyida':i['policyida'],'userida':i['userida'],'amounta':i['amounta'],'datea':i['datea']}
                ls.append(a)
            tot+=i["amounta"]
            print(tot,"--------------------------------------------------------------------------------")
    return  tot







@app.route('/and_user_view_fund_requirements', methods=['POST'])
def and_user_view_fund_requirements():
    db=Db()
    qry="SELECT *, DATE_FORMAT(request.Date, '%d-%m-%Y') AS rdt  FROM `request` JOIN `organization` ON `request`.`Org_lid`=`organization`.`Org_lid`"
    res=db.select(qry)
    ks = []
    total=0
    for i in res:
        k = i['R_id']
        s = checkdonst(k)
        total=s-i['Amount']

        # k = i['R_id']
        # s = 0
        # s = checkdonst(k)
        # b = 0
        #
        #
        # if s >= i['Amount']:
        #     b = 0
        # else:
        #     b = i['Amount'] - s

        ks.append({'am': i['Amount'], 'R_id': i['R_id'],'Org_lid':i["Org_lid"],"Name":i["Name"], 'Amount': s,'Address1':i["Address1"],'Address2':i["Address2"],'Address3':i["Address3"],'Purpose':i["Purpose"],"Date":i["rdt"],"Status":i["Status"],"Org_Name":i["Org_Name"],'total':total})
    print(ks)
    return jsonify(status="ok",data=ks)


def checkbalance(amount,accountnumber,privatekey):
    from web3 import Web3, HTTPProvider
    blockchain_address = "http://127.0.0.1:7545"

    web3 = Web3(HTTPProvider(blockchain_address))

    if web3.isConnected():
        acc1 = accountnumber
        acc2 = "0xF31f0b495ecB28A0Cd30E80FbEd835073eE37F0C"

        prvkey = privatekey
        nonce = web3.eth.getTransactionCount(acc1)

        abcd = web3.eth.get_balance(acc1)
        abcd = web3.fromWei(abcd, 'ether')
        print(abcd)

        tx = {
            'nonce': nonce,
            'to': acc2,
            'value': web3.toWei(int(amount), 'ether'),
            'gas': 200000,
            'gasPrice': web3.toWei('50', 'gwei')
        }
        signedtx = web3.eth.account.sign_transaction(tx, prvkey)
        hashx = web3.eth.send_raw_transaction(signedtx.rawTransaction)
        print(web3.toHex(hashx))


def checktotalamount(reqid):
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions

    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    blocknumber = web3.eth.get_block_number()
    print(blocknumber)
    lq=[]
    for i in range(blocknumber-1,4, -1):
        a = web3.eth.get_transaction_by_block(i, 0)
        try:
            decoded_input = contract.decode_function_input(a['input'])
            print(decoded_input)
            print("ku")
            print(decoded_input)
            lq.append(decoded_input[1])
        except Exception as a:
            pass

    print(lq)
    tot=0
    ls=[]
    for i in lq:
        print(i["policyida"])
        if i["policyida"]==int(reqid):
            # ls.append(i)
            print(i['userida'],"aaaaaaaaaaaaaaaaa")

            qry="SELECT * FROM `user` WHERE `u_lid`='"+str(i['userida'])+"'"
            db=Db()
            res=db.selectOne(qry)
            if res is not None:
                a={'amounta':i['amounta'],'userida':i['userida'],'datea':i['datea'],'username':res['User_Name'],'place':res['Place'],'post':res['Post'],'pin':res['Pin'],'district': res['District'],'photo':res['Photo'], 'email':res['Mail_Id'],'phone':res['Contact'] }
                ls.append(a)
            tot+=i["amounta"]
    print(ls)
    return  tot



@app.route('/and_user_delete_profile', methods=['POST'])
def and_user_delete_profile():
    return jsonify(status="ok")

@app.route('/and_user_view_reply', methods=['POST'])
def and_user_view_reply():
    db=Db()
    lid=request.form['lid']
    qry="select * from `complaint` where `User_lid`='"+lid+"'"
    res=db.select(qry)
    return jsonify(status="ok",data=res)

@app.route('/and_user_view_status_of_each_donation', methods=['POST'])
def and_user_view_status_of_each_donation():
    return jsonify(status="ok")




@app.route('/and_payment_details', methods=['POST'])
def and_payment_details():
    print(request.form,"================")
    account_number=request.form['account_number']
    key_id=request.form['key_id']
    rid=request.form["r_id"]
    amount=request.form['amount']
    lid=request.form['lid']
    checkbalance(amount, account_number, key_id)
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
        print(contract_abi)
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    blocknumber = web3.eth.get_block_number()
    print(blocknumber)

    policyid = rid
    print(policyid)
    userid = lid

    from datetime import datetime
    date = datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
    print(policyid)
    # message2 = contract.functions.addTransaction(blocknumber + 1, policyid, userid, amount, date).transact()
    message2 = contract.functions.addTransaction(int(policyid), int(policyid), int(userid), int(amount), date).transact()
    print(amount, "Hihihihiihi likhil")
    print(message2)


    return jsonify(status="ok")








@app.route('/and_view_donations',methods=['post'])
def and_view_donations():
    lid=request.form['lid']
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions

    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)

    blocknumber = web3.eth.get_block_number()
    print(blocknumber)
    lq = []
    for i in range(blocknumber, 5, -1):
        a = web3.eth.get_transaction_by_block(i, 0)
        try:
            decoded_input = contract.decode_function_input(a['input'])
            print(decoded_input)
            print("ku")
            print(decoded_input)
            lq.append(decoded_input[1])
        except Exception as a:
            pass

    print(lq)
    tot = 0
    ls = []

    for i in lq:
        print(i["policyida"])
        if str(i["userida"]) == str(lid):
        #     # ls.append(i)
        #     print(i['userida'], "aaaaaaaaaaaaaaaaa")
            qry = "SELECT * FROM `request` JOIN `organization` ON `organization`.`Org_lid`=`request`.`Org_lid` WHERE `R_id`='"+str(i['reqida'])+"'"
            db = Db()
            res = db.selectOne(qry)
            if res is not None:
                a = {'reqida': i['reqida'],'policyida':i['policyida'],'userida':i['userida'],'amounta':i['amounta'],'datea':i['datea'],'name':res['Name'],'purpose':res['Purpose'],'orgname':res['Org_Name'],'status':res['Status'],'Org_lid':res['Org_lid'] }
                ls.append(a)
            tot += i["amounta"]
        print("final results")
        print(ls,"=======================================")
    return jsonify(status="ok",data=ls,total=tot)





if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
