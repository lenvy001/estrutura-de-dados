import sqlite3

from cadastro_acesso import cria_tabela_usuarios, login_usuario, verificar_acesso

def conectar_db():
    return sqlite3.connect("estoque.db")

def criar_tabela():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            quantidade INTEGER NOT NULL CHECK (quantidade >= 0),
            preco REAL NOT NULL CHECK (preco > 0)
        )
    """)
    conn.commit()
    conn.close()

def inserir_dados(nome, quantidade, preco):
    print(f"\n📝 Confirma inserção?")
    print(f"Nome: {nome} | Qtd: {quantidade} | Preço: R$ {preco:.2f}")
    confirmacao = input("Digite (s/n): ").strip().lower()
    
    if confirmacao == "s":
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM estoque WHERE nome = ?", (nome,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO estoque (nome, quantidade, preco) VALUES (?, ?, ?)", (nome, quantidade, preco))
            conn.commit()
            print(f"✅ {nome} inserido com sucesso\n")
        else:
            print(f"⚠️ {nome} já existe no banco de dados\n")
        conn.close()
    else:
        print(f"❌ Inserção cancelada\n")

def deletar_dados(nome):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM estoque WHERE nome = ?",(nome,))
    resultado = cursor.fetchone()
    
    if resultado is not None:
        print(f"\n🗑️  Confirma exclusão?")
        print(f"Nome: {resultado[1]} | Qtd: {resultado[2]} | Preço: R$ {resultado[3]:.2f}")
        confirmacao = input("Digite (s/n): ").strip().lower()
        
        if confirmacao == "s":
            cursor.execute("DELETE FROM estoque WHERE nome = ?", (nome,))
            conn.commit()
            print(f"✅ {nome} deletado com sucesso\n")
        else:
            print(f"❌ Exclusão cancelada\n")
    else:
        print(f"⚠️ {nome} não encontrado no banco de dados\n")
    conn.close()

def listar_dados():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM estoque")
    dados = cursor.fetchall()
    conn.close()
    
    if dados:
        print("\n" + "="*60)
        print(f"{'ID':<5} {'NOME':<20} {'QUANTIDADE':<12} {'PREÇO':<10}")
        print("="*60)
        for row in dados:
            print(f"{row[0]:<5} {row[1]:<20} {row[2]:<12} R$ {row[3]:.2f}")
        print("="*60 + "\n")
    else:
        print("\n⚠ Banco de dados vazio!\n")

def solicitar_aprovacao_gerente():
    print("\n🔒 Aprovação do gerente necessária")
    nome = input("Nome do gerente: ").strip()
    senha = input("Senha do gerente: ").strip()
    nivel = verificar_acesso(nome, senha)
    if nivel == 1:
        print("✅ Aprovação concedida\n")
        return True
    print("❌ Aprovação negada\n")
    return False

def menu(nivel_acesso):
    criar_tabela()
    while True:
        print("\n=== MENU ESTOQUE ===")
        print("1 - Inserir produto")
        print("2 - Deletar produto")
        print("3 - Listar produtos")
        print("4 - Sair")
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "1":
            if nivel_acesso == 3:
                print("❌ Acesso negado: nível 3 não pode inserir.\n")
                continue
            if nivel_acesso == 2 and not solicitar_aprovacao_gerente():
                continue
            nome = input("Nome do produto: ").strip()
            try:
                quantidade = int(input("Quantidade: "))
                preco = float(input("Preço: "))
                inserir_dados(nome, quantidade, preco)
            except ValueError:
                print("❌ Entrada inválida!")
                
        elif opcao == "2":
            if nivel_acesso == 3:
                print("❌ Acesso negado: nível 3 não pode deletar.\n")
                continue
            if nivel_acesso == 2 and not solicitar_aprovacao_gerente():
                continue
            nome = input("Nome do produto a deletar: ").strip()
            deletar_dados(nome)
            
        elif opcao == "3":
            listar_dados()
            
        elif opcao == "4":
            print("\n👋 Até logo!")
            break
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    criar_tabela()
    cria_tabela_usuarios()
    nome_logado, nivel = login_usuario()
    if nivel is None:
        print("\n❌ Login inválido. Encerrando.")
    else:
        menu(nivel)