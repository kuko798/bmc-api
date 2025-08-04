from flask import Flask, request, jsonify, abort
from marshmallow import Schema, fields, ValidationError

app = Flask(__name__)


EBOARD = [
    {
      "position": "Co-President",
      "name": "Kobe Uko",
      "hometown": "St.Louis, MO",
      "year": "Senior",
      "major": "Computer Science",
      "bio": "",
      "id": 1
    },
    {
      "position": "Co-President",
      "name": "Lateef Saheed",
      "hometown": "Appleton, WI",
      "year": "Senior",
      "major": "Biology",
      "bio": "",
      "id": 2
    },
    {
      "position": "Secretary",
      "name": "Matthias Dagne",
      "hometown": "Chicago, IL",
      "year": "Senior",
      "major": "Political Science",
      "bio": "",
      "id": 3
    },
    {
      "position": "Communications Chair",
      "name": "Nate Mcginnis",
      "hometown": "Northbrook, IL",
      "year": "Senior",
      "major": "Political Science",
      "bio": "",
      "id": 4
    },
    {
      "position": "Events Coordinator",
      "name": "Richard Kariuki",
      "hometown": "Rochester, MN",
      "year": "Junior",
      "major": "Materials Science & Engineering",
      "bio": "",
      "id": 5
    },
    {
      "position": "Digital Network Chair",
      "name": "Henos Aman",
      "hometown": "Chicago, IL",
      "year": "Senior",
      "major": "Finance and Legal Studies",
      "bio": "",
      "id": 6
    },
    {
      "position": "Treasurer",
      "name": "Isaiah Dobbins",
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

member_schema  = MemberSchema()
members_schema = MemberSchema(many=True)


def find_member(member_id: int):
    return next((m for m in EBOARD if m["id"] == member_id), None)



@app.route("/members", methods=["GET"])
def list_members():
    """Return the entire E-board roster."""
    return members_schema.jsonify(EBOARD)

@app.route("/members/<int:member_id>", methods=["GET"])
def get_member(member_id):
    """Return a single member (404 if not found)."""
    member = find_member(member_id)
    if not member:
        abort(404, description="Member not found.")
    return member_schema.jsonify(member)

@app.route("/members", methods=["POST"])
def create_member():
    """Create a new member and return it with 201 status."""
    try:
        new_member = member_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_member["id"] = (max(m["id"] for m in EBOARD) + 1) if EBOARD else 1
    EBOARD.append(new_member)
    return member_schema.jsonify(new_member), 201

@app.route("/members/<int:member_id>", methods=["PUT"])
def update_member(member_id):
    """Replace an existing member (create if absent)."""
    try:
        updates = member_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    member = find_member(member_id)
    if member:
        member.update(updates)
        return member_schema.jsonify(member)
    else: 
        updates["id"] = member_id
        EBOARD.append(updates)
        return member_schema.jsonify(updates), 201

@app.route("/members/<int:member_id>", methods=["PATCH"])
def patch_member(member_id):
    """Partial update."""
    member = find_member(member_id)
    if not member:
        abort(404, description="Member not found.")

  
    try:
        updates = member_schema.load(request.get_json(), partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400

    member.update(updates)
    return member_schema.jsonify(member)

@app.route("/members/<int:member_id>", methods=["DELETE"])
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
    app.run(debug=True)
