from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Livro, Categoria, Reserva
from datetime import date, timedelta

User = get_user_model()


class CoreModelTests(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nome="Literatura Brasileira")
        self.livro = Livro.objects.create(
            titulo="Dom Casmurro",
            autor="Machado de Assis",
            editora="Editora Garnier",
            quantidade=3,
            corredor="A",
            prateleira="2",
            data_limite_dias=15
        )
        self.livro.categorias.add(self.categoria)
        self.aluno = User.objects.create_user(
            username="aluno_teste",
            password="SenhaForte123!",
            first_name="João",
            last_name="Silva"
        )
        self.admin = User.objects.create_user(
            username="admin_teste",
            password="SenhaForte123!",
            first_name="Bibliotecário",
            is_staff=True
        )

    def test_livro_is_available(self):
        self.assertTrue(self.livro.is_available)
        self.livro.quantidade = 0
        self.livro.save()
        self.assertFalse(self.livro.is_available)

    def test_reserva_lifecycle_estoque(self):
        # 1. Criar reserva deve decrementar estoque
        estoque_inicial = self.livro.quantidade
        reserva = Reserva.objects.create(
            livro=self.livro,
            usuario=self.aluno,
            status='preparando'
        )
        self.livro.refresh_from_db()
        self.assertEqual(self.livro.quantidade, estoque_inicial - 1)

        # 2. Ao marcar como devolvido, deve restituir estoque
        reserva.status = 'devolvido'
        reserva.save()
        self.livro.refresh_from_db()
        self.assertEqual(self.livro.quantidade, estoque_inicial)
        self.assertIsNotNone(reserva.data_devolucao_efetiva)

    def test_limite_tres_reservas_por_aluno(self):
        client = Client()
        client.login(username="aluno_teste", password="SenhaForte123!")

        livro2 = Livro.objects.create(titulo="Memórias Póstumas", autor="Machado", editora="Garnier", quantidade=2)
        livro3 = Livro.objects.create(titulo="Quincas Borba", autor="Machado", editora="Garnier", quantidade=2)
        livro4 = Livro.objects.create(titulo="O Cortiço", autor="Aluísio", editora="Garnier", quantidade=2)

        # Cria 3 reservas ativas
        Reserva.objects.create(livro=self.livro, usuario=self.aluno, status='preparando')
        Reserva.objects.create(livro=livro2, usuario=self.aluno, status='preparando')
        Reserva.objects.create(livro=livro3, usuario=self.aluno, status='preparando')

        # Tenta reservar o 4º livro via POST
        response = client.post(reverse('processar_reserva', args=[livro4.id]))
        # Deve redirecionar e bloquear a 4ª reserva
        self.assertEqual(Reserva.objects.filter(usuario=self.aluno).exclude(status='devolvido').count(), 3)


class CoreViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.categoria = Categoria.objects.create(nome="Ficção Científica")
        self.livro = Livro.objects.create(
            titulo="Neuromancer",
            autor="William Gibson",
            editora="Aleph",
            quantidade=2
        )
        self.livro.categorias.add(self.categoria)

    def test_catalogo_view(self):
        response = self.client.get(reverse('catalogo'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Neuromancer")

    def test_buscar_livros_api(self):
        response = self.client.get(reverse('buscar_livros_api') + '?q=Neuro')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['titulo'], "Neuromancer")

    def test_creditos_view(self):
        response = self.client.get(reverse('creditos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Arthur")
        self.assertContains(response, "Nicolas")
        self.assertContains(response, "Beatriz")
