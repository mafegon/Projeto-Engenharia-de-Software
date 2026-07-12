# 🎓 Plataforma de Anúncios de Estágios Acadêmicos
Repositório destinado ao projeto final da disciplina de Engenharia de Software, ministrada pelo **Professor Adolfo Colares**, na **Universidade Federal do Amapá (UNIFAP)**, no semestre de 2026.1

## 👥 Componentes do Grupo
- Daniela Sepeda
- Elton Braian
- Geovanni Rodrigues
- Maria Fernanda Fernandes
- Vitória Ataíde

## 📚 Sobre o projeto
Observa-se, no âmbito das instituições de ensino técnico e superior, uma demanda constante por estágios acadêmicos por parte dos discentes, bem como a necessidade de órgãos e empresas anunciarem e preencherem vagas de estágio em diversas categorias.

O objetivo deste projeto é desenvolver uma plataforma web capaz de unificar os interesses de ambas as partes **(acadêmicos e organizações concedentes)**, oferecendo aos alunos uma **visualização direta das vagas de estágio disponíveis**  e proporcionar às empresas **uma plataforma de cadastro unificada e versátil às suas necessidades**.

## 🧰 Stack oficial

- **Aplicação web e backend:** Python com Django.
- **Interface:** templates do Django com Tailwind CSS.
- **Integração de estilos:** [django-tailwind](https://github.com/timonweb/django-tailwind).
- **Banco de dados:** PostgreSQL.

Django concentra as páginas, autenticação, regras de negócio e acesso a dados. O Tailwind CSS será integrado ao projeto pelo `django-tailwind`. Esta é a definição tecnológica oficial do projeto.

## ☁️ Hospedagem web atual

- **Código e integração:** GitHub.
- **Aplicação Django:** Render Web Service.
- **Persistência nesta fase:** memória do processo, sem banco de dados.
- **Banco futuro:** PostgreSQL no Supabase, após entrega e aprovação da equipe de banco.
- **Arquivos estáticos:** WhiteNoise no serviço Django.

**Aplicação publicada:** https://projeto-estagios.onrender.com

O deploy foi validado por HTTPS com health check, CSS e JavaScript estáticos, cadastro, perfil, filtros, favorito e candidatura. O código publicado corresponde à branch `main` deste repositório.

Depois do deploy, o sistema pode ser acessado pelo endereço HTTPS público do Render sem manter um computador local ligado. Nesta fase, `DATABASES = {}` e os cadastros, tokens, favoritos, candidaturas e alterações de perfil ficam somente na memória do processo. Eles podem desaparecer a qualquer reinício, novo deploy ou suspensão do serviço. Não use dados pessoais ou credenciais reais.

O plano gratuito do Render pode suspender o serviço por inatividade. O primeiro acesso após a suspensão pode levar algum tempo enquanto a instância inicia novamente (cold start).

## 💻 Preparação local

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python backend\manage.py check
python backend\manage.py tailwind build
python backend\manage.py runserver
```

O ambiente atual não usa SQLite, PostgreSQL ou Supabase: `DATABASES = {}`. A equipe de banco é responsável pelo futuro projeto Supabase, pelo schema e pela aprovação das migrations.

## 🔐 Variáveis de ambiente

Copie `.env.example` apenas como referência e configure as variáveis no sistema operacional ou no painel do Render:

- `DJANGO_SECRET_KEY`;
- `DJANGO_DEBUG`;
- `DJANGO_SECURE_HSTS_SECONDS`;
- `RUN_MIGRATIONS`.

No Render, o hostname externo é incorporado automaticamente por `RENDER_EXTERNAL_HOSTNAME`. `DATABASE_URL` permanece comentada em `.env.example` apenas como contrato de integração futura. Nunca publique senha de banco nem chave `service_role`.

## ✅ Rotas e validação

- `/`: login e cadastro;
- `/vagas/`: consulta e filtros de vagas;
- `/vagas/<slug>/`: detalhes, favorito e candidatura;
- `/perfil/`: perfil do aluno;
- `/backend-status/`: estado técnico da API;
- `/api/v1/`: API HTTP;
- `/health/`: verificação de saúde usada pelo Render.

```powershell
python backend\manage.py check
python backend\manage.py test
```

### 📋 Requisitos Funcionais
- **RF-01:** permitir o cadastro e autenticação de alunos interessados em vagas de estágio.
- **RF-02:** permitir o cadastro e autenticação de empresas ou organizações concedentes.
- **RF-03:** permitir que empresas cadastrem, editem e removam vagas de estágio.
- **RF-04:** permitir que alunos visualizem a lista de vagas disponíveis.
- **RF-05:** permitir a consulta de detalhes de uma vaga, incluindo área, descrição, requisitos, modalidade, carga horária e informações da empresa.
- **RF-06:** permitir a filtragem de vagas por área, modalidade, localidade ou outros critérios relevantes.
- **RF-07:** permitir que alunos manifestem interesse ou se candidatem a uma vaga de estágio.
- **RF-08:** permitir que empresas acompanhem os candidatos vinculados às suas vagas.

### ⚙️ Requisitos Não Funcionais
- **RNF-01:** a plataforma deve possuir interface simples, responsiva e adequada para uso em computadores e dispositivos móveis.
- **RNF-02:** o sistema deve proteger dados pessoais de alunos e empresas, considerando boas práticas de segurança e privacidade.
- **RNF-03:** o sistema deve apresentar tempo de resposta adequado para consultas e listagem de vagas.
- **RNF-04:** a documentação do projeto deve ser mantida de forma organizada para facilitar o trabalho em equipe.
- **RNF-05:** o código deve seguir padrões de organização, legibilidade e manutenção definidos pela equipe.
- **RNF-06:** a plataforma deve permitir evolução futura para novos perfis, filtros e fluxos de candidatura.

## 📁 Documentação
- [Documento de Requisitos de Software](docs/relatorios/requisitos-software.md)
- [Documento de Visão](docs/relatorios/documento-visao.md)
- [User Stories e Critérios de Aceitação](docs/relatorios/user-stories.md)
- [Hospedagem web no Render e integração futura com Supabase](docs/relatorios/hospedagem-web.md)
- [Relatórios](docs/relatorios)
- [Modelagem](docs/modelagem)
- [Guia de contribuição e padrão obrigatório de commits](CONTRIBUTING.md)
