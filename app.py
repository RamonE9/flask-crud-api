from flask import Flask, request, jsonify, Response
from flask_mysqldb import MySQL
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required
)
from dicttoxml import dicttoxml

app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'school_db'

app.config['JWT_SECRET_KEY'] = 'secretkey'

mysql = MySQL(app)
jwt = JWTManager(app)

@app.route('/')
def home():
    return jsonify({
        'message': 'Flask CRUD API is running'
    })


@app.route('/login', methods=['POST'])
def login():

    try:
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        # Simple hardcoded login
        if username == 'admin' and password == 'admin123':

            access_token = create_access_token(identity=username)

            return jsonify({
                'access_token': access_token
            }), 200

        return jsonify({
            'error': 'Invalid username or password'
        }), 401

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500



@app.route('/students', methods=['POST'])
@jwt_required()
def add_student():

    try:
        data = request.get_json()

        name = data.get('name')
        course = data.get('course')
        age = data.get('age')

        # Input validation
        if not name or not course or not age:
            return jsonify({
                'error': 'All fields are required'
            }), 400

        cur = mysql.connection.cursor()

        query = """
        INSERT INTO studebts(name, course, age)
        VALUES(%s, %s, %s)
        """

        values = (name, course, age)

        cur.execute(query, values)

        mysql.connection.commit()

        cur.close()

        return jsonify({
            'message': 'Student added successfully'
        }), 201

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/students', methods=['GET'])
def get_students():

    try:

        format_type = request.args.get('format', 'json')

        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM studebts")

        rows = cur.fetchall()

        cur.close()

        students = []

        for row in rows:
            students.append({
                'id': row[0],
                'name': row[1],
                'course': row[2],
                'age': row[3]
            })

        # XML OUTPUT
        if format_type == 'xml':

            xml = dicttoxml(
                students,
                custom_root='students',
                attr_type=False
            )

            return Response(
                xml,
                mimetype='application/xml'
            )

        # JSON OUTPUT
        return jsonify(students)

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/students/<int:id>', methods=['GET'])
def get_student(id):

    try:

        cur = mysql.connection.cursor()

        query = "SELECT * FROM students WHERE id=%s"

        cur.execute(query, (id,))

        row = cur.fetchone()

        cur.close()

        if row is None:
            return jsonify({
                'error': 'Student not found'
            }), 404

        student = {
            'id': row[0],
            'name': row[1],
            'course': row[2],
            'age': row[3]
        }

        return jsonify(student)

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500



@app.route('/students/<int:id>', methods=['PUT'])
@jwt_required()
def update_student(id):

    try:

        data = request.get_json()

        name = data.get('name')
        course = data.get('course')
        age = data.get('age')

        if not name or not course or not age:
            return jsonify({
                'error': 'All fields are required'
            }), 400

        cur = mysql.connection.cursor()

        query = """
        UPDATE students
        SET name=%s, course=%s, age=%s
        WHERE id=%s
        """

        values = (name, course, age, id)

        cur.execute(query, values)

        mysql.connection.commit()

        cur.close()

        return jsonify({
            'message': 'Student updated successfully'
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/students/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_student(id):

    try:

        cur = mysql.connection.cursor()

        query = "DELETE FROM students WHERE id=%s"

        cur.execute(query, (id,))

        mysql.connection.commit()

        cur.close()

        return jsonify({
            'message': 'Student deleted successfully'
        })

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/students/search', methods=['GET'])
def search_students():

    try:

        keyword = request.args.get('name')

        if not keyword:
            return jsonify({
                'error': 'Please provide name parameter'
            }), 400

        cur = mysql.connection.cursor()

        query = """
        SELECT * FROM students
        WHERE name LIKE %s
        """

        search_value = "%" + keyword + "%"

        cur.execute(query, (search_value,))

        rows = cur.fetchall()

        cur.close()

        students = []

        for row in rows:
            students.append({
                'id': row[0],
                'name': row[1],
                'course': row[2],
                'age': row[3]
            })

        return jsonify(students)

    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True)