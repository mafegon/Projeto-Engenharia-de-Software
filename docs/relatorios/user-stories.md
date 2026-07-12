# User Stories e Critérios de Aceitação

## 1. Objetivo
Este documento registra histórias de usuário iniciais para orientar a implementação e validação da Plataforma de Anúncios de Estágios Acadêmicos.

## 2. Histórias de Usuário

### US-01 - Cadastro de aluno
**Como** aluno,  
**quero** criar uma conta na plataforma,  
**para** acessar vagas de estágio disponíveis.

**Critérios de aceitação:**
- O aluno deve informar dados básicos para cadastro.
- O sistema deve validar campos obrigatórios.
- O sistema deve impedir cadastro com dados inválidos.
- Após cadastro válido, o aluno deve conseguir acessar a plataforma.

### US-02 - Login de aluno
**Como** aluno cadastrado,  
**quero** fazer login na plataforma,  
**para** consultar e acompanhar vagas de estágio.

**Critérios de aceitação:**
- O sistema deve autenticar o aluno com credenciais válidas.
- O sistema deve recusar credenciais inválidas.
- Após login, o aluno deve acessar as funcionalidades disponíveis para seu perfil.

### US-03 - Cadastro de empresa
**Como** empresa ou organização concedente,  
**quero** criar uma conta na plataforma,  
**para** divulgar vagas de estágio.

**Critérios de aceitação:**
- A empresa deve informar dados básicos para cadastro.
- O sistema deve validar campos obrigatórios.
- O sistema deve permitir acesso às funcionalidades de empresa após cadastro válido.

### US-04 - Publicação de vaga
**Como** empresa cadastrada,  
**quero** cadastrar uma vaga de estágio,  
**para** divulgá-la aos alunos interessados.

**Critérios de aceitação:**
- A empresa deve informar título, descrição, área, modalidade e carga horária da vaga.
- O sistema deve validar as informações obrigatórias.
- Após o cadastro, a vaga deve aparecer na listagem de vagas disponíveis.

### US-05 - Edição de vaga
**Como** empresa cadastrada,  
**quero** editar uma vaga publicada,  
**para** corrigir ou atualizar informações.

**Critérios de aceitação:**
- A empresa deve visualizar apenas vagas cadastradas por ela.
- O sistema deve permitir alteração dos dados da vaga.
- As alterações salvas devem aparecer na consulta da vaga.

### US-06 - Visualização de vagas
**Como** aluno,  
**quero** visualizar vagas de estágio disponíveis,  
**para** identificar oportunidades compatíveis com meu interesse.

**Critérios de aceitação:**
- O sistema deve exibir uma lista de vagas disponíveis.
- Cada vaga listada deve apresentar informações resumidas.
- O aluno deve conseguir acessar os detalhes de uma vaga selecionada.

### US-07 - Filtro de vagas
**Como** aluno,  
**quero** filtrar vagas por critérios relevantes,  
**para** encontrar oportunidades mais adequadas ao meu perfil.

**Critérios de aceitação:**
- O sistema deve permitir filtragem por pelo menos um critério definido pela equipe.
- A listagem deve ser atualizada conforme o filtro aplicado.
- O sistema deve informar quando não houver vagas compatíveis com o filtro.

### US-08 - Candidatura ou manifestação de interesse
**Como** aluno,  
**quero** manifestar interesse em uma vaga,  
**para** sinalizar à empresa que desejo participar do processo.

**Critérios de aceitação:**
- O aluno deve estar autenticado para manifestar interesse.
- O sistema deve registrar o interesse do aluno na vaga.
- O sistema deve evitar registros duplicados para a mesma vaga e aluno.

### US-09 - Acompanhamento de candidatos
**Como** empresa,  
**quero** visualizar alunos interessados nas minhas vagas,  
**para** acompanhar possíveis candidatos.

**Critérios de aceitação:**
- A empresa deve visualizar interessados apenas em vagas cadastradas por ela.
- O sistema deve listar os alunos interessados por vaga.
- A listagem deve apresentar informações básicas necessárias para contato ou análise futura.

### US-10 - Salvamento de vagas
**Como** aluno,  
**quero** salvar vagas de interesse,  
**para** acessá-las posteriormente com facilidade.

**Critérios de aceitação:**
- O aluno deve estar autenticado para salvar vagas.
- O sistema deve permitir visualizar vagas salvas anteriormente.
- O sistema deve evitar salvar a mesma vaga mais de uma vez para o mesmo aluno.

## 3. Observações
As histórias descritas são uma base inicial. A equipe poderá incluir novas histórias, alterar prioridades e detalhar fluxos conforme a definição das tecnologias e regras de negócio.
