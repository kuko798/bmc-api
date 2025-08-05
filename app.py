from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from marshmallow import Schema, fields, ValidationError

app = Flask(__name__)

CORS(
    app,
    resources={r"/members*": {"origins": [
        "http://localhost:5173",
        "https://your-frontend-domain.com"
    ]}},
    supports_credentials=False  
)

EBOARD = [
    {
      "position": "Co-President",
      "name": "Kobe Uko",
      "img": "ebimg\IMG_E6074.JPG",
      "hometown": "St.Louis, MO",
      "year": "Senior",
      "major": "Computer Science",
      "bio": "",
      "id": 1
    },
    {
      "position": "Co-President",
      "name": "Lateef Saheed",
      "img": "ebimg\IMG_E6073.JPG",
      "hometown": "Appleton, WI",
      "year": "Senior",
      "major": "Biology",
      "bio": "",
      "id": 2
    },
    {
      "position": "Secretary",
      "name": "Matthias Dagne",
      "img": "ebimg\IMG_E6069.JPG",
      "hometown": "Chicago, IL",
      "year": "Senior",
      "major": "Political Science",
      "bio": "",
      "id": 3
    },
    {
      "position": "Communications Chair",
      "name": "Nate Mcginnis",
      "img": "ebimg\IMG_E6070.JPG",
      "hometown": "Northbrook, IL",
      "year": "Senior",
      "major": "Political Science",
      "bio": "",
      "id": 4
    },
    {
      "position": "Events Coordinator",
      "name": "Richard Kariuki",
      "img": "ebimg\IMG_E6070.JPG",
      "hometown": "Rochester, MN",
      "year": "Junior",
      "major": "Materials Science & Engineering",
      "bio": "",
      "id": 5
    },
    {
      "position": "Digital Network Chair",
      "name": "Henos Aman",
      "img": "ebimg\IMG_E6068.JPG",
      "hometown": "Chicago, IL",
      "year": "Senior",
      "major": "Finance and Legal Studies",
      "bio": "",
      "id": 6
    },
    {
      "position": "Treasurer",
      "name": "Isaiah Dobbins",
      "img": "ebimg\IMG_E6072.JPG",
      "hometown": "Novi, MI",
      "year": "Senior",
      "major": "Neurobiology and Music",
      "bio": "",
      "id": 7
    }
    
]

class MemberSchema(Schema):
    id        = fields.Int(dump_only=True)
    position  = fields.Str(required=True)
    name      = fields.Str(required=True)
    hometown  = fields.Str(required=True)
    year      = fields.Str(required=True)
    major     = fields.Str(required=True)
    bio       = fields.Str()

member_schema   = MemberSchema()
members_schema  = MemberSchema(many=True)


def find_member(member_id: int):
    return next((m for m in EBOARD if m["id"] == member_id), None)


@app.get("/members")
def list_members():
    """Return the entire E-board roster."""
    return jsonify(members_schema.dump(EBOARD)), 200


@app.get("/members/<int:member_id>")
def get_member(member_id):
    """Return a single member (404 if not found)."""
    member = find_member(member_id)
    if member is None:
        abort(404, description="Member not found.")
    return jsonify(member_schema.dump(member)), 200


@app.post("/members")
def create_member():
    """Create a new member."""
    try:
        new_member = member_schema.load(request.get_json())  
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_member["id"] = max((m["id"] for m in EBOARD), default=0) + 1
    EBOARD.append(new_member)
    return jsonify(member_schema.dump(new_member)), 201


@app.put("/members/<int:member_id>")
def replace_member(member_id):
    """Full replace (or create) a member."""
    try:
        data = member_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    member = find_member(member_id)
    if member:
        member.update(data)
        member["id"] = member_id         
        return jsonify(member_schema.dump(member)), 200
    else:
        data["id"] = member_id
        EBOARD.append(data)
        return jsonify(member_schema.dump(data)), 201


@app.patch("/members/<int:member_id>")
def patch_member(member_id):
    """Partial update."""
    member = find_member(member_id)
    if member is None:
        abort(404, description="Member not found.")

    try:
        updates = member_schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400

    member.update(updates)
    return jsonify(member_schema.dump(member)), 200


@app.delete("/members/<int:member_id>")
def delete_member(member_id):
    """Delete a member (idempotent)."""
    member = find_member(member_id)
    if member:
        EBOARD.remove(member)
    return "", 204


@app.errorhandler(404)
def not_found(err):
    return jsonify(error=str(err)), 404

@app.errorhandler(400)
def bad_request(err):
    return jsonify(error=str(err)), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)