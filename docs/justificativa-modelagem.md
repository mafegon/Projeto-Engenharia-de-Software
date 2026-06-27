Justificativa das Decisões de Modelagem (Aula 10)
1. Aplicação do Conceito de Herança (Usuario e Aluno):
No diagrama de classes, observou-se uma relação de generalização/especialização (herança). Para otimizar o reaproveitamento de código e evitar redundâncias, criamos a classe base Usuario contendo os atributos comuns (id, nome, email, senha) e métodos globais de autenticação (login, logout, alterarSenha). A classe Aluno herda diretamente de Usuario, estendendo-a com atributos específicos do contexto acadêmico (curso, semestre, telefone). No código Python, isso foi traduzido utilizando a sintaxe de herança class Aluno(Usuario): e invocando o construtor da classe pai via super().__init__().

2. Implementação de Encapsulamento:
Para respeitar estritamente os modificadores de acesso do diagrama de classes — onde os atributos estavam definidos com o sinal de menos (-), indicando visibilidade privada —, aplicamos o conceito de encapsulamento em Python utilizando o prefixo de sublinhado (_) antes de cada propriedade (ex: self._email, self._vagas_salvas). Isso restringe o acesso direto aos estados dos objetos, garantindo que alterações ocorram apenas por meio dos métodos da classe.

3. Tipagem e Assinatura de Métodos (Type Hinting):
As operações mapeadas no diagrama, como candidatar(v: Vaga): boolean, foram traduzidas para métodos que utilizam dicas de tipo (type hinting) nativas do Python. Isso garante clareza no desenvolvimento da plataforma, deixando explícito que o método espera uma instância da classe Vaga e retorna um valor booleano, simulando fielmente as restrições e comportamentos especificados na modelagem UML do draw.io.
