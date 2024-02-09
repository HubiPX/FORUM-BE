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


    # definicje używane w wielu testach wykorzystywane poprzez self.

    def admin_login(self):
        login_data = {
            "username": "admin",
            "password": "admin"
        }
        response = self.client.post('api/login', json=login_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["username"], "admin")
        self.assertEqual(response.json["is_admin"], 4)
        # logger.info('Test - poprawne logowanie ADMIN.')
        return 0

    def admin_logout(self):
        response = self.client.get('/api/logout')
        self.assertEqual(response.status_code, 200)
        # logger.info('Test - poprawne wylogowanie ADMIN.')
        return 0

    def create_user(self):
        data = {
            "username": "test_user",
            "password": "test_password",
            "repassword": "test_password"
        }

        response = self.client.post('/api/users/create', json=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.decode('utf-8'), 'Utworzono konto pomyślnie!')
        # logger.info('Test - poprawne tworzenia konta.')
        return 0

    def login_user(self):
        login_data = {
            "username": "test_user",
            "password": "test_password"
        }
        response = self.client.post('api/login', json=login_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["username"], "test_user")
        self.assertEqual(response.json["is_admin"], 0)
        user_id = response.json["user_id"]
        # logger.info('Test - poprawne logowanie na test_user.')
        return user_id

    def logout_user(self):
        response = self.client.get('/api/logout')
        self.assertEqual(response.status_code, 200)
        # logger.info('Test - poprawne wylogowanie test_user.')
        return 0

    def delete_user(self, user_id):
        data = {
            "days": "2580"
        }

        response = self.client.post(f'api/admin/{user_id}/delete', json=data)
        self.assertEqual(response.status_code, 200)
        # logger.info('Test - poprawne usunięcie test_user.')

    def user_set_admin_lvl(self, user_id, admin_lvl):
        data = {
            "admin": f"{admin_lvl}"
        }
        response = self.client.post(f'api/admin/{user_id}/lvl-admin', json=data)
        self.assertEqual(response.status_code, 200)
        # logger.info(f'Test - poprawne ustawienie admin-lvl na {admin_lvl} dla test_user.')

    #####################################################################
    def test_admin_login_and_logout(self):
        self.admin_login()
        self.admin_logout()
        logger.info('Test 1 - logowanie i wylogowanie na ADMINa.')

    def test_admin_show_users(self):
        self.admin_login()

        response = self.client.get('/api/admin')
        self.assertEqual(response.status_code, 200)
        logger.info('Test 2 - poprawne pobranie listy użytkowników przez ADMINa.')

        self.admin_logout()

    def test_create_user(self):
        self.create_user()
        user_id = self.login_user()  # przypisanie id_user
        self.logout_user()
        self.admin_login()

        self.delete_user(user_id)
        self.admin_logout()
        logger.info('Test 3 - poprawne tworzenie konta użytkownika.')

    def test_create_user_with_different_passwords(self):
        data = {
            "username": "test_user",
            "password": "test_password",
            "repassword": "different_password"
        }

        response = self.client.post('/api/users/create', json=data)
        self.assertEqual(response.status_code, 406)
        self.assertEqual(response.data.decode('utf-8'), 'Podane hasła są różne!')
        logger.info('Test 4 - niepoprawne tworzenia konta z różnymi hasłami.')

    def test_change_user(self):
        self.create_user()
        user_id = self.login_user()
        self.logout_user()
        self.admin_login()

        for i in range(4):
            self.user_set_admin_lvl(user_id, i)
        logger.info('Test 5 - poprawne ustawienie admin-lvl od 0 do 3 dla test_user.')
        response = self.client.get(f'/api/admin/{user_id}/reset-password')
        self.assertEqual(response.status_code, 200)
        logger.info('Test 5 - poprawna zmiana hasła dla test_user.')

        data = {
            "new_score": "1000"
        }
        response = self.client.post(f'api/admin/{user_id}/set-score', json=data)
        self.assertEqual(response.status_code, 200)
        logger.info('Test 5 - poprawna zmiana ilości expa test_user.')

        self.delete_user(user_id)
        self.admin_logout()

    def test_change_password(self):
        self.create_user()
        user_id = self.login_user()

        data = {
            "password": "test_password",
            "new_password": "nowe2",
            "new_password2": "nowe2"
        }

        response = self.client.post(f'api/users/change-password', json=data)
        self.assertEqual(response.status_code, 200)
        logger.info('Test 6 - poprawna zmiana hasła.')

        self.admin_login()
        self.delete_user(user_id)
        self.admin_logout()


if __name__ == '__main__':
    unittest.main()
