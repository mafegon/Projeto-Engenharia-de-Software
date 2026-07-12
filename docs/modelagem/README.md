# Modelagem do Sistema

Esta pasta reúne a documentação de modelagem do sistema de gerenciamento de vagas de estágio e a implementação inicial das classes solicitadas, conforme requerido pelo professor durante o andamento da disciplina. 

## Estrutura da pasta

- `diagramas_de_classes/`: contém a documentação do diagrama de classes, a justificativa das decisões de modelagem e o PDF exportado pelo draw.io.
- `implementacao/`: contém uma implementação em Python de parte das classes modeladas, além de um arquivo de teste simples para validar o funcionamento.

## Diagrama de Classes

O diagrama de classes foi criado no draw.io e exportado como PDF no arquivo `diagramas_de_classes/diagrama_de_classes.pdf`. Ele representa a estrutura do sistema de gerenciamento de vagas de estágio de forma organizada e de fácil manutenção.

A modelagem considera as principais entidades do sistema:

- `Usuário`: classe base com informações comuns de autenticação e identificação, como id, nome, e-mail e senha.
- `Aluno`: especialização de `Usuário`, com dados acadêmicos e funcionalidades voltadas para candidatura e salvamento de vagas.
- `Empresa`: especialização de `Usuário`, responsável pela publicação e manutenção das vagas.
- `Vaga`: representa uma oportunidade de estágio publicada por uma empresa.
- `Candidatura`: representa o processo de inscrição de um aluno em uma vaga, registrando informações como data, status e currículo.
- `Salvamento_Vaga`: representa as vagas salvas por alunos, permitindo observações e marcação de favoritas sem misturar essa funcionalidade com o processo de candidatura.

## Justificativa das decisões de modelagem 

O diagrama de classes foi desenvolvido para representar a estrutura do sistema de gerenciamento de vagas de estágio de forma organizada e de fácil manutenção.

Foi utilizada a **herança** entre as classes `Usuário`, `Aluno` e `Empresa`, pois tanto alunos quanto empresas compartilham informações básicas, como id, nome, e-mail e senha, mas possuem funcionalidades específicas.

### Composição entre `Empresa` e `Vaga`

A relação entre `Empresa` e `Vaga` foi modelada como composição, pois a vaga depende diretamente da existência de uma empresa para fazer sentido no sistema.

Uma vaga só pode ser criada e mantida por uma empresa cadastrada. Portanto, ela é parte integrante da empresa no contexto da plataforma. Caso a empresa seja removida do sistema, suas vagas associadas também deixam de existir, caracterizando uma relação de dependência forte.

## Implementação

A pasta `implementacao/` contém uma versão inicial em Python das classes da modelagem.

### Aplicação do conceito de herança (`Usuario` e `Aluno`)

No diagrama de classes, observou-se uma relação de generalização/especialização, também chamada de herança. Para otimizar o reaproveitamento de código e evitar redundâncias, foi criada a classe base `Usuario`, contendo os atributos comuns `id`, `nome`, `email` e `senha`, além dos métodos globais de autenticação `login`, `logout` e `alterarSenha`.

A classe `Aluno` herda diretamente de `Usuario`, estendendo-a com atributos específicos do contexto acadêmico, como `curso`, `semestre` e `telefone`. No código Python, essa decisão foi traduzida pela sintaxe `class Aluno(Usuario):` e pela chamada ao construtor da classe pai com `super().__init__()`.

### Implementação de encapsulamento

Para respeitar os modificadores de acesso do diagrama de classes, em que os atributos estavam definidos com o sinal de menos (`-`), indicando visibilidade privada, foi aplicado o conceito de encapsulamento em Python por meio do prefixo de sublinhado (`_`) antes de cada propriedade, como `self._email` e `self._vagas_salvas`.

Essa escolha restringe o acesso direto aos estados dos objetos e reforça que alterações devem ocorrer por meio dos métodos da própria classe.

### Tipagem e assinatura de métodos

As operações mapeadas no diagrama, como `candidatar(v: Vaga): boolean`, foram traduzidas para métodos que utilizam dicas de tipo, conhecidas como *type hinting*, nativas do Python.

Isso garante mais clareza durante o desenvolvimento da plataforma, deixando explícito que o método espera uma instância da classe `Vaga` e retorna um valor booleano. Dessa forma, o código simula de maneira mais fiel as restrições e comportamentos especificados na modelagem UML feita no draw.io.

A classe `Vaga` foi criada para armazenar todas as informações referentes às oportunidades publicadas pelas empresas. Já a classe `Candidatura` representa o processo de inscrição de um aluno em uma vaga, registrando informações como data, status e currículo.

A classe `Salvamento_Vaga` foi modelada separadamente para permitir que os alunos salvem vagas de interesse, adicionem observações e marquem vagas como favoritas, mantendo essa funcionalidade independente do processo de candidatura.

As associações e multiplicidades foram definidas para refletir os relacionamentos do sistema, permitindo que uma empresa publique várias vagas, que um aluno possa realizar diversas candidaturas e salvar diferentes vagas. Essa modelagem promove reutilização de código, reduz redundâncias e facilita futuras manutenções e expansões do sistema.

### `models.py`

O arquivo `models.py` implementa as classes `Usuario`, `Aluno` e uma versão simplificada de `Vaga`.

A classe `Usuario` representa a base comum dos usuários do sistema. Ela possui os atributos protegidos `_id`, `_nome`, `_email` e `_senha`, além dos métodos:

- `login(email, senha)`: compara os dados recebidos com o e-mail e a senha cadastrados e retorna `True` quando estão corretos.
- `logout()`: método reservado para representar a saída do usuário do sistema.
- `alterarSenha(novaSenha)`: altera a senha quando o novo valor é válido e retorna `True`; caso contrário, retorna `False`.

A classe `Aluno` herda de `Usuario`, reutilizando os atributos e métodos comuns. Além disso, adiciona os atributos `_curso`, `_semestre`, `_telefone` e `_vagas_salvas`.

Ela também implementa os métodos:

- `candidatar(v)`: recebe uma vaga e retorna `True` quando a vaga informada é válida.
- `salvarVaga(v)`: adiciona uma vaga à lista de vagas salvas caso ela ainda não esteja salva.
- `visualizarVagas()`: retorna a lista de vagas salvas pelo aluno.

A classe `Vaga` aparece de forma simplificada, com apenas o atributo `_titulo`. Ela foi criada para permitir que os métodos do aluno sejam testados sem erro de importação, mesmo antes da implementação completa da classe `Vaga` prevista no diagrama.

### `main.py`

O arquivo `main.py` funciona como um teste manual da implementação. Ele instancia um aluno, valida o uso da herança e executa os principais métodos disponíveis.

Para executar o teste, use:

```bash
python docs/modelagem/implementacao/main.py
```

## Relação entre modelagem e código

A implementação atual representa uma primeira versão prática do diagrama de classes. Ela já demonstra a herança entre `Usuario` e `Aluno`, o encapsulamento por meio de atributos protegidos e alguns comportamentos previstos para alunos.

Nem todas as classes do diagrama foram implementadas completamente. As classes `Empresa`, `Candidatura` e `Salvamento_Vaga` ainda aparecem como parte da modelagem documentada, mas não possuem implementação completa nesta versão do código. A classe `Vaga` também está simplificada e serve apenas como apoio aos testes da classe `Aluno`.

Mesmo sendo parcial, a implementação valida a ideia central da modelagem: separar responsabilidades, reutilizar atributos comuns por herança e manter funcionalidades específicas em suas respectivas classes.
