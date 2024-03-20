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

    def test_failed_create_user(self):
        self.create_user()
        user_id = self.login_user()
        data = {
            "username": "test_user",
            "password": "test_password",
            "repassword": "test_password"
        }

        response = self.client.post('/api/users/create', json=data)
        self.assertEqual(response.status_code, 406)
        self.assertEqual(response.data.decode('utf-8'), 'Jest już użytkownik o takim nicku.')
        logger.info('Test 4 - niepoprawne tworzenia konta - istnieje takie konto.')
        self.admin_login()
        self.delete_user(user_id)
        self.admin_logout()

        data = {
            "username": "test_user",
            "password": "test_password",
            "repassword": "different_password"
        }

        response = self.client.post('/api/users/create', json=data)
        self.assertEqual(response.status_code, 406)
        self.assertEqual(response.data.decode('utf-8'), 'Podane hasła są różne!')
        logger.info('Test 4 - niepoprawne tworzenia konta - różne hasła.')

        data = {
            "username": "te",
            "password": "test_password",
            "repassword": "test_password"
        }

        response = self.client.post('/api/users/create', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode('utf-8'), 'Login jest za krótki!')
        logger.info('Test 4 - niepoprawne tworzenia konta - za krótka nazwa.')

        data = {
            "username": "test_user",
            "password": "te",
            "repassword": "te"
        }

        response = self.client.post('/api/users/create', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode('utf-8'), 'Hasło jest za krótkie!')
        logger.info('Test 4 - niepoprawne tworzenia konta - za krótkie hasło.')

        data = {
            "username": "test_user",
            "password": "test_passwordtest_password",
            "repassword": "test_passwordtest_password"
        }

        response = self.client.post('/api/users/create', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode('utf-8'), 'Hasło jest za długie!')
        logger.info('Test 4 - niepoprawne tworzenia konta - za długie hasło.')

        data = {
            "username": "test_usertest_usertest_user",
            "password": "test_password",
            "repassword": "test_password"
        }

        response = self.client.post('/api/users/create', json=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode('utf-8'), 'Login jest za długi!')
        logger.info('Test 4 - niepoprawne tworzenia konta - za długi login.')

    def test_change_user(self):
        self.create_user()
        user_id = self.login_user()
        self.logout_user()
        self.admin_login()

        for i in range(4):
            if i != 1:
                self.user_set_admin_lvl(user_id, i)
            else:
                self.user_set_admin_lvl(user_id, 110)  # 110 oznacza range 1 i 10dni
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

        self.logout_user()
        self.admin_login()
        self.delete_user(user_id)
        self.admin_logout()

    def test_failed_login(self):
        login_data = {
            "username": "",
            "password": "test_password"
        }
        response = self.client.post('api/login', json=login_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode('utf-8'), 'Brak nazwy użytkownika!')
        logger.info('Test 7 - błąd logowania - brak nazwy.')

        login_data = {
            "username": "test_user",
            "password": ""
        }
        response = self.client.post('api/login', json=login_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.decode('utf-8'), 'Brak hasła!')
        logger.info('Test 7 - błąd logowania - brak hasła.')

        login_data = {
            "username": "no_test_user",
            "password": "test_password"
        }
        response = self.client.post('api/login', json=login_data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data.decode('utf-8'), 'Brak użytkownika o tym nicku!')
        logger.info('Test 7 - błąd logowania - brak takiego konta.')

        self.create_user()
        user_id = self.login_user()
        self.logout_user()

        login_data = {
            "username": "test_user",
            "password": "test_incorrect_password"
        }
        response = self.client.post('api/login', json=login_data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data.decode('utf-8'), 'Podane hasło jest nieprawidłowe!')
        logger.info('Test 7 - błąd logowania - błędne hasło.')

        self.admin_login()
        days = 2
        data = {
            "days": f"{days}"
        }
        response = self.client.post(f'api/admin/{user_id}/delete', json=data)
        self.assertEqual(response.status_code, 200)
        logger.info(f'Test 7 - poprawne zbanowanie test_user na {days} dni.')
        self.admin_logout()

        login_data = {
            "username": "test_user",
            "password": "test_password"
        }
        response = self.client.post('api/login', json=login_data)
        self.assertEqual(response.status_code, 403)
        logger.info('Test 7 - błąd logowania - zbanowane konto.')

        self.admin_login()
        self.delete_user(user_id)
        self.admin_logout()

    def test_failed_change_password(self):
        self.create_user()
        user_id = self.login_user()

        data = {
            "password": "test_password", "new_password": "nowe", "new_password2": "nowe2"
        }

        response = self.client.post(f'api/users/change-password', json=data)
        self.assertEqual(response.status_code, 406)
        logger.info('Test 8 - błąd zmiany hasła - różne nowe hasła.')

        data = {
            "password": "", "new_password": "nowe2", "new_password2": "nowe2"
        }

        response = self.client.post(f'api/users/change-password', json=data)
        self.assertEqual(response.status_code, 400)
        logger.info('Test 8 - błąd zmiany hasła - brak starego hasła.')

        data = {
            "password": "test_password", "new_password": "", "new_password2": ""
        }

        response = self.client.post(f'api/users/change-password', json=data)
        self.assertEqual(response.status_code, 400)
        logger.info('Test 8 - błąd zmiany hasła - brak nowego hasła.')

        data = {
            "password": "test_incorrect_password", "new_password": "nowe2", "new_password2": "nowe2"
        }

        response = self.client.post(f'api/users/change-password', json=data)
        self.assertEqual(response.status_code, 400)
        logger.info('Test 8 - błąd zmiany hasła - błędne stare hasło.')

        data = {
            "password": "test_password", "new_password": "test_password", "new_password2": "test_password"
        }

        response = self.client.post(f'api/users/change-password', json=data)
        self.assertEqual(response.status_code, 400)
        logger.info('Test 8 - błąd zmiany hasła - stare hasło jest takie samo jak nowe.')

        self.logout_user()
        self.admin_login()
        self.delete_user(user_id)
        self.admin_logout()

    def test_user_posts(self):
        self.create_user()
        user_id = self.login_user()

        data = {
            "content": "dodawanie nowego posta na kanał"
        }

        response = self.client.post(f'api/postssug/create', json=data)
        self.assertEqual(response.status_code, 201)
        logger.info('Test 9 - dodanie nowego posta na kanał')

        response = self.client.get('/api/postssug/all/1')
        self.assertEqual(response.status_code, 200)
        last_post_id = json.loads(response.data)[0]['id']
        logger.info('Test 9 - pobranie postów z kanału')

        data = {
            "content": "edytowanie posta na kanał"
        }

        response = self.client.post(f'api/postssug/{last_post_id}/edit', json=data)
        self.assertEqual(response.status_code, 201)
        logger.info('Test 9 - edytowanie posta na kanale')

        response = self.client.get(f'/api/postssug/{last_post_id}/delete')
        self.assertEqual(response.status_code, 200)
        logger.info('Test 9 - usuwanie posta na kanale.')

        self.logout_user()
        self.admin_login()
        self.delete_user(user_id)
        self.admin_logout()


if __name__ == '__main__':
    unittest.main()
