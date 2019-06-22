import os
from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, flash, request, redirect, url_for, jsonify, abort, current_app
from automate import db, Mail
from flask_mail import Message
from flask_login import login_required, current_user
from automate.stores.forms import storeForm, eggstoreForm
from automate.models import Activitylog, Feeditem, Feedstock, Feedtype, Vendor, Farmitem, Purchase, Production, Receivable, Formulation, Feedcost, Customer, Pen, Allocation, Eggsale, Eggstock
from automate.feedmill.utils import (update, wordTruncate, numberDecreament, numberDecimal, numberFormat, numberMonth, 
                                    color_sample, receivable_update, updateproduction, tonnesToBag, eggstock_update)

stores = Blueprint('stores', __name__)

# STORE PORTAL ROUTE
@stores.route('/storemgt/store_portal')
@login_required
def store_portal():
    image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)
    return render_template('storemgt/store_portal.html', title='Store Portal', image_file=image_file)


# STORE OVERVIEW ROUTE
@stores.route('/storemgt/store_overview', methods=['GET', 'POST'])
@login_required
def store_overview():
    # call update function
    update()
    # run update production
    updateproduction()
    # Receivable update
    receivable_update()
    # Eggstock Update
    eggstock_update()

    # Fetch Closing Stock of feed produced
    closing_production = Production.query.filter(Production.date == date.today()).all()
    if closing_production:
        prod_colors = color_sample(int(closing_production[-1].feedtype_id) + 1)
    else:
        prod_colors = 0


    # Fetch Closing Stock of feed item
    all_feedstock = Feedstock.query.filter(Feedstock.date == date.today()).all()
    if all_feedstock:
        stock_colors_qty = color_sample(int(all_feedstock[-1].feeditem_id) + 1)
        stock_colors_price = color_sample(int(all_feedstock[-1].feeditem_id) + 1)
    else:
        stock_colors_qty = 0
        stock_colors_price = 0

    
    # Fetch the available farm item
    all_farmitem = Receivable.query.filter(Receivable.date == date.today(), Receivable.c_qty !=0).all()
    if all_farmitem:
        farmitem_colors = color_sample(int(all_farmitem[-1].farmitem_id) + 1)
    else:
        farmitem_colors = 0


    # Fetch all pending notifications
    all_activities = Activitylog.query.filter(Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

    # Fetch all User specific notifications
    user_activities = Activitylog.query.filter(Activitylog.user_id == current_user.id, Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

    # Current user Image
    image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)

    return render_template('storemgt/store_overview.html', title='Store Overview', ficon="store", date=datetime.now(), closing_production=closing_production,
                           prod_colors=prod_colors, all_feedstock=all_feedstock, stock_colors_qty=stock_colors_qty, stock_colors_price=stock_colors_price, all_farmitem=all_farmitem,
                           farmitem_colors=farmitem_colors, image_file=image_file, all_activities=all_activities, user_activities=user_activities)


# STORE VENDORS ROUTE
@stores.route('/storemgt/store_vendors', methods=['GET', 'POST'])
@login_required
def store_vendors():
    # Update Receivable db
    receivable_update()

    # instantiate the store form
    form = storeForm()


    # Handle Processing of New Vendor
    if request.method == 'POST' and request.form.get('check') == 'add_vendor':
        vendor_name = request.form.get('vendor')
        vendor_name = vendor_name.title()

        # Check if vendor name exist in vendor db
        check_vendor_name = Vendor.query.filter(Vendor.vendor == vendor_name).first()
        if check_vendor_name:
            flash(vendor_name+' already exist in database, please rename', 'warning')
        else:
            new_vendor = Vendor(vendor = vendor_name)
            db.session.add(new_vendor)
            db.session.commit()

            flash(vendor_name+' added successfully', 'success')
            return redirect(url_for('stores.store_vendors'))


    # Handle processing of rename vendor form
    if request.method == 'POST' and request.form.get('check') == 'rename_vendor':
        vendor_id = request.form.get('vendorId')
        old_vendor_name = request.form.get('old_vendor_name')
        new_vendor_name = request.form.get('new_vendor_name')
        new_vendor_name = new_vendor_name.title()

        # Check if name exist in vendor db
        check_new_name = Vendor.query.filter(Vendor.vendor == new_vendor_name).first()
        if new_vendor_name == old_vendor_name:
            flash('New vendor name is the same as Old name', 'warning')
        elif check_new_name:
            flash(new_vendor_name+' already exist in database', 'warning')
        else:
            _ = Vendor.query.filter(Vendor.id == vendor_id).update({'vendor': new_vendor_name})
            db.session.commit()

            flash('Vendor renamed successfully', 'success')
            return redirect(url_for('stores.store_vendors'))


    # Handle Processing of delete Vendor Form
    if request.method == 'POST' and request.form.get('check') == 'delete_vendor':
        # Get vemdor id
        vendor_delete_id = request.form.get('vendor_delete_id')

        # Get vendor id row
        vendor_data = Vendor.query.filter(Vendor.id == vendor_delete_id).first()

        # Get user info and activities
        user = current_user.id
        user_activity = 'Delete Request for Vendor - '+vendor_data.vendor+' Received'
        request_query = 'Vendor of id '+vendor_delete_id

        # Add Data to the Activitylog database
        new_activity = Activitylog(user_id = user, activity = user_activity, request = request_query)
        db.session.add(new_activity)
        db.session.commit()

        flash('Delete Request for '+ vendor_data.vendor +' Sent', 'success')
        return redirect(url_for('stores.store_vendors'))

        
    # Handle processing of New Farm item
    if request.method == 'POST' and request.form.get('check') == 'add_farmitem':
        farmitem_name = request.form.get('farmitem')
        farmitem_name = farmitem_name.capitalize()

        # Check if Farmitem exists in the farmitem db
        check_farmitem =  Farmitem.query.filter(Farmitem.item == farmitem_name).first()
        if check_farmitem:
            flash(farmitem_name+' already exists in database, please rename', 'warning')
        else:
            new_farmitem = Farmitem(item = farmitem_name)
            db.session.add(new_farmitem)
            db.session.commit()

            # Update the receivable db
            # Check if the new farmitem exists in Receivable db
            check_receivable = Receivable.query.filter(Receivable.date == date.today(), Receivable.farmitem_id == new_farmitem.id).first()
            if check_receivable:
                pass
            else:
                new_receivable_item = Receivable(farmitem_id=new_farmitem.id)
                db.session.add(new_receivable_item)
                db.session.commit() 

            flash(farmitem_name+' added successfully', 'success')
            return redirect(url_for('stores.store_vendors'))


    # Handle processing for rename farmitem form
    if request.method == 'POST' and request.form.get('check') == 'rename_farmitem':
        farmitem_id = request.form.get('farmitemId')
        old_farmitem_name = request.form.get('old_farmitem_name')
        new_farmitem_name = request.form.get('new_farmitem_name')
        new_farmitem_name = new_farmitem_name.capitalize()

        # Check if farmitem exist in farmitem db
        check_farmitem_name = Farmitem.query.filter(Farmitem.item == new_farmitem_name).first()
        if new_farmitem_name == old_farmitem_name:
            flash('New farm item name is the same as the Old name', 'warning')
        elif check_farmitem_name:
            flash(new_farmitem_name+' already exist in database', 'warning')
        else:
            _ = Farmitem.query.filter(Farmitem.id == farmitem_id).update({'item': new_farmitem_name})
            db.session.commit()

            flash('Farmitem renamed successfully', 'success')
            return redirect(url_for('stores.store_vendors'))


    # Handle Processing of delete farmitem Form
    if request.method == 'POST' and request.form.get('check') == 'delete_farmitem':
        # Get farmitem id
        farmitem_delete_id = request.form.get('farmitem_delete_id')

        # Get farmitem id row
        farmitem_data = Farmitem.query.filter(Farmitem.id == farmitem_delete_id).first()

        # Get user info and activities
        user = current_user.id
        user_activity = 'Delete Request for Farmitem - '+farmitem_data.item+' Received'
        request_query = 'Farmitem of id '+farmitem_delete_id

        # Add Data to the Activitylog database
        new_activity = Activitylog(user_id = user, activity = user_activity, request = request_query)
        db.session.add(new_activity)
        db.session.commit()

        flash('Delete Request for '+ farmitem_data.item +' Sent', 'success')
        return redirect(url_for('stores.store_vendors'))


    # Fetch all vendors list in vendor db
    vendor_list = Vendor.query.all()
    if vendor_list:
        vendor_color = color_sample(int(vendor_list[-1].id) + 1)
    else:
        vendor_color = 0


    # Fetch all farm items in farm item db
    farmitem_list = Farmitem.query.all()
    if farmitem_list:
        farmitem_color = color_sample(int(farmitem_list[-1].id) + 1)
    else:
        farmitem_color = 0


    # Fetch all pending notifications
    all_activities = Activitylog.query.filter(Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

    # Fetch all User specific notifications
    user_activities = Activitylog.query.filter(Activitylog.user_id == current_user.id, Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()


    # Current User Image
    image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)

    return render_template('storemgt/store_vendors.html', title='Store Vendors', ficon="users", date=datetime.now(), 
                        image_file=image_file, form=form, vendor_list=vendor_list, vendor_color=vendor_color, farmitem_list=farmitem_list, farmitem_color=farmitem_color, 
                        all_activities=all_activities, user_activities=user_activities)


# Route to populate vendor rename form
@stores.route('/rename_vendor', methods=['POST'])
def rename_vendor():
    vendor_id = request.get_data('id').decode('utf-8')
    vendor_id = int(vendor_id)

    vendor_row = Vendor.query.filter(Vendor.id == vendor_id).first()
    vendorList = []
    vendorDict = {}

    vendorDict['id'] = vendor_row.id
    vendorDict['vendor'] = vendor_row.vendor
    vendorList.append(vendorDict)

    return jsonify({'vendor_data': vendorList})


# Route to populate Farmitem rename form
@stores.route('/rename_farmitem', methods=['POST'])
def rename_farmitem():
    farmitem_id = request.get_data('id').decode('utf-8')
    farmitem_id = int(farmitem_id)

    farmitem_row = Farmitem.query.filter(Farmitem.id == farmitem_id).first()
    farmitemList = []
    farmitemDict = {}

    farmitemDict['id'] = farmitem_row.id
    farmitemDict['farmitem'] = farmitem_row.item
    farmitemList.append(farmitemDict)

    return jsonify({'farmitem_data': farmitemList})


# STORE PURCHASES ROUTE
@stores.route('/storemgt/store_purchases/<purchase>', methods=['GET', 'POST'])
@login_required
def store_purchases(purchase):
    # Update Receivable db
    receivable_update() 

    # Feed Purcahase
    if purchase == 'feed_purchase':
        # instantiate the store form
        form = storeForm()

        
        # Handle New Feed Purchase form processing
        if request.method == 'POST' and request.form.get('check') == 'add_feed_purchase':
            # get feed purchase data
            f_item_id = request.form.get('f_item_id')
            f_vendor_id = request.form.get('f_vendor_id')
            f_item_quantity = request.form.get('f_item_quantity')
            f_item_price = request.form.get('f_item_price')
            f_item_price = float(f_item_price)

            # Add to Purcahase db
            new_feed_purchase = Purchase(feeditem_id=f_item_id, vendor_id=f_vendor_id, v_qty=f_item_quantity, v_price=f_item_price)
            db.session.add(new_feed_purchase)
            db.session.commit()

            # Update Feedstock db with purchased feed item
            v_qtylist = []
            v_pricelist = []
            v_qtysum = 0
            v_pricesum = 0

            all_qty = Purchase.query.filter(Purchase.date == date.today(), Purchase.feeditem_id == f_item_id).all()
            for qty in all_qty:
                v_qtylist.append(qty.v_qty)
                v_pricelist.append(qty.v_price)

            for sum in v_qtylist:
                v_qtysum = v_qtysum + sum

            for avg in v_pricelist:
                v_pricesum = v_pricesum + avg

            vendor_avg_price = v_pricesum / (int(len(v_pricelist)))
            
            stock_row = Feedstock.query.filter(Feedstock.date == date.today(), Feedstock.feeditem_id == f_item_id).first()
            stock_row.v_qty = v_qtysum
            stock_row.v_price = vendor_avg_price
            db.session.commit()

            stock_row.c_qty = (stock_row.o_qty + v_qtysum) - (stock_row.p_qty)
            db.session.commit()

            # Calcuate the closing price
            total_stock = (stock_row.o_qty * stock_row.o_price)
            total_purchase = (v_qtysum * f_item_price)
            total_qty = (stock_row.o_qty + v_qtysum)

            closing_price = (total_stock + total_purchase) / (total_qty)
            stock_row.c_price = round(closing_price, 2)
            db.session.commit()

            v_qtylist.clear()
            v_qtysum = 0

            flash('Feed purchase added successfully', 'success')
            return redirect(url_for('stores.store_purchases', purchase='feed_purchase'))

        
        # ****************************************
        # Handle Update of feed purchase Processing
        if request.method == 'POST' and request.form.get('check') == 'update_feed':
            # Get Updated info
            row_id = request.form.get('row_id')
            vendor_id = request.form.get('vendor_update_id')
            feed_id = request.form.get('feeditem_update_id')
            updated_qty = request.form.get('update_qty')
            updated_price = request.form.get('update_price')

            vendor_id = int(vendor_id)
            feed_id = int(feed_id)
            updated_qty = float(updated_qty)
            updated_price = float(updated_price)

            # Update the row of purchased feeditem roe id
            purchase_row = Purchase.query.filter(Purchase.id == row_id).first()
            purchase_row.feeditem_id = feed_id
            purchase_row.vendor_id = vendor_id
            purchase_row.v_qty = updated_qty
            purchase_row.v_price = updated_price
            db.session.commit()

            # Loop through all purchase item with the updated date
            qty_list = []
            price_list = []
            sumTotal = 0
            priceTotal = 0

            feeditems = Feeditem.query.all()
            for item in feeditems:
                feeditems_purchased = Purchase.query.filter(Purchase.date == purchase_row.date, Purchase.feeditem_id == item.id).all()
                if feeditems_purchased:
                    for feeditem in feeditems_purchased:
                        qty_list.append(feeditem.v_qty)
                        price_list.append(feeditem.v_price)
                     
                    for sum in qty_list:
                        sumTotal = sumTotal + sum

                    for avg in price_list:
                        priceTotal = priceTotal + avg

                    item_price_avg = priceTotal / int(len(price_list))
                    
                    feedstock_row = Feedstock.query.filter(Feedstock.date == purchase_row.date, Feedstock.feeditem_id == item.id).first()
                    feedstock_row.v_qty = sumTotal
                    feedstock_row.v_price = item_price_avg
                    db.session.commit()

                    feedstock_row.c_qty = (feedstock_row.o_qty + sumTotal) - (feedstock_row.p_qty)
                    db.session.commit()

                    # Calcuate the closing price
                    total_update_stock = (feedstock_row.o_qty * feedstock_row.o_price)
                    total_update_purchase = (sumTotal * item_price_avg)
                    total_update_qty = (feedstock_row.o_qty + sumTotal)

                    closing_update_price = (total_update_stock + total_update_purchase) / (total_update_qty)
                    feedstock_row.c_price = round(closing_update_price, 2)
                    db.session.commit()

                    qty_list.clear()
                    sumTotal = 0

                    # Update the Feedstock down from the date updated
                    next_stocks = Feedstock.query.filter(Feedstock.date > purchase_row.date, Feedstock.feeditem_id == item.id).all()
                    if next_stocks:
                        for stock in next_stocks:
                            prev_stocks = Feedstock.query.filter(Feedstock.date == stock.date - timedelta(days=1), Feedstock.feeditem_id == item.id).first()

                            # Update the opening quantity and opening price
                            stock.o_qty = prev_stocks.c_qty
                            stock.o_price = prev_stocks.c_price
                            db.session.commit()

                            # Calculate the new c_qty
                            stock.c_qty = (stock.o_qty + stock.v_qty) - (stock.p_qty)
                            db.session.commit()

                            # Calculate the new c_price
                            opening_stockTotal = (stock.o_qty * stock.o_price)
                            vendor_stockTotal = (stock.v_qty * stock.v_price)
                            total_stockQuantity = (stock.o_qty + stock.v_qty)

                            cls_stockPrice = (opening_stockTotal + vendor_stockTotal) / (total_stockQuantity)
                            stock.c_price = round(cls_stockPrice, 2)
                            db.session.commit()

                    else:
                        pass

                    # Update the opening price of the updated item for all next date on the formulation table
                    # check if formulation table exists
                    checkFormulation = Feedtype.query.all()
                    if checkFormulation:
                        update_stockFormulations = Formulation.query.filter(Formulation.feeditem_id == item.id, Formulation.date > purchase_row.date).all()
                        for stockForm in update_stockFormulations:
                            stock_price = Feedstock.query.filter(Feedstock.feeditem_id == item.id, Feedstock.date == stockForm.date).first()
                            stockForm.o_price = stock_price.o_price
                            db.session.commit()

                            stockForm.total = (stockForm.formula * stockForm.o_price)
                            db.session.commit()

                        # Update Cost table
                        # Fetch Overhead FeedCost
                        filepath = os.path.join(current_app.root_path, 'overhead.txt')
                        with open(filepath, 'r') as reader:
                            overhead_cost = int(reader.read())
                        
                        # Set Feedlist Array to hold feed total
                        c_totallist = []
                        c_sum = 0

                        costRow = Feedcost.query.filter(Feedcost.date > purchase_row.date).all()
                        for cost in costRow:
                            formulations = Formulation.query.filter(Formulation.date == cost.date, Formulation.feedtype_id == cost.feedtype_id).all()
                            for form in formulations:
                                c_totallist.append(form.total)

                            for num in c_totallist:
                                c_sum = c_sum + num
                                    
                            totalPrice = (float(c_sum) + overhead_cost) / 20
                            cost.price = totalPrice

                            db.session.commit()

                            c_totallist.clear()
                            c_sum = 0
                    else:
                        pass

                else:
                    pass
                    

            flash('Feeditem purchased updated, successfully', 'success')    
            return redirect(url_for('stores.store_purchases', purchase='feed_purchase'))


        # Fetch Vendor list
        vendors_list = Vendor.query.all()

        # Fetch Feed Items
        feeditem_list = Feeditem.query.all()


        # Fetch Purchased Feed item
        year = date.today().strftime('%Y')
        month = date.today().strftime('%m')

        
        month_query = request.args.get('month', month)
        year_query = request.args.get('year', year)

        page = request.args.get('page', 1, type=int)

        feeditem_purchased = Purchase.query.filter(db.extract('year', Purchase.date)==year_query).\
                                filter(db.extract('month', Purchase.date)==month_query).\
                                    filter(Purchase.farmitem_id == None).order_by(Purchase.id.desc()).paginate(page, current_app.config['SINGLE_DATA_PER_PAGE'], error_out=True)

        
        # Feed item purchase  filter form population
        feed_purchase_dates = Purchase.query.filter(Purchase.farmitem_id == None).all()
        feed_purchase_month = []
        feed_purchase_year = []

        for data in feed_purchase_dates:
            f_month = data.date.strftime('%m')
            f_year = data.date.strftime('%Y')

            if f_month in feed_purchase_month:
                pass
            else:
                feed_purchase_month.append(f_month)

            if f_year in feed_purchase_year:
                pass
            else:
                feed_purchase_year.append(f_year)


        # HANDLE MONTH AND DATE FILTERS
        if request.method == 'POST' and request.form.get('check') == 'gobutton':
            year_select = request.form.get('year')
            month_select = request.form.get('month')

            if year_select and month_select:
                feeditem_purchased = Purchase.query.filter(db.extract('year', Purchase.date)==year_select).\
                            filter(db.extract('month', Purchase.date)==month_select).\
                                filter(Purchase.farmitem_id == None).order_by(Purchase.id.desc()).paginate(page, current_app.config['SINGLE_DATA_PER_PAGE'], error_out=True)

                flash('Feeditems purchased for '+numberMonth(month_select)+' '+year_select+' Selected', 'success')
                return redirect(url_for('stores.store_purchases', purchase='feed_purchase', month=month_select, year=year_select))

            else:
                flash('Please make a selection', 'warning')

        
        # Handle Vendor Search Filters
        if request.method == 'POST' and request.form.get('check') == 'vendor_search':
            month_query = request.args.get('month', month)
            year_query = request.args.get('year', year)
            vendor_query = request.form.get('vendor_select')
            vendor_query = int(vendor_query)

            page = 1

            if vendor_query:
                feeditem_purchased = Purchase.query.filter(db.extract('year', Purchase.date)==year_query).\
                                filter(db.extract('month', Purchase.date)==month_query).\
                                    filter(Purchase.vendor_id == vendor_query).\
                                        filter(Purchase.farmitem_id == None).order_by(Purchase.id.desc()).paginate(page, current_app.config['SINGLE_DATA_PER_PAGE'], error_out=True)
                
                flash('Vendor search was successful', 'success')
            else:
                flash('Please make a selection', 'warning') 

            

        
        # Handle Feeditem Search Filter
        if request.method == 'POST' and request.form.get('check') == 'feeditem_search':
            month_query = request.args.get('month', month)
            year_query = request.args.get('year', year)
            feeditem_query = request.form.get('feeditem_select')
            feeditem_query = int(feeditem_query)

            page = 1

            if feeditem_query:
                feeditem_purchased = Purchase.query.filter(db.extract('year', Purchase.date)==year_query).\
                                filter(db.extract('month', Purchase.date)==month_query).\
                                    filter(Purchase.feeditem_id == feeditem_query).order_by(Purchase.id.desc()).paginate(page, current_app.config['SINGLE_DATA_PER_PAGE'], error_out=True)
                
                flash('Feeditem search was successful', 'success')
            else:
                flash('Please make a selection', 'warning') 

            
        # Fetch all pending notifications
        all_activities = Activitylog.query.filter(Activitylog.status == 'pending').\
                                order_by(Activitylog.id.desc()).limit(3).all()

        # Fetch all User specific notifications
        user_activities = Activitylog.query.filter(Activitylog.user_id == current_user.id, Activitylog.status == 'pending').\
                                order_by(Activitylog.id.desc()).limit(3).all()


        # Current User Image
        image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)

        return render_template('storemgt/store_feedpurchases.html', title='Store Feed Purchases', ficon="store", 
                        date=datetime.now(), form=form, image_file=image_file, vendors_list=vendors_list, feeditem_list=feeditem_list, feeditem_purchased=feeditem_purchased,
                        feed_purchase_month=feed_purchase_month, feed_purchase_year=feed_purchase_year, all_activities=all_activities, user_activities=user_activities)



    # *******************
    # Non Feed Purcahase
    # *******************
    elif purchase == 'non_feed_purchase':
        # instantiate the store form
        form = storeForm()


        # Handle New non-feed item purchased form processing
        if request.method == 'POST' and request.form.get('check') == 'add_farmitem_purchase':
            # Get farm item purchased info
            nf_farmitem_id = request.form.get('nf_farmitem_id')
            nf_vendor_id = request.form.get('nf_vendor_id')
            nf_farmitem_qty = request.form.get('nf_farmitem_qty')
            nf_farmitem_price = request.form.get('nf_farmitem_price')
            nf_farmitem_qty = float(nf_farmitem_qty)
            nf_farmitem_price = float(nf_farmitem_price)

            non_feed_purchase = Purchase(farmitem_id=nf_farmitem_id, vendor_id=nf_vendor_id, v_qty=nf_farmitem_qty, v_price=nf_farmitem_price)
            db.session.add(non_feed_purchase)
            db.session.commit()

            # Update receivable db with new purchased farm item
            nf_qtylist = []
            nf_sum = 0

            all_nonfeed = Purchase.query.filter(Purchase.date == date.today(), Purchase.farmitem_id == nf_farmitem_id).all()
            for nonfeed in all_nonfeed:
                nf_qtylist.append(nonfeed.v_qty)

            for sum in nf_qtylist:
                nf_sum = nf_sum + sum

            receivable_row = Receivable.query.filter(Receivable.date == date.today(), Receivable.farmitem_id == nf_farmitem_id).first()
            receivable_row.v_qty = nf_sum
            receivable_row.v_price = nf_farmitem_price
            db.session.commit()

            receivable_row.c_qty = (receivable_row.o_qty + nf_sum) - (receivable_row.issued_qty)
            db.session.commit()

            flash('Farm Item added succsessfully', 'success')
            return redirect(url_for('stores.store_purchases', purchase='non_feed_purchase'))


        # Handle update form for farmitem purchases
        if request.method == 'POST' and request.form.get('check') == 'update_farmitem':
            row_id = request.form.get('farm_id')
            vendor_id = request.form.get('vendor_update_id')
            farmitem_id = request.form.get('farmitem_update_id')
            nf_qty = request.form.get('nf_update_qty')
            nf_price = request.form.get('nf_update_price')

            vendor_id = int(vendor_id)
            farmitem_id = int(farmitem_id)
            nf_qty = float(nf_qty)
            nf_price = float(nf_price)
        
            nf_purchase_row = Purchase.query.filter(Purchase.id == row_id).first()
            nf_purchase_row.farmitem_id = farmitem_id
            nf_purchase_row.vendor_id = vendor_id
            nf_purchase_row.v_qty = nf_qty
            nf_purchase_row.v_price = nf_price
            db.session.commit()

            # Update the receivable db for that updated date
            updateList = []
            updateSum = 0

            farmitems = Farmitem.query.all()
            for item in farmitems:
                nf_row = Purchase.query.filter(Purchase.date == nf_purchase_row.date, Purchase.farmitem_id == item.id).all()
                if nf_row:
                    for row in nf_row:
                        updateList.append(row.v_qty)

                    updatePrice = nf_row[-1].v_price
                    for sum in updateList:
                        updateSum = updateSum + sum

                    receivable_data = Receivable.query.filter(Receivable.date == nf_purchase_row.date, Receivable.farmitem_id == item.id).first()
                    receivable_data.v_qty = updateSum
                    receivable_data.v_price = updatePrice
                    db.session.commit()

                    receivable_data.c_qty = (receivable_data.o_qty + updateSum) - (receivable_data.issued_qty)
                    db.session.commit()
                
                    updateList.clear()
                    updateSum = 0

                    # Update receivable db datas after the updated date
                    next_receivables = Receivable.query.filter(Receivable.date > nf_purchase_row.date, Receivable.farmitem_id == item.id).all()
                    if next_receivables:
                        for next_item in next_receivables:
                            prev_receivable = Receivable.query.filter(Receivable.date == next_item.date - timedelta(days=1), Receivable.farmitem_id == item.id).first()

                            # Update the opening quantity and vendor price
                            next_item.o_qty = prev_receivable.c_qty
                            next_item.v_price = prev_receivable.v_price
                            db.session.commit()

                            # Update the closing quantity
                            next_item.c_qty = (next_item.o_qty + next_item.v_qty) - (next_item.issued_qty)
                            db.session.commit()

                    else:
                        pass

                else:
                    pass

            flash('Farm Item purchased updated, succsessfully', 'success')
            return redirect(url_for('stores.store_purchases', purchase='non_feed_purchase'))            


        # Fetch Vendor list
        vendors_list = Vendor.query.all()

        # Fetch Farm Items
        farmitem_list = Farmitem.query.all()


        # Fetch Purchased Feed item
        year = date.today().strftime('%Y')
        month = date.today().strftime('%m')

        month_query = request.args.get('month', month)
        year_query = request.args.get('year', year)

        page = request.args.get('page', 1, type=int)

        farmitem_purchased = Purchase.query.filter(db.extract('year', Purchase.date)==year_query).\
                                filter(db.extract('month', Purchase.date)==month_query).\
                                    filter(Purchase.feeditem_id == None).order_by(Purchase.id.desc()).paginate(page, current_app.config['SINGLE_DATA_PER_PAGE'], error_out=True)


        # Feed item purchase  filter form population
        nf_purchase_dates = Purchase.query.filter(Purchase.feeditem_id == None).all()
        nf_purchase_month = []
        nf_purchase_year = []

        for data in nf_purchase_dates:
            nf_month = data.date.strftime('%m')
            nf_year = data.date.strftime('%Y')

            if nf_month in nf_purchase_month:
                pass
            else:
                nf_purchase_month.append(nf_month)

            if nf_year in nf_purchase_year:
                pass
            else:
                nf_purchase_year.append(nf_year)


        # HANDLE MONTH AND DATE FILTERS
        if request.method == 'POST' and request.form.get('check') == 'gobutton_nf':
            year_select = request.form.get('year')
            month_select = request.form.get('month')

            if year_select and month_select:
                farmitem_purchased = Purchase.query.filter(db.extract('year', Purchase.date)==year_select).\
                                filter(db.extract('month', Purchase.date)==month_select).\
                                    filter(Purchase.feeditem_id == None).order_by(Purchase.id.desc()).paginate(page, current_app.config['SINGLE_DATA_PER_PAGE'], error_out=True)

                flash('Farmitems Purchased for '+numberMonth(month_select)+' '+year_select+' Selected', 'success')
                return redirect(url_for('stores.store_purchases', purchase='non_feed_purchase', month=month_select, year=year_select))

            else:
                flash('Please make a selection', 'warning')

        # HANDLE FILTER VENDOR SEARCHES
        if request.method == 'POST' and request.form.get('check') == 'nf_vendor_search':
            month_query = request.args.get('month', month)
            year_query = request.args.get('year', year)
            vendor_query = request.form.get('nf_vendor_select')
            vendor_query = int(vendor_query)

            page = 1

            if vendor_query:
                farmitem_purchased = Purchase.query.filter(db.extract('year', Purchase.date)==year_query).\
                                filter(db.extract('month', Purchase.date)==month_query).\
                                    filter(Purchase.vendor_id == vendor_query).\
                                        filter(Purchase.feeditem_id == None).order_by(Purchase.id.desc()).paginate(page, current_app.config['SINGLE_DATA_PER_PAGE'], error_out=True)
                
                flash('Vendor search was successful', 'success')
            else:
                flash('Please make a selection', 'warning') 


        # HANDLE FILTER FARMITEM SEARCHES 
        if request.method == 'POST' and request.form.get('check') == 'nf_farmitem_search':
            month_query = request.args.get('month', month)
            year_query = request.args.get('year', year)
            farmitem_query = request.form.get('nf_farmitem_select')
            farmitem_query = int(farmitem_query)

            page = 1

            if farmitem_query:
                farmitem_purchased = Purchase.query.filter(db.extract('year', Purchase.date)==year_query).\
                                filter(db.extract('month', Purchase.date)==month_query).\
                                    filter(Purchase.farmitem_id == farmitem_query).order_by(Purchase.id.desc()).paginate(page, current_app.config['SINGLE_DATA_PER_PAGE'], error_out=True)
                
                flash('Farmitem search was successful', 'success')
            else:
                flash('Please make a selection', 'warning') 


        # Fetch all pending notifications
        all_activities = Activitylog.query.filter(Activitylog.status == 'pending').\
                                order_by(Activitylog.id.desc()).limit(3).all()

        # Fetch all User specific notifications
        user_activities = Activitylog.query.filter(Activitylog.user_id == current_user.id, Activitylog.status == 'pending').\
                                order_by(Activitylog.id.desc()).limit(3).all()


        # Current User Image
        image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)

        return render_template('storemgt/store_nonfeedpurchases.html', title='Store Non-Feed Purchases', ficon="store", 
                        date=datetime.now(), form=form, image_file=image_file, vendors_list=vendors_list, farmitem_list=farmitem_list, nf_purchase_month=nf_purchase_month,
                        nf_purchase_year=nf_purchase_year, farmitem_purchased=farmitem_purchased, all_activities=all_activities, user_activities=user_activities)

    else:
        pass


# HANDLE UPDATE FEED FORM POPULATION
@stores.route('/update_feed', methods=['POST'])
def update_feed():
    get_id = request.get_data('id').decode('utf-8')
    get_id = int(get_id)
    purchase_row = Purchase.query.filter(Purchase.id == get_id).first()

    purchaseList = []
    purchaseDict = {}

    purchaseDict['id'] = purchase_row.id
    purchaseDict['vendor'] = purchase_row.vendor_id
    purchaseDict['feeditem'] = purchase_row.feeditem_id
    purchaseDict['qty'] = purchase_row.v_qty
    purchaseDict['price'] = purchase_row.v_price
    purchaseList.append(purchaseDict)

    return jsonify({'purchase_data': purchaseList})


# HANDLE UPDATE NONFEED FORM POPULATION
@stores.route('/update_nonfeed', methods=['POST'])
def update_nfitem():
    get_id = request.get_data('id').decode('utf-8')
    get_id = int(get_id)
    purchase_nf_row = Purchase.query.filter(Purchase.id == get_id).first()

    purchaseNfList = []
    purchaseNfDict = {}

    purchaseNfDict['id'] = purchase_nf_row.id
    purchaseNfDict['vendor'] = purchase_nf_row.vendor_id
    purchaseNfDict['farmitem'] = purchase_nf_row.farmitem_id
    purchaseNfDict['qty'] = purchase_nf_row.v_qty
    purchaseNfDict['price'] = purchase_nf_row.v_price
    purchaseNfList.append(purchaseNfDict)

    return jsonify({'purchase_nf': purchaseNfList})


# STORE STOCK ROUTE
@stores.route('/storemgt/store_stock', methods=['GET', 'POST'])
@login_required
def store_stock():
    # instantiate the store form
    form = storeForm()

  
    # HANDLE OUTFLOW OF FEED OUT OF STORE FORM PROCESSING
    if request.method == 'POST' and request.form.get('check') == 'feed_outflow':
        # Get outflow info
        feed_out_id = request.form.get('feed_type_id')
        feed_department = request.form.get('department')
        feed_qty = request.form.get('feed_qty')

        feed_department = feed_department.capitalize()
        feed_qty = float(feed_qty)

        feed_stock = Production.query.filter(Production.date == date.today(), Production.feedtype_id == feed_out_id).first()
        feed_stock.issued_qty = feed_qty
        feed_stock.department = feed_department
        db.session.commit()

        # Update Production Closing Stock
        feed_stock.c_qty = (feed_stock.o_qty + feed_stock.p_qty) - (feed_stock.issued_qty)
        db.session.commit()

        flash('Feed Outflow submitted successfully', 'success')
        return redirect(url_for('stores.store_stock'))


    # HANDLE UPDATE OUTFLOW OF FEED OUT OF STORE FORM PROCESSING
    if request.method == 'POST' and request.form.get('check') == 'update_feed_outflow':
        update_id = request.form.get('update_id')
        update_qty = request.form.get('update_qty')
        update_dept = request.form.get('update_dept')

        # Update Production row for that row id
        update_row = Production.query.filter(Production.id == update_id).first()
        update_row.issued_qty = update_qty
        update_row.department = update_dept
        db.session.commit()

        # Update the closing Stock
        update_row.c_qty = (update_row.o_qty + update_row.p_qty) - (update_row.issued_qty)
        db.session.commit()

        # Update productions from that date down
        next_prod = Production.query.filter(Production.date > update_row.date, Production.feedtype_id == update_row.feedtype_id).all()
        if next_prod:
            for nxt in next_prod:
                prev_prod = Production.query.filter(Production.date == nxt.date - timedelta(days=1), Production.feedtype_id == update_row.feedtype_id).first()
               
                # Update opening qty
                nxt.o_qty = prev_prod.c_qty
                db.session.commit()

                # Update Closing Qty
                nxt.c_qty = (nxt.o_qty + nxt.p_qty) - (nxt.issued_qty)
                db.session.commit()

        else:
            pass

        flash('Feed outflow updated successfully', 'success')
        return redirect(url_for('stores.store_stock'))


    # Fetch Purchased Feed item
    year = date.today().strftime('%Y')
    month = date.today().strftime('%m')

    month_query = request.args.get('month', month)
    year_query = request.args.get('year', year)

    page = request.args.get('page', 1, type=int)

    production_data = Production.query.filter(db.extract('year', Production.date)==year_query).\
                            filter(db.extract('month', Production.date)==month_query).order_by(Production.id.desc()).paginate(page, current_app.config['MULTIPLE_DATA_PER_PAGE'], error_out=True)


    # Fetch all Feedtype in db
    feedtypes = Feedtype.query.all() 


    # HANDLE FILTER FEEDSTOCK FORM POPULATION
    production_dates = Production.query.all()
    production_month = []
    production_year = []

    for data in production_dates:
        p_month = data.date.strftime('%m')
        p_year = data.date.strftime('%Y')

        if p_month in production_month:
            pass
        else:
            production_month.append(p_month)

        if p_year in production_year:
            pass
        else:
            production_year.append(p_year)


    # HANDLE MONTH AND DATE FILTERS
    if request.method == 'POST' and request.form.get('check') == 'gobutton':
        year_select = request.form.get('year')
        month_select = request.form.get('month')

        if year_select and month_select:
            production_data = Production.query.filter(db.extract('year', Production.date)==year_select).\
                        filter(db.extract('month', Production.date)==month_select).order_by(Production.id.desc()).paginate(page, current_app.config['MULTIPLE_DATA_PER_PAGE'], error_out=True)

            flash('Feed stock for '+numberMonth(month_select)+' '+year_select+' Selected', 'success')
            return redirect(url_for('stores.store_stock', month=month_select, year=year_select))

        else:
            flash('Please make a selection', 'warning')


    # HANDLE FILTER FEEDTYPE SEARCHES
    if request.method == 'POST' and request.form.get('check') == 'feedtype_search':
        month_query = request.args.get('month', month)
        year_query = request.args.get('year', year)
        feedtype_query = request.form.get('feedtype_select')
        feedtype_query = int(feedtype_query)

        page = 1

        if feedtype_query:
            production_data = Production.query.filter(db.extract('year', Production.date)==year_query).\
                            filter(db.extract('month', Production.date)==month_query).\
                                filter(Production.feedtype_id==feedtype_query).order_by(Production.id.desc()).paginate(page, current_app.config['MULTIPLE_DATA_PER_PAGE'], error_out=True)
            
            flash('Feedtype search was successful', 'success')
        else:
            flash('Please make a selection', 'warning') 
            


    # Fetch all pending notifications
    all_activities = Activitylog.query.filter(Activitylog.status == 'pending').\
                                order_by(Activitylog.id.desc()).limit(3).all()

    # Fetch all User specific notifications
    user_activities = Activitylog.query.filter(Activitylog.user_id == current_user.id, Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

    # Current User Image
    image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)


    return render_template('storemgt/store_stock.html', title='Store Stock', ficon="store", date=datetime.now(), image_file=image_file, form=form, feedtypes=feedtypes,
                            production_data=production_data, production_month=production_month, production_year=production_year, all_activities=all_activities, user_activities=user_activities)



# HANDLE UPDATE OUTFLOW FORM POPULATION
@stores.route('/feed_outflow', methods=['POST'])
def feed_outflow():
    outflow_id = request.get_data('id').decode('utf-8')
    outflow_id = int(outflow_id)
    outflow_row = Production.query.filter(Production.id == outflow_id).first()

    outflow_list = []
    outflow_dict = {}

    outflow_dict['id'] = outflow_row.id
    outflow_dict['qty'] = outflow_row.issued_qty
    outflow_dict['dept'] = outflow_row.department
    outflow_list.append(outflow_dict)

    return jsonify({'outflow_info': outflow_list})


# STORE RECEIVABLES ROUTE
@stores.route('/storemgt/store_receivables', methods=['GET', 'POST'])
@login_required
def store_receivables():
    # call receivable db update
    receivable_update()

    # instantiate the store form
    form = storeForm()


    # Handle Processing of new farmitem outflow
    if request.method == 'POST' and request.form.get('check') == 'farmitem_outflow':
        # Get farmitem info
        farmitem_id = request.form.get('farmitem_id')
        farmitem_dept = request.form.get('farmitem_dept')
        farmitem_qty = request.form.get('farmitem_qty')

        farmitem_id = int(farmitem_id)
        farmitem_qty = int(farmitem_qty)

        farmitem_row = Receivable.query.filter(Receivable.date == date.today(), Receivable.farmitem_id == farmitem_id).first()
        # Update the Issued qty and re-calculate the closing stock
        farmitem_row.issued_qty = farmitem_qty
        farmitem_row.department =farmitem_dept
        db.session.commit()

        farmitem_row.c_qty = (farmitem_row.o_qty + farmitem_row.v_qty) - (farmitem_row.issued_qty)
        db.session.commit()

        flash('Farm item outflow submitted successfully', 'success')
        return redirect(url_for('stores.store_receivables'))


    # Handle processing of update farmitem outflow
    if request.method == 'POST' and request.form.get('check') == 'nf_update_outflow':
        # Get farmitem update info
        nf_row_id = request.form.get('nf_row_id')
        nf_outflow_qty = request.form.get('nf_outflow_qty')
        nf_outflow_dept = request.form.get('nf_outflow_dept')

        nf_row_id = int(nf_row_id)
        nf_outflow_qty = int(nf_outflow_qty)

        nf_update_row = Receivable.query.filter(Receivable.id == nf_row_id).first()
        nf_update_row.issued_qty = nf_outflow_qty
        nf_update_row.department = nf_outflow_dept
        db.session.commit()

        nf_update_row.c_qty = (nf_update_row.o_qty + nf_update_row.v_qty) - (nf_update_row.issued_qty)
        db.session.commit()

        # Update Receivable db from the updated date down
        next_receivable_rows = Receivable.query.filter(Receivable.date > nf_update_row.date).all()
        for next_row in next_receivable_rows:
            prev_receivable_row = Receivable.query.filter(Receivable.date == next_row.date - timedelta(days=1), Receivable.farmitem_id == nf_update_row.farmitem_id).first()
            # update the opening qty and re-calculate the closing qty
            next_row.o_qty = prev_receivable_row.c_qty
            db.session.commit()

            next_row.c_qty = (next_row.o_qty + next_row.v_qty) - (next_row.issued_qty)
            db.session.commit()

        flash('Farm item outflow updated successfully', 'success')
        return redirect(url_for('stores.store_receivables'))
        

    # Fetch Purchased Feed item
    year = date.today().strftime('%Y')
    month = date.today().strftime('%m')

    year_query = request.args.get('year', year)
    month_query = request.args.get('month', month)

    page = request.args.get('page', 1, type=int)

    receivable_data = Receivable.query.filter(db.extract('year', Receivable.date)==year_query).\
                            filter(db.extract('month', Receivable.date)==month_query).order_by(Receivable.id.desc()).paginate(page, current_app.config['SINGLE_DATA_PER_PAGE'], error_out=True)

    
    # Fetch all Farmitem in db
    farmitems = Receivable.query.filter(Receivable.date == date.today(), Receivable.c_qty !=0).all() 

    all_farmitems = Farmitem.query.all()

    # Handle Receivable Filter form population
    receivable_dates = Receivable.query.all()
    receivable_month = []
    receivable_year = []

    for data in receivable_dates:
        r_month = data.date.strftime('%m')
        r_year = data.date.strftime('%Y')

        if r_month in receivable_month:
            pass
        else:
            receivable_month.append(r_month)

        if r_year in receivable_year:
            pass
        else:
            receivable_year.append(r_year)


    # HANDLE MONTH AND DATE FILTERS
    if request.method == 'POST' and request.form.get('check') == 'gobutton':
        year_select = request.form.get('year')
        month_select = request.form.get('month')

        if year_select and month_select:
            receivable_data = Receivable.query.filter(db.extract('year', Receivable.date)==year_select).\
                            filter(db.extract('month', Receivable.date)==month_select).order_by(Receivable.id.desc()).paginate(page, current_app.config['SINGLE_DATA_PER_PAGE'], error_out=True)

            flash('Receivables for '+numberMonth(month_select)+' '+year_select+' Selected', 'success')
            return redirect(url_for('stores.store_receivables'))

        else:
            flash('Please make a selection', 'warning')
    

    # HANDLE FILTER OF FARMITEM RECEIVABLE SEARCHES
    if request.method == 'POST' and request.form.get('check') == 'farmitem_search':
        month_query = request.args.get('month', month)
        year_query = request.args.get('year', year)
        farm_item_query = request.form.get('farmitem_select')
        farm_item_query = int(farm_item_query)

        page = 1

        if farm_item_query:
            receivable_data = Receivable.query.filter(db.extract('year', Receivable.date)==year_query).\
                            filter(db.extract('month', Receivable.date)==month_query).\
                                filter(Receivable.farmitem_id==farm_item_query).order_by(Receivable.id.desc()).paginate(page, current_app.config['SINGLE_DATA_PER_PAGE'], error_out=True)
        else:
            flash('Please make a selection', 'warning')


    # Fetch all pending notifications
    all_activities = Activitylog.query.filter(Activitylog.status == 'pending').\
                                order_by(Activitylog.id.desc()).limit(3).all()

    # Fetch all User specific notifications
    user_activities = Activitylog.query.filter(Activitylog.user_id == current_user.id, Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()


    # Current User Image
    image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)


    return render_template('storemgt/store_receivables.html', title='Store Receivables', ficon="store", date=datetime.now(), form=form, farmitems=farmitems,
                        receivable_data=receivable_data, image_file=image_file, receivable_month=receivable_month, receivable_year=receivable_year, all_farmitems=all_farmitems, all_activities=all_activities, user_activities=user_activities)


# HANDLE FARMITEM OUTFLOW UPDATE FORM POPULATION
@stores.route('/farmitem_outflow_update', methods=['POST'])
def farmitem_outflow():
    farmitem_row_id = request.get_data('id').decode('utf_8')
    farmitem_row_id = int(farmitem_row_id)

    update_row = Receivable.query.filter(Receivable.id == farmitem_row_id).first()
    update_list = []
    update_dict = {}

    update_dict['id'] = update_row.id
    update_dict['dept'] = update_row.department
    update_dict['qty'] = update_row.issued_qty
    update_list.append(update_dict)

    return jsonify({'farmitem_info': update_list})



# ***********************************************************************
# EGG STORE ROUTES STARTS HERE
# ***********************************************************************


# EGG STORE OVERVIEW ROUTE
@stores.route('/storemgt/eggstore_overview', methods=['GET', 'POST'])
@login_required
def eggstore_overview():
    # call receivable db update
    receivable_update()
    # Eggstock Update
    eggstock_update()

    # Initialize Form
    form = eggstoreForm


    # Fetch all pending notifications
    all_activities = Activitylog.query.filter(Activitylog.status == 'pending').\
                                order_by(Activitylog.id.desc()).limit(3).all()

    # Fetch all User specific notifications
    user_activities = Activitylog.query.filter(Activitylog.user_id == current_user.id, Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()


    # Current user image
    image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)


    return render_template('storemgt/eggstore_overview.html', title='Egg-Store Overview', ficon="store", date=datetime.now(), form=form, 
                            image_file=image_file, all_activities=all_activities, user_activities=user_activities)



# EGG STORE CUSTOMER ROUTE
@stores.route('/storemgt/eggstore_customers', methods=['GET', 'POST'])
@login_required
def eggstore_customers():
    # Initialize Form
    form = eggstoreForm

    # HANDLE PROCESSING OF NEW CUSTOMER
    if request.method == 'POST' and request.form.get('check') == 'new_customer':
        customer_name = request.form.get('customer_name')
        customer_name = customer_name.title()

        customer_split = customer_name.split(" ")
        if len(customer_split) == 2:
            customer_name = "_".join(customer_split)
        else:
            customer_name = customer_name

        # Check if customer name exists
        check_customer_name = Customer.query.filter(Customer.customer == customer_name).first()
        if check_customer_name:
            flash(customer_name+' already exists, please rename', 'warning')
        else:
            add_customer = Customer(customer=customer_name)
            db.session.add(add_customer)
            db.session.commit()

            flash(customer_name+' added successfully', 'success')
            return redirect(url_for('stores.eggstore_customers'))


    # HANDLE PROCESSING OF CUSTOMER RENAME FORM
    if request.method == 'POST' and request.form.get('check') == 'rename_customer':
        name_id = request.form.get('name_id')
        old_name = request.form.get('oldname')
        new_name = request.form.get('newname')
        new_name = new_name.title()

        # Check if name exist in customer db
        check_new_customer = Customer.query.filter(Customer.customer == new_name).first()
        if new_name == old_name:
            flash('New customer name is the same as the old customer name', 'warning')
        elif check_new_customer:
            flash(new_name+' already exists in the database', 'warning')
        else:
            _ = Customer.query.filter(Customer.id == name_id).update({'customer':new_name})
            db.session.commit()

            flash('Customer renamed successfully', 'success')
            return redirect(url_for('stores.eggstore_customers'))


    # HANDLE PROCESSING CUSTOMER DELETE FORM
    if request.method == 'POST' and request.form.get('check') == 'delete_customer':
        # Get customer id
        delete_id = request.form.get('delete_id')

        # Get customer id row
        customer_del = Customer.query.filter(Customer.id == delete_id).first()
        
        # Get User info and activities
        user = current_user.id
        user_activity = 'Delete Request for Customer - '+customer_del.customer+' Received'
        request_query = 'Customer of id '+delete_id

         # Add Data to the Activitylog database
        new_activity = Activitylog(user_id = user, activity = user_activity, request = request_query)
        db.session.add(new_activity)
        db.session.commit()

        flash('Delete Request for '+ customer_del.customer +' Sent', 'success')
        return redirect(url_for('stores.eggstore_customers'))


    # FETCH ALL CUSTOMERS NAMESss
    customers_list = Customer.query.all()
    if customers_list:
        customers_colors = color_sample(int(customers_list[-1].id) + 1)
    else:
        customers_colors = 0

    
    # Fetch all pending notifications
    all_activities = Activitylog.query.filter(Activitylog.status == 'pending').\
                                order_by(Activitylog.id.desc()).limit(3).all()

    # Fetch all User specific notifications
    user_activities = Activitylog.query.filter(Activitylog.user_id == current_user.id, Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

     # Current user image
    image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)

    return render_template('storemgt/eggstore_customers.html', title='Egg-Store Customers', ficon="users", date=datetime.now(), form=form, customers_list=customers_list, customers_colors=customers_colors,
                            image_file=image_file, all_activities=all_activities, user_activities=user_activities)



# Rouute to process customer rename form population
@stores.route('/rename_customer', methods=['POST'])
def rename_customer():
    customer_id = request.get_data('id').decode('utf-8')
    customer_id = int(customer_id)
    customer_row = Customer.query.filter(Customer.id == customer_id).first()

    customer_list = []
    customer_dict = {}

    customer_dict['id'] = customer_row.id
    customer_dict['name'] = customer_row.customer
    customer_list.append(customer_dict)

    return jsonify({'customer_info': customer_list})


# EGG STORE STOCK ROUTE
@stores.route('/storemgt/eggstore_stock', methods=['GET', 'POST'])
@login_required
def eggstore_stock():
    # Eggstock Update
    eggstock_update()

    # Initialize Form
    form = eggstoreForm

    # ADD NEW PEN PROCESSING
    if request.method == 'POST' and request.form.get('check') == 'new_pen':
        # Get new pen info
        pen_name =  request.form.get('pen_name')
        pen_name = pen_name.title()

        pen_split = pen_name.split(" ")
        if len(pen_split) == 2:
            pen_name = "_".join(pen_split)
        else:
            pen_name = pen_name

        # Check if pen name exists in database
        check_pen_name = Pen.query.filter(Pen.pen == pen_name).first()
        if check_pen_name:
            flash(pen_name+' already exists in database', 'warning')
        else:
            new_pen = Pen(pen=pen_name)
            db.session.add(new_pen)
            db.session.commit()

            flash(pen_name+' added, successfully', 'success')
            return redirect(url_for('stores.eggstore_stock'))


    # HANDLE PEN RENAME FORM PROCESSING
    if request.method == 'POST' and request.form.get('check') == 'rename_pen':
        # Get pen info
        pen_id = request.form.get('pen_id')
        old_pen_name = request.form.get('pen_old_name')
        new_pen_name = request.form.get('pen_new_name')

        pen_id = int(pen_id)
        new_pen_name = new_pen_name.title()

        # Check id new pen name exists in database
        check_new_pen_name = Pen.query.filter(Pen.pen == new_pen_name).first()
        if new_pen_name == old_pen_name:
            flash('New pen name is the same as old pen name', 'warning')
        elif check_new_pen_name:
            flash(new_pen_name+' already exists in database, please rename', 'warning')
        else:
            _ = Pen.query.filter(Pen.id == pen_id).update({'pen':new_pen_name})
            db.session.commit()

            flash('Pen renamed successfully', 'success')
            return redirect(url_for('stores.eggstore_stock'))
            
        
    # HANDLE DELETE OF PEN PROCESSING
    if request.method == 'POST' and request.form.get('check') == 'delete_pen':
        # Get Pen Id
        pen_delete_id = request.form.get('pen_delete_id')

        # Get Pen id row
        pen_data = Pen.query.filter(Pen.id == pen_delete_id).first()

        # Get User Indo and Activities
        user = current_user.id
        user_activity = 'Delete Request for Pen - '+pen_data.pen+' Received'
        request_query = 'Pen of id '+pen_delete_id

        # Add Data to the Activitylog database
        new_activity = Activitylog(user_id = user, activity = user_activity, request = request_query)
        db.session.add(new_activity)
        db.session.commit()

        flash('Delete Request for '+ pen_data.pen +' Sent', 'success')
        return redirect(url_for('stores.eggstore_stock'))


    # HANDLE PROCESSING OF NEW EGG STOCK
    if request.method == 'POST' and request.form.get('check') == 'new_stock':
        # Get stock info
        stock_pen = request.form.get('pen_name_id')
        stock_production = request.form.get('pen_production')
        stock_cracks = request.form.get('pen_cracks')

        stock_pen = int(stock_pen)
        stock_production = float(stock_production)
        stock_cracks = float(stock_cracks)

        # Check if production exists for the given pen and current date
        check_stock_row = Eggstock.query.filter(Eggstock.date == date.today(), Eggstock.pen_id == stock_pen).first()
        if check_stock_row:
            check_stock_row.p_qty = stock_production
            check_stock_row.cracks = stock_cracks
            db.session.commit()

            check_stock_row.c_qty = (check_stock_row.o_qty + check_stock_row.p_qty) - (check_stock_row.sales + check_stock_row.cracks)
            db.session.commit()

            flash('New egg stock submitted successfully', 'success')
            return redirect(url_for('stores.eggstore_stock'))
            
        else:
            new_stock_row = Eggstock(pen_id=stock_pen, p_qty=stock_production, cracks=stock_cracks)
            db.session.add(new_stock_row)
            db.session.commit()

            new_stock_row.c_qty = (new_stock_row.o_qty + new_stock_row.p_qty) - (new_stock_row.sales + new_stock_row.cracks)
            db.session.commit()

            flash('New egg stock submitted successfully', 'success')
            return redirect(url_for('stores.eggstore_stock'))


    # FETCH ALL PEN IN DATABASE
    pen_list = Pen.query.all()
    if pen_list:
        pen_colors = color_sample(int(pen_list[-1].id) + 1) 
    else:
        pen_colors = 0


    # FETCH ALL EGGSTOCK ROW IN DATABASE
    month = date.today().strftime('%m')
    year = date.today().strftime('%Y')


    month_query = request.args.get('month', month)
    year_query = request.args.get('year', year)

    page = request.args.get('page', 1, type=int)

    eggstock_list = Eggstock.query.filter(db.extract('month', Eggstock.date)==month_query).\
                    filter(db.extract('year', Eggstock.date)==year_query).\
                        order_by(Eggstock.id.desc()).paginate(page, current_app.config['MULTIPLE_DATA_PER_PAGE'], error_out=True)


    # Filter month  and year form population
    egg_stock_data = Eggstock.query.all()
    eggstock_month = []
    eggstock_year = []

    for stock in egg_stock_data:
        egg_month = stock.date.strftime('%m')
        egg_year = stock.date.strftime('%Y')

        if egg_month in eggstock_month:
            pass
        else:
            eggstock_month.append(egg_month)

        if egg_year in eggstock_year:
            pass
        else:
            eggstock_year.append(egg_year)

    
    # HANDLE MONTH AND YEAR FILTER PROCESSING 
    if request.method == 'POST' and request.form.get('check') == 'gobutton':
        month_select = request.form.get('month')
        year_select = request.form.get('year')

        if month_select and year_select:
            eggstock_list = Eggstock.query.filter(db.extract('month', Eggstock.date)==month_select).\
                    filter(db.extract('year', Eggstock.date)==year_select).\
                        order_by(Eggstock.id.desc()).paginate(page, current_app.config['MULTIPLE_DATA_PER_PAGE'], error_out=True)

            flash('Egg stock for '+numberMonth(month_select)+' '+year_select+' selected', 'success')
            return redirect(url_for('stores.eggstore_stock', month=month_select, year=year_select))
                        
        else:
            flash('Please make a selection', 'warning')


    # HANDLE PEN FILTER PROCESSING
    if request.method == 'POST' and request.form.get('check') == 'pen_search':
        # Get Pen id
        pen_select = request.form.get('pen_select')
        month_query = request.args.get('month', month)
        year_query = request.args.get('year', year)
        pen_select = int(pen_select)

        page = 1

        if pen_select:
            eggstock_list = Eggstock.query.filter(db.extract('month', Eggstock.date)==month_query).\
                    filter(db.extract('year', Eggstock.date)==year_query).\
                        filter(Eggstock.pen_id == pen_select).\
                            order_by(Eggstock.id.desc()).paginate(page, current_app.config['MULTIPLE_DATA_PER_PAGE'], error_out=True)

            flash('Pen search was successful', 'success')
        else:
            flash('Please make a selection', 'warning')


    # HANDLE UPDATE OF EGGSTOCK FORM PROCESSING
    if request.method == 'POST' and request.form.get('check') == 'update_eggstock':
        # Get update details
        eggstock_row_id = request.form.get('eggstock_row_id')
        eggstock_production = request.form.get('u_production')
        eggstock_cracks = request.form.get('u_cracks')
        
        eggstock_row_id = int(eggstock_row_id)
        eggstock_production = int(eggstock_production)
        eggstock_cracks = int(eggstock_cracks)

        # Query the database with the eggstock row id
        eggstock_data = Eggstock.query.filter(Eggstock.id == eggstock_row_id).first()

        # Update the production and crack quantity
        eggstock_data.p_qty = eggstock_production
        eggstock_data.cracks = eggstock_cracks
        db.session.commit()

        # Update the closing stock
        eggstock_data.c_qty = (eggstock_data.o_qty + eggstock_data.p_qty) - (eggstock_data.sales + eggstock_data.cracks)
        db.session.commit()

        # Update all dates after the current updated date
        eggstock_next = Eggstock.query.filter(Eggstock.date > eggstock_data.date, Eggstock.pen_id == eggstock_data.pen_id).all()
        for next_stock in eggstock_next:
            eggstock_prev = Eggstock.query.filter(Eggstock.date == next_stock.date - timedelta(days=1), Eggstock.pen_id == eggstock_data.pen_id).first()

            # update the opening stock
            next_stock.o_qty = eggstock_prev.c_qty
            db.session.commit()

            # Update the closing stock
            next_stock.c_qty = (next_stock.o_qty + next_stock.p_qty) - (next_stock.sales + next_stock.cracks)
            db.session.commit()

        flash('Eggstock updated successfully', 'success')
        return redirect(url_for('stores.eggstore_stock'))


    # Fetch all pending notifications
    all_activities = Activitylog.query.filter(Activitylog.status == 'pending').\
                                order_by(Activitylog.id.desc()).limit(3).all()

    # Fetch all User specific notifications
    user_activities = Activitylog.query.filter(Activitylog.user_id == current_user.id, Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()


    # Current user image
    image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)


    return render_template('storemgt/eggstore_stock.html', title='Egg-Store Stock', ficon="users", date=datetime.now(), form=form, pen_list=pen_list, pen_colors=pen_colors, eggstock_list=eggstock_list, eggstock_month=eggstock_month, eggstock_year=eggstock_year,
                            image_file=image_file, all_activities=all_activities, user_activities=user_activities)


 # HANDLE PEN RENAME FORM POPULATION
@stores.route('/rename_pen', methods=['POST'])
def rename_pen():
    pen_name_id = request.get_data('id').decode('utf-8')
    pen_name_id = int(pen_name_id)
    pen_row = Pen.query.filter(Pen.id == pen_name_id).first()

    penList = []
    penDict = {}

    penDict['id'] = pen_row.id 
    penDict['name'] = pen_row.pen
    penList.append(penDict)

    return jsonify({'pen_info': penList})   


# HANDLE EGGSTOCK UPDATE FORM POPULATION
@stores.route('/update_eggstock', methods=['POST'])
def update_eggstock():
    stock_id = request.get_data('id').decode('utf-8')
    stock_id = int(stock_id)
    eggstock_row = Eggstock.query.filter(Eggstock.id == stock_id).first()

    eggstockList = []
    eggstockDict = {}

    eggstockDict['id'] = eggstock_row.id
    eggstockDict['production'] = eggstock_row.p_qty
    eggstockDict['cracks'] = eggstock_row.cracks
    eggstockList.append(eggstockDict)

    return jsonify({'eggstock_info': eggstockList})


# EGG STORE SUPPLY ROUTE
@stores.route('/storemgt/eggstore_supply', methods=['GET', 'POST'])
@login_required
def eggstore_supply():
    # Initialize Form
    form = eggstoreForm


    # Fetch all pending notifications
    all_activities = Activitylog.query.filter(Activitylog.status == 'pending').\
                                order_by(Activitylog.id.desc()).limit(3).all()

    # Fetch all User specific notifications
    user_activities = Activitylog.query.filter(Activitylog.user_id == current_user.id, Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()


     # Current user image
    image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)


    return render_template('storemgt/eggstore_supply.html', title='Egg-Store Supply', ficon="users", date=datetime.now(), form=form, 
                            image_file=image_file, all_activities=all_activities, user_activities=user_activities)