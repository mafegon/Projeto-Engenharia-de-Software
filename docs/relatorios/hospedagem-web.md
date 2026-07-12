# Hospedagem Web no Render sem Banco de Dados

## 1. Objetivo

Disponibilizar a aplicação por um endereço HTTPS público, sem exigir que o usuário instale Python, Django ou Tailwind CSS e sem depender de um computador local ligado. Nesta fase não há banco de dados.

## 2. Arquitetura

```text
GitHub
  └── código-fonte e acionamento do deploy
        ↓
Render
  └── Django, Gunicorn, regras de negócio, templates e arquivos estáticos
        └── dados efêmeros na memória do processo
```

O endereço entregue ao usuário será o domínio público do serviço Render. O tráfego do navegador até o Render usa HTTPS.

O código atual define `DATABASES = {}`. Cadastros, sessões da API, favoritos, candidaturas e edições de perfil ficam em memória e podem desaparecer em reinícios, novos deploys ou suspensões da instância. A versão publicada é adequada para demonstração com dados fictícios, não para armazenar dados pessoais reais.

## 3. Responsabilidades

### Backend

- configurar Django para receber valores por variáveis de ambiente;
- manter o endpoint `/health/`;
- executar a aplicação com Gunicorn;
- servir arquivos estáticos com WhiteNoise;
- validar os contratos e as regras de negócio.

### Banco de dados

- criar e administrar o projeto Supabase;
- fornecer a URL de conexão de forma segura;
- definir schema, constraints e políticas;
- revisar e autorizar migrations;
- manter cópias de segurança compatíveis com o plano adotado.

### Frontend

- manter templates e componentes visuais;
- editar o aplicativo `theme`;
- validar responsividade e acessibilidade;
- gerar os estilos Tailwind usados pela aplicação.

## 4. Banco de dados futuro

O Supabase não faz parte da publicação atual. Quando a equipe de banco concluir e aprovar o schema, as migrations e as políticas, o Django poderá receber uma `DATABASE_URL` protegida. Para um serviço Django persistente em rede IPv4, a equipe deverá avaliar a URL do **Session pooler** exibida no botão **Connect** do projeto Supabase.

```text
postgresql://postgres.PROJECT_REF:PASSWORD@aws-0-REGION.pooler.supabase.com:5432/postgres
```

O exemplo permanece comentado em `.env.example`; ele não é configurado no `render.yaml` e não abre conexão nesta fase. Uma senha real deverá existir apenas nas variáveis protegidas do Render e nos ambientes autorizados.

## 5. Configuração no Render

O arquivo `render.yaml` prepara um Web Service gratuito com:

- build executado por `bash build.sh`;
- servidor `gunicorn --chdir backend --workers 1 config.wsgi:application --bind 0.0.0.0:$PORT`;
- verificação de saúde em `/health/`;
- Python 3.13;
- segredo Django gerado pelo Render;
- `DJANGO_DEBUG=false`, HSTS ativo e `RUN_MIGRATIONS=false`;
- hostname e origem HTTPS incorporados automaticamente a partir de `RENDER_EXTERNAL_HOSTNAME`.

No painel do Render, configure:

```text
DJANGO_DEBUG=false
DJANGO_SECURE_HSTS_SECONDS=3600
RUN_MIGRATIONS=false
```

O Render gera `DJANGO_SECRET_KEY`. Não configure `DATABASE_URL` antes da etapa de banco. Domínios personalizados futuros devem ser adicionados a `DJANGO_ALLOWED_HOSTS` e `DJANGO_CSRF_TRUSTED_ORIGINS`.

## 6. Build

O `build.sh` executa:

1. instalação das dependências;
2. instalação do compilador standalone do Tailwind;
3. build do CSS;
4. coleta dos arquivos estáticos;
O build não executa migrations. `RUN_MIGRATIONS=false` explicita essa decisão, mas não autoriza migrations quando alterado: qualquer fluxo futuro deverá ser implementado e revisado pela equipe de banco.

## 7. Segurança

- nunca versionar `.env`;
- nunca publicar a senha PostgreSQL;
- nunca expor a chave `service_role`;
- manter `DJANGO_DEBUG=false` na hospedagem;
- não inserir dados pessoais ou senhas reais enquanto a persistência for em memória;
- usar somente conexões SSL quando o banco futuro for integrado;
- trocar imediatamente qualquer credencial exposta.

## 8. Rotas publicadas

- `/`: login e cadastro;
- `/vagas/`: consulta e filtros;
- `/vagas/<slug>/`: detalhe da vaga;
- `/perfil/`: perfil;
- `/backend-status/`: diagnóstico técnico;
- `/api/v1/`: API;
- `/health/`: health check.

## 9. Validação antes da apresentação

- abrir o endereço do Render com antecedência;
- verificar `/health/`;
- testar cadastro, login, filtros, favorito, candidatura e perfil com dados fictícios;
- validar arquivos estáticos;
- avisar que os dados são efêmeros;
- manter vídeo de contingência.

O plano gratuito pode suspender o serviço quando estiver inativo. O primeiro acesso após a suspensão pode apresentar cold start; isso não significa que o endereço deixou de existir.

## 10. Validação local

```powershell
python backend\manage.py check
python backend\manage.py test
```

Para simular as principais configurações de produção, use `DJANGO_DEBUG=false`, um `DJANGO_SECRET_KEY` temporário e `RENDER_EXTERNAL_HOSTNAME` fictício.

## 11. Referências oficiais

- [Conexões PostgreSQL do Supabase](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [Deploy de Django no Render](https://render.com/docs/deploy-django)
- [Checklist de produção do Django](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
