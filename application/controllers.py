from flask import Flask,render_template, request, redirect, url_for, flash, session

from functools import wraps
from application.database import *

def routes(app):

    def login_required(role=None):
        def wrapper(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if 'email' not in session:
                    return redirect(url_for('login'))

                if role and session.get('role') != role:
                    flash('Unauthorized access','warning')
                    print('unauthorzed')
                    if session['role']=='admin':
                        return redirect(url_for('admin_dashboard'))
                    elif session['role']=='user':
                        return redirect(url_for('user_dashboard'))

                return f(*args, **kwargs)
            return decorated_function
        return wrapper


    @app.route('/')
    def index():
        return render_template('index.html')
    @app.route('/login',methods=['GET', 'POST'])
    def login():
        if request.method=='POST':
            
            email=request.form.get('email')
            password=request.form.get('password')
            user=User.query.filter_by(email=email,password=password).first()
            print(email, password)
            print(user)
            if email in session:
                session.clear()

            if user:
                if user.role == 'admin' :
                    session['email'] = email
                    session['name'] = user.name
                    session['user_id']= user.id
                    session['role']='admin'
                    flash('Hello Admin', 'success')
                    return redirect(url_for('admin_dashboard'))
                else:
                    session['email'] = email
                    session['user_id']= user.id
                    session['name'] = user.name
                    session['phone_number']=user.phone_number
                    session['role']='user'
                    flash('Login successful', 'success')
                    return redirect(url_for('user_dashboard'))
            else:
                flash('Invalid credentials', 'danger')
                print('Invalid credentials', 'danger')
                return redirect(url_for('login'))


        return render_template('login.html')
    @app.route('/register',methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            name=request.form.get('name')
            phone_number=request.form.get('phone_number')
            email = request.form['email']
            password = request.form['password']
            user=User.query.filter_by(email=email).first()
            if user:
                flash('Email already exists', 'danger')
                print('Email already exists', 'danger')
                return redirect(url_for('register'))
            else:
                new_user = User(email=email, password=password, name=name, phone_number=phone_number)
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful', 'success')
                print('Registration successful', 'success')
                return redirect(url_for('login'))
        return render_template('register.html')
    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))
    @app.route('/admin/dashboard')
    @login_required(role='admin')
    def admin_dashboard():

        if 'email' not in session:
            return redirect(url_for('login'))
        else:

            return render_template('admin_dashboard.html',admin=User.query.filter(User.role=='admin').first(),lots=Parking_lot.query.all())

    @app.route('/admin/edit_parking_lot/<lot_id>', methods=['GET', 'POST'])
    @login_required(role='admin')
    def edit_parking_lot(lot_id):
        if 'email' not in session:
            return redirect(url_for('login'))
        lot=Parking_lot.query.get(lot_id)
        if request.method == 'POST':
            action=request.form.get('spot_action')
            price = float(request.form.get('price'))
            lot.price = price
            spot_count = int(request.form.get('spot_count') or 0)
            empty_spots = Parking_spot.query.filter_by(lot_id=lot.id, status='A').count() 
            in_active_spots = Parking_spot.query.filter_by(lot_id=lot.id, is_active=False).all()
            in_active_spots_count = len(in_active_spots)
            if action== 'add':
                for i in range(int(spot_count)):
                    if in_active_spots_count > 0:
                        spot = in_active_spots.pop(0)
                        spot.status = 'A'
                        spot.is_active = True
                        in_active_spots_count = len(in_active_spots)
                    else:
                        new_spot = Parking_spot(lot_id=lot.id, status='A', is_active=True)
                        db.session.add(new_spot)
                lot.maximum_number_of_spot += int(spot_count)
                flash('spots added success','success')
            elif action == 'delete' :
                if empty_spots >= int(spot_count):
                    spots_to_delete = Parking_spot.query.filter_by(lot_id=lot.id, status='A',is_active=True).limit(int(spot_count)).all()
                    for spot in spots_to_delete:
                        spot.is_active = False
                    lot.maximum_number_of_spot -= int(spot_count)
                    flash('spots deleted','success')
                else:
                    flash('Not enough empty spots to delete', 'warning')
                    return redirect(url_for('edit_parking_lot', lot_id=lot.id))
            db.session.commit()
            flash('Parking lot updated successfully', 'success')
            return redirect(url_for('admin_dashboard'))
        return render_template('edit_parking_lot.html', email=session['email'],lot=lot)
    @app.route('/admin/dashboard/new_parking_lot', methods=['GET', 'POST'])
    @login_required(role='admin')
    def new_parking_lot():
        if 'email' not in session:
            return redirect(url_for('login'))
        if request.method == 'POST':
            prime_location_name=request.form.get('prime_location_name')
            address = request.form.get('address')
            price = request.form.get('price')
            pincode = request.form.get('pincode')
            maximum_number_of_spot = request.form.get('maximum_number_of_spot')
            lot= Parking_lot.query.filter_by(prime_location_name=prime_location_name,address=address,pincode=pincode).first()
            print(lot)
            if lot:
                flash('parking lot already exists', 'danger')
                return redirect(url_for('new_parking_lot'))
            else:
                new_lot = Parking_lot(prime_location_name=prime_location_name, address=address, price=price, pincode=pincode, maximum_number_of_spot=maximum_number_of_spot)
                db.session.add(new_lot)
                db.session.commit()

                for i in range(int(maximum_number_of_spot)):
                    new_spot = Parking_spot(lot_id=new_lot.id,status='A')
                    db.session.add(new_spot)
                db.session.commit()

                flash('New parking lot added successfully', 'success')
                return redirect(url_for('admin_dashboard'))

        return render_template('new_parking_lot.html', email=session['email'])
    
    @app.route('/admin/dasboard/deactivate_lot/<int:lot_id>', methods=['GET','POST'])
    @login_required(role='admin')
    def deactivate_lot(lot_id):
        lot = Parking_lot.query.get(lot_id)
        if request.method == 'POST':
            if not lot:
                flash("Parking lot not found.", "danger")
                return redirect(url_for('admin_dashboard'))
            occupied_spots = Parking_spot.query.filter_by(lot_id=lot.id, status='O').count()
            if occupied_spots > 0:
                flash("Cannot deactivate lot with active spots.", "warning")
                return redirect(url_for('admin_dashboard'))
            else:
                lot.status="inactive"
                db.session.commit()
                flash("lot deleted sucess",'success')
        return redirect(url_for('admin_dashboard'))
    
    @app.route('/admin/dashboard/inactive_lots', methods=['GET','POST'])
    @login_required(role='admin')
    def inactive_lots():
        if 'email' not in session:
            return redirect(url_for('login'))
        lots = Parking_lot.query.filter_by(status='inactive').all()
        return render_template('inactive_lots.html', email=session['email'], lots=lots,user=User.query.get(session['user_id']))
    @app.route('/activate_lot/<int:lot_id>', methods=['GET', 'POST'])
    @login_required(role='admin')
    def activate_lot(lot_id):
        lot = Parking_lot.query.get(lot_id)
        if request.method == 'POST':
            if not lot:
                flash("Parking lot not found.", "danger")
                return redirect(url_for('admin_dashboard'))
            else:
                lot.status="active"
                db.session.commit()
                flash("lot activated sucess",'success')
        return redirect(url_for('admin_dashboard'))
    @app.route('/deactivate_spot/<int:spot_id>', methods=['GET', 'POST'])
    def deactivate_spot(spot_id):
        if 'email' not in session:
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            spot = Parking_spot.query.get(spot_id)
            spot.is_active = False
            lot_id=spot.lot_id
            lot = Parking_lot.query.get(lot_id)
            lot.maximum_number_of_spot -= 1
            db.session.commit()
            flash("Spot deactivated successfully", "success")
           
        return redirect(url_for('admin_dashboard'))
    @app.route('/admin/users',methods=['GET'])
    @login_required(role='admin')
    def users():
        if 'email' not in session:
            return redirect(url_for('login'))
        users = User.query.all()
        return render_template('users.html', users=users,admin=User.query.get(1))
    @app.route('/user/dashboard', methods=['GET','POST'])
    @login_required(role='user')
    def user_dashboard():
        if 'email' not in session:
            return redirect(url_for('login'))
        user_id= session['user_id']
        user=User.query.get(user_id)
        reservations = Reserve_spot.query.filter_by(user_id=user_id).all()
        
        return render_template('user_dashboard.html', user=user,reservations=reservations)
    @app.route('/user/book', methods=['GET', 'POST'])
    @login_required(role='user')
    def searching_parking_lot():
        if 'email' not in session:
            return redirect(url_for('login'))
        email = session['email']
        name = session['name']
        if request.method == 'POST':
            filter_type = request.form.get('filter_type')
            search_query = request.form.get('search_query')
            lots=[]

            if search_query:
                if filter_type == 'location':
                    query = Parking_lot.query.filter(
                        Parking_lot.status == 'active',
                        Parking_lot.prime_location_name.ilike(f"%{search_query}%")
                    )
                elif filter_type == 'pincode':
                    query = Parking_lot.query.filter(
                        Parking_lot.status == 'active',
                        Parking_lot.pincode.ilike(f"%{search_query}%")
                    )
                else:
                    query = Parking_lot.query.filter(False)  
                    flash('No lots Found','warning')
                    flash('check address/pincode','info')
                lots = query.all()

                return render_template('searching_parking_lot.html',
                                    lots=lots,
                                    search_term=search_query,
                                    filter_type=filter_type,
                                    user=User.query.get(session['user_id'])
                                    )

        return render_template('searching_parking_lot.html',name=name,user=User.query.filter(User.id==str(session['user_id'])).first())
    @app.route('/user/book_spot/<int:lot_id>', methods=['GET', 'POST'])
    @login_required(role='user')
    def book_spot(lot_id):
        if 'email' not in session:
            return redirect(url_for('login'))
        email = session['email']
        user_id = session['user_id']
        booklot = Parking_lot.query.get(lot_id)
        spots= Parking_spot.query.filter_by(lot_id=lot_id, status='A', is_active=True).first()
        spot_id= spots.id
        if request.method == 'POST':
            vehicle_number = request.form.get('vehicle_number')

            new_reservation = Reserve_spot(
                spot_id=request.form.get('spot_id'),
                user_id=user_id,
                vehicle_number=vehicle_number
            )
            spots.status = 'O' 
            db.session.add(new_reservation)
            db.session.commit()
            flash('Spot booked successfully', 'success')
            return redirect(url_for('user_dashboard'))
        return render_template('book_spot.html', spot_id=spot_id, lot_id=lot_id, user_id=user_id)   
    @app.route('/user/dashboard/release_spot/<int:reservation_id>', methods=['GET','POST'])
    @login_required(role='user')
    def release_spot(reservation_id):
        if 'email' not in session:
            return redirect(url_for('login'))
        reservation = Reserve_spot.query.get(reservation_id)
        end_time = datetime.utcnow()
        lot=reservation.spot.lot
        duration = (end_time - reservation.start_time).total_seconds() / 3600
        estimated_cost = round(duration * lot.price , 2)
        if request.method == 'POST':
            if reservation:
                spot = Parking_spot.query.get(reservation.spot_id)
                spot.status = 'A' 
                reservation.end_time = end_time
                
                reservation.total_cost = estimated_cost  
                db.session.commit()
                flash('Spot released successfully', 'success')
                return redirect(url_for('user_dashboard'))
            else:
                flash('Reservation not found', 'danger')
                return redirect(url_for('user_dashboard'))
        return render_template('release_spot.html', reservation=reservation,estimated_cost=estimated_cost,end_time=end_time)     
    @app.route('/edit_profile/<int:user_id>', methods=['GET', 'POST'])
    def edit_profile(user_id):
        if 'email' not in session:
            return redirect(url_for('login'))
        user = User.query.get(user_id)
        if request.method == 'POST':
            user.name = request.form.get('name')
            user.phone_number = request.form.get('phone_number')
            new_password = request.form.get('password')
            if new_password:
                user.password = new_password
            db.session.commit()
            flash('Profile updated successfully', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        return render_template('edit_profile.html', user=user)
    @app.route('/user/summary/<int:user_id>', methods=['GET'])
    @login_required(role='user')
    def user_summary(user_id):
        if 'email' not in session:
            return redirect(url_for('login'))
        stats={}
        user_reservations=Reserve_spot.query.filter_by(user_id=user_id).all()
        total_amount_spent=0
        curr_parked=0
        active_reservations=[]
        for i in user_reservations:
            if i.total_cost:
                total_amount_spent+=i.total_cost
                curr_parked+=1
            else:
                active_reservations.append(i)
        return render_template('user_summary.html',
                               active_reservations=active_reservations,
                               total_reservations=len(user_reservations),
                               total_cost=total_amount_spent,
                               name=session['name'],
                               user=User.query.get(user_id))
    @app.route('/admin/lots/occupied_spot/details/<int:spot_id>',methods=['GET'])
    @login_required(role='admin')
    def occupied_spot_details(spot_id):
        if 'email' not in session:
            return redirect(url_for('login'))
        spot=Parking_spot.query.get(spot_id)

        reservation=Reserve_spot.query.filter_by(spot_id=spot_id,end_time=None).first()
        now=datetime.utcnow()
        total_time=(now-reservation.start_time).total_seconds() / 3600
        estimated_cost = round(total_time * spot.lot.price , 2)
        return render_template('occupied_spot_details.html',estimated_cost=estimated_cost,spot=spot,reservation=reservation)

    @app.route('/admin/summary',methods=['GET'])
    @login_required(role='admin')
    def admin_summary():
        stats={'total_lots':[],'total_spots':[],'occupied_spots':[],'total_reservations':[],
               "total_revenue":[],"total_users":[]}
        stats['total_lots'].append(Parking_lot.query.filter(Parking_lot.status=='active').count())
        stats['total_lots'].append(Parking_lot.query.filter(Parking_lot.status=='inactive').count())
        stats['total_spots'].append(Parking_spot.query.filter(Parking_spot.is_active==1).count())
        stats['occupied_spots'].append(Parking_spot.query.filter(Parking_spot.is_active==1,Parking_spot.status=='O').count())
        stats['total_reservations'].append(Reserve_spot.query.count())
        stats['total_reservations'].append(Reserve_spot.query.filter(Reserve_spot.end_time==None).count())
        reservations = Reserve_spot.query.filter(Reserve_spot.end_time != None).all()
        
        stats['total_revenue'].append(round(sum(r.total_cost for r in reservations if r.total_cost),2))

        stats['total_users'].append(User.query.filter(User.role=='user').count())
        return render_template('admin_summary.html',stats=stats,admin=User.query.get(1))





            