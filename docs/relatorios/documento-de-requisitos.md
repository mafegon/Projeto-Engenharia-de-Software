# Documento de Requisitos
##1 Descrição do problema
##1.1 Problema
Alunos de instituições de ensino técnico e superior precisam encontrar oportunidades de estágio de forma clara e centralizada. Ao mesmo tempo, empresas e organizações concedentes precisam divulgar vagas e alcançar candidatos compatíveis com suas necessidades.

Atualmente, a divulgação de vagas pode ocorrer por canais dispersos, dificultando a consulta pelos alunos e o acompanhamento pelas organizações.

##1.2 Usuário-alvo

Alunos: usuários que buscam oportunidades de estágio.
Empresas e organizações concedentes: usuários que publicam vagas e acompanham interessados.
Equipe acadêmica: interessados no acompanhamento e avaliação do projeto.

##2 Requisitos Funcionais
- **RF-01:** o sistema deve permitir o cadastro de alunos.
- **RF-02:** o sistema deve permitir o login de alunos cadastrados.
- **RF-03:** o sistema deve permitir o cadastro de empresas ou organizações concedentes.
- **RF-04:** o sistema deve permitir o login de empresas cadastradas.
- **RF-05:** o sistema deve permitir que empresas cadastrem vagas de estágio.
- **RF-06:** o sistema deve permitir que empresas editem vagas publicadas por elas.
- **RF-07:** o sistema deve permitir que empresas removam ou desativem vagas publicadas por elas.
- **RF-08:** o sistema deve permitir que alunos visualizem vagas disponíveis.
- **RF-09:** o sistema deve permitir que alunos consultem os detalhes de uma vaga.
- **RF-10:** o sistema deve permitir que alunos filtrem vagas por critérios como área, modalidade, localidade ou carga horária.
- **RF-11:** o sistema deve permitir que alunos se candidatem a vagas cujo processo ocorra de forma interna na plataforma, ou redirecionar o aluno caso o meio seja externo.
- **RF-12:** O sistema deve permitir que empresas visualizem a lista de alunos interessados nas vagas com processo seletivo interno.
- **RF-13:** o sistema deve permitir que os alunos salvem vagas para consulta posterior.
- **RF-14:** o sistema deve permitir que a empresa informe, ao cadastrar uma vaga, se o processo de candidatura ocorrerá pela própria plataforma ou por meio externo.
- **RF-15:** O sistema deve permitir que o aluno visualize a lista de vagas às quais se candidatou internamente.

## 3. Requisitos Não-Funcionais (RNF) - Categorizados por FURPS+

*Os requisitos abaixo foram definidos com métricas mensuráveis, adequadas para a realidade tecnológica do projeto (Django + Tailwind CSS) e as limitações do ambiente de hospedagem temporário (Render gratuito).*

| ID | Categoria (FURPS+) | Descrição Mensurável |
| :--- | :--- | :--- |
| **RNF-01** | **Usabilidade (Usability)** | A interface construída com Tailwind CSS deve ser totalmente responsiva, adaptando-se sem quebra de layout de 360px (mobile básico) até 1920px (telas de computadores). |
| **RNF-02** | **Desempenho (Performance)** | O tempo de carregamento da rota de consulta de vagas (`/vagas/`) não deve exceder 2 segundos **após a inicialização da instância no servidor (desconsiderando o cold start do plano gratuito do Render)**. |
| **RNF-03** | **Confiabilidade (Reliability)** | O sistema deve garantir a consistência e o funcionamento lógico das operações de cadastro e login em memória durante o tempo de atividade da sessão atual da aplicação (enquanto o processo no servidor não for reiniciado). |
| **RNF-04** | **Segurança (+)** | Todas as páginas do sistema devem ser carregadas obrigatoriamente através do protocolo seguro HTTPS e a aplicação deve utilizar o middleware padrão do Django para proteção contra ataques comuns (como CSRF e XSS). |
| **RNF-05** | **Suportabilidade (Supportability)** | A plataforma deve ser compatível com as 2 últimas versões estáveis de navegadores baseados em Chromium (Google Chrome, Microsoft Edge, Opera), além do Firefox e Safari. |

## 4. Users Stories

### US-01 - Cadastro de Aluno
* **Como** um estudante em busca de estágio,  
* **quero** criar uma conta na plataforma informando e-mail e senha,  
* **para** que eu possa me identificar no sistema e acessar as oportunidades disponíveis.
* **Critérios de aceitação:**
  - O sistema deve exigir obrigatoriamente e-mail e senha no formulário de cadastro.
  - O e-mail inserido deve ser validado sintaticamente (deve conter `@` e um domínio válido).
  - O sistema deve impedir o cadastro caso o e-mail informado já exista na memória da aplicação.
  - Após o cadastro bem-sucedido, o aluno deve ser automaticamente autenticado e direcionado para a listagem de vagas.

### US-02 - Login de Aluno
* **Como** um aluno cadastrado,  
* **quero** realizar o login utilizando minhas credenciais de acesso,  
* **para** que eu possa acessar as vagas de estágio e as configurações do meu perfil.
* **Critérios de aceitação:**
  - O sistema deve autenticar o usuário caso o e-mail e a senha correspondam a um registro válido em memória.
  - Se as credenciais estiverem incorretas, o sistema deve exibir um alerta visual de erro e manter o usuário na tela de login.
  - Após o login, a sessão do aluno deve permanecer ativa e ele deve ser redirecionado para a rota `/vagas/`.

### US-03 - Cadastro de Empresa
* **Como** um representante de empresa ou organização concedente,  
* **quero** criar uma conta corporativa informando os dados básicos da instituição,  
* **para** que eu possa publicar vagas e gerenciar candidatos.
* **Critérios de aceitação:**
  - O formulário deve exigir nome da empresa, e-mail institucional e senha de acesso.
  - O sistema deve registrar o tipo de conta como "Empresa" para liberar o acesso ao painel de publicação.
  - Após a conclusão do cadastro com sucesso, a empresa deve ser redirecionada para a página inicial com a sessão ativa.

### US-04 - Publicação de Vaga
* **Como** uma empresa autenticada na plataforma,  
* **quero** cadastrar uma nova vaga de estágio detalhando suas características e o tipo de candidatura,  
* **para** que ela seja exibida para os alunos interessados.
* **Critérios de aceitação:**
  - O formulário de cadastro de vaga deve exigir obrigatoriamente: Título, Descrição, Área de Atuação, Modalidade (Remoto/Presencial), Localidade, Carga Horária e Tipo de Candidatura (Interna ou Link Externo).
  - Se algum campo obrigatório for enviado em branco, o sistema deve bloquear o salvamento e apontar o campo com erro.
  - Assim que a vaga for salva, ela deve ser listada imediatamente na rota pública de consulta de vagas `/vagas/`.

### US-05 - Edição de Vaga
* **Como** uma empresa cadastrada,  
* **quero** editar as informações de uma vaga que minha organização publicou,  
* **para** corrigir dados ou atualizar os requisitos do processo seletivo.
* **Critérios de aceitação:**
  - O sistema deve permitir a alteração de qualquer campo da vaga, exceto o ID único ou o proprietário da publicação.
  - A aplicação deve impedir estritamente que uma empresa tente editar ou acessar as rotas de edição de vagas criadas por outras organizações.
  - Os dados modificados devem se refletir na página de detalhes da vaga (`/vagas/<slug>/`) imediatamente após o salvamento.

### US-06 - Visualização de Vagas
* **Como** um aluno ativo na plataforma,  
* **quero** visualizar a listagem de vagas de estágio disponíveis,  
* **para** identificar as oportunidades compatíveis com meus interesses.
* **Critérios de aceitação:**
  - A rota `/vagas/` deve renderizar cartões (*cards*) contendo informações resumidas de cada vaga (Título, Empresa, Modalidade, Localidade e Carga Horária).
  - Ao clicar em um card de vaga, o aluno deve ser direcionado para a rota de detalhes específica (`/vagas/<slug>/`).

### US-07 - Filtro de Vagas
* **Como** um aluno buscando uma oportunidade específica,  
* **quero** filtrar as vagas listadas por área, modalidade, localidade ou carga horária,  
* **para** visualizar apenas as opções relevantes ao meu perfil.
* **Critérios de aceitação:**
  - Os filtros aplicados pelo usuário devem atualizar dinamicamente a listagem de vagas exibida na tela `/vagas/`.
  - Se os critérios selecionados não retornarem nenhum resultado na busca, a tela deve exibir a mensagem: "Nenhuma vaga encontrada para estes critérios".

### US-08 - Candidatura ou Manifestação de Interesse
* **Como** um aluno autenticado na plataforma,  
* **quero** manifestar interesse em uma vaga de estágio selecionada,  
* **para** que o sistema registre minha participação no processo seletivo.
* **Critérios de aceitação:**
  - O botão de candidatura/manifestação de interesse só deve estar ativo se o aluno estiver devidamente logado no sistema.
  - Para vagas com candidatura **interna**, o sistema deve associar o ID do aluno à vaga em memória e desabilitar o botão para impedir inscrições duplicadas.
  - Para vagas com candidatura **externa** (conforme RF-14), o sistema deve abrir o link indicado pela empresa em uma nova aba do navegador ao clicar no botão.

### US-09 - Acompanhamento de Candidatos
* **Como** uma empresa cadastrada,  
* **quero** visualizar a lista de alunos que se candidataram às vagas publicadas pela minha organização,  
* **para** analisar os currículos e contatar os interessados.
* **Critérios de aceitação:**
  - A empresa só deve ter acesso aos dados de candidatos inscritos nas vagas que ela mesma criou.
  - O sistema só deve listar candidatos para vagas cuja modalidade de candidatura seja "Interna".
  - A lista de candidatos associada a cada vaga deve exibir informações básicas (como Nome e E-mail de contato) do aluno de forma clara.

### US-10 - Salvamento de Vagas (Favoritos)
* **Como** um aluno autenticado,  
* **quero** salvar vagas de meu interesse,  
* **para** que eu possa consultá-las facilmente no meu perfil no futuro.
* **Critérios de aceitação:**
  - O aluno deve conseguir favoritar ou desfavoritar a vaga diretamente na rota de detalhes (`/vagas/<slug>/`).
  - O sistema deve impedir que a mesma vaga seja favoritada mais de uma vez pelo mesmo usuário.
  - A lista de vagas favoritadas deve ser renderizada de forma organizada em uma seção dedicada dentro da rota `/perfil/`.

## 5. Priorização (MVP vs. Desejáveis vs. Futuros)

A priorização foi estruturada para garantir uma entrega incremental e funcional focada no fluxo de ponta a ponta da aplicação: Cadastro -> Publicação de Vaga -> Visualização -> Candidatura.

### Essenciais (MVP)
*Funcionalidades vitais para o núcleo da aplicação. Sem estes itens o sistema não atinge seu propósito principal.*
*   **Requisitos Funcionais:** RF-01, RF-02, RF-03, RF-04, RF-05, RF-08, RF-09, RF-11 e RF-14.
*   **User Stories:** US-01, US-02, US-03, US-04, US-06 e US-08.

### Desejáveis
*Funcionalidades importantes que completam a experiência de gestão das vagas, painéis de controle e melhoram a experiência do usuário.*
*   **Requisitos Funcionais:** RF-06, RF-07, RF-10, RF-12, RF-13 e RF-15.
*   **User Stories:** US-05, US-07, US-09 e US-10.

### Futuros
*Escopo planejado para versões posteriores do produto, dependentes da conclusão e aprovação da integração da camada de persistência definitiva em rede (PostgreSQL no Supabase).*
*   **Upload de Currículos em PDF:** Permitir o upload de currículos na rota `/perfil/` para visualização e download no painel da empresa.
*   **Notificações por E-mail:** Envio automatizado de alertas para alunos quando uma vaga compatível com sua área for cadastrada.
*   **Painel Administrativo Acadêmico:** Relatórios estatísticos de candidaturas criados exclusivamente para a coordenação institucional.

> **Nota sobre os Requisitos Não-Funcionais (RNFs):** Por serem restrições arquiteturais e de qualidade que cruzam todo o sistema, os RNFs não entram na tabela de priorização modular por funcionalidade; todos são tratados como **Prioridade Máxima** e devem ser garantidos desde a primeira versão entregue do MVP.

---

## 6. Glossário

*   **Efêmero / Memória do Processo:** Tipo de armazenamento volátil (RAM) utilizado temporariamente nesta fase da aplicação (`DATABASES = {}`). Os dados criados existem apenas no ciclo de vida atual do processo do Gunicorn e desaparecem a qualquer novo deploy, reinicialização ou suspensão do serviço por inatividade no Render.
*   **Cold Start (Partida Fria):** O intervalo de tempo (geralmente entre 30 e 50 segundos) que o plano gratuito do Render necessita para inicializar o contêiner e a aplicação Django quando recebe uma requisição HTTP após um período de suspensão por inatividade.
*   **Slug:** Uma string de URL amigável e legível por humanos (geralmente gerada a partir do título da vaga, convertendo letras em minúsculas, removendo acentos e substituindo espaços por traços) utilizada para identificar recursos de forma limpa na rota `/vagas/<slug>/`.
*   **Candidatura Interna:** Fluxo no qual todo o registro de interesse e a consulta de dados dos alunos candidatos ocorre integralmente dentro das rotas e painéis da própria plataforma.
*   **Candidatura Externa:** Fluxo onde a contratação e triagem ocorre fora do ambiente do sistema. A plataforma atua apenas como canal de divulgação, redirecionando o aluno via link para formulários ou plataformas de terceiros.
*   **Organização Concedente:** Termo técnico-legal utilizado para designar as empresas, instituições públicas ou ONGs aptas a disponibilizar vagas de estágio e assinar termos de compromisso acadêmico.
