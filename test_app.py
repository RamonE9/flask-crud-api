from app import app
import json

client = app.test_client()

def get_token():

    response = client.post(
        '/login',
        json={
            'username': 'admin',
            'password': 'admin123'
        }
    )

    data = json.loads(response.data)

    return data['access_token']


def test_home():

    response = client.get('/')

    assert response.status_code == 200


def test_login_success():

    response = client.post(
        '/login',
        json={
            'username': 'admin',
            'password': 'admin123'
        }
    )

    assert response.status_code == 200


def test_login_failed():

    response = client.post(
        '/login',
        json={
            'username': 'wrong',
            'password': 'wrong'
        }
    )

    assert response.status_code == 401


def test_get_students():

    response = client.get('/students')

    assert response.status_code == 200


def test_get_single_student():

    response = client.get('/students/1')

    assert response.status_code in [200, 404]


def test_search_student():

    response = client.get(
        '/students/search?name=John'
    )

    assert response.status_code == 200


def test_xml_output():

    response = client.get(
        '/students?format=xml'
    )

    assert response.status_code == 200
    assert response.content_type == 'application/xml; charset=utf-8'


def test_add_student():

    token = get_token()

    response = client.post(
        '/students',
        headers={
            'Authorization': f'Bearer {token}'
        },
        json={
            'name': 'Test Student',
            'course': 'BSIT',
            'age': 20
        }
    )

    assert response.status_code == 201


def test_add_student_invalid():

    token = get_token()

    response = client.post(
        '/students',
        headers={
            'Authorization': f'Bearer {token}'
        },
        json={
            'name': '',
            'course': '',
            'age': ''
        }
    )

    assert response.status_code == 400


def test_update_student():

    token = get_token()

    response = client.put(
        '/students/1',
        headers={
            'Authorization': f'Bearer {token}'
        },
        json={
            'name': 'Updated Student',
            'course': 'BSCS',
            'age': 25
        }
    )

    assert response.status_code in [200, 404]


def test_delete_student():

    token = get_token()

    response = client.delete(
        '/students/1',
        headers={
            'Authorization': f'Bearer {token}'
        }
    )

    assert response.status_code in [200, 404]


def test_unauthorized_access():

    response = client.post(
        '/students',
        json={
            'name': 'Unauthorized',
            'course': 'BSIT',
            'age': 20
        }
    )

    assert response.status_code == 401