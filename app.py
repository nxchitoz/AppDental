
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gestor Dental IA", layout="wide")

# Simulaciones en memoria
if "doctores" not in st.session_state:
    st.session_state.doctores = []

if "pacientes" not in st.session_state:
    st.session_state.pacientes = []

if "citas" not in st.session_state:
    st.session_state.citas = []

st.title("🦷 Gestor Inteligente para Consultorios Dentales")

menu = st.sidebar.selectbox("Menú principal", ["Registrar Doctor", "Registrar Paciente", "Agendar Cita", "Panel Diario"])

# Registrar Doctor
if menu == "Registrar Doctor":
    st.header("➕ Registrar Doctor")
    nombre = st.text_input("Nombre del doctor")
    especialidad = st.text_input("Especialidad")
    if st.button("Guardar Doctor"):
        st.session_state.doctores.append({"nombre": nombre, "especialidad": especialidad})
        st.success("✅ Doctor guardado exitosamente")

# Registrar Paciente
elif menu == "Registrar Paciente":
    st.header("➕ Registrar Paciente")
    nombre_paciente = st.text_input("Nombre del paciente")
    edad = st.number_input("Edad", min_value=1, step=1)
    contacto = st.text_input("Teléfono o correo")
    if st.button("Guardar Paciente"):
        st.session_state.pacientes.append({"nombre": nombre_paciente, "edad": edad, "contacto": contacto})
        st.success("✅ Paciente guardado correctamente")

# Agendar Cita
elif menu == "Agendar Cita":
    st.header("📅 Agendar Cita")
    if st.session_state.pacientes and st.session_state.doctores:
        paciente = st.selectbox("Seleccionar paciente", [p['nombre'] for p in st.session_state.pacientes])
        doctor = st.selectbox("Seleccionar doctor", [d['nombre'] for d in st.session_state.doctores])
        fecha = st.date_input("Fecha")
        hora = st.time_input("Hora")
        tratamiento = st.text_input("Tratamiento")
        costo = st.number_input("Costo", min_value=0.0, step=1.0)
        if st.button("Guardar Cita"):
            st.session_state.citas.append({
                "paciente": paciente,
                "doctor": doctor,
                "fecha": fecha,
                "hora": hora,
                "tratamiento": tratamiento,
                "costo": costo
            })
            st.success("✅ Cita agendada correctamente")
    else:
        st.warning("Debe registrar al menos un doctor y un paciente.")

# Panel Diario
elif menu == "Panel Diario":
    st.header("📊 Panel Diario")
    hoy = datetime.now().date()
    citas_hoy = [c for c in st.session_state.citas if c['fecha'] == hoy]
    if citas_hoy:
        df = pd.DataFrame(citas_hoy)
        st.dataframe(df)
        total = sum(c["costo"] for c in citas_hoy)
        st.subheader(f"Total ingresos del día: ${total:.2f}")
        if st.button("📥 Exportar Excel"):
            df.to_excel("reporte_diario.xlsx", index=False)
            with open("reporte_diario.xlsx", "rb") as f:
                st.download_button("Descargar Excel", f, file_name="reporte_diario.xlsx")
    else:
        st.info("No hay citas registradas para hoy.")
