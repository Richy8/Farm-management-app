import os
from random import sample
from datetime import datetime, date, timedelta
from flask import current_app
from automate import db
from automate.models import Feeditem, Feedtype, Formulation, Feedcost, Feedstock, Production, Farmitem, Receivable, Eggstock, Pen
from automate.feedmill.routes import feedmill


# Set colors list
def color_sample(num):
    colors = ['red', 'green', 'blue', 'deep-purple', 'brown', 'deep-orange', 'teal', 'blue-grey', 'purple', 'cyan', 'elegant-color', 'unique-color', 'mdb-color', 'stylish-color', 'grey', 'black accent-3', 'secondary-color', 'pink darken-2', 'red accent-1', 'blue-gradient', 'aqua-gradient', 'purple-gradient', 'orange darken-4']
    return sample(colors, num)

# Template filter
@feedmill.app_template_filter()
def numberFormat(value):
    new_value = round(int(value), 0)
    return format(new_value, ',d')

# Template Filter
@feedmill.app_template_filter()
def tonnesToBag(value):
    new_value =  round(int(value*20), 0)
    return format(new_value, ',d')

# Template filter
@feedmill.app_template_filter()
def numberDecimal(value):
    return round(value, 2)

# Template filter
@feedmill.app_template_filter()
def numberMonth(value):
    if value == '01':
        return 'January'
    elif value == '02':
        return 'February'
    elif value == '03':
        return 'March'
    elif value == '04':
        return 'April'
    elif value == '05':
        return 'May'
    elif value == '06':
        return 'June'
    elif value == '07':
        return 'July'
    elif value == '08':
        return 'August'
    elif value == '09':
        return 'September'
    elif value == '10':
        return 'October'
    elif value == '11':
        return 'November'
    elif value == '12':
        return 'December'

# Template filter
@feedmill.app_template_filter()
def numberDecreament(value):
    total_feed = Feedtype.query.count()
    total_feed = int(total_feed) + 1
    new_val = int(value) - total_feed
    return new_val

# Template filter
@feedmill.app_template_filter()
def wordTruncate(value):
    if len(value) > 5:
        value = value[0:5]+'..'
    else:
        pass
    return value

# Template filter

# Daily Feed Stock Updates
def update():
    today = date.today()
    yesterday = today - timedelta(days=1)
    items = Feeditem.query.all()
    check_today = Feedstock.query.filter(Feedstock.date == today).all()
    check_yesterday = Feedstock.query.filter(Feedstock.date == yesterday).all()
    if check_today:
        pass
    else:
        for item in items:
            daily = Feedstock(date=today, feeditem_id=item.id)
            db.session.add(daily)

        db.session.commit()

        for y_item in check_yesterday:
            _ = Feedstock.query.filter(Feedstock.date == today, Feedstock.feeditem_id == y_item.feeditem_id).\
                            update({'o_qty':y_item.c_qty, 'o_price':y_item.c_price, 'c_qty':y_item.c_qty, 'c_price':y_item.c_price})

        db.session.commit()
    
    # Update Formulation For Today
    form_yesterday = Formulation.query.filter(Formulation.date == yesterday).all()
    form_today = Formulation.query.filter(Formulation.date == today).all()
    if form_today:
        pass
    else:
        get_feedtypes = Feedtype.query.all()
        get_feeditems = Feeditem.query.all()
        
        for feed_type in get_feedtypes:
            for feed_item in get_feeditems:
                daily_formulation = Formulation(date=today, feedtype_id=feed_type.id, feeditem_id=feed_item.id)
                db.session.add(daily_formulation)

        db.session.commit()

        for y_form in form_yesterday:
            _ = Formulation.query.\
                filter(Formulation.date == today, Formulation.feedtype_id == y_form.feedtype_id, Formulation.feeditem_id == y_form.feeditem_id).\
                    update({'formula': y_form.formula})
        
        db.session.commit()
    
    # Cost update
    feedtype = Feedtype.query.all()
    if feedtype:
        for f_type in feedtype:
            check_cost = Feedcost.query.filter(Feedcost.date == today, Feedcost.feedtype_id == f_type.id).first()
            if check_cost:
                pass
            else:
                upd8_cost = Feedcost(date=today, feedtype_id=f_type.id)
                db.session.add(upd8_cost)
        
            # Update the opening stock on the formulation table
            current_stock = Feedstock.query.filter(Feedstock.date == today).order_by(Feedstock.feeditem_id.asc()).all()
            for c_stock in current_stock:
                _ = Formulation.query.filter(Formulation.date == today, Formulation.feeditem_id == c_stock.feeditem_id).\
                                    update({'o_price':c_stock.o_price})

        db.session.commit()
        
        all_formulation = Formulation.query.filter(Formulation.date == today).all()
        for form in all_formulation:
            total = float(form.formula * form.o_price)
            
            _ = Formulation.query.\
                    filter(Formulation.date == today, Formulation.feedtype_id == form.feedtype_id, Formulation.feeditem_id == form.feeditem_id).\
                    update({'total': total})
        
        db.session.commit()

        # Fetch Overhead FeedCost
        filepath = os.path.join(current_app.root_path, 'overhead.txt')
        with open(filepath, 'r') as reader:
            feed_cost = int(reader.read())
        
        # Set Feedlist Array to hold feed total
        feedlist = []
        sum = 0

        costs = Feedcost.query.filter_by(date = today).all()
        for cost in costs:
            formulations = Formulation.query.filter(Formulation.date == today, Formulation.feedtype_id == cost.feedtype_id).all()
            for form in formulations:
                feedlist.append(form.total)

            for f in feedlist:
                sum = sum + f
                    
            total_cost = (float(sum) + feed_cost) / 20
            total_cost = float(total_cost)
            _ = Feedcost.query.filter(Feedcost.date == today, Feedcost.feedtype_id == cost.feedtype_id).\
                            update({'price': total_cost})

            feedlist.clear()
            sum = 0

        db.session.commit()

    else:
        pass

# Daily Production Update
def updateproduction():
    today = date.today()
    yesterday = today - timedelta(days=1)
    yesterday_production = Production.query.filter(Production.date == yesterday).all()
    today_production = Production.query.filter(Production.date == today).all()

    # Check if today_production exist in production db
    feedtypes = Feedtype.query.all()
    for f_type in feedtypes:
        today_feeds = Production.query.filter(Production.date == today, Production.feedtype_id == f_type.id).first()
        if today_feeds:
            pass
        else:
            new_prod_row = Production(date = today, feedtype_id = f_type.id)
            db.session.add(new_prod_row)
            db.session.commit()

    # Check if yesterday production exists in production db
    if yesterday_production:
        for y_prod in yesterday_production:
            _ = Production.query.filter(Production.date == today, Production.feedtype_id == y_prod.feedtype_id).\
                            update({'o_qty': y_prod.c_qty, 'c_qty': y_prod.c_qty})
            
        db.session.commit()
    else:
        pass


# Daily update of receivable database
def receivable_update():
    today = date.today()
    yesterday = today - timedelta(days=1)
    yesterday_receivable = Receivable.query.filter(Receivable.date == yesterday).all()
    today_receivable = Receivable.query.filter(Receivable.date == today).all()

    # Check if today receivable exists
    if today_receivable:
        pass
    else:
        all_farmitems = Farmitem.query.all()
        for farm in all_farmitems:
            new_receivable_row = Receivable(date = today, farmitem_id = farm.id)
            db.session.add(new_receivable_row)
            
        db.session.commit()

        # Check if yesterday production exists in production db
        if yesterday_receivable:
            for y_receive in yesterday_receivable:
                _ = Receivable.query.filter(Receivable.date == today, Receivable.farmitem_id == y_receive.farmitem_id).\
                                update({'o_qty': y_receive.c_qty, 'c_qty': y_receive.c_qty, 'v_price': y_receive.v_price})
               
            db.session.commit()
        else:
            pass


# Daily update of Eggstock
def eggstock_update():
    today = date.today()
    yesterday = today - timedelta(days=1)
    _ = Eggstock.query.filter(Eggstock.date == yesterday).all()
    today_eggstock = Eggstock.query.filter(Eggstock.date == today).all()

    # Check if eggstock for today exists
    if today_eggstock:
        pass
    else:
        all_pen = Pen.query.all()
        for pen in all_pen:
            get_yesterday_stock = Eggstock.query.filter(Eggstock.date == yesterday, Eggstock.pen_id == pen.id).first()

            if get_yesterday_stock:
                new_eggstock = Eggstock(date=today, pen_id=pen.id, o_qty=get_yesterday_stock.c_qty)
                db.session.add(new_eggstock)
                db.session.commit()

                # Update the new closing stock
                new_eggstock.c_qty = (new_eggstock.o_qty + new_eggstock.p_qty) - (new_eggstock.sales + new_eggstock.cracks)
                db.session.commit()

            else:
                pass


# update()
# receivable_update()
# updateproduction()
# eggstock_update()