from datetime import datetime
from flask import current_app
from automate import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin

# USER MODEL
class User(db.Model, UserMixin):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    picture = db.Column(db.String(80), nullable=False, default='avatar.png')
    role = db.Column(db.String(80), nullable=False)
    activitylogs = db.relationship('Activitylog', backref='user', lazy=True, passive_deletes=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
        
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# USER MODEL

# ACTIVITIES MODEL
class Activitylog(db.Model):
    __tablename__ = 'activitylogs'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id, ondelete='CASCADE'))
    activity = db.Column(db.String(200))
    request = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')

    def __repr__(self):
        return f"Activitylog('{self.date}', '{self.user_id}', '{self.activity}', '{self.request}', '{self.status}')"
# ACTIVITIES MODEL

# FEEDMILL MODEL
class Feeditem(db.Model):
    __tablename__ = 'feeditems'
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(50))
    qty = db.Column(db.Float, default=0)
    price = db.Column(db.Float, default=0)
    date_created = db.Column(db.Date, default=datetime.utcnow)
    feedstocks = db.relationship('Feedstock', backref='feeditem', lazy=True, passive_deletes=True)
    formulations = db.relationship('Formulation', backref='feeditem', lazy=True, passive_deletes=True)
    purchases = db.relationship('Purchase', backref='feeditem', lazy=True, passive_deletes=True) 

    def __repr__(self):
        return f"Feeditem('{self.item}', '{self.qty}', '{self.price}')"

class Feedstock(db.Model):
    __tablename__ = 'feedstocks'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow)
    feeditem_id = db.Column(db.Integer, db.ForeignKey(Feeditem.id, ondelete='CASCADE'))
    o_qty = db.Column(db.Float, default=0)
    o_price = db.Column(db.Float, default=0)
    v_qty = db.Column(db.Float, default=0)
    v_price = db.Column(db.Float, default=0)
    p_qty = db.Column(db.Float, default=0)
    u_prod = db.Column(db.Float, default=0)
    c_qty = db.Column(db.Float, default=0)
    c_price = db.Column(db.Float, default=0)

    def __repr__(self):
        return f"Stock('{self.date}', '{self.feeditem_id}', '{self.o_qty}', '{self.o_price}')"

class Feedtype(db.Model):
    __tablename__ = 'feedtypes'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(150))
    date_created = db.Column(db.Date, default=datetime.utcnow)
    formulations = db.relationship('Formulation', backref='feedtype', lazy=True, passive_deletes=True)
    feedcosts = db.relationship('Feedcost', backref='feedtype', lazy=True, passive_deletes=True)
    productions = db.relationship('Production', backref='feedtype', lazy=True, passive_deletes=True) 

    def __repr__(self):
        return f"Feedtype('{self.type}')"

class Formulation(db.Model):
    __tablename__ = 'formulations'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow)
    feedtype_id = db.Column(db.Integer, db.ForeignKey(Feedtype.id, ondelete='CASCADE'))
    feeditem_id = db.Column(db.Integer, db.ForeignKey(Feeditem.id, ondelete='CASCADE'))
    formula = db.Column(db.Float, default=0)
    o_price = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)

    def __repr__(self):
        return f"Formulation('{self.date}', '{self.feedtype_id}', '{self.formula}', '{self.o_price}', '{self.total}')"

class Feedcost(db.Model):
    __tablename__ = 'feedcosts'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow)
    feedtype_id = db.Column(db.Integer, db.ForeignKey(Feedtype.id, ondelete='CASCADE'))
    price = db.Column(db.Float, default=0)

    def __repr__(self):
        return f"Cost('{self.date}', '{self.feedtype_id}', '{self.price}')"

# FEEDMILL MODEL

# STORE MODEL
class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    vendor = db.Column(db.String(100))
    date_created = db.Column(db.Date, default=datetime.utcnow)
    purchases = db.relationship('Purchase', backref='vendor', lazy=True, passive_deletes=True) 

    def __repr__(self):
        return f"Vendor('{self.vendor}', '{self.date_created}')"

class Farmitem(db.Model):
    __tablename__ = 'farmitems'
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100))
    date_created = db.Column(db.Date, default=datetime.utcnow)
    purchases = db.relationship('Purchase', backref='farmitem', lazy=True, passive_deletes=True) 
    receivables = db.relationship('Receivable', backref='farmitem', lazy=True, passive_deletes=True) 

    def __repr__(self):
        return f"Farmitem('{self.item}', '{self.date_created}')"

class Purchase(db.Model):
    __tablename__ = 'purchases'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow)
    feeditem_id = db.Column(db.Integer, db.ForeignKey(Feeditem.id, ondelete='CASCADE'))
    farmitem_id = db.Column(db.Integer, db.ForeignKey(Farmitem.id, ondelete='CASCADE'))
    vendor_id = db.Column(db.Integer, db.ForeignKey(Vendor.id, ondelete='CASCADE'))
    v_qty = db.Column(db.Float, default=0) 
    v_price = db.Column(db.Float, default=0)
    comment = db.Column(db.Text)

    def __repr__(self):
        return f"Purchase('{self.date}', '{self.feeditem_id}', '{self.farmitem_id}', '{self.vendor_id}', '{self.v_qty}', '{self.v_price}')"

class Production(db.Model):
    __tablename__ = 'productions'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow)
    feedtype_id = db.Column(db.Integer, db.ForeignKey(Feedtype.id, ondelete='CASCADE'))
    o_qty = db.Column(db.Float, default=0) 
    p_qty = db.Column(db.Float, default=0)
    issued_qty = db.Column(db.Float, default=0)
    department = db.Column(db.String(100))
    c_qty = db.Column(db.Float, default=0)
    comment = db.Column(db.Text)

    def __repr__(self):
        return f"Production('{self.date}', '{self.feedtype_id}', '{self.o_qty}', '{self.p_qty}', '{self.issued_qty}', '{self.department}', '{self.c_qty}')"

class Receivable(db.Model):
    __tablename__ = 'receivables'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow)
    farmitem_id = db.Column(db.Integer, db.ForeignKey(Farmitem.id, ondelete='CASCADE'))
    o_qty = db.Column(db.Float, default=0) 
    v_qty = db.Column(db.Float, default=0)
    v_price = db.Column(db.Float, default=0)
    issued_qty = db.Column(db.Float, default=0)
    department = db.Column(db.String(100))
    c_qty = db.Column(db.Float, default=0)
    comment = db.Column(db.Text)

    def __repr__(self):
        return f"Receivable('{self.date}', '{self.farmitem_id}', '{self.o_qty}', '{self.v_qty}', '{self.issued_qty}', '{self.department}', '{self.c_qty}')"

# STORE MODEL

# EGGSTORE MODEL
class Pen(db.Model):
    __tablename__ = 'pens'
    id = db.Column(db.Integer, primary_key=True)
    pen = db.Column(db.String(50))
    date_created = db.Column(db.Date, default=datetime.utcnow)
    eggstocks = db.relationship('Eggstock', backref='pen', lazy=True, passive_deletes=True) 
    allocations = db.relationship('Allocation', backref='pen', lazy=True, passive_deletes=True) 
    birdstocks = db.relationship('Birdstock', backref='pen', lazy=True, passive_deletes=True) 

    def __repr__(self):
        return f"Pen('{self.pen}', '{self.date_created}')"

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(50))
    date_created = db.Column(db.Date, default=datetime.utcnow)
    allocations = db.relationship('Allocation', backref='customer', lazy=True, passive_deletes=True)
    eggsales = db.relationship('Eggsale', backref='customer', lazy=True, passive_deletes=True)


    def __repr__(self):
        return f"Pen('{self.customer}', '{self.date_created}')"

class Eggstock(db.Model):
    __tablename__ = 'eggstocks'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow)
    pen_id = db.Column(db.Integer, db.ForeignKey(Pen.id, ondelete='CASCADE'))
    o_qty = db.Column(db.Float, default=0)
    p_qty = db.Column(db.Float, default=0)
    sales = db.Column(db.Float, default=0)
    cracks = db.Column(db.Float, default=0)
    c_qty = db.Column(db.Float, default=0)
    comment = db.Column(db.Text)

    def __repr__(self):
        return f"Eggstock('{self.date}', '{self.pen_id}', '{self.o_qty}', '{self.p_qty}', '{self.sales}', '{self.cracks}', '{self.c_qty}')"

class Allocation(db.Model):
    __tablename__ = 'allocations'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, db.ForeignKey(Customer.id, ondelete='CASCADE'))
    pen_id = db.Column(db.Integer, db.ForeignKey(Pen.id, ondelete='CASCADE'))
    size = db.Column(db.String(50))
    qty = db.Column(db.Float, default=0)

    def __repr__(self):
        return f"Allocation('{self.date}', '{self.customer_id}', '{self.pen_id}', '{self.size}', '{self.qty}')"

class Eggsale(db.Model):
    __tablename__ = 'eggsales'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, db.ForeignKey(Customer.id, ondelete='CASCADE'))
    o_bal = db.Column(db.Float, default=0)
    requested = db.Column(db.Float, default=0)
    supplied = db.Column(db.Float, default=0)
    returned = db.Column(db.Float, default=0)
    replaced = db.Column(db.Float, default=0)
    c_bal = db.Column(db.Float, default=0)
    size = db.Column(db.String(50))
    comment = db.Column(db.Text)

    def __repr__(self):
        return f"Eggsale('{self.date}', '{self.customer_id}', '{self.o_bal}', '{self.requested}', '{self.supplied}', '{self.returned}', '{self.returned}', '{self.replaced}', '{self.c_bal}')"

class Birdstock(db.Model):
    __tablename__ = 'birdstocks'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow)
    pen_id = db.Column(db.Integer, db.ForeignKey(Pen.id, ondelete='CASCADE'))
    o_stock = db.Column(db.Integer, default=0)
    mortality = db.Column(db.Integer, default=0)
    sales = db.Column(db.Integer, default=0)
    c_stock = db.Column(db.Integer, default=0)
    comment = db.Column(db.Text)

    def __repr__(self):
        return f"Birdstock('{self.date}', '{self.pen_id}', '{self.o_stock}', '{self.mortality}', '{self.sales}', '{self.c_stock}')"
# EGGSTORE MODEL
