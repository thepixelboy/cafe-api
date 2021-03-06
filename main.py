import random
from flask import Flask, jsonify, render_template, request, make_response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

##Connect to Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)

        return dictionary

    def __init__(self, cafe_dict):
        self.name = cafe_dict["name"]
        self.map_url = cafe_dict["map_url"]
        self.img_url = cafe_dict["img_url"]
        self.location = cafe_dict["loc"]
        self.seats = cafe_dict["seats"]
        self.has_toilet = bool(cafe_dict["toilet"])
        self.has_wifi = bool(cafe_dict["wifi"])
        self.has_sockets = bool(cafe_dict["sockets"])
        self.can_take_calls = bool(cafe_dict["calls"])
        self.coffee_price = cafe_dict["coffee_price"]


@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    # Get the total number of rows
    row_count = Cafe.query.count()
    # Generate a random number for skipping some records
    random_offset = random.randint(0, row_count - 1)
    # Return the first record after skipping random_offset rows
    random_cafe = Cafe.query.offset(random_offset).first()

    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all")
def get_all_cafes():
    cafes = db.session.query(Cafe).all()

    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


@app.route("/search")
def search():
    location = request.args.get("loc")
    cafe = db.session.query(Cafe).filter_by(location=location).first()

    if cafe:
        return jsonify(cafe=cafe.to_dict(), status=200)
    else:
        # Using make_response to allow for status codes (404 Not found here)
        return make_response(jsonify(error={"Not found": "Sorry, we don't have a cafe at that location."}), 404)


## HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add_new_cafe():
    new_cafe = Cafe(request.form)
    db.session.add(new_cafe)
    db.session.commit()

    return make_response(jsonify(response={"success": "Successfully added the new cafe."}), 201)


## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    new_price = request.args.get("new-price")
    cafe = db.session.query(Cafe).get(cafe_id)

    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()

        return jsonify(response={"success": "Successfully updated the price."})
    else:
        return make_response(
            jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
        )


## HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = "physic-rang-rascal-hydro"
    requested_api = request.args.get("api-key")

    if api_key == requested_api:
        cafe = db.session.query(Cafe).get(cafe_id)

        if cafe:
            db.session.delete(cafe)
            db.session.commit()

            return make_response(jsonify(response={"success": "Successfully deleted the cafe from the database."}))
        else:
            return make_response(
                jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
            )
    else:
        return make_response(
            jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403
        )


if __name__ == "__main__":
    app.run(debug=True)
