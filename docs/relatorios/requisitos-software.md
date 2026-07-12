# Documento de Requisitos de Software

## 1. Identificação
- **Projeto:** Plataforma de Anúncios de Estágios Acadêmicos
- **Disciplina:** Engenharia de Software
- **Instituição:** Universidade Federal do Amapá (UNIFAP)
- **Semestre:** 2026.1
- **Versão do documento:** 0.1
- **Status:** versão inicial para discussão e complementação pela equipe

## 2. Objetivo
Este documento apresenta uma definição inicial dos requisitos da Plataforma de Anúncios de Estágios Acadêmicos. A proposta é registrar uma base organizada para orientar o desenvolvimento, a comunicação entre os integrantes da equipe e as futuras validações do projeto.

## 3. Contexto
Instituições de ensino técnico e superior possuem alunos em busca de oportunidades de estágio, enquanto empresas e órgãos concedentes precisam divulgar vagas e encontrar candidatos compatíveis. O projeto propõe uma plataforma web para aproximar esses dois públicos, centralizando a divulgação, consulta e acompanhamento de vagas de estágio.

## 4. Escopo Inicial
O sistema deverá oferecer recursos básicos para cadastro de alunos, cadastro de organizações, publicação de vagas, visualização de oportunidades e manifestação de interesse por parte dos alunos.

Nesta versão inicial, o documento não pretende descrever todos os fluxos, regras ou exceções do sistema. Esses pontos deverão ser refinados pela equipe ao longo do projeto.

## 5. Partes Interessadas
- **Alunos:** usuários que buscam vagas de estágio.
- **Empresas e organizações concedentes:** usuários que divulgam vagas e acompanham candidatos.
- **Equipe do projeto:** responsáveis por análise, desenvolvimento, testes e documentação.
- **Professor da disciplina:** responsável por avaliação e acompanhamento acadêmico.

## 6. Requisitos Funcionais
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
- **RF-11:** o sistema deve permitir que alunos manifestem interesse ou se candidatem a uma vaga.
- **RF-12:** o sistema deve permitir que empresas visualizem alunos interessados em suas vagas.
- **RF-13:** o sistema deve permitir que os alunos salvem vagas para consulta posterior.
- **RF-14:** o sistema deve permitir que a empresa informe, ao cadastrar uma vaga, se o processo de candidatura ocorrerá pela própria plataforma ou por meio externo.

## 7. Requisitos Não Funcionais
- **RNF-01:** a plataforma deve ser acessível por navegador web.
- **RNF-02:** a interface deve ser responsiva para computadores, tablets e celulares.
- **RNF-03:** o sistema deve proteger dados pessoais de alunos e empresas.
- **RNF-04:** o sistema deve utilizar mecanismos de autenticação para controlar o acesso às funcionalidades.
- **RNF-05:** as páginas de listagem e consulta devem apresentar tempo de resposta adequado para uso acadêmico.
- **RNF-06:** o código-fonte deve ser organizado de forma clara, favorecendo manutenção e evolução.
- **RNF-07:** a documentação deve ser mantida em uma pasta própria do repositório.
- **RNF-08:** o sistema deve ser projetado para permitir inclusão futura de novos filtros, perfis e regras de candidatura.
- **RFN-09:** A plataforma deve estar disponível para acesso na maior parte do tempo, garantindo que alunos e empresas possam utilizá-la sem interrupções frequentes.
- **RNF-10:** A plataforma deve estar disponível para acesso na maior parte do tempo, garantindo que alunos e empresas possam utilizá-la sem interrupções frequentes.

## 8. Regras de Negócio Iniciais
- **RN-01:** somente empresas cadastradas devem poder publicar vagas.
- **RN-02:** alunos devem estar cadastrados para manifestar interesse em uma vaga.
- **RN-03:** uma vaga deve conter informações mínimas para publicação, como título, descrição, área, modalidade e dados da organização.
- **RN-04:** cada empresa deve gerenciar apenas as vagas cadastradas por ela.
- **RN-05:** alunos não devem poder se candidatar mais de uma vez para a mesma vaga.
- **RN-06:** vagas com candidatura externa devem conter obrigatoriamente um link ou instrução clara para inscrição.
- **RN-07:** uma vaga encerrada ou inativada pela empresa não deve mais aparecer na listagem de oportunidades disponíveis para os alunos.
- **RN-08:** o perfil e as informações de contato do aluno só devem ficar acessíveis para a empresa após a formalização da candidatura na respectiva vaga.
- **RN-09:** a alteração dos dados de uma vaga já publicada não deve invalidar ou cancelar as candidaturas que já foram realizadas anteriormente para aquela oportunidade.
- **RN-10:** o histórico de candidaturas e de vagas encerradas deve ser preservado para consulta das partes envolvidas, não sendo apagado definitivamente do sistema.

## 9. Organização Recomendada do Repositório
```text
/
├── README.md
├── docs/
│   └── requisitos-software.md
├── src/
│   ├── frontend/
│   └── backend/
└── tests/
```

A estrutura acima é uma sugestão inicial e pode ser ajustada conforme as tecnologias escolhidas pela equipe.

## 10. Critérios Básicos de Aceitação
- Alunos conseguem visualizar vagas disponíveis.
- Empresas conseguem cadastrar pelo menos uma vaga.
- Uma vaga cadastrada apresenta informações suficientes para o aluno entender a oportunidade.
- O README aponta para a documentação de requisitos.
- A documentação mantém requisitos funcionais e não funcionais identificados por código.
- As histórias de usuário possuem critérios de aceitação básicos.

## 11. Pendências para Refinamento
- Definir tecnologias de frontend, backend e banco de dados.
- Detalhar os campos obrigatórios dos cadastros.
- Definir fluxo completo de candidatura.
- Definir regras de aprovação, expiração ou remoção de vagas.
- Definir responsabilidades da equipe por módulo.
