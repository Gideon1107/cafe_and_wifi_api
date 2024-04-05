import random

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from werkzeug.exceptions import NotFound

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''
API_KEY = "TopSecretAPIKey"
app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self,column.name)
        return dictionary

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random", methods=["GET"])
def get_random_cafe():
    all_cafes = db.session.execute(db.select(Cafe)).scalars().all()
    random_cafe: Cafe = random.choice(all_cafes)
    return jsonify(random_cafe.to_dict())

@app.route("/all", methods=["GET"])
def get_all_cafe():
    all_cafes = db.session.execute(db.select(Cafe)).scalars().all()
    all_cafes_list = []
    for cafes in all_cafes:
        all_cafes_list.append(cafes.to_dict())
    all_cafes_dict = {
        "cafes": all_cafes_list
    }
    return jsonify(all_cafes_dict)



@app.route("/search")
def get_cafe_by_location():
    query_location = request.args.get('loc')
    cafe_by_location = db.session.execute(db.select(Cafe).where(Cafe.location == query_location))
    cafe_by_location: Cafe = cafe_by_location.scalar()
    try:
        if cafe_by_location.location == query_location:
            return jsonify(cafe_by_location.to_dict())
    except AttributeError:
        return jsonify({"errors":
                        {"Not Found": "Sorry, we don't have a cafe at that location"}
                        })

# HTTP POST - Create Record
@app.route("/add", methods=["GET","POST"])
def add_cafe():
    if request.method == 'POST':
        with app.app_context():
            new_cafe = Cafe(
                            name=request.form.get('name'),
                            map_url=request.form.get('map_url'),
                            img_url=request.form.get('img_url'),
                            location=request.form.get('location'),
                            seats=request.form.get('seats'),
                            has_toilet=bool(request.form.get('has_toilet')),
                            has_wifi=bool(request.form.get('has_wifi')),
                            has_sockets=bool(request.form.get('has_socket')),
                            can_take_calls=bool(request.form.get('can_take_calls')),
                            coffee_price=request.form.get('coffee_price')
                        )
            db.session.add(new_cafe)
            db.session.commit()
    return jsonify({"response":
                        {"success": "Successfully added the new cafe"}
                        })

# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def patch_cafe(cafe_id):
    try:
        cafe_to_patch = db.get_or_404(Cafe, cafe_id)
        print(cafe_to_patch)
        new_price = request.args.get('new_price')
        cafe_to_patch.coffee_price = new_price
        db.session.commit()
        print(new_price)
        return jsonify({"success": "Successfully updated the price"})
    except NotFound:
        return jsonify({"errors":
                        {"Not Found": "Sorry, a cafe with that id was not found in the database"}
                        }), 404

# HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>", methods=["GET", "DELETE"])
def delete_cafe(cafe_id):
    try:
        cafe_to_delete = db.get_or_404(Cafe, cafe_id)
        api_key = request.args.get('api-key')
        if api_key == API_KEY:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify({"success": "Cafe has been deleted successfully"}), 200
        else:
            return jsonify({"errors": "Invalid API Key"}), 403
    except NotFound:
        return jsonify({"errors":
                            {"Not Found": "Sorry, a cafe with that id was not found in the database"}}), 404


if __name__ == '__main__':
    app.run(debug=True)
