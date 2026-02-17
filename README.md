# Sistema de Estoque + Controle de Acesso (Python + SQLite)

Projeto de estudo com:
- controle de usuários por nível de acesso
- autenticação por login/senha
- cadastro e gestão de itens de estoque
- persistência em SQLite

## Estrutura

- `cadastro_acesso.py`  
  Responsável por usuários, login, permissões e níveis de acesso.

- `entrada_dados_sqlite.py`  
  Responsável pelo CRUD de estoque com regras de acesso por nível.

- `estoque.db`  
  Banco SQLite usado pelos dois módulos.

## Níveis de acesso

- **Nível 1 (gerente)**
  - acesso total
  - pode criar usuários
  - pode alterar nível de acesso de outros usuários
  - pode inserir/deletar/listar itens de estoque

- **Nível 2 (supervisor)**
  - acesso operacional
  - pode inserir/deletar no estoque somente com aprovação do nível 1
  - pode listar estoque

- **Nível 3 (funcionário)**
  - acesso somente visualização
  - pode listar estoque
  - não pode inserir/deletar itens

## Regras importantes já implementadas

- cada usuário possui: `nome`, `salario`, `nivel_acesso` e `ativo`
- senha salva como hash (`sha256`), não em texto puro
- login só permite usuários ativos (`ativo = 1`)
- criação do primeiro usuário (bootstrap) cria automaticamente como nível 1
- migração básica de tabela antiga de usuários ao iniciar

## Como executar

No terminal, dentro da pasta do projeto (`estoque_validaçao`):

```bash
python cadastro_acesso.py
```

Abre o menu de usuários (login, criação, alteração de nível, listagem).

Para executar o módulo de estoque:

```bash
python entrada_dados_sqlite.py
```

## Fluxo recomendado (primeira execução)

1. Rodar `cadastro_acesso.py`
2. Criar o primeiro usuário (será nível 1)
3. Fazer login com esse usuário
4. Criar usuários de nível 2 e 3
5. Rodar `entrada_dados_sqlite.py` para operar o estoque

## Observações

- Banco atual: SQLite local (`estoque.db`)
- Interface gráfica com Tkinter está no escopo futuro
