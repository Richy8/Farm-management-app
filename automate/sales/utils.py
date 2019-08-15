import os
from datetime import datetime, date, timedelta
from flask import current_app
from automate import db
from automate.models import Customer, Salescost
from automate.sales.routes import sales


# Template Filter
@sales.app_template_filter()
def wordSeparator(value):
    word_split = value.split("_")
    return " ".join(word_split)


# Insert EGG size into the Salescost db
def insert_eggsize():
    eggcost = Salescost.query.filter(Salescost.category == 'Egg').count()

    if eggcost > 0:
        pass
    else:
        pullet = Salescost(category='Egg', sales_type='Pullet')
        small = Salescost(category='Egg', sales_type='Small')
        medium = Salescost(category='Egg', sales_type='Medium')
        big = Salescost(category='Egg', sales_type='Big')
        adult = Salescost(category='Egg', sales_type='Adult')
        beij = Salescost(category='Egg', sales_type='BEIJ')

        db.session.add_all([pullet,small,medium,big,adult,beij])
        db.session.commit()

# Insert crop type into Salescost db
def insert_croptype():
    croptypes = Salescost.query.filter(Salescost.category == 'Crop').count()

    if croptypes > 0:
        pass
    else:
        cassava = Salescost(category ='Crop', sales_type='Cassava')
        palms = Salescost(category ='Crop', sales_type='Palms')
        ugwu = Salescost(category ='Crop', sales_type='Ugwu')
        typeA = Salescost(category ='Crop', sales_type='TypeA')
        typeB = Salescost(category ='Crop', sales_type='TypeB')
        typeC = Salescost(category ='Crop', sales_type='TypeC')
        typeD = Salescost(category ='Crop', sales_type='TypeD')
        typeE = Salescost(category ='Crop', sales_type='TypeE')
        typeF = Salescost(category ='Crop', sales_type='TypeF')
        suckers = Salescost(category ='Crop', sales_type='Suckers')

        db.session.add_all([cassava, palms, ugwu, typeA, typeB, typeC, typeD, typeE, typeF, suckers])
        db.session.commit()


# Insert Bird type into the Salescost db
def insert_birdtype():
    birdcost = Salescost.query.filter(Salescost.category == 'Bird').count()

    if birdcost > 0:
        pass
    else:
        poc = Salescost(category='Bird', sales_type='POC')
        pol = Salescost(category='Bird', sales_type='POL')
        spent_layer = Salescost(category='Bird', sales_type='Spent_Layer')
        broiler = Salescost(category='Bird', sales_type='Broiler')
        noiler = Salescost(category='Bird', sales_type='Noiler')
        cockerel = Salescost(category='Bird', sales_type='Cockerel')

        db.session.add_all([poc,pol,spent_layer,broiler,noiler,cockerel])
        db.session.commit()

    
# Insert Dressed Bird type into the Salescost db
def insert_dressed_birdtype():
    dressed_bird_cost = Salescost.query.filter(Salescost.category == 'Dressed_bird').count()

    if dressed_bird_cost > 0:
        pass
    else:
        cock = Salescost(category='Dressed_bird', sales_type='Cock')
        layer = Salescost(category='Dressed_bird', sales_type='Layer')
        broiler = Salescost(category='Dressed_bird', sales_type='Broiler')

        db.session.add_all([cock, layer, broiler])
        db.session.commit()


# Insert Manure type into the Salescost db
def insert_manure_type():
    manure_cost = Salescost.query.filter(Salescost.category == 'Manure').count()

    if manure_cost > 0:
        pass
    else:
        black = Salescost(category='Manure', sales_type='Black')
        white = Salescost(category='Manure', sales_type='White')

        db.session.add_all([black, white])
        db.session.commit()


# Insert Sacks type into the Salescost db
def insert_sack_type():
    sack_cost = Salescost.query.filter(Salescost.category == 'Sack').count()

    if sack_cost > 0:
        pass
    else:
        big = Salescost(category='Sack', sales_type='Big')
        small = Salescost(category='Sack', sales_type='Small')

        db.session.add_all([big, small])
        db.session.commit()