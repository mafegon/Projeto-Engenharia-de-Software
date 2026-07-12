# codigo-fonte/backend/main.py
from models import Aluno, Vaga

def rodar_teste():
    print("--- INICIANDO TESTE DAS CLASSES ---")
    
    # 1. Instanciando a classe Aluno (testando construtor e herança)
    aluno = Aluno(
        id=1, 
        nome="Maria Fernanda", 
        email="maria@unifap.br", 
        senha="senhaSegura123", 
        curso="Ciência da Computação", 
        semestre="2026.1", 
        telefone="96999999999"
    )
    print(f"Aluno criado com sucesso: {aluno._nome} (Curso: {aluno._curso})")

    # 2. Testando o método login (herdado da classe base Usuario)
    print("\n[Testando Login]")
    login_sucesso = aluno.login("maria@unifap.br", "senhaSegura123")
    print(f"Login com dados corretos: {login_sucesso}") # Deve exibir True
    
    login_falha = aluno.login("maria@unifap.br", "senhaErrada")
    print(f"Login com dados incorretos: {login_falha}") # Deve exibir False

    # 3. Testando métodos específicos do Aluno
    print("\n[Testando Funcionalidades do Aluno]")
    vaga_ti = Vaga("Estágio em Engenharia de Software")
    
    candidatura = aluno.candidatar(vaga_ti)
    print(f"Candidatura realizada: {candidatura}") # Deve exibir True
    
    salvamento = aluno.salvarVaga(vaga_ti)
    print(f"Vaga salva nos favoritos: {salvamento}") # Deve exibir True

    print("\n--- TESTE FINALIZADO COM SUCESSO ---")

if __name__ == "__main__":
    rodar_teste()