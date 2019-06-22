from automate import db, create_app
from automate.models import (User, Activitylog, Feeditem, Feedstock, Feedtype, Formulation, Feedcost, Vendor, Farmitem, Purchase, Production, 
                    Receivable, Pen, Customer, Eggstock, Allocation, Eggsale, Birdstock)
from flask_script import Manager, Shell
from flask_migrate import MigrateCommand

app = create_app()
app.debug = True
manager = Manager(app)

# app_context = app.app_context().push()

def make_shell_context():
    return dict(app=app, db=db, User=User, Activitylog=Activitylog, Feeditem=Feeditem, Feedstock=Feedstock,
                 Feedtype=Feedtype, Formulation=Formulation, Feedcost=Feedcost, Vendor=Vendor, Farmitem=Farmitem, Purchase=Purchase, Production=Production, Receivable=Receivable, Pen=Pen, Customer=Customer, Eggstock=Eggstock, Allocation=Allocation, Eggsale=Eggsale, Birdstock=Birdstock)

manager.add_command('shell', Shell(make_context = make_shell_context))
manager.add_command('db', MigrateCommand)

# if __name__ == '__main__':
#     app.run(debug=True)
    
if __name__ == '__main__':
    manager.run()