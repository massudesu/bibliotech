from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from usuarios.forms import CustomUserCreationForm
from usuarios.templatetags.phone_filters import phone_format

User = get_user_model()


class UsuarioFormAndModelTests(TestCase):
    def test_cadastro_com_acentos_portugueses(self):
        form_data = {
            'username': 'joao_silva',
            'first_name': 'João',
            'last_name': 'Conceição',
            'email': 'joao@escola.edu.br',
            'telefone': '(11) 98765-4321',
            'genero': 'M',
            'password1': 'SenhaSegura123!',
            'password2': 'SenhaSegura123!',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Erros no formulário: {form.errors}")
        user = form.save()
        self.assertEqual(user.first_name, 'João')
        self.assertEqual(user.last_name, 'Conceição')
        self.assertEqual(user.telefone, '11987654321')

    def test_phone_format_filter(self):
        # 11 dígitos (celular)
        self.assertEqual(phone_format('11987654321'), '(11) 98765-4321')
        # 10 dígitos (fixo)
        self.assertEqual(phone_format('1133334444'), '(11) 3333-4444')
        # Vazio
        self.assertEqual(phone_format(''), '')


class UsuarioAuthViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='aluno_login',
            password='SenhaValida123!',
            first_name='Maria',
            last_name='Souza'
        )

    def test_login_sucesso(self):
        response = self.client.post(reverse('login'), {
            'username': 'aluno_login',
            'password': 'SenhaValida123!'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_login_senha_incorreta(self):
        response = self.client.post(reverse('login'), {
            'username': 'aluno_login',
            'password': 'SenhaErrada!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_logout(self):
        self.client.login(username='aluno_login', password='SenhaValida123!')
        response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)
