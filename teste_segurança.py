import pytest
import hashlib
# Importe a função do seu arquivo original
from cadastro_acesso import gerar_hash_senha

def test_gerar_hash_deve_retornar_string_hexadecimal():
    senha = "admin"
    resultado = gerar_hash_senha(senha)
    
    # Verifica se o retorno é uma string e se tem 64 caracteres (padrão SHA-256)
    assert isinstance(resultado, str)
    assert len(resultado) == 64

def test_hashes_de_senhas_diferentes_devem_ser_distintos():
    hash_1 = gerar_hash_senha("senha123")
    hash_2 = gerar_hash_senha("outrasenha")
    
    assert hash_1 != hash_2

def test_mesma_senha_deve_gerar_sempre_o_mesmo_hash():
    # Isso garante que seu sistema não vai barrar o usuário por erro de geração
    assert gerar_hash_senha("123456") == gerar_hash_senha("123456")

