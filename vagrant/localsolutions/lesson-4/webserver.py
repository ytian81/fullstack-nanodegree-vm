from flask import Flask, render_template, request, redirect, url_for, jsonify, flash

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/restaurants/JSON')
def show_all_restaurants_json():
  restaurants = session.query(Restaurant).all()
  return jsonify(Restaurants=[restaurant.serialize for restaurant in restaurants])

@app.route('/')
@app.route('/restaurants')
def show_all_restaurants():
  restaurants = session.query(Restaurant).all()
  return render_template('restaurants.html', restaurants=restaurants)

@app.route('/restaurant/new', methods=['GET', 'POST'])
def add_restaurant():
  if request.method == 'GET':
    return render_template('newrestaurant.html')
  else:
    new_restaurant = Restaurant(name=request.form['new_restaurant_name'])
    session.add(new_restaurant)
    session.commit()
    flash('New Restaurant Added')
    return redirect(url_for('show_all_restaurants'))

@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def edit_restaurant(restaurant_id):
  to_edit_restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
  if request.method == 'GET':
    return render_template('editrestaurant.html', restaurant_id=restaurant_id,
            old_restaurant_name=to_edit_restaurant.name)
  else:
    old_name = to_edit_restaurant.name
    to_edit_restaurant.name = request.form['new_restaurant_name']
    new_name = to_edit_restaurant.name
    session.add(to_edit_restaurant)
    session.commit()
    flash('%s is updated as %s'%(old_name, new_name))
    return redirect(url_for('show_all_restaurants'))

@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def delete_restaurant(restaurant_id):
  to_delete_restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
  if request.method == 'GET':
    return render_template('deleterestaurant.html', restaurant_id=restaurant_id,
          delete_restaurant_name=to_delete_restaurant.name)
  else:
    old_name = to_delete_restaurant.name
    session.delete(to_delete_restaurant)
    session.commit()
    flash('%s is deleted'%(old_name))
    return redirect(url_for('show_all_restaurants'))

@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def show_restaurant_menu_json(restaurant_id):
  items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
  return jsonify(MenuItems=[item.serialize for item in items])

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def show_restaurant_item_json(restaurant_id, menu_id):
  items = session.query(MenuItem).filter_by(id=menu_id).all()
  return jsonify(MenuItems=[item.serialize for item in items])

@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def show_restaurant_menu(restaurant_id):
  restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
  items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
  return render_template('menu.html', restaurant_name=restaurant.name,
          restaurant_id=restaurant_id, items=items)

@app.route('/restaurant/<int:restaurant_id>/menu/new', methods=['GET', 'POST'])
def add_menu_item(restaurant_id):
  restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
  if request.method == 'GET':
    return render_template('newmenu.html', restaurant_id=restaurant_id)
  else:
    new_item = MenuItem(name=request.form['new_item_name'],
                        description=request.form['new_item_description'],
                        price=request.form['new_item_price'],
                        course=request.form['new_item_course'],
                        restaurant=restaurant)
    session.add(new_item)
    session.commit()
    flash('New Item Added')
    return redirect(url_for('show_restaurant_menu', restaurant_id=restaurant_id))

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET', 'POST'])
def edit_menu_item(restaurant_id, menu_id):
  to_edit_item = session.query(MenuItem).filter_by(id=menu_id).one()
  if request.method == 'GET':
    return render_template('editmenu.html', restaurant_id=restaurant_id, menu_id=menu_id,
           old_item_name=to_edit_item.name)
  else:
    old_name = to_edit_item.name
    to_edit_item.name=request.form['new_item_name']
    new_name = to_edit_item.name
    session.add(to_edit_item)
    session.commit()
    flash('%s is updated as %s'%(old_name, new_name))
    return redirect(url_for('show_restaurant_menu', restaurant_id=restaurant_id))

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET', 'POST'])
def delete_menu_item(restaurant_id, menu_id):
  to_delete_item = session.query(MenuItem).filter_by(id=menu_id).one()
  if request.method == 'GET':
    return render_template('deletemenu.html', restaurant_id=restaurant_id, menu_id=menu_id,
            delete_item_name=to_delete_item.name)
  else:
    old_name = to_delete_item.name
    session.delete(to_delete_item)
    session.commit()
    flash('%s is deleted'%(old_name))
    return redirect(url_for('show_restaurant_menu', restaurant_id=restaurant_id)) 

if __name__ == '__main__':
  app.secret_key = 'Super Secret Key'
  app.debug = True
  app.run(host='0.0.0.0', port=5000)
