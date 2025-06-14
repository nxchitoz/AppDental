
import streamlit as st
import pandas as pd
from datetime import datetime, date, time

st.set_page_config(page_title="Gestor Dental IA", layout="wide")

# Inicializar datos simulados en memoria
if "doctores" not in st.session_state:
    st.session_state.doctores = []

if "pacientes" not in st.session_state:
    st.session_state.pacientes = []

if "citas" not in st.session_state:
    st.session_state.citas = []

st.markdown("<h1 style='text-align: center;'>🦷 Gestor Dental IA</h1>", unsafe_allow_html=True)
st.markdown("---")

col1, col2 = st.columns(2)

# REGISTRO DE DOCTORES
with col1:
    st.subheader("➕ Registrar Doctor")
    with st.form("doctor_form"):
        nombre_doc = st.text_input("Nombre del doctor")
        especialidad = st.text_input("Especialidad")
        submitted_doc = st.form_submit_button("Guardar Doctor")
        if submitted_doc:
            st.session_state.doctores.append({"nombre": nombre_doc, "especialidad": especialidad})
            st.success("✅ Doctor registrado")

# REGISTRO DE PACIENTES
with col2:
    st.subheader("➕ Registrar Paciente")
    with st.form("paciente_form"):
        nombre_pac = st.text_input("Nombre del paciente")
        edad = st.number_input("Edad", min_value=1)
        contacto = st.text_input("Teléfono o correo")
        submitted_pac = st.form_submit_button("Guardar Paciente")
        if submitted_pac:
            st.session_state.pacientes.append({"nombre": nombre_pac, "edad": edad, "contacto": contacto})
            st.success("✅ Paciente registrado")

st.markdown("---")
st.subheader("📅 Agendar Cita")

if st.session_state.pacientes and st.session_state.doctores:
    paciente = st.selectbox("Seleccionar paciente", [p['nombre'] for p in st.session_state.pacientes])
    doctor = st.selectbox("Seleccionar doctor", [d['nombre'] for d in st.session_state.doctores])
    fecha = st.date_input("Seleccionar fecha", value=date.today())
    hora = st.time_input("Seleccionar hora")
    tratamiento = st.text_input("Tratamiento")
    costo = st.number_input("Costo", min_value=0.0, step=1.0)

    if st.button("Guardar Cita"):
        conflict = any(c['fecha'] == fecha and c['hora'] == hora and c['doctor'] == doctor for c in st.session_state.citas)
        if conflict:
            st.warning("⚠️ Ya existe una cita con ese doctor a esa hora.")
        else:
            st.session_state.citas.append({
                "paciente": paciente,
                "doctor": doctor,
                "fecha": fecha,
                "hora": hora,
                "tratamiento": tratamiento,
                "costo": costo
            })
            st.success("✅ Cita agendada exitosamente")

    # Mostrar calendario del día con citas por hora
    st.markdown(f"#### 📆 Agenda para el {fecha.strftime('%d-%m-%Y')}")
    citas_dia = [c for c in st.session_state.citas if c['fecha'] == fecha and c['doctor'] == doctor]
    if citas_dia:
        df_citas = pd.DataFrame(citas_dia)
        df_citas['hora'] = df_citas['hora'].astype(str)
        df_citas = df_citas.sort_values("hora")
        st.table(df_citas[['hora', 'paciente', 'tratamiento', 'costo']])
    else:
        st.info("No hay citas para este día con este doctor.")

else:
    st.warning("Debe registrar al menos un paciente y un doctor para agendar citas.")

st.markdown("---")
st.subheader("📊 Panel Diario")

hoy = datetime.now().date()
citas_hoy = [c for c in st.session_state.citas if c['fecha'] == hoy]

if citas_hoy:
    df = pd.DataFrame(citas_hoy)
    df['hora'] = df['hora'].astype(str)
    df = df.sort_values("hora")
    st.dataframe(df)
    total = sum(c["costo"] for c in citas_hoy)
    st.markdown(f"### 💰 Total ingresos hoy: ${total:.2f}")
    if st.button("📥 Exportar Reporte Diario"):
        df.to_excel("reporte_diario.xlsx", index=False)
        with open("reporte_diario.xlsx", "rb") as f:
            st.download_button("Descargar Excel", f, file_name="reporte_diario.xlsx")
else:
    st.info("No hay citas registradas para hoy.")
