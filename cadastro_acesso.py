import sqlite3
import hashlib

CARGOS_VALIDOS = ("gerente", "supervisor", "operado")

NIVEL_PARA_CARGO = {
    1: "gerente",
    2: "supervisor",
    3: "operado"
}

PERMISSOES = {
    "gerente": "acesso total ao banco de dados",
    "supervisor": "acesso total ao banco de dados",
    "operado": "acesso apenas para visualizacao dos dados"
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
                cargo TEXT NOT NULL CHECK (cargo IN ('gerente', 'supervisor', 'operado')),
                ativo INTEGER NOT NULL DEFAULT 1 CHECK (ativo IN (0, 1))
            )
        """)

        cursor.execute("PRAGMA table_info(usuarios)")
        colunas = {coluna[1] for coluna in cursor.fetchall()}

        if "salario" not in colunas:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN salario REAL NOT NULL DEFAULT 1")

        if "cargo" not in colunas:
            cursor.execute("ALTER TABLE usuarios ADD COLUMN cargo TEXT NOT NULL DEFAULT 'operado'")

        if "nivel_acesso" in colunas:
            cursor.execute("SELECT id, nivel_acesso, cargo FROM usuarios")
            usuarios = cursor.fetchall()
            for usuario_id, nivel_legado, cargo_atual in usuarios:
                if cargo_atual:
                    continue
                cargo_migrado = NIVEL_PARA_CARGO.get(nivel_legado, "operado")
                cursor.execute(
                    "UPDATE usuarios SET cargo = ? WHERE id = ?",
                    (cargo_migrado, usuario_id)
                )

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

        cursor.execute("UPDATE usuarios SET cargo = 'operado' WHERE cargo IS NULL OR TRIM(cargo) = ''")
        cursor.execute("UPDATE usuarios SET cargo = 'operado' WHERE cargo = 'funcionario' OR cargo = 'operador'")

        conn.commit()

def cria_usuario(nome, senha, salario, cargo):
    nome = nome.strip()
    cargo = cargo.strip().lower()

    if not nome:
        print("❌ Nome obrigatório\n")
        return
    if salario <= 0:
        print("❌ Salário deve ser maior que zero\n")
        return
    if cargo not in CARGOS_VALIDOS:
        print("❌ Cargo inválido! Use gerente, supervisor ou operado\n")
        return
    if not senha.strip():
        print("❌ Senha obrigatória\n")
        return

    senha_hash = gerar_hash_senha(senha)

    try:
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO usuarios (nome, senha_hash, salario, cargo, ativo) VALUES (?, ?, ?, ?, 1)",
                (nome, senha_hash, salario, cargo)
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
            "SELECT cargo FROM usuarios WHERE nome = ? AND senha_hash = ? AND ativo = 1",
            (nome, senha_hash)
        )
        resultado = cursor.fetchone()

        if resultado is not None:
            cargo = resultado[0]
            print(f"✅ Acesso concedido! Cargo: {cargo}\n")
            return cargo
        else:
            print(f"❌ Acesso negado! Nome ou senha incorretos\n")
            return None
    
def alterar_acesso(cargo_logado, nome_alvo, novo_cargo):
    try:
        novo_cargo = novo_cargo.strip().lower()

        if cargo_logado != "gerente":
            print("❌ Apenas gerente pode alterar cargo\n")
            return

        if novo_cargo not in CARGOS_VALIDOS:
            print(f"❌ Cargo inválido! Use gerente, supervisor ou operado\n")
            return
        
        with conectar_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM usuarios WHERE nome = ? AND ativo = 1", (nome_alvo,))
            resultado = cursor.fetchone()

            if resultado is not None:
                cursor.execute("UPDATE usuarios SET cargo = ? WHERE nome = ?", (novo_cargo, nome_alvo))
                conn.commit()
                print(f"✅ Cargo de {nome_alvo} alterado para {novo_cargo}\n")
            else:
                print(f"❌ Usuário {nome_alvo} não encontrado ou inativo\n")
    except Exception as e:
        print(f"❌ Erro ao alterar acesso: {e}\n")

def listar_usuarios():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nome, cargo FROM usuarios")
    usuarios = cursor.fetchall()
    conn.close()
    
    print("\n👥 Lista de Usuários:")
    for nome, cargo in usuarios:
        print(f"Nome: {nome} | Cargo: {cargo}")
    print()

def existe_usuario_cadastrado():
    with conectar_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total = cursor.fetchone()[0]
    return total > 0

def pode_inserir(cargo):
    return cargo in ["gerente", "supervisor"]

def pode_deletar(cargo):
    return cargo in ["gerente", "supervisor"]

def pode_visualizar(cargo):
    return cargo in CARGOS_VALIDOS

def login_usuario():
    print("\n🔐 Login de Usuário")
    nome = input("Nome: ").strip()
    senha = input("Senha: ").strip()
    cargo = verificar_acesso(nome, senha)
    if cargo is not None:
        print(f"👋 Bem-vindo: {nome}")
        return nome, cargo
    return None, None

def menu_acesso():
    nome_logado = None
    cargo_logado = None

    while True:
        print("\n📋 Menu de Acesso")
        if nome_logado is not None:
            print(f"👤 Logado como: {nome_logado} | Cargo: {cargo_logado}")
        else:
            print("👤 Nenhum usuário logado")
        print("1. Login")
        print("2. Criar usuário")
        print("3. Alterar cargo")
        print("4. Listar usuários")
        print("5. Sair")

        escolha = input("Escolha uma opção: ").strip()

        try:
            if escolha == "1":
                nome_logado, cargo_logado = login_usuario()
            elif escolha == "2":
                if not existe_usuario_cadastrado():
                    print("\n⚙️ Primeiro usuário do sistema (será criado como gerente)")
                    nome = input("Nome do usuário: ").strip()
                    senha = input("Senha do usuário: ").strip()
                    salario = float(input("Salário do usuário: ").strip())
                    cria_usuario(nome, senha, salario, "gerente")
                    continue

                if cargo_logado is None:
                    print("❌ Faça login antes de criar usuários\n")
                    continue
                if cargo_logado != "gerente":
                    print("❌ Apenas gerente pode criar usuários\n")
                    continue

                nome = input("Nome do usuário: ").strip()
                senha = input("Senha do usuário: ").strip()
                salario = float(input("Salário do usuário: ").strip())
                cargo = input("Cargo (gerente, supervisor ou operado): ").strip().lower()
                cria_usuario(nome, senha, salario, cargo)
            elif escolha == "3":
                if cargo_logado is None:
                    print("❌ Faça login antes de alterar cargos\n")
                    continue
                if cargo_logado != "gerente":
                    print("❌ Apenas gerente pode alterar cargos\n")
                    continue

                print(f"🔎 Usuário logado: {nome_logado} | Cargo: {cargo_logado}")
                nome_alvo = input("Nome do usuário para alterar cargo: ").strip()
                novo_cargo = input("Novo cargo (gerente, supervisor ou operado): ").strip().lower()
                alterar_acesso(cargo_logado, nome_alvo, novo_cargo)
            elif escolha == "4":
                if cargo_logado is None:
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