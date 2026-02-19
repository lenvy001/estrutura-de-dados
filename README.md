# Sistema de Estoque + Controle de Acesso (Python + SQLite)

Projeto de estudo com:
- controle de usuários por cargo
- autenticação por login/senha
- cadastro e gestão de itens de estoque
- persistência em SQLite

## Estrutura

- `cadastro_acesso.py`  
  Responsável por usuários, login, permissões e cargos.

- `entrada_dados_sqlite.py`  
  Responsável pelo CRUD de estoque com regras de acesso por cargo.

- `estoque.db`  
  Banco SQLite usado pelos dois módulos.

## Cargos e acessos

- **Gerente**
  - acesso total
  - pode criar usuários
  - pode alterar cargo de outros usuários
  - pode inserir/deletar/listar itens de estoque

- **Supervisor**
  - acesso total
  - pode inserir/deletar/listar itens de estoque

- **Operado**
  - acesso somente visualização
  - pode listar estoque
  - não pode inserir/deletar itens

## Regras importantes já implementadas

- cada usuário possui: `nome`, `salario`, `cargo` e `ativo`
- senha salva como hash (`sha256`), não em texto puro
- login só permite usuários ativos (`ativo = 1`)
- criação do primeiro usuário (bootstrap) cria automaticamente como gerente
- migração de tabela antiga com `nivel_acesso` para `cargo` ao iniciar

## Como executar

No terminal, dentro da pasta do projeto (`estoque_validaçao`):

```bash
python cadastro_acesso.py
```

Abre o menu de usuários (login, criação, alteração de cargo, listagem).

Para executar o módulo de estoque:

```bash
python entrada_dados_sqlite.py
```

## Fluxo recomendado (primeira execução)

1. Rodar `cadastro_acesso.py`
2. Criar o primeiro usuário (será gerente)
3. Fazer login com esse usuário
4. Criar usuários com os cargos `supervisor` e `operado`
5. Rodar `entrada_dados_sqlite.py` para operar o estoque

## Observações

- Banco atual: SQLite local (`estoque.db`)
- Interface gráfica com Tkinter está no escopo futuro
