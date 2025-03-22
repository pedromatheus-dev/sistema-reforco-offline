import streamlit as st
from datetime import datetime, timedelta, date
import json
import os

# Função para salvar os dados no arquivo JSON
def salvar_dados(alunos, aulas):
    for aula in aulas:
        aula["data"] = aula["data"].strftime("%d/%m/%Y")  
        aula["hora_inicio"] = aula["hora_inicio"].strftime("%H:%M")  
        aula["hora_fim"] = aula["hora_fim"].strftime("%H:%M")  

    with open("dados.json", "w") as file:
        json.dump({"alunos": alunos, "aulas": aulas}, file, indent=4)

# Função para carregar os dados do arquivo JSON
def carregar_dados():
    if os.path.exists("dados.json"):
        with open("dados.json", "r") as file:
            dados = json.load(file)

            for aula in dados["aulas"]:
                aula["data"] = datetime.strptime(aula["data"], "%d/%m/%Y").date()
                aula["hora_inicio"] = datetime.strptime(aula["hora_inicio"], "%H:%M").time()
                aula["hora_fim"] = datetime.strptime(aula["hora_fim"], "%H:%M").time()

            return dados
    return {"alunos": {}, "aulas": []}

dados = carregar_dados()
alunos = dados["alunos"]
global aulas
aulas = dados["aulas"]

# Converter duração para horas e minutos
def formatar_duracao(duracao):
    horas = int(duracao)
    minutos = int((duracao - horas) * 60)
    return f"{horas}:{minutos:02d}"

# Sidebar para navegar entre as telas
st.sidebar.title("Navegação")
pagina = st.sidebar.radio("Escolha uma opção", ["Cadastro de Alunos", "Registro de Aulas", "Informações de Pagamento", "Consultar Aulas", "Excluir Aluno", "Excluir Aula"])

# Cadastro de Alunos
if pagina == "Cadastro de Alunos":
    st.title("Cadastro de Alunos")
    nome_aluno = st.text_input("Nome do Aluno")
    valor_hora = st.number_input("Valor por Hora (R$)", min_value=0.0, format="%.2f")

    dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    dias_aulas = st.multiselect("Dias de Aula", dias_semana, placeholder="Escolha o(s) dia(s) da semana")

    if st.button("Cadastrar Aluno"):
        if nome_aluno and valor_hora and dias_aulas:
            alunos[nome_aluno] = {"valor_hora": valor_hora, "dias_aulas": dias_aulas}
            salvar_dados(alunos, aulas)
            st.success(f"Aluno {nome_aluno} cadastrado com sucesso!")
        else:
            st.error("Por favor, preencha todos os campos.")

# Registro de Aulas
elif pagina == "Registro de Aulas":
    st.title("Registro de Aulas")
    if alunos:
        nome_aluno_aula = st.selectbox("Selecione o Aluno", options=list(alunos.keys()))
        data_aula = st.date_input("Data da Aula", format="DD/MM/YYYY")
        hora_inicio = st.time_input("Início da Aula", value=datetime.strptime("15:00", "%H:%M").time(), step=timedelta(minutes=10))
        hora_fim = st.time_input("Fim da Aula", value=datetime.strptime("16:00", "%H:%M").time(), step=timedelta(minutes=10))

        if st.button("Registrar Aula"):
            if nome_aluno_aula and data_aula and hora_inicio and hora_fim:
                duracao = (datetime.combine(date.min, hora_fim) - datetime.combine(date.min, hora_inicio)).seconds / 3600.0
                valor_hora = alunos[nome_aluno_aula]["valor_hora"]
                total = duracao * valor_hora
                aulas.append({
                    "nome": nome_aluno_aula,
                    "data": data_aula,
                    "hora_inicio": hora_inicio,
                    "hora_fim": hora_fim,
                    "duracao": duracao,
                    "total": total
                })
                salvar_dados(alunos, aulas)
                st.success(f"Aula registrada para {nome_aluno_aula} no dia {data_aula.strftime('%d/%m/%Y')}. Total: R${total:.2f}")
            else:
                st.error("Por favor, preencha todos os campos.")
    else:
        st.warning("Nenhum aluno cadastrado ainda.")

# Informações de Pagamento
elif pagina == "Informações de Pagamento":
    st.title("Informações de Pagamento")
    if alunos:
        nome_aluno_consulta = st.selectbox("Selecione o Aluno", options=list(alunos.keys()))

        hoje = datetime.today()
        data_inicio = st.date_input("Data de Início", value=date(hoje.year, hoje.month, 1), format="DD/MM/YYYY")
        data_fim = st.date_input("Data de Fim", value=(date(hoje.year, hoje.month, 1) + timedelta(days=30)), format="DD/MM/YYYY")
        
        ano = st.number_input("Ano", min_value=2025, max_value=2100, value=2025)

        if st.button("Consultar Pagamento"):
            aulas_filtradas = [aula for aula in aulas if aula["nome"] == nome_aluno_consulta and data_inicio <= aula["data"] <= data_fim]

            if aulas_filtradas:
                total_mensal = sum(aula["total"] for aula in aulas_filtradas)
                st.info(f"Total a ser pago para {nome_aluno_consulta} entre {data_inicio.strftime('%d/%m/%Y')} e {data_fim.strftime('%d/%m/%Y')}: R${total_mensal:.2f}")

                st.subheader("Aulas Registradas:")
                for aula in aulas_filtradas:
                    st.text(f"- Data: {aula['data'].strftime('%d/%m/%Y')}, Duração: {formatar_duracao(aula['duracao'])}h, Valor: R${aula['total']:.2f}")
            else:
                st.warning(f"Sem aulas registradas para {nome_aluno_consulta} nesse período.")
    else:
        st.warning("Nenhum aluno cadastrado para consulta.")

# Consulta de Aulas por Período
elif pagina == "Consultar Aulas":
    st.title("Consulta de Aulas")

    hoje = datetime.today()

    data_inicio = st.date_input("Data de Início", value=date(hoje.year, hoje.month, 1), format="DD/MM/YYYY")
    data_fim = st.date_input("Data de Fim", value=(date(hoje.year, hoje.month, 1) + timedelta(days=30)), format="DD/MM/YYYY")

    if st.button("Consultar"):
        aulas_filtradas = [aula for aula in aulas if data_inicio <= aula["data"] <= data_fim]

        if aulas_filtradas:
            st.subheader("Aulas no Período:")
            for aula in aulas_filtradas:
                st.text(f"- {aula['nome']}: {aula['data'].strftime('%d/%m/%Y')} ({aula['hora_inicio'].strftime('%H:%M')} - {aula['hora_fim'].strftime('%H:%M')})")
        else:
            st.warning("Nenhuma aula encontrada nesse período.")

# Excluir Aluno
if pagina == "Excluir Aluno":
    st.title("Excluir Aluno")
    if alunos:
        nome_aluno_excluir = st.selectbox("Selecione o Aluno", options=list(alunos.keys()))
        excluir_aulas = st.checkbox("Excluir também os registros de aulas e pagamentos?")
        
        if st.button("Excluir Aluno"):
            del alunos[nome_aluno_excluir]
            if excluir_aulas:
                aulas = [aula for aula in aulas if aula["nome"] != nome_aluno_excluir]
            salvar_dados(alunos, aulas)
            st.success(f"Aluno {nome_aluno_excluir} e seus registros foram excluídos com sucesso!")
    else:
        st.warning("Nenhum aluno cadastrado para excluir.")

# Excluir Aula
elif pagina == "Excluir Aula":
    st.title("Excluir Aula")
    if aulas:
        aula_selecionada = st.selectbox("Selecione a Aula para excluir", [
            f"{aula['nome']} - {aula['data'].strftime('%d/%m/%Y')} ({aula['hora_inicio'].strftime('%H:%M')} - {aula['hora_fim'].strftime('%H:%M')})"
            for aula in aulas
        ])

        if st.button("Excluir Aula"):
            aulas = [aula for aula in aulas if f"{aula['nome']} - {aula['data'].strftime('%d/%m/%Y')} ({aula['hora_inicio'].strftime('%H:%M')} - {aula['hora_fim'].strftime('%H:%M')})" != aula_selecionada]
            salvar_dados(alunos, aulas)
            st.success("Aula excluída com sucesso!")
    else:
        st.warning("Nenhuma aula registrada para excluir.")
