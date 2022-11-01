from flask import Flask, jsonify, request
import os
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPDigestAuth
from flask_migrate import Migrate


base_dir = os.path.dirname(__file__)

app = Flask(__name__)

auth = HTTPDigestAuth()

app.config['SECRET_KEY'] = 'secret key here'

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
    os.path.join(base_dir, "db.sqlite")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

ids = {'aws': 'candidate'}


class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    amount = db.Column(db.Integer, default=0)


class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale = db.Column(db.Float, default=0)


migrate = Migrate(app, db)


@app.route('/')
def aws():
    return 'AWS'


@auth.get_password
def get_pw(id):
    if id in ids:
        return ids.get(id)
    return None


@app.route('/secret')
@auth.login_required
def digest():
    return 'SUCCESS'


@app.route('/v1/stocks', methods=['GET', 'POST', 'DELETE'])
def stocks():
    if request.method == 'POST':
        if not request.json['name'] or not request.json['amount']:
            return {"message": "ERROR"}
        name = request.json['name']
        amount = request.json['amount']
        if type(amount) != int:
            return {"message": "ERROR"}
        stock = Stock(name=name, amount=amount)
        db.session.add(stock)
        db.session.commit()
        res = jsonify(request.json)
        res.headers['Location'] = f'{request.host_url}v1/stocks/{name}'
        return res
        # post時の処理
    elif request.method == 'GET':
        stocks = Stock.query.order_by(Stock.name).all()
        items = {}
        for stock in stocks:
            items[stock.name] = stock.amount
        return items

    else:
        Stock.query.delete()
        db.session.commit()
        return {'message': 'Successfully deleted.'}


@app.route("/v1/stocks/<name>", methods=['GET'])
def stock(name):
    try:
        stock = Stock.query.filter_by(name=name).one()
    except Exception:
        return {"message": "ERROR"}
    return {stock.name: stock.amount}


@app.route('/v1/sales', methods=['GET', 'POST'])
def sales():
    if request.method == 'POST':
        if not request.json['name']:
            return {"message": "ERROR"}
        name = request.json['name']
        if request.json['amount']:
            amount = request.json['amount']
        else:
            amount = 1
        if type(amount) != int or type(name) != str:
            return {"message": "ERROR"}
        if request.json['price']:
            price = request.json['price']
        else:
            price = 0

        try:
            stock = Stock.query.filter_by(name=name).one()
        except Exception:
            return {"message": "ERROR"}

        if stock.amount < amount:
            amount = stock.amount
        stock.amount -= amount
        db.session.add(stock)

        try:
            sale = Sale.query.one_or_none()
        except Exception:
            return {"message": "ERROR"}

        if sale is None:
            sale = Sale()
        add_sale = amount * price
        sale.sale += add_sale
        db.session.add(sale)
        db.session.commit()

        res = jsonify(request.json)
        res.headers['Location'] = f'{request.host_url}v1/sales/{name}'
        return res

    else:
        try:
            sale = Sale.query.one_or_none()
        except Exception:
            return {"message": "ERROR"}

        if sale is None:
            sale = Sale()
            db.session.add(sale)
            db.session.commit()

        return {'sale': round(sale.sale, 2)}


if __name__ == "__main__":
    app.run(debug=True, port=8080)
