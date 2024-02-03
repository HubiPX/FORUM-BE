import unittest
import json
from flask_testing import TestCase
from main import app, db
from loguru import logger


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

    def test_admin_login(self):
        login_data = {
            "username": "admin",
            "password": "admin"
        }
        response = self.client.post('api/login', json=login_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["username"], "admin")
        self.assertEqual(response.json["is_admin"], 4)
        logger.info('Test 1 - poprawne logowanie ADMIN.')

        response = self.client.get('/api/logout')
        self.assertEqual(response.status_code, 200)
        logger.info('Test 2 - poprawne wylogowanie ADMIN.')

    def test_admin_show_users(self):
        login_data = {
            "username": "admin",
            "password": "admin"
        }
        response = self.client.post('api/login', json=login_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["username"], "admin")
        self.assertEqual(response.json["is_admin"], 4)
        logger.info('Test 1 - poprawne logowanie ADMIN.')

        response = self.client.get('/api/admin')
        self.assertEqual(response.status_code, 200)
        logger.info('Test 2 - poprawne pobranie listy użytkowników.')

        response = self.client.get('/api/logout')
        self.assertEqual(response.status_code, 200)
        logger.info('Test 2 - poprawne wylogowanie ADMIN.')

    def test_create_user(self):
        data = {
            "username": "test_user",
            "password": "test_password",
            "repassword": "test_password"
        }

        response = self.client.post('/api/users/create', json=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.decode('utf-8'), 'Utworzono konto pomyślnie!')
        logger.info('Test 2 - poprawne tworzenia konta.')

        login_data = {
            "username": "test_user",
            "password": "test_password"
        }
        response = self.client.post('api/login', json=login_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["username"], "test_user")
        self.assertEqual(response.json["is_admin"], 0)
        x = response.json["user_id"]
        logger.info('Test 2 - poprawne logowanie na test_user.')

        response = self.client.get('/api/logout')
        self.assertEqual(response.status_code, 200)
        logger.info('Test 2 - poprawne wylogowanie test_user.')

        login_data = {
            "username": "admin",
            "password": "admin"
        }
        response = self.client.post('api/login', json=login_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["username"], "admin")
        self.assertEqual(response.json["is_admin"], 4)
        logger.info('Test 2 - poprawne logowanie ADMIN.')

        data = {
            "days": "2580"
        }

        response = self.client.post(f'api/admin/{x}/delete', json=data)
        self.assertEqual(response.status_code, 200)
        logger.info('Test 2 - poprawne usunięcie test_user.')

        response = self.client.get('/api/logout')
        self.assertEqual(response.status_code, 200)
        logger.info('Test 2 - poprawne wylogowanie ADMIN.')

    def test_create_user_with_different_passwords(self):
        data = {
            "username": "test_user",
            "password": "test_password",
            "repassword": "different_password"
        }

        response = self.client.post('/api/users/create', json=data)
        self.assertEqual(response.status_code, 406)
        self.assertEqual(response.data.decode('utf-8'), 'Podane hasła są różne!')
        logger.info('Test 3 - niepoprawne tworzenia konta z różnymi hasłami.')

    def test_change_user(self):
        data = {
            "username": "test_user",
            "password": "test_password",
            "repassword": "test_password"
        }

        response = self.client.post('/api/users/create', json=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.decode('utf-8'), 'Utworzono konto pomyślnie!')
        logger.info('Test 2 - poprawne tworzenia konta.')

        login_data = {
            "username": "test_user",
            "password": "test_password"
        }
        response = self.client.post('api/login', json=login_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["username"], "test_user")
        self.assertEqual(response.json["is_admin"], 0)
        x = response.json["user_id"]
        logger.info('Test 2 - poprawne logowanie na test_user.')

        response = self.client.get('/api/logout')
        self.assertEqual(response.status_code, 200)
        logger.info('Test 2 - poprawne wylogowanie test_user.')

        login_data = {
            "username": "admin",
            "password": "admin"
        }
        response = self.client.post('api/login', json=login_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["username"], "admin")
        self.assertEqual(response.json["is_admin"], 4)
        logger.info('Test 2 - poprawne logowanie ADMIN.')

        for i in range(4):
            data = {
                "admin": f"{i}"
            }

            response = self.client.post(f'api/admin/{x}/lvl-admin', json=data)
            self.assertEqual(response.status_code, 200)
            logger.info(f'Test 2 - poprawne ustawienie admin-lvl na {i} dla test_user.')

        response = self.client.get(f'/api/admin/{x}/reset-password')
        self.assertEqual(response.status_code, 200)
        logger.info('Test 2 - poprawna zmiana hasła dla test_user.')

        login_data = {
            "new_score": "1000"
        }
        response = self.client.post(f'api/admin/{x}/set-score', json=login_data)
        self.assertEqual(response.status_code, 200)
        logger.info('Test 2 - poprawna zmiana ilości expa test_user.')

        data = {
            "days": "2580"
        }

        response = self.client.post(f'api/admin/{x}/delete', json=data)
        self.assertEqual(response.status_code, 200)
        logger.info('Test 2 - poprawne usunięcie test_user.')

        response = self.client.get('/api/logout')
        self.assertEqual(response.status_code, 200)
        logger.info('Test 2 - poprawne wylogowanie ADMIN.')


if __name__ == '__main__':
    unittest.main()
