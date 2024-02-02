import unittest
import json
from flask_testing import TestCase
from main import app, db


class TestUserBlueprint(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_database.db'
        return app

    def setUp(self):
        db.create_all()

    #def tearDown(self):
        #db.session.remove()
        #db.drop_all()

    def test_create_user(self):
        data = {
            "username": "test_users",
            "password": "test_password",
            "repassword": "test_password"
        }

        response = self.client.post('/api/users/create', json=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.decode('utf-8'), 'Utworzono konto pomyślnie!')
        print("Test - poprawne tworzenia konta.")

    def test_create_user_with_different_passwords(self):
        data = {
            "username": "test_user",
            "password": "test_password",
            "repassword": "different_password"
        }

        response = self.client.post('/api/users/create', json=data)
        self.assertEqual(response.status_code, 406)
        self.assertEqual(response.data.decode('utf-8'), 'Podane hasła są różne!')
        print("Test - niepoprawne tworzenia konta z różnymi hasłami.")

    def test_test_user_login(self):
        login_data = {
            "username": "test_user",
            "password": "test_password"
        }
        response = self.client.post('api/login', json=login_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["username"], "test_user")
        self.assertEqual(response.json["is_admin"], 0)
        x = response.json["user_id"]
        print("Test - poprawne logowanie na test_user.")

    def test_admin_login(self):
        login_data = {
            "username": "admin",
            "password": "admin"
        }
        response = self.client.post('api/login', json=login_data)

        # Sprawdź, czy odpowiedź jest poprawna
        self.assertEqual(response.status_code, 200)
        # Dodatkowe sprawdzenie, czy uzyskane dane są zgodne z oczekiwaniami
        self.assertEqual(response.json["username"], "admin")
        self.assertEqual(response.json["is_admin"], 4)  # Przykładowe sprawdzenie, oczekuje 0 dla admina
        print("Test - poprawne logowanie ADMIN.")

        del_user_data = {
            "days": "2580"
        }

        response = self.client.post(f'api/admin/27/delete', json=del_user_data)
        self.assertEqual(response.status_code, 200)
        print("Test - poprawne usunięcie test_user.")


if __name__ == '__main__':
    unittest.main()
