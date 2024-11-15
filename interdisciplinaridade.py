import streamlit as st
import mysql.connector
from mysql.connector import Error

def conectar():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            database="aula",
            user="root",
            password="131989",
            port="3306"
        )
        conn.autocommit = False
        return conn
    except Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

def bloquear_cliente(cursor, id_cliente):
    try:
        # Bloqueia o registro para evitar alterações concorrentes
        cursor.execute("SELECT * FROM cliente WHERE idcliente = %s FOR UPDATE NOWAIT;", (id_cliente,))
        return cursor.fetchone()
    except Error as e:
        if "lock wait timeout" in str(e) or "Lock wait timeout exceeded" in str(e):
            st.error(f"O cliente (ID {id_cliente}) já está sendo editado por outro usuário.")
        else:
            st.error(f"Erro ao bloquear cliente: {e}")
        return None

def editar_cliente(conexao, id_cliente, novo_nome, novo_limite):
    cursor = conexao.cursor()
    try:
        cursor.execute("UPDATE cliente SET nome = %s, limite = %s WHERE idcliente = %s;", 
                       (novo_nome, novo_limite, id_cliente))
        return True
    except Error as e:
        st.error(f"Erro ao editar cliente: {e}")
        conexao.rollback()
        return False

def main():
    st.title("Sistema de Edição de Cliente")
    
    conexao = conectar()
    if not conexao:
        return

    cursor = conexao.cursor()

    id_cliente = st.number_input("Digite o ID do cliente que deseja editar", min_value=1, step=1)
    cliente = None

    if st.button("Selecionar Cliente"):
        cliente = bloquear_cliente(cursor, id_cliente)
        if cliente:
            st.success(f"Cliente selecionado com sucesso (ID {id_cliente}).")
            st.write(f"Dados atuais: Nome: {cliente[1]}, Limite: {cliente[2]}")
    
    if cliente:
        novo_nome = st.text_input("Novo nome do cliente", value=cliente[1])
        novo_limite = st.number_input("Novo limite do cliente", value=float(cliente[2]), step=0.01)

        if st.button("Confirmar Alteração"):
            if editar_cliente(conexao, id_cliente, novo_nome, novo_limite):
                conexao.commit()
                st.success("Alteração confirmada com sucesso!")
            else:
                st.error("Alteração não pôde ser concluída.")
        
        if st.button("Cancelar Alteração"):
            conexao.rollback()
            st.info("Alteração cancelada.")

    cursor.close()
    conexao.close()

if __name__ == "__main__":
    main()
