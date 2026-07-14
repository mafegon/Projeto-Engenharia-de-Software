# Gestão de Processo

## 1.1 Metodologia Adotada e Justificativa (Kanban)
Adotamos o **Kanban** como metodologia ágil para a gestão do desenvolvimento do nosso sistema. A escolha do Kanban justifica-se pelo contexto e limitações do projeto:

* **Flexibilidade no fluxo de trabalho:** Como a equipe possui rotinas acadêmicas e profissionais paralelas, o Kanban permitiu que cada integrante puxasse tarefas de acordo com sua disponibilidade semanal, sem a pressão de metas fixas e rígidas de tempo (comum nas Sprints do Scrum).
* **Foco no fluxo contínuo:** Evitamos gargalos no desenvolvimento limitando o trabalho em progresso (*WIP - Work in Progress*). Dessa forma, uma funcionalidade do Django só era iniciada após a conclusão ou revisão da anterior.
* **Redução de reuniões formais:** O quadro visual eliminou a necessidade de ritos diários complexos, permitindo que a comunicação ocorresse de forma assíncrona pelo WhatsApp/Discord e síncrona diretamente nas revisões de código.

---

## 1.2 Product Backlog (Lista Priorizada de User Stories)

Abaixo está o estado atual do nosso Backlog de histórias de usuário mapeado no fluxo Kanban:

| ID | História de Usuário (US) | Prioridade | Status |
| :--- | :--- | :--- | :--- |
| **US-01** | Cadastro de Aluno | Essencial (MVP) | Concluído |
| **US-02** | Login de Aluno | Essencial (MVP) | Concluído |
| **US-03** | Cadastro de Empresa | Essencial (MVP) | Concluído |
| **US-04** | Publicação de Vaga | Essencial (MVP) | Concluído |
| **US-06** | Visualização de Vagas | Essencial (MVP) | Concluído |
| **US-08** | Candidatura / Interesse | Essencial (MVP) | Concluído |
| **US-05** | Edição de Vaga | Desejável | 
| **US-07** | Filtro de Vagas | Desejável | 
| **US-09** | Acompanhamento de Candidatos | Desejável | 
| **US-10** | Salvamento de Vagas (Favoritos) | Desejável |

---

## 1.3 Evidência do Fluxo (Quadro Kanban)


## 1.4 Lições Aprendidas

Durante o desenvolvimento deste projeto, a equipe pôde experimentar na prática os desafios reais de engenharia de software sob prazos acadêmicos rigorosos. O que deu certo foi a escolha de uma stack ágil e integrada (Django + Tailwind CSS), que facilitou a criação rápida de interfaces responsivas e a estruturação de rotas limpas, além da excelente organização visual das tarefas através do Trello, o que evitou o caos na divisão das atividades do grupo. Por outro lado, o que enfrentamos como principal limitação foi a oscilação de foco e a gestão de tempo da equipe. Como dividimos a rotina com outras obrigações, a falta de um ritmo constante no início fez com que acumulássemos o desenvolvimento e a integração de código na reta final do prazo. Se fôssemos fazer diferente hoje, estabeleceríamos metas semanais menores e entregas parciais obrigatórias desde o primeiro dia de projeto. Isso distribuiria melhor o esforço do grupo ao longo do calendário, garantindo um foco contínuo no MVP e evitando a sobrecarga de trabalho nos dias que antecederam a entrega final.
