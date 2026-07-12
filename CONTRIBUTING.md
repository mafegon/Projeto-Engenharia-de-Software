# Guia de contribuição

## Regra obrigatória para commits

Toda mensagem de commit deve seguir o padrão de commits semânticos adotado em
[iuricode/padroes-de-commits](https://github.com/iuricode/padroes-de-commits).

Formato obrigatório:

```text
:emoji: tipo: descrição curta
```

Exemplos:

```text
:sparkles: feat: Adiciona cadastro
:bug: fix: Corrige login
:books: docs: Atualiza requisitos
:white_check_mark: test: Testa candidaturas
:recycle: refactor: Simplifica autenticação
:wrench: chore: Ajusta configuração
```

### Tipos aceitos

- `feat`: nova funcionalidade;
- `fix`: correção de defeito;
- `docs`: alteração exclusiva de documentação;
- `test`: criação ou alteração de testes;
- `build`: dependências e processo de build;
- `perf`: melhoria de desempenho;
- `style`: formatação sem mudança funcional;
- `refactor`: refatoração sem nova funcionalidade ou correção;
- `chore`: configuração e tarefas de manutenção;
- `ci`: integração contínua;
- `raw`: configurações, dados ou parâmetros;
- `cleanup`: remoção de código desnecessário;
- `remove`: exclusão de arquivos ou funcionalidades obsoletas.

### Regras de escrita

1. Use um emoji coerente com o tipo do commit.
2. Use uma descrição objetiva, preferencialmente com até quatro palavras.
3. Separe mudanças de naturezas diferentes em commits diferentes.
4. Use o corpo do commit quando for necessário explicar motivo, impacto ou instruções futuras.
5. Não use mensagens vagas como `.`, `ajustes` ou `ja ajeitei`.
6. Revise o diff e execute as validações aplicáveis antes do commit.

## Fluxo antes de publicar

1. Atualize sua branch com a origem.
2. Revise apenas os arquivos que pertencem à mudança.
3. Execute os testes ou verificações disponíveis.
4. Crie commits pequenos e semanticamente coerentes.
5. Envie a branch e informe os SHAs para revisão.
