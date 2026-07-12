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
- [Relatórios](docs/relatorios)
- [Modelagem](docs/modelagem)
- [Guia de contribuição e padrão obrigatório de commits](CONTRIBUTING.md)

