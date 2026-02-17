import sqlite3
import hashlib

CARGOS = {
    1: "gerente",
    2: "supervisor",
    3: "funcionario"
}

PERMISSOES = {
    1: "acesso total ao banco de dados",
    2: "acesso total, mas alteracoes aplicadas somente com confirmacao do nivel 1",
    3: "acesso apenas para visualizacao dos dados"
}

def conectar_db():
    return sqlite3.connect("estoque.db")

def gerar_hash_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

def cria_tabela_usuarios():
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL,
                salario REAL NOT NULL CHECK (salario > 0),
                nivel_acesso INTEGER NOT NULL CHECK (nivel_acesso IN (1, 2, 3)),
                ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
            )
        """)

        cursor.execute("PRAGMA table_info(usuarios)")
        colunas = {coluna[1] for coluna in cursor.fetchall()}

        if "salario" not in colunas:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN salario REAL NOT NULL DEFAULT 1")

        if "nivel_acesso" not in colunas:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN nivel_acesso INTEGER NOT NULL DEFAULT 3")

        if "senha_hash" not in colunas and "senha" in colunas:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN senha_hash TEXT")
            cursor.execute("SELECT id, senha FROM usuarios")
            usuarios = cursor.fetchall()
            for usuario_id, senha_legada in usuarios:
                hash_senha = gerar_hash_senha(senha_legada)
                cursor.execute(
                    "UPDATE usuarios SET senha_hash = ? WHERE id = ?",
                    (hash_senha, usuario_id)
                )

        if "ativo" not in colunas:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN ativo INTEGER NOT NULL DEFAULT 1")

        if "senha_hash" in colunas:
            cursor.execute("UPDATE usuarios SET senha_hash = '' WHERE senha_hash IS NULL")

        conn.commit()

def cria_usuario(nome, senha, salario, nivel_acesso):
    nome = nome.strip()

    if not nome:
        print("❌ Nome obrigatório\n")
        return
    if salario <= 0:
        print("❌ Salário deve ser maior que zero\n")
        return
    if nivel_acesso not in (1, 2, 3):
        print("❌ Nível inválido! Use 1, 2 ou 3\n")
        return
    if not senha.strip():
        print("❌ Senha obrigatória\n")
        return

    senha_hash = gerar_hash_senha(senha)

    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usuarios (nome, senha_hash, salario, nivel_acesso, ativo) VALUES (?, ?, ?, ?, 1)",
                (nome, senha_hash, salario, nivel_acesso)
            )
        print(f"✅ Usuário {nome} criado com sucesso\n")
    except sqlite3.IntegrityError:
        print(f"⚠️ Usuário {nome} já existe no banco de dados\n")
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}\n")

def verificar_acesso(nome, senha):
    senha_hash = gerar_hash_senha(senha)
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nivel_acesso FROM usuarios WHERE nome = ? AND senha_hash = ? AND ativo = 1",
            (nome, senha_hash)
        )
        resultado = cursor.fetchone()

        if resultado is not None:
            nivel_acesso = resultado[0]
            print(f"✅ Acesso concedido! Nível de acesso: {nivel_acesso}\n")
            return nivel_acesso
        else:
            print(f"❌ Acesso negado! Nome ou senha incorretos\n")
            return None
    
def alterar_acesso(nivel_logado, nome_alvo, novo_nivel):
    try:
        if nivel_logado != 1:
            print("❌ Apenas nível 1 (gerente) pode alterar nível de acesso\n")
            return

        if novo_nivel not in [1, 2, 3]:
            print(f"❌ Nível inválido! Use 1, 2 ou 3\n")
            return
        
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM usuarios WHERE nome = ? AND ativo = 1", (nome_alvo,))
            resultado = cursor.fetchone()

            if resultado is not None:
                cursor.execute("UPDATE usuarios SET nivel_acesso = ? WHERE nome = ?", (novo_nivel, nome_alvo))
                conn.commit()
                print(f"✅ Nível de acesso de {nome_alvo} alterado para {novo_nivel}\n")
            else:
                print(f"❌ Usuário {nome_alvo} não encontrado ou inativo\n")
    except Exception as e:
        print(f"❌ Erro ao alterar acesso: {e}\n")

def listar_usuarios():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nome, nivel_acesso FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    
    print("\n👥 Lista de Usuários:")
    for nome, nivel in usuarios:
        print(f"Nome: {nome} | Nível de Acesso: {nivel}")
    print()

def existe_usuario_cadastrado():
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total = cursor.fetchone()[0]
    return total > 0

def pode_inserir(nivel):
    return nivel in [1, 2]

def pode_deletar(nivel):
    return nivel in [1, 2]

def pode_visualizar(nivel):
    return nivel in [1, 2, 3]

def login_usuario():
    print("\n🔐 Login de Usuário")
    nome = input("Nome: ").strip()
    senha = input("Senha: ").strip()
    nivel = verificar_acesso(nome, senha)
    if nivel is not None:
        print(f"👋 Bem-vindo: {nome}")
        return nome, nivel
    return None, None

def menu_acesso():
    nome_logado = None
    nivel_logado = None

    while True:
        print("\n📋 Menu de Acesso")
        if nome_logado is not None:
            print(f"👤 Logado como: {nome_logado} | Nível: {nivel_logado}")
        else:
            print("👤 Nenhum usuário logado")
        print("1. Login")
        print("2. Criar usuário")
        print("3. Alterar nível de acesso")
        print("4. Listar usuários")
        print("5. Sair")

        escolha = input("Escolha uma opção: ").strip()

        try:
            if escolha == "1":
                nome_logado, nivel_logado = login_usuario()
            elif escolha == "2":
                if not existe_usuario_cadastrado():
                    print("\n⚙️ Primeiro usuário do sistema (será criado como nível 1)")
                    nome = input("Nome do usuário: ").strip()
                    senha = input("Senha do usuário: ").strip()
                    salario = float(input("Salário do usuário: ").strip())
                    cria_usuario(nome, senha, salario, 1)
                    continue

                if nivel_logado is None:
                    print("❌ Faça login antes de criar usuários\n")
                    continue
                if nivel_logado != 1:
                    print("❌ Apenas nível 1 (gerente) pode criar usuários\n")
                    continue

                nome = input("Nome do usuário: ").strip()
                senha = input("Senha do usuário: ").strip()
                salario = float(input("Salário do usuário: ").strip())
                nivel_acesso = int(input("Nível de acesso (1, 2 ou 3): ").strip())
                cria_usuario(nome, senha, salario, nivel_acesso)
            elif escolha == "3":
                if nivel_logado is None:
                    print("❌ Faça login antes de alterar níveis\n")
                    continue
                if nivel_logado != 1:
                    print("❌ Apenas nível 1 (gerente) pode alterar níveis\n")
                    continue

                print(f"🔎 Usuário logado: {nome_logado} | Nível: {nivel_logado}")
                nome_alvo = input("Nome do usuário para alterar nível: ").strip()
                novo_nivel = int(input("Novo nível de acesso (1, 2 ou 3): ").strip())
                alterar_acesso(nivel_logado, nome_alvo, novo_nivel)
            elif escolha == "4":
                if nivel_logado is None:
                    print("❌ Faça login antes de listar usuários\n")
                    continue
                listar_usuarios()
            elif escolha == "5":
                print("Saindo...")
                break
            else:
                print("Opção inválida! Tente novamente.\n")
        except ValueError:
            print("❌ Entrada inválida! Use números quando solicitado.\n")
        except Exception as e:
            print(f"❌ Erro inesperado: {e}\n")

if __name__ == "__main__":
    cria_tabela_usuarios()
    menu_acesso()