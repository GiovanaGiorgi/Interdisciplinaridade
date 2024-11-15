import streamlit as st
import mysql.connector

# Função para conectar ao banco
def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="131989",
        database="aula"
    )

# Função principal
def main():
    st.title("Sistema de Alteração de Clientes")

    # Estado persistente com session_state
    if "id_cliente" not in st.session_state:
        st.session_state.id_cliente = None
    if "dados_cliente" not in st.session_state:
        st.session_state.dados_cliente = None
    if "transacao_ativa" not in st.session_state:
        st.session_state.transacao_ativa = False

    # Botão para listar clientes
    if st.button("Listar clientes"):
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM cliente")
        clientes = cursor.fetchall()
        conexao.close()

        st.write("Clientes cadastrados:")
        for cliente in clientes:
            st.write(f"ID: {cliente[0]}, Nome: {cliente[1]}, Limite: {cliente[2]}")

    # Input para selecionar ID do cliente
    id_cliente = st.text_input("Digite o ID do cliente para editar:")

    if id_cliente and st.button("Carregar cliente"):
        conexao = conectar()
        cursor = conexao.cursor()
        try:
            cursor.execute("SELECT * FROM cliente WHERE idcliente = %s FOR UPDATE NOWAIT", (id_cliente,))
            cliente = cursor.fetchone()

            if cliente:
                st.session_state.id_cliente = id_cliente
                st.session_state.dados_cliente = cliente
                st.session_state.transacao_ativa = True
                st.success("Cliente carregado com sucesso.")
            else:
                st.error("Cliente não encontrado.")
        except mysql.connector.errors.DatabaseError as e:
            st.error(f"Erro ao carregar cliente: {e}")
        finally:
            conexao.close()

    # Exibe os dados atuais e permite edição
    if st.session_state.dados_cliente:
        st.write(f"**ID**: {st.session_state.dados_cliente[0]}")
        novo_nome = st.text_input("Nome:", st.session_state.dados_cliente[1])
        novo_limite = st.number_input("Limite:", value=float(st.session_state.dados_cliente[2]), step=0.01)

        # Botão para confirmar alteração
        if st.button("Confirmar alteração"):
            conexao = conectar()
            cursor = conexao.cursor()
            try:
                cursor.execute(
                    "UPDATE cliente SET nome = %s, limite = %s WHERE idcliente = %s",
                    (novo_nome, novo_limite, st.session_state.id_cliente)
                )
                conexao.commit()
                st.success("Alteração realizada com sucesso!")
                # Finaliza a transação e limpa o estado
                st.session_state.dados_cliente = None
                st.session_state.id_cliente = None
                st.session_state.transacao_ativa = False
            except Exception as e:
                conexao.rollback()
                st.error(f"Erro ao salvar alterações: {e}")
            finally:
                conexao.close()

        # Botão para cancelar alteração
        if st.button("Cancelar alteração"):
            st.session_state.dados_cliente = None
            st.session_state.id_cliente = None
            st.session_state.transacao_ativa = False
            st.warning("Alteração cancelada.")

if __name__ == "__main__":
    main()
