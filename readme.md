# Teste IPM

O projeto `Test IPM` foi desenvolvida para teste seletivo integrando o Docker para gerenciar os contêineres das aplicações e serviços necessários, incluindo FastAPI, PostgreSQL, pgAdmin e MinIO S3 Storage

## Recursos

- **FastAPI**: Utilizado para a criação da API, oferecendo rotas para o CRUD de arquivos.
- **PostgreSQL**: Banco de dados relacional para o armazenamento de metadados dos arquivos.
- **pgAdmin**: Interface gráfica opcional para gerenciar o banco de dados PostgreSQL.
- **MinIO S3 Storage**: Armazenamento dos arquivos de imagem (JPG, JPEG, PNG) e wayline (KML, KMZ).

## Funcionalidades

- **CRUD de Arquivos de Mídia**: Permite o upload, listagem, atualização e exclusão de arquivos de mídia `media_object_key` (`JPG`, `JPEG`, `PNG`) com validação de formato.
- **CRUD de Arquivos Wayline**: Gerencia arquivos wayline `wayline_object_key` (`KML`, `KMZ`) com validação de formato.
- **Armazenamento Seguro**: Os arquivos são armazenados no MinIO, enquanto outras informaçoes são mantidos no PostgreSQL.

## Instalação

Siga os passos abaixo para configurar e executar o projeto localmente.

1. **Clone o Repositório**

```bash
git clone <url-do-repositorio>
cd test-ipm
```

2. **Execução**

```bash
docker-compose up --build

```

2. **Rotas**

Rota CRUD API

```bash
localhost:8000/
```

ROTA MINIO

```bash
localhost:9001/
```

ROTA PGADMIN ( Não fazia parte das exigências, mas acabei fazendo a integração )

```bash
localhost:5050/
```

3. **Buscar Tabelas no Postgres**

```bash
docker-compose exec -it db-ipm psql -U postgres
\dt
SELECT * FROM media_file;
SELECT * FROM wayline_file;

```
