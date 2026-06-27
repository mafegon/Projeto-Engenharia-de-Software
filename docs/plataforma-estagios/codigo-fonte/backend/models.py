# codigo-fonte/backend/models.py
from typing import List

class Usuario:
    def __init__(self, id: int, nome: str, email: str, senha: str):
        self._id: int = id
        self._nome: str = nome
        self._email: str = email
        self._senha: str = senha

    def login(self, email: str, senha: str) -> bool:
        if self._email == email and self._senha == senha:
            return True
        return False

    def logout(self) -> None:
        pass

    def alterarSenha(self, novaSenha: str) -> bool:
        if novaSenha:
            self._senha = novaSenha
            return True
        return False


class Aluno(Usuario):
    def __init__(self, id: int, nome: str, email: str, senha: str, curso: str, semestre: str, telefone: str):
        # O super() garante que os atributos da classe pai (Usuario) sejam gerados
        super().__init__(id, nome, email, senha)
        self._curso: str = curso
        self._semestre: str = semestre
        self._telefone: str = telefone
        self._vagas_salvas: List['Vaga'] = []

    def candidatar(self, v: 'Vaga') -> bool:
        if v:
            return True
        return False

    def salvarVaga(self, v: 'Vaga') -> bool:
        if v not in self._vagas_salvas:
            self._vagas_salvas.append(v)
            return True
        return False

    def visualizarVagas(self) -> List['Vaga']:
        return self._vagas_salvas

# Criamos uma classe Vaga simples apenas para o código do Aluno não dar erro de importação
class Vaga:
    def __init__(self, titulo: str):
        self._titulo = titulo