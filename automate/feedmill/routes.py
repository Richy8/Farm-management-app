import os
from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, flash, request, redirect, url_for, jsonify, abort, current_app
from automate import db, mail
from automate.feedmill import feedmill
from flask_mail import Message
from flask_login import login_required, current_user
from automate.feedmill.forms import FeeditemForm, RenameitemForm, ProductionUpdateForm, VendorForm, FeedTypeForm, OverheadCostForm
from automate.models import Feeditem, Feedtype, Formulation, Feedcost, Feedstock, Activitylog, User, Production
from automate.feedmill.utils import update, updateproduction, wordTruncate, numberDecreament, numberDecimal, numberFormat, numberMonth, color_sample, receivable_update


# FeedMill Overview Route
@feedmill.route('/feedmgt/feedmill_overview', methods=['GET', 'POST'])
@login_required
def feedoverview():
    # call update function
    update()
    # run update production
    updateproduction()
    # Receivable update
    receivable_update()

    form = OverheadCostForm()
    filepath = os.path.join(current_app.root_path, 'overhead.txt')
    if form.validate_on_submit():
        cost = str(form.overhead.data)
        # Write cost to the overhead txt file
        with open(filepath, 'w') as writer:
            writer.write(cost)
            flash('Overhead Cost Updated Successfully', 'success')

    # Read current overhead cost from the txt file
    with open(filepath, 'r') as reader:
        output = format(int(reader.read()), ',d')

    # Fetch feedcost
    feedcost = Feedcost.query.filter_by(date=date.today()).all()
    if feedcost:
        cost_colors = color_sample(len(feedcost) + 1)
    else:
        cost_colors = 0

    # Fetch Feed item and price
    feeditems = Feedstock.query.filter_by(date=date.today()).all()
    color_query = Feeditem.query.all()
    if color_query:
        price_colors = color_sample(int(color_query[-1].id) + 1)
    else:
        price_colors = 0

    # Fetch daily productions of feedtypes
    productions = Production.query.filter(Production.date == date.today()).all()
    if productions:
        prod_colors = color_sample(int(productions[-1].feedtype_id) + 1)
    else:
        prod_colors = 0

    # Fetch all pending notifications
    all_activities = Activitylog.query.filter(Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

    # Fetch all User specific notifications
    user_activities = Activitylog.query.filter(Activitylog.user_id == current_user.id, Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

    # User Image
    image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)

    return render_template("feedmgt/feedoverview.html", title="Feed Overview",
                        ficon="store", date=datetime.now(), form=form, image_file=image_file, output=output,
                        feedcost=feedcost, feeditems=feeditems, cost_colors=cost_colors, price_colors=price_colors, 
                        productions=productions, prod_colors=prod_colors, all_activities=all_activities, user_activities=user_activities)


# Route to get Overview closing quantity chart
@feedmill.route('/overview_chart', methods=['GET'])
def overview_chart():
    item_stock = Feedstock.query.filter(Feedstock.date == date.today()).all()
    
    itemlist = []

    for item in item_stock:
        itemDict = {}
        itemDict['id'] = item.feeditem_id
        itemDict['item'] = item.feeditem.item
        itemDict['c_qty'] = item.c_qty
        itemlist.append(itemDict)

    return jsonify({'items': itemlist})


# Feed Inventory Route
@feedmill.route('/feedmgt/feed_inventory', methods=['GET', 'POST'])
@login_required
def feedinventory():
    # Run Daily Update and production
    update()
    updateproduction()

    # Instatiate Forms
    form = FeeditemForm()
    form2 = RenameitemForm()

    # Process request for New Item
    if request.method == 'POST' and request.form.get('check') == 'check':
        fitem = request.form.get('feeditem')
        fqty = request.form.get('quantity')
        fprice = request.form.get('unitprice')

        # Concatenate Items if the word is more than one
        listitem = fitem.split(" ")
        if len(listitem) == 2:
            new_item = "_".join(listitem)
        else:
            new_item = fitem

        # Check if feeditem already exists
        check_item = Feeditem.query.filter_by(item=new_item).first()
        if check_item:
            flash('Feeditem already exist', 'warning')
            return redirect(url_for('feedmill.feedinventory'))

        # Add New Feeditem
        newfeed = Feeditem(item=new_item, qty=fqty, price=fprice)
        db.session.add(newfeed)
        db.session.commit()

        # Check if Feeditem exists in the Feedstock database
        check_stock = Feedstock.query.filter(Feedstock.date == date.today(), Feedstock.feeditem_id == newfeed.id).first()
        if check_stock:
            pass
        else:
            # Add Feeditem to Feedstock database
            add_stock = Feedstock(date=date.today(), feeditem_id=newfeed.id, o_qty=newfeed.qty, o_price=newfeed.price, c_qty=newfeed.qty, c_price=newfeed.price)
            db.session.add(add_stock)
            db.session.commit()

        # Check If Feedtype exists, then add new feed to formulation
        check_feedtype = Feedtype.query.all()

        if check_feedtype:
            for feedtype in check_feedtype:
                # Check if Feeditem exists in Formulation table
                check_formulation = Formulation.query.\
                    filter(Formulation.date == date.today(), Formulation.feedtype_id == feedtype.id, Formulation.feeditem_id == newfeed.id).first()
            
            if check_formulation:
                pass
            else:
                for feedtype2 in check_feedtype:
                    # Add new feediten to formulation table
                    add_form = Formulation(date=date.today(), feedtype_id=feedtype2.id, feeditem_id=newfeed.id)
                    db.session.add(add_form)
                
                db.session.commit()
        else:
            pass
       
        flash('Feed Item Added Successfully..', 'success')

    # Rename form processing
    if request.method == 'POST' and request.form.get('check') == 'rename':
        item_id = request.form.get('nameId')
        old_name = request.form.get('oldname')
        new_name = request.form.get('newname')

        check_feed = Feeditem.query.filter_by(item = new_name.capitalize()).first()

        if old_name == new_name:
            flash('"' + new_name + '" is same as the old name', 'info')
        elif check_feed:
            flash('Name already exist', 'warning')
        else:
            feed_item = Feeditem.query.filter_by(id=item_id).first()
            feed_item.item = new_name
            db.session.commit()
            flash('Feed Item Renamed Successfully..', 'success')

    # Fetch all Items
    items = Feeditem.query.all()
    # Set Colors
    if items:
        item_colors = color_sample(int(items[-1].id) + 1)
    else: 
        item_colors = 0

    # Fetch First Feed item details
    year = date.today().strftime('%Y')
    month = date.today().strftime('%m')

    year_query = request.args.get('year', year)
    month_query = request.args.get('month', month)

    # Get id from the argument parameter
    numberOne = Feeditem.query.all()
    if numberOne:
        first_id = request.args.get('item', numberOne[0].id, type=int)
    else:
        first_id = request.args.get('item', 1, type=int)

    # Get all month associated with feed item
    by_month = Feedstock.query.filter(Feedstock.feeditem_id == first_id).all()
    monthlist = []

    for m in by_month:
        m_data = m.date.strftime('%m')

        if m_data in monthlist:
            pass
        else:
            monthlist.append(m_data)

    # Get all year associated with feed item
    by_year = Feedstock.query.filter(Feedstock.feeditem_id == first_id).all()
    yearlist = []

    for m in by_year:
        y_data = m.date.strftime('%Y')

        if y_data in yearlist:
            pass
        else:
            yearlist.append(y_data)
    

    # Try and Except Block to select current month and year
   

    try:
        page = request.args.get('page', 1, type=int)

        first_item = Feedstock.query.filter(db.extract('year', Feedstock.date) == year_query).\
                        filter(db.extract('month', Feedstock.date) == month_query).\
                        filter(Feedstock.feeditem_id == first_id).order_by(Feedstock.id.desc()).paginate(page, current_app.config['SINGLE_DATA_PER_PAGE'], error_out=True)

        item_create_date = Feedstock.query.filter(db.extract('year', Feedstock.date) == year).\
                        filter(db.extract('month', Feedstock.date) == month).\
                        filter(Feedstock.feeditem_id == first_id).order_by(Feedstock.id.desc()).all()

    except:
        first_item = None
        item_create_date  = None

    # Filter by month and year block query
    if request.method == 'POST' and request.form.get('check') == 'gobutton':
        month_select = request.form.get('month')
        year_select = request.form.get('year')

        if month_select and year_select:
            page = request.args.get('page', 1, type=int)

            first_item = Feedstock.query.filter(db.extract('year', Feedstock.date) == year_select).\
                        filter(db.extract('month', Feedstock.date) == month_select).\
                        filter(Feedstock.feeditem_id == first_id).order_by(Feedstock.id.desc()).paginate(page, current_app.config['SINGLE_DATA_PER_PAGE'], error_out=True)
            
            item = Feeditem.query.filter(Feeditem.id == first_id).first()
            flash(item.item+' Inventory ' +numberMonth(month_select)+' - '+year_select, 'success')
            return redirect(url_for('feedmill.feedinventory', item=first_id, month=month_select, year=year_select
            ))
        else:
            
            flash('Please make a selection', 'warning')


    # Delete processing Request
    if request.method == 'POST' and request.form.get('check') == 'delete':
        # Get feeditem_id
        feeditem_id = request.form.get('feeditem_id')
        feeditem_data = Feeditem.query.filter(Feeditem.id == feeditem_id).first()

        # Get user info and activities
        user = current_user.id
        user_activity = 'Delete Request for Feeditem - '+feeditem_data.item+' Received'
        request_query = 'Feeditem of id '+feeditem_id

        # Add Data to the Activitylog database
        new_activity = Activitylog(user_id = user, activity = user_activity, request = request_query)
        db.session.add(new_activity)
        db.session.commit()

        flash('Delete Request for '+ feeditem_data.item +' Sent', 'success')
        return redirect(url_for('feedmill.feedinventory'))

    # Fetch all pending notifications
    all_activities = Activitylog.query.filter(Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

    # Fetch all User specific notifications
    user_activities = Activitylog.query.filter(Activitylog.user_id == current_user.id, Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

    # Current User Profile Image
    image_file = url_for('static', filename='wt-profile-pics/' + current_user.picture)

    return render_template("feedmgt/feedinventory.html", title="Feed Inventory", ficon="store", form=form,
                            form2=form2, date=datetime.now(), image_file=image_file, items=items, item_colors=item_colors,
                            first_item=first_item, monthlist=monthlist, yearlist=yearlist, item_create_date=item_create_date, all_activities=all_activities, user_activities=user_activities)


# Route to handle update of stocks in feed inventory
@feedmill.route('/update_stock', methods=['POST'])
def update_stock():
    if request.method == 'POST':
        update_id = request.form.get('update_id')
        update_qty = request.form.get('quantity')
        update_price = request.form.get('unitprice')

        # Update the Stock quantity and price of the stock id
        newStock = Feedstock.query.filter(Feedstock.id == update_id).first()
        newStock.o_qty = update_qty
        newStock.o_price = update_price
        db.session.commit()

        # Update the closing stock of the stock id
        newStock.c_qty = (newStock.o_qty + newStock.v_qty) - (newStock.p_qty)
        db.session.commit()

        # Update the closing price of the stock id
        o_stockTotal = (newStock.o_qty * newStock.o_price)
        v_stockTotal = (newStock.v_qty * newStock.v_price)
        stock_qty = (newStock.o_qty + newStock.v_qty)

        closing_stockPrice = (o_stockTotal + v_stockTotal) / (stock_qty)
        newStock.c_price = round(closing_stockPrice, 2)
        db.session.commit()

        # Query for all other row below the updated stock id
        next_stockRows = Feedstock.query.filter(Feedstock.feeditem_id == newStock.feeditem_id, Feedstock.date > newStock.date).all()

        for next_stockRow in next_stockRows:
            # Query for the previous row before the current one
            previous_stockRow = Feedstock.query.filter(Feedstock.date == next_stockRow.date - timedelta(days = 1), Feedstock.feeditem_id == newStock.feeditem_id).first()

            # Update opening quantity and opening price for the next row
            next_stockRow.o_qty = previous_stockRow.c_qty
            next_stockRow.o_price = previous_stockRow.c_price
            db.session.commit()

            # Calculate the new c_qty
            next_stockRow.c_qty = (next_stockRow.o_qty + next_stockRow.v_qty) - (next_stockRow.p_qty)
            db.session.commit()

            # Calculate the new c_price
            opening_stockTotal = (next_stockRow.o_qty * next_stockRow.o_price)
            vendor_stockTotal = (next_stockRow.v_qty * next_stockRow.v_price)
            total_stockQuantity = (next_stockRow.o_qty + next_stockRow.v_qty)

            cls_stockPrice = (opening_stockTotal + vendor_stockTotal) / (total_stockQuantity)
            next_stockRow.c_price = round(cls_stockPrice, 2)
            db.session.commit()

        # Update the opening price of the updated item for all next date on the formulation table
        # check if formulation table exists
        checkFormulation = Feedtype.query.all()
        if checkFormulation:
            update_stockFormulations = Formulation.query.filter(Formulation.feeditem_id == newStock.feeditem_id, Formulation.date > newStock.date).all()
            for stockForm in update_stockFormulations:
                stock_price = Feedstock.query.filter(Feedstock.feeditem_id == newStock.feeditem_id, Feedstock.date == stockForm.date).first()
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
            totallist = []
            sum = 0

            costRow = Feedcost.query.filter(Feedcost.date > newStock.date).all()
            for cost in costRow:
                formulations = Formulation.query.filter(Formulation.date == cost.date, Formulation.feedtype_id == cost.feedtype_id).all()
                for form in formulations:
                    totallist.append(form.total)

                for num in totallist:
                    sum = sum + num
                        
                totalPrice = (float(sum) + overhead_cost) / 20
                cost.price = float(totalPrice)

                db.session.commit()

                totallist.clear()
                sum = 0
        else:
            pass

        flash('Stock updated successfully', 'success')
        return redirect(url_for('feedmill.feedinventory'))


# Route to get feeditem details to populate the rename item form
@feedmill.route('/getitem_id', methods=['POST'])
def getitem_id():
    item_id = request.get_data('id').decode('utf-8')
    item_id = int(item_id)
    item_row = Feeditem.query.filter_by(id=item_id).first()

    # Create an empty list and an empty dictionary also
    itemlist = []

    itemDict = {}
    itemDict['id'] = item_row.id
    itemDict['item'] = item_row.item

    itemlist.append(itemDict)

    return jsonify({'item': itemlist})


# Route to get opening stock and price of feeditem to populate the update form
@feedmill.route('/getstock_id', methods=['POST'])
def getstock_id():
    stock_id = request.get_data('id').decode('utf-8')
    stock_id = int(stock_id)
    stock_row = Feedstock.query.filter_by(id=stock_id).first()

    # Create an empty list and an empty dictionary also
    stocklist = []

    stockDict = {}
    stockDict['o_qty'] = stock_row.o_qty
    stockDict['o_price'] = stock_row.o_price

    stocklist.append(stockDict)

    return jsonify({'stock': stocklist})



# Feed Production Route
@feedmill.route('/feedmgt/feed_production', methods=['GET', 'POST'])
@login_required
def feedproduction():
    # update production
    updateproduction()

    # Instantiate form
    form2 = ProductionUpdateForm()

    # Batch update of production
    if request.method == 'POST' and request.form.get('check') == 'batchUpdate':
        # Get the requested update date
        production_date = request.form.get('date')

        # Check if date exist in Production db
        check_date = Production.query.filter(Production.date == production_date).first()
        if check_date:
            get_feedtypes = Feedtype.query.all()
            for feed in get_feedtypes:
                request_feed = request.form.get(feed.type)

                production_row = Production.query.filter(Production.date == production_date, Production.feedtype_id == feed.id).first()
                if production_row:
                    production_row.p_qty = request_feed
                    db.session.commit()

                    # update the closing production
                    production_row.c_qty = (production_row.o_qty + production_row.p_qty) - (production_row.issued_qty)
                    db.session.commit()
 
                else:
                    pass

            # Get all dates after the updated date
            next_productions = Production.query.filter(Production.date > production_date).all()
            for next_prod in next_productions:

                all_feedtypes = Feedtype.query.all()
                for feed in all_feedtypes:
                    prev_production = Production.query.filter(Production.date == next_prod.date - timedelta(days=1), Production.feedtype_id == feed.id).first()
                    current_production = Production.query.filter(Production.date == next_prod.date, Production.feedtype_id == feed.id).first()

                    # update the opening production
                    current_production.o_qty = prev_production.c_qty
                    db.session.commit()

                    # update the closing production
                    current_production.c_qty = (current_production.o_qty + current_production.p_qty) - (current_production.issued_qty)
                    db.session.commit()


            # Update the feedstock db for that date
            itemList = {}
            production_db = Production.query.filter(Production.date == production_date).all()
            for prod in production_db:
                formulation_db = Formulation.query.filter(Formulation.date == production_date, Formulation.feedtype_id == prod.feedtype_id).all()

                for item in formulation_db:
                    itemList[item.feeditem_id] = (item.formula * prod.p_qty)
                
                for key, value in itemList.items():
                    stock_db = Feedstock.query.filter(Feedstock.date == production_date, Feedstock.feeditem_id == key).first()
                    stock_db.u_prod = stock_db.u_prod + value
                    db.session.commit()

                    stock_db.p_qty = stock_db.u_prod
                    db.session.commit()

                    stock_db.c_qty = (stock_db.o_qty + stock_db.v_qty) - (stock_db.p_qty)
                    db.session.commit()

            # Reset the stock u_prod column to 0
            _ = Feedstock.query.filter(Feedstock.date == production_date).update({'u_prod': 0})
            db.session.commit()

            # Update all feed stock dates after the updated date
            get_feedstocks = Feedstock.query.filter(Feedstock.date > production_date).all()
            for stock in get_feedstocks:

                # Query for all feed items
                get_feeditems = Feeditem.query.all()
                for item in get_feeditems:
                    prev_stock = Feedstock.query.filter(Feedstock.date == stock.date - timedelta(days=1), Feedstock.feeditem_id == item.id).first()
                    current_stock = Feedstock.query.filter(Feedstock.date == stock.date, Feedstock.feeditem_id == item.id).first()

                    # update the opening stock
                    current_stock.o_qty = prev_stock.c_qty
                    db.session.commit()

                    # update the closing stock
                    current_stock.c_qty = (current_stock.o_qty + current_stock.v_qty) - (current_stock.p_qty)
                    db.session.commit()
                    
            flash('Update on '+production_date+' was successful!', 'success')
            return redirect(url_for('feedmill.feedproduction'))

        else:
            flash(production_date+' was not found in database', 'warning')
            return redirect(url_for('feedmill.feedproduction'))

        

    # Fetch Feed items
    feeditems = Feeditem.query.all()
    feedtypes = Feedtype.query.all()

    # Fetch all pending notifications
    all_activities = Activitylog.query.filter(Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

    # Fetch all User specific notifications
    user_activities = Activitylog.query.filter(Activitylog.user_id == current_user.id, Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

    # User Image
    image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)

    return render_template("feedmgt/feedproduction.html", title="Feed Production", form2=form2, 
                        ficon="industry", date=datetime.now(), image_file=image_file, feedtypes=feedtypes, feeditems=feeditems, all_activities=all_activities, user_activities=user_activities)
    
    
# processing route for daily feedtype production
@feedmill.route('/p_process', methods=['POST'])
def processproduction():
    if request.method == 'POST':
        # run update production
        updateproduction()


        check_production = Feedstock.query.filter(Feedstock.date == date.today()).first()
        if check_production.p_qty == 0:
            all_feedtypes = Feedtype.query.all()
            for feedType in all_feedtypes:
                # Add feed produced to production db 
                feedProduced = request.form.get(feedType.type)

                # Update the production qty
                _ = Production.query.filter(Production.date == date.today(), Production.feedtype_id == feedType.id).update({'p_qty': feedProduced})
                
            db.session.commit()

            # update the closing_qty
            todayProduction = Production.query.filter(Production.date == date.today()).all()
            for t_prod in todayProduction:
                t_prod.c_qty = (t_prod.o_qty + t_prod.p_qty) - (t_prod.issued_qty)
                
            db.session.commit()

            # Update the feedstock db with the individual feeditem consumed
            itemList = {}
            production_db = Production.query.filter(Production.date == date.today()).all()
            for prod in production_db:
                formulation_db = Formulation.query.filter(Formulation.date == date.today(), Formulation.feedtype_id == prod.feedtype_id).all()

                for item in formulation_db:
                    itemList[item.feeditem_id] = (item.formula * prod.p_qty)
                
                for key, value in itemList.items():
                    stock_db = Feedstock.query.filter(Feedstock.date == date.today(), Feedstock.feeditem_id == key).first()
                    stock_db.p_qty = stock_db.p_qty + value
                    db.session.commit()

                    stock_db.c_qty = (stock_db.o_qty + stock_db.v_qty) - (stock_db.p_qty)
                    db.session.commit()

            flash('Production added successfully', 'success')
            return redirect(url_for('feedmill.feedproduction'))
        else:
            flash('Production was added earlier, try updating!', 'warning')
            return redirect(url_for('feedmill.feedproduction'))



# Feed Types Route
@feedmill.route('/feedmgt/feed_types', methods=['GET', 'POST'])
@login_required
def feedtypes():
    form = FeedTypeForm()
    form2 = FeedTypeForm()

    # Adding a new feed type
    if request.method == 'POST' and request.form.get('check') == 'check':

        feedtype = request.form.get('feedtype')
        check_feedtype = Feedtype.query.filter_by(type=feedtype).first()
        if check_feedtype:
            flash('Feedtype already exist', 'warning')
            return redirect(url_for('feedmill.feedtypes'))
        else:
            new_feedtype = Feedtype(type=feedtype)
            db.session.add(new_feedtype)
            db.session.commit()

        f_type = Feedtype.query.filter_by(type=feedtype).first()
        check_formulation = Formulation.query.filter_by(feedtype_id=f_type.id).first()
        if check_formulation:
            pass
        else:
            feeditem = Feeditem.query.all()
            for item in feeditem:
                formula = request.form.get(item.item)

                insert_formulation = Formulation(date=date.today(), feedtype_id=f_type.id, feeditem_id=item.id, formula=formula)
                db.session.add(insert_formulation)

            db.session.commit()

        update()
        flash('Feedtype created successfully', 'success')
        return redirect(url_for('feedmill.feedtypes'))


    # Updating an existing feed type
    if request.method == 'POST' and request.form.get('check') == 'check2':
        
        feed_id = request.form.get('feedid')
        feed_type = request.form.get('feedtype')

        feed_row = Feedtype.query.filter(Feedtype.id == feed_id).first()
        check_type = Feedtype.query.filter(Feedtype.type == feed_type).first()
        if check_type:
            pass
        else:
            feed_row.type = feed_type
            db.session.commit()

        # Get formulations
        items = Feeditem.query.all()
        for item in items:
            feed_formula = request.form.get(item.item)

            # Update Existing Formula
            update_formulation = Formulation.query.filter(Formulation.date == date.today(), Formulation.feedtype_id == feed_id, Formulation.feeditem_id == item.id).order_by(Formulation.feeditem_id.asc()).all()

            for f_update in update_formulation:
                f_update.formula = feed_formula

        db.session.commit()
        flash(feed_type +' updated successfully', 'success')
        return redirect(url_for('feedmill.feedtypes'))


    # Handle deletion of feedtype
    if request.method == 'POST' and request.form.get('check') == 'delete':
        request_id = request.form.get('feedtype_id')

        # Query the Feedtype db
        feedtype_data = Feedtype.query.filter(Feedtype.id == request_id).first()

        # Get user info and activities
        user = current_user.id
        user_activity = 'Delete Request for Feedtype - '+feedtype_data.type+' Received'
        request_query = 'Feedtype of id '+request_id

        # Add Data to the Activitylog database
        del_feedtype = Activitylog(user_id = user, activity = user_activity, request = request_query)
        db.session.add(del_feedtype)
        db.session.commit()

        flash('Delete Request for '+ feedtype_data.type +' Sent', 'success')
        return redirect(url_for('feedmill.feedtypes'))
       

    # Fetch Feed items
    feeditems = Feeditem.query.all()
    # Fetch Feed types
    feedtypes = Feedtype.query.all()

    if feedtypes:
        type_colors = color_sample(int(feedtypes[-1].id) + 3)
    else:
        type_colors = 0

    # Fetch all today's formulation
    formulations = Formulation.query.filter(Formulation.date == date.today()).all()

    # Fetch all pending notifications
    all_activities = Activitylog.query.filter(Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

    # Fetch all User specific notifications
    user_activities = Activitylog.query.filter(Activitylog.user_id == current_user.id, Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

    # User Image
    image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)

    return render_template("feedmgt/feedtypes.html", title="Feed Types", form = form, form2 = form2, ficon = "boxes",
                         date = datetime.now(), image_file=image_file, feeditems=feeditems, feedtypes=feedtypes, type_colors=type_colors, formulations=formulations, all_activities=all_activities, user_activities=user_activities)
    

# Route to fetch all feedtype chart data
@feedmill.route('/feedtype_id', methods=['POST'])
def feedtype_id():
    feed_id = request.get_data('id').decode('utf-8')
    feed_id = int(feed_id)
    feedtypes = Formulation.query.filter(Formulation.date == date.today(), Formulation.feedtype_id == feed_id, Formulation.formula != 0).all()

    typelist = []

    for feedtype in feedtypes:
        typeDict = {}
        typeDict['item'] = feedtype.feeditem.item
        typeDict['type'] = feedtype.feedtype.type
        typeDict['formula'] = feedtype.formula
        typelist.append(typeDict)

    return jsonify({'feedlist': typelist})


# Route to populate feedtype update form
@feedmill.route('/feedtype_form', methods=['POST'])
def feedtype_form():
    type_id = request.get_data('type_id').decode('utf_8')
    type_id = int(type_id)
    form_row = Formulation.query.filter(Formulation.date == date.today(), Formulation.feedtype_id == type_id).order_by(Formulation.feeditem_id.asc()).all()

    formula_list = []
    
    for form in form_row:
        formDict = {}
        formDict['id'] = form.feedtype_id
        formDict['type'] = form.feedtype.type
        formDict['item'] = form.feeditem.item
        formDict['formula'] = form.formula
        formula_list.append(formDict)

    return jsonify({'feedtypes': formula_list})


# FeedCost Route
@feedmill.route('/feedmgt/feed_cost', methods=['GET', 'POST'])
@login_required
def feedcost():
    # Fetch Feed cost
    year = date.today().strftime('%Y')
    month = date.today().strftime('%m')

    year_query = request.args.get('year', year)
    month_query = request.args.get('month', month)

    feedtypes = Feedtype.query.all()

    page =  request.args.get('page', 1, type=int)

    feedcost = Feedcost.query.filter(db.extract('year', Feedcost.date) == year_query).\
                    filter(db.extract('month', Feedcost.date) == month_query).order_by(Feedcost.id.desc()).paginate(page, current_app.config['MULTIPLE_DATA_PER_PAGE'], error_out=True)

    cost_dates = Feedcost.query.all()
    cost_month = []
    cost_year = []

    for data in cost_dates:
        c_month = data.date.strftime('%m')
        c_year = data.date.strftime('%Y')

        if c_month in cost_month:
            pass
        else:
            cost_month.append(c_month)

        if c_year in cost_year:
            pass
        else:
            cost_year.append(c_year)

     # Filter by month and year block query
    if request.method == 'POST' and request.form.get('check') == 'gobutton':
        month_select = request.form.get('month')
        year_select = request.form.get('year')

        if month_select and year_select:
            feedcost = Feedcost.query.filter(db.extract('year', Feedcost.date) == year_select).\
                    filter(db.extract('month', Feedcost.date) == month_select).order_by(Feedcost.id.desc()).paginate(page, current_app.config['MULTIPLE_DATA_PER_PAGE'], error_out=True)
            
            flash('Feed Cost at ' + numberMonth(month_select)+' - '+year_select, 'success')
            return redirect(url_for('feedmill.feedcost', month=month_select, year=year_select))
        else:
            flash('Please make a selection', 'warning')


    # HANDLE FEEDTYPE FILTER SEARCH
    if request.method == 'POST' and request.form.get('check') == 'feedtype_search':
        month_query = request.args.get('month', month)
        year_query = request.args.get('year', year)
        feedtype_query = request.form.get('feedtype_select')
        feedtype_query = int(feedtype_query)

        page = 1

        if feedtype_query:
            feedcost = Feedcost.query.filter(db.extract('year', Feedcost.date) == year_query).\
                    filter(db.extract('month', Feedcost.date) == month_query).\
                        filter(Feedcost.feedtype_id == feedtype_query).order_by(Feedcost.id.desc()).paginate(page, current_app.config['MULTIPLE_DATA_PER_PAGE'], error_out=True)

        else:
            flash('Please make a selection', 'warning')


    # Fetch all pending notifications
    all_activities = Activitylog.query.filter(Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

    # Fetch all User specific notifications
    user_activities = Activitylog.query.filter(Activitylog.user_id == current_user.id, Activitylog.status == 'pending').\
                            order_by(Activitylog.id.desc()).limit(3).all()

    # User Image
    image_file = url_for('static', filename='wt-profile-pics/'+current_user.picture)

    return render_template("feedmgt/feedcost.html", title="Feed Cost", ficon="dollar-sign",
                        date = datetime.now(), image_file=image_file, feedcost=feedcost, cost_month=cost_month, cost_year=cost_year, feedtypes=feedtypes, all_activities=all_activities, user_activities=user_activities)


