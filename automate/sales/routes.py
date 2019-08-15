import os
from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, flash, request, redirect, url_for, jsonify, abort, current_app
from automate import db, Mail
from automate.sales import sales
from flask_mail import Message
from flask_login import login_required, current_user
from automate.sales.forms import salesForm
from automate.models import Activitylog, Feeditem, Feedstock, Feedtype, Vendor, Farmitem, Purchase, Production, Receivable, Formulation, Feedcost, Customer, Pen, Allocation, Eggsupply, Eggstock, Salescost, Salesone, Salesoneitem
from automate.sales.utils import wordSeparator, insert_eggsize, insert_croptype, insert_birdtype, insert_dressed_birdtype, insert_manure_type, insert_sack_type
from automate.feedmill.utils import (update, wordTruncate, numberDecreament, numberDecimal, numberFormat, numberMonth, 
                                    color_sample, receivable_update, updateproduction, tonnesToBag, eggstock_update)

# Register Sales Blueprint
# salesmgt = Blueprint('salesmgt', __name__)


# Routes for Sales Overview
@sales.route('/salesmgt/overview', methods=['POST', 'GET'])
@login_required
def sales_overview():

    # Fetch all pending notifications
    all_activities = Activitylog.query.filter(Activitylog.status == 'pending').\
                                order_by(Activitylog.id.desc()).limit(3).all()

    # Fetch all User specific notifications
    user_activities = Activitylog.query.filter(Activitylog.user_id == current_user.id, Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

    # Current User Photo
    image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)

    return render_template('/salesmgt/sales_overview.html', title="Sales Overview", ficon="shopping-cart", date=datetime.now(), image_file=image_file, all_activities=all_activities, user_activities=user_activities)


# Routes for sales Customers
@sales.route('/salesmgt/customers', methods=['POST', 'GET'])
@login_required
def sales_customers():
    form = salesForm()

    # HANDLE PROCESSING OF NEW CUSTOMER
    if request.method == 'POST' and request.form.get('check') == 'new_customer':
        customer_name_initial = request.form.get('customer_name')
        customer_name = customer_name_initial.title()

        customer_split = customer_name.split(" ")
        if len(customer_split) > 1:
            customer_name = "_".join(customer_split)
        else:
            customer_name = customer_name

        customer_email = request.form.get('customer_email')
        customer_phone = request.form.get('customer_phone')
        customer_gender = request.form.get('customer_gender')
        customer_address = request.form.get('customer_address')
        customer_city = request.form.get('customer_city')
        customer_state = request.form.get('customer_state')
        customer_region = request.form.get('customer_region')
        customer_type = request.form.getlist('customer_type')

        if len(customer_type) > 1:
            customer_type = ",".join(customer_type)
        else:
            customer_type = customer_type[0]
        # print(customer_type)

        # Create New Customer
        new_customer = Customer(customer=customer_name, email=customer_email, phone=customer_phone, gender=customer_gender,address=customer_address, city=customer_city, state=customer_state,region=customer_region, customer_type=customer_type)
        
        db.session.add(new_customer)
        db.session.commit()

        flash(customer_name_initial+' added successfully', 'success')
        return redirect(url_for('sales.sales_customers'))

    
    # Delete processing Request
    if request.method == 'POST' and request.form.get('check') == 'delete_customer':
        # Get feeditem_id
        customer_id = request.form.get('delete_id')
        customer_data = Customer.query.filter(Customer.id == customer_id).first()

        # Get user info and activities
        user = current_user.id
        user_activity = 'Delete Request for Customer - '+customer_data.customer+' Received'
        request_query = 'Customer of id '+customer_id

        # Add Data to the Activitylog database
        new_activity = Activitylog(user_id = user, activity = user_activity, request = request_query)
        db.session.add(new_activity)
        db.session.commit()

        c_name = wordSeparator(customer_data.customer)

        flash('Delete Request for '+ c_name +' Sent', 'success')
        return redirect(url_for('sales.sales_customers'))


    # Update Customers
    if request.method=='POST' and request.form.get('check') == 'update_customer':
        customer_id = request.form.get('customer_id')
        customer_name_initial = request.form.get('customer_name')
        customer_name = customer_name_initial.title()

        customer_split = customer_name.split(" ")
        if len(customer_split) > 1:
            customer_name = "_".join(customer_split)
        else:
            customer_name = customer_name

        customer_email = request.form.get('customer_email')
        customer_phone = request.form.get('customer_phone')
        customer_gender = request.form.get('customer_gender')
        customer_address = request.form.get('customer_address')
        customer_city = request.form.get('customer_city')
        customer_state = request.form.get('customer_state')
        customer_region = request.form.get('customer_region')
        customer_type = request.form.getlist('customer_type')

        if len(customer_type) > 1:
            customer_type = ",".join(customer_type)
        else:
            customer_type = customer_type[0]

        # Update existing Customer
        _ = Customer.query.filter(Customer.id == customer_id).update({'customer':customer_name, 'email':customer_email, 'phone':customer_phone, 'gender':customer_gender, 'address':customer_address, 'city':customer_city, 'state':customer_state, 'region':customer_region, 'customer_type':customer_type})
        
        db.session.commit()

        flash(customer_name_initial+' updated successfully', 'success')
        return redirect(url_for('sales.sales_customers'))


    # FETCH ALL CUSTOMERS
    page = request.args.get('page', 1, type=int)
    all_customers = Customer.query.order_by(Customer.id.desc()).paginate(page, current_app.config['MULTIPLE_DATA_PER_PAGE'], error_out=True)


    # Handle Customer Type Search Query
    if request.method == 'POST' and request.form.get('check') == 'gobutton':
        customer_type = request.form.get('customer_type')

        page = 1
        if customer_type == 'Crop':
            crop_list = ['Crop', 'Pineapple', 'Palms', 'Cassava']
            all_customers = Customer.query.filter(db.or_(Customer.customer_type.like('%'+crop_list[0]+'%'), Customer.customer_type.like('%'+crop_list[1]+'%'), Customer.customer_type.like('%'+crop_list[2]+'%'), Customer.customer_type.like('%'+crop_list[3]+'%') )).order_by(Customer.id.desc()).paginate(page, current_app.config['MULTIPLE_DATA_PER_PAGE'], error_out=True)

            flash(customer_type+' customers selected', 'success')
        elif customer_type != 'Crop':
            all_customers = Customer.query.filter(Customer.customer_type.like('%'+customer_type+'%')).order_by(Customer.id.desc()).paginate(page, current_app.config['MULTIPLE_DATA_PER_PAGE'], error_out=True)

            flash(customer_type+' customers selected', 'success')
        else:
            flash('Please make a selection', 'warning')


    # State Search Query
    if request.method == 'POST' and request.form.get('check') == 'search_state':
        search_state = request.form.get('state')

        if search_state:
            all_customers = Customer.query.filter(Customer.state.like('%'+search_state+'%')).order_by(Customer.id.desc()).paginate(page, current_app.config['MULTIPLE_DATA_PER_PAGE'], error_out=True)

            flash(search_state+' searched successfully', 'success')
        else:
            flash('Please make a selection', 'warning')


    
    # Region Search Query
    if request.method == 'POST' and request.form.get('check') == 'search_region':
        search_region = request.form.get('region')

        if search_region:
            all_customers = Customer.query.filter(Customer.region.like('%'+search_region+'%')).order_by(Customer.id.desc()).paginate(page, current_app.config['MULTIPLE_DATA_PER_PAGE'], error_out=True)

            flash(search_region+' searched successfully', 'success')
        else:
            flash('Please make a selection', 'warning')


    # Fetch all pending notifications
    all_activities = Activitylog.query.filter(Activitylog.status == 'pending').\
                                order_by(Activitylog.id.desc()).limit(3).all()

    # Fetch all User specific notifications
    user_activities = Activitylog.query.filter(Activitylog.user_id == current_user.id, Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

    # Current User Photo
    image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)

    return render_template('/salesmgt/sales_customers.html', title="Sales Customers", ficon="users", date=datetime.now(), form=form, all_customers=all_customers, image_file=image_file, all_activities=all_activities, user_activities=user_activities)


# Rouute to process customer rename form population
@sales.route('/edit_customer', methods=['POST'])
def edit_customer():
    customer_id = request.get_data('id').decode('utf-8')
    customer_id = int(customer_id)
    customer_row = Customer.query.filter(Customer.id == customer_id).first()

    customer_list = []
    customer_dict = {}

    customer_dict['id'] = customer_row.id
    customer_dict['name'] = wordSeparator(customer_row.customer)
    customer_dict['address'] = customer_row.address
    customer_dict['email'] = customer_row.email
    customer_dict['phone'] = customer_row.phone
    customer_dict['gender'] = customer_row.gender
    customer_dict['city'] = customer_row.city
    customer_dict['state'] = customer_row.state
    customer_dict['region'] = customer_row.region
    customer_dict['type'] = customer_row.customer_type.split(",")
    customer_list.append(customer_dict)

    return jsonify({'customer_info': customer_list})


# Route for Egg sales
@sales.route('/salesmgt/egg_sales', methods=['POST', 'GET'])
@login_required
def egg_sales():
    # Insert Eggsizes to salescost db
    insert_eggsize()
    # Form
    form = salesForm()


    # Handle updating of Eggcost details
    if request.method == 'POST' and request.form.get('check') == 'update_eggcost':
        # Get eggcost details
        pullet_egg = request.form.get('Pullet-egg')
        small_egg = request.form.get('Small-egg')
        medium_egg = request.form.get('Medium-egg')
        big_egg = request.form.get('Big-egg')
        adult_egg = request.form.get('Adult-egg')
        beij_egg = request.form.get('BEIJ-egg')

        eggsize_cost = {}
        eggsize_cost['Pullet'] = pullet_egg
        eggsize_cost['Small'] = small_egg
        eggsize_cost['Medium'] = medium_egg
        eggsize_cost['Big'] = big_egg
        eggsize_cost['Adult'] = adult_egg
        eggsize_cost['BEIJ'] = beij_egg

        # Update the Egg Cost db
        for size, cost in eggsize_cost.items():
            _ = Salescost.query.filter(Salescost.category == 'Egg', Salescost.sales_type == size).update({'cost': cost})

        db.session.commit()

        flash('Eggcost updated successfully','success')
        return redirect(url_for('sales.egg_sales'))


    # Handle Processing of new egg sales
    if request.method == 'POST' and request.form.get('check') == 'new_egg_sales':
       

        flash('Egg sales submitted successfully','success')
        return redirect(url_for('sales.egg_sales'))


    # Handle Processing of Egg sale updates
    if request.method == 'POST' and request.form.get('check') == 'update_egg_sales':
        # Get Egg Sales details
       
        flash('Egg sales updated successfully', 'success')
        return redirect(url_for('sales.egg_sales'))


    # Handle Processing of Egg sale remark updates
    if request.method == 'POST' and request.form.get('check') == 'remark-update':
        # Get Egg Sales remark details
       
        flash('Egg sales remark updated successfully', 'success')
        return redirect(url_for('sales.egg_sales'))


     # Handle Processing of Egg sale cost updates
    if request.method == 'POST' and request.form.get('check') == 'cost-update':
        # Get Egg Sales cost details
        
        flash('Egg sales cost details updated successfully', 'success')
        return redirect(url_for('sales.egg_sales'))


    # Handle Processing of Egg sale payment updates
    if request.method == 'POST' and request.form.get('check') == 'payment-details':
        # Get Egg sales payment details
       
        flash('Egg sales payment details updated successfully', 'success')
        return redirect(url_for('sales.egg_sales'))


    # Filter month  and year form population
    egg_sale_data = Salesone.query.all()
    eggsale_month = []
    eggsale_year = []

    for sale in egg_sale_data:
        egg_month = sale.date.strftime('%m')
        egg_year = sale.date.strftime('%Y')

        if egg_month in eggsale_month:
            pass
        else:
            eggsale_month.append(egg_month)

        if egg_year in eggsale_year:
            pass
        else:
            eggsale_year.append(egg_year)


    # Fetch all Egg Customers
    egg = 'Egg'
    egg_customers = Customer.query.filter(Customer.customer_type.like('%'+egg+'%')).all()


    # Fetch all pens
    all_pens = Pen.query.all()


    # Fetch all Eggcost Values
    eggcost = Salescost.query.filter(Salescost.category == 'Egg').all()


    # Fetch all Egg sales
    month = date.today().strftime('%m')
    year = date.today().strftime('%Y')


    month_query = request.args.get('month', month)
    year_query = request.args.get('year', year)

    page = request.args.get('page', 1, type=int)

    eggsales_list = Salesone.query.filter(db.extract('month', Salesone.date)==month_query).\
                    filter(db.extract('year', Salesone.date)==year_query).\
                        order_by(Salesone.id.desc()).paginate(page, current_app.config['MULTIPLE_DATA_PER_PAGE'], error_out=True)  


    # Handle Month and Year Filter
    if request.method == 'POST' and request.form.get('check') == 'gobutton':
        month_select = request.form.get('month')
        year_select = request.form.get('year')

        if month_select and year_select:
            eggsales_list = Salesone.query.filter(db.extract('month', Salesone.date)==month_select).\
                    filter(db.extract('year', Salesone.date)==year_select).\
                        order_by(Salesone.id.desc()).paginate(page, current_app.config['MULTIPLE_DATA_PER_PAGE'], error_out=True)

            flash('Egg sales for '+numberMonth(month_select)+' '+year_select+' selected', 'success')
            return redirect(url_for('sales.egg_sales', month=month_select, year=year_select))
                        
        else:
            flash('Please make a selection', 'warning')


    # Handle Egg sales customer filter
    if request.method == 'POST' and request.form.get('check') == 'egg-customers':
        customer_select = int(request.form.get('customer-filter'))
        month_query = request.args.get('month', month)
        year_query = request.args.get('year', year)

        page = 1

        if customer_select:
            eggsales_list = Salesone.query.filter(db.extract('month', Salesone.date)==month_query).\
                    filter(db.extract('year', Salesone.date)==year_query).\
                        filter(Salesone.customer_id == customer_select).\
                            order_by(Salesone.id.desc()).paginate(page, current_app.config['MULTIPLE_DATA_PER_PAGE'], error_out=True)

            flash('Customer search was successful', 'success')
        else:
            flash('Please make a selection', 'warning')

   
    # Fetch all pending notifications
    all_activities = Activitylog.query.filter(Activitylog.status == 'pending').\
                                order_by(Activitylog.id.desc()).limit(3).all()

    # Fetch all User specific notifications
    user_activities = Activitylog.query.filter(Activitylog.user_id == current_user.id, Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

    # Current User Photo
    image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)

    return render_template('/salesmgt/egg_sales.html', title="Egg Sales", ficon="users", date=datetime.now(), form=form, egg_customers=egg_customers, eggsale_month=eggsale_month, eggsale_year=eggsale_year, eggsales_list=eggsales_list, eggcost=eggcost, all_pens=all_pens, image_file=image_file, all_activities=all_activities, user_activities=user_activities)



# Route for Bird sales
@sales.route('/salesmgt/bird_sales', methods=['POST', 'GET'])
@login_required
def bird_sales():
     # Insert birdtypes into salescost db
    insert_birdtype()
    # Forms
    form = salesForm()


     # Handle Update of Crop Cost Update
    if request.method == 'POST' and request.form.get('check') == 'update_birdcost':
        # Get Crop Cost Values

        poc = request.form.get('POC')
        pol = request.form.get('POL')
        spent_layer = request.form.get('Spent_Layer')
        broiler = request.form.get('Broiler')
        noiler = request.form.get('Noiler')
        cockerel = request.form.get('Cockerel')

        birddict = {}
        birddict['POC'] = poc
        birddict['POL'] = pol
        birddict['Spent_Layer'] = spent_layer
        birddict['Broiler'] = broiler
        birddict['Noiler'] = noiler
        birddict['Cockerel'] = cockerel

        # Loop through crop dict
        for birdtype, cost in birddict.items():
            _ = Salescost.query.filter(Salescost.category=='Bird', Salescost.sales_type == birdtype).update({'cost': cost})

        db.session.commit()

        flash('Bird cost updated successfully', 'success')
        return redirect(url_for('sales.bird_sales'))



    # Fetch all Bird types
    egg_producing = Salescost.query.filter(Salescost.category == 'Bird').limit(3).all()
    meat_producing = Salescost.query.filter(Salescost.category == 'Bird').offset(3).all()
    all_birds = Salescost.query.filter(Salescost.category == 'Bird').all()

   
    # Fetch all pending notifications
    all_activities = Activitylog.query.filter(Activitylog.status == 'pending').\
                                order_by(Activitylog.id.desc()).limit(3).all()

    # Fetch all User specific notifications
    user_activities = Activitylog.query.filter(Activitylog.user_id == current_user.id, Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

    # Current User Photo
    image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)

    return render_template('/salesmgt/bird_sales.html', title="Bird Sales", ficon="users", date=datetime.now(), form=form, egg_producing=egg_producing, meat_producing=meat_producing, all_birds=all_birds, image_file=image_file, all_activities=all_activities, user_activities=user_activities)


# Route for Egg sales
@sales.route('/salesmgt/crop_sales', methods=['POST', 'GET'])
@login_required
def crop_sales():
    # Insert croptypes into salescost db
    insert_croptype()
    # Forms
    form = salesForm()

    # Handle Update of Crop Cost Update
    if request.method == 'POST' and request.form.get('check') == 'update_cropcost':
        # Get Crop Cost Values

        cassava = request.form.get('Cassava')
        palms = request.form.get('Palms')
        ugwu = request.form.get('Ugwu')
        typeA = request.form.get('TypeA')
        typeB = request.form.get('TypeB')
        typeC = request.form.get('TypeC')
        typeD = request.form.get('TypeD')
        typeE = request.form.get('TypeE')
        typeF = request.form.get('TypeF')
        suckers = request.form.get('Suckers')

        cropdict = {}
        cropdict['Cassava'] = cassava
        cropdict['Palms'] = palms
        cropdict['Ugwu'] = ugwu
        cropdict['TypeA'] = typeA
        cropdict['TypeB'] = typeB
        cropdict['TypeC'] = typeC
        cropdict['TypeD'] = typeD
        cropdict['TypeE'] = typeE
        cropdict['TypeF'] = typeF
        cropdict['Suckers'] = suckers

        # Loop through crop dict
        for croptype, cost in cropdict.items():
            _ = Salescost.query.filter(Salescost.category=='Crop', Salescost.sales_type == croptype).update({'cost': cost})

        db.session.commit()

        flash('Crop cost updated successfully', 'success')
        return redirect(url_for('sales.crop_sales'))


    # Fetch all croptypes
    croptypes = Salescost.query.filter(Salescost.category=='Crop').limit(3).all()
    pineapple_types = Salescost.query.filter(Salescost.category=='Crop').offset(3).all()


    # Fetch all pending notifications
    all_activities = Activitylog.query.filter(Activitylog.status == 'pending').\
                                order_by(Activitylog.id.desc()).limit(3).all()

    # Fetch all User specific notifications
    user_activities = Activitylog.query.filter(Activitylog.user_id == current_user.id, Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

    # Current User Photo
    image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)

    return render_template('/salesmgt/crop_sales.html', title="Crop Sales", ficon="users", date=datetime.now(), form=form, croptypes=croptypes, pineapple_types=pineapple_types, image_file=image_file, all_activities=all_activities, user_activities=user_activities)


# Route for Egg sales
@sales.route('/salesmgt/other_sales/<sales_type>', methods=['POST', 'GET'])
@login_required
def other_sales(sales_type):
    form = salesForm()
    # Get Path details
    path = request.path.split('/')[-1]
   
    # Fetch all pending notifications
    all_activities = Activitylog.query.filter(Activitylog.status == 'pending').\
                                order_by(Activitylog.id.desc()).limit(3).all()

    # Fetch all User specific notifications
    user_activities = Activitylog.query.filter(Activitylog.user_id == current_user.id, Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

    # Current User Photo
    image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)


    #######################
    # DRESSED BIRDS
    #######################
    if sales_type == 'dressed_bird':
        # Insert Dressed Bird details into SalesCost DB
        insert_dressed_birdtype()

        # Handle Update of dressed bird Cost
        if request.method == 'POST' and request.form.get('check') == 'update_dressed_birdcost':
            # Get dressed bird cost values
            cock = request.form.get('Cock')
            layer = request.form.get('Layer')
            broiler = request.form.get('Broiler')
            
            dressed_bird_dict = {}
            dressed_bird_dict['Cock'] = cock
            dressed_bird_dict['Layer'] = layer
            dressed_bird_dict['Broiler'] = broiler

            for dressed_bird, cost in dressed_bird_dict.items():
                _ = Salescost.query.filter(Salescost.category == 'Dressed_bird', Salescost.sales_type == dressed_bird).update({'cost': cost})

            db.session.commit()
            
            flash('Dressed bird cost updated successfully', 'success')
            return redirect(url_for('sales.other_sales', sales_type='dressed_bird'))


        # Fetch all dressed bird
        dressed_birds = Salescost.query.filter(Salescost.category == 'Dressed_bird').all()

        return render_template('/salesmgt/dressed_birds.html', title="Dressed Bird Sales", ficon="users", date=datetime.now(), form=form, path=path, dressed_birds=dressed_birds, image_file=image_file, all_activities=all_activities, user_activities=user_activities)


     #######################
    # CRACKS
    #######################
    elif sales_type == 'cracks':

        return render_template('/salesmgt/cracks.html', title="Crack Sales", ficon="users", date=datetime.now(), form=form, path=path, image_file=image_file, all_activities=all_activities, user_activities=user_activities)


     #######################
    # MANURE
    #######################
    elif sales_type == 'manure':
        # Insert Manure Type to Salescost DB
        insert_manure_type()

        # Handle Update of dressed bird Cost
        if request.method == 'POST' and request.form.get('check') == 'update_manurecost':
            # Get dressed bird cost values
            black = request.form.get('Black')
            white = request.form.get('White')
            
            manure_dict = {}
            manure_dict['Black'] = black
            manure_dict['White'] = white

            for manure_type, cost in manure_dict.items():
                _ = Salescost.query.filter(Salescost.category == 'Manure', Salescost.sales_type == manure_type).update({'cost': cost})

            db.session.commit()
            
            flash('Manure cost updated successfully', 'success')
            return redirect(url_for('sales.other_sales', sales_type='manure'))

        # Fetch all manure type
        manure_type = Salescost.query.filter(Salescost.category == 'Manure').all()
    
        return render_template('/salesmgt/manure.html', title="Manure Sales", ficon="users", date=datetime.now(), form=form, path=path, manure_type=manure_type, image_file=image_file, all_activities=all_activities, user_activities=user_activities)


     #######################
    # SACKS
    #######################
    elif sales_type == 'sacks':
        # Insert Sack Type to Salescost DB
        insert_sack_type()

        # Handle Update of dressed bird Cost
        if request.method == 'POST' and request.form.get('check') == 'update_sackcost':
            # Get dressed bird cost values
            big = request.form.get('Big')
            small = request.form.get('Small')
            
            sack_dict = {}
            sack_dict['Big'] = big
            sack_dict['Small'] = small

            for sack_type, cost in sack_dict.items():
                _ = Salescost.query.filter(Salescost.category == 'Sack', Salescost.sales_type == sack_type).update({'cost': cost})

            db.session.commit()
            
            flash('Sack cost updated successfully', 'success')
            return redirect(url_for('sales.other_sales', sales_type='sacks'))

        # Fetch all Sack type
        sack_type = Salescost.query.filter(Salescost.category == 'Sack').all()
    
        return render_template('/salesmgt/sacks.html', title="Sack Sales", ficon="users", date=datetime.now(), form=form, path=path, sack_type=sack_type, image_file=image_file, all_activities=all_activities, user_activities=user_activities)


     #######################
    # METAL_SCRAP
    #######################
    elif sales_type == 'metal_scrap':
    
        return render_template('/salesmgt/metal_scrap.html', title="Metal Scrap Sales", ficon="users", date=datetime.now(), form=form, path=path, image_file=image_file, all_activities=all_activities, user_activities=user_activities)

    else:
        pass