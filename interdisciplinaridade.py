import mysql.connector

# Função para conectar ao banco de dados
def conectar():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            database="aula",        
            user="root",            
            password="131989",      
            port="3306"             
        )
        conn.autocommit = False  # Desativa o autocommit
        return conn
    except mysql.connector.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função principal para iniciar a transação
def iniciar_transacao():
    conexao = conectar()
    if conexao is None:
        print("Falha na conexão. Finalizando...")
        return

    cursor = conexao.cursor()

    try:
        # Receber o id do cliente do usuário
        id_cliente_dinamico = input("Digite o ID do cliente que deseja editar: ")

        # Iniciar transação e tentar bloquear o registro
        cursor.execute("BEGIN;")
        cursor.execute("SELECT * FROM cliente WHERE idcliente = %s FOR UPDATE;", (id_cliente_dinamico,))

        # Buscar e exibir informações do cliente
        cliente = cursor.fetchone()
        if cliente is None:
            print("Cliente não encontrado.")
            conexao.rollback()
            return

        # Exibir dados atuais
        print(f"Dados atuais do Cliente (ID {id_cliente_dinamico}): Nome: {cliente[1]}, Limite: {cliente[2]}")

        # Solicitar novos valores para nome e limite
        novo_nome = input("Digite o novo nome para o cliente: ")
        novo_limite = input("Digite o novo limite para o cliente: ")

        # Atualizar com os novos valores
        cursor.execute("UPDATE cliente SET nome = %s, limite = %s WHERE idcliente = %s;",
                       (novo_nome, novo_limite, id_cliente_dinamico))

        # Confirmar com o usuário
        confirmacao = input("Deseja confirmar a alteração? (s/n): ")
        if confirmacao.lower() == 's':
            conexao.commit()
            print("Transação concluída e confirmada.")
        else:
            conexao.rollback()
            print("Transação cancelada.")

    except psycopg2.errors.LockNotAvailable:
        # Tratar erro de bloqueio, indicando que outro usuário está usando o registro
        print("Erro: o registro está em uso por outro usuário. Tente novamente mais tarde.")

    except psycopg2.errors.SerializationFailure:
        # Tratar erro de conflito (usuário precisa atualizar)
        print("Erro: o registro foi atualizado por outro usuário. Atualize os dados antes de tentar novamente.")

    except Exception as e:
        # Tratar outros erros e desfazer transação
        conexao.rollback()
        print("Erro na transação:", e)

    finally:
        cursor.close()
        conexao.close()

# Executa o script
if __name__ == "__main__":
    iniciar_transacao()
