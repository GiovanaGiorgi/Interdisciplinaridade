import streamlit as st
import mysql.connector

# Função para conectar ao banco de dados MySQL
def conectar():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            database="aula",        # Banco de dados
            user="root",            # Usuário MySQL
            password="131989",      # Senha do MySQL
            port="3306"             # Porta do MySQL
        )
        conn.autocommit = False  # Desativa o autocommit para controle manual de transações
        return conn
    except mysql.connector.Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para editar o cliente
def editar_cliente(id_cliente, novo_nome, novo_limite):
    conexao = conectar()
    if conexao is None:
        return
    
    cursor = conexao.cursor()

    try:
        # Iniciar transação
        cursor.execute("START TRANSACTION;")
        
        # Seleciona o cliente com o id fornecido para verificar os dados
        cursor.execute("SELECT nome, limite FROM cliente WHERE idcliente = %s;", (id_cliente,))
        cliente = cursor.fetchone()
        
        if cliente is None:
            st.error("Cliente não encontrado.")
            conexao.rollback()  # Desfaz a transação
            return

        # Mostrar os dados atuais do cliente
        nome_atual, limite_atual = cliente
        st.write(f"Dados atuais do Cliente (ID {id_cliente}): Nome: {nome_atual}, Limite: {limite_atual}")

        # Debug: Verificar os valores que estão sendo comparados
        st.write(f"Comparando os dados atuais com os novos dados fornecidos.")
        st.write(f"Nome atual: {nome_atual} | Novo nome: {novo_nome}")
        st.write(f"Limite atual: {limite_atual} | Novo limite: {novo_limite}")

        # Comparar com os novos dados fornecidos pelo usuário
        # Remove espaços em branco e compara sem diferenciar maiúsculas/minúsculas
        if nome_atual.strip().lower() == novo_nome.strip().lower() and limite_atual == novo_limite:
            st.warning("Nenhuma alteração detectada nos dados do cliente.")
            conexao.rollback()  # Não faz nada se os dados não foram alterados
            return

        # Atualiza os dados do cliente
        st.write("Alterando os dados do cliente...")  # Debug
        cursor.execute("UPDATE cliente SET nome = %s, limite = %s WHERE idcliente = %s;", 
                       (novo_nome, novo_limite, id_cliente))

        # Espera a confirmação do usuário para efetuar o commit
        st.write(f"Tem certeza que deseja alterar os dados do cliente (ID {id_cliente})?")

        # Aguardar confirmação do usuário
        if st.button("Confirmar alteração"):
            try:
                # Se a confirmação for dada, faz o commit
                conexao.commit()  # Confirma as alterações no banco de dados
                st.success("Alteração realizada com sucesso!")
            except mysql.connector.Error as e:
                conexao.rollback()  # Desfaz a transação em caso de erro
                st.error(f"Erro ao realizar a alteração: {e}")
        elif st.button("Cancelar alteração"):
            conexao.rollback()  # Desfaz as alterações
            st.info("Alteração cancelada.")
    
    except mysql.connector.Error as e:
        conexao.rollback()  # Desfaz a transação em caso de erro
        st.error(f"Erro ao realizar a alteração: {e}")
    
    finally:
        cursor.close()
        conexao.close()

# Função principal da interface Streamlit
def main():
    st.title("Sistema de Edição de Cliente")
    
    # Entrada do ID do cliente
    id_cliente = st.number_input("Digite o ID do cliente que deseja editar", min_value=1)
    
    if id_cliente:
        # Carregar os dados do cliente
        conexao = conectar()
        if conexao is None:
            return
        
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM cliente WHERE idcliente = %s;", (id_cliente,))
        cliente = cursor.fetchone()
        
        if cliente:
            st.write(f"Dados atuais do Cliente (ID {id_cliente}): Nome: {cliente[1]}, Limite: {cliente[2]}")
            
            # Entradas para novos dados
            novo_nome = st.text_input("Novo nome do cliente", value=cliente[1])
            novo_limite = st.number_input("Novo limite", value=float(cliente[2]), step=0.01)  # Converte para float
            
            # Ação para editar
            if st.button("Editar Cliente"):
                editar_cliente(id_cliente, novo_nome, novo_limite)
        else:
            st.error("Cliente não encontrado.")
        
        cursor.close()
        conexao.close()

if __name__ == "__main__":
    main()