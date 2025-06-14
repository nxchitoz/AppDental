
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import urllib.parse

st.set_page_config(page_title="Gestor Dental IA", layout="wide")

# Inicializar estructuras
if "doctores" not in st.session_state:
    st.session_state.doctores = []

if "pacientes" not in st.session_state:
    st.session_state.pacientes = []

if "citas" not in st.session_state:
    st.session_state.citas = []

if "detalles" not in st.session_state:
    st.session_state.detalles = []

if "hora_seleccionada" not in st.session_state:
    st.session_state.hora_seleccionada = None

st.title("🦷 Gestor Dental IA")
st.markdown("---")

# Módulos principales
st.subheader("📌 Módulos principales")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("➕ Registrar Doctor"):
        st.session_state.view = "doctor"
with col2:
    if st.button("➕ Registrar Paciente"):
        st.session_state.view = "paciente"
with col3:
    if st.button("📅 Agendar Cita"):
        st.session_state.view = "cita"

col4, col5 = st.columns(2)
with col4:
    if st.button("📊 Panel Diario"):
        st.session_state.view = "panel"
with col5:
    if st.button("📁 Registro Completo"):
        st.session_state.view = "registro"

# REGISTRAR DOCTOR
if st.session_state.get("view") == "doctor":
    st.subheader("➕ Registrar Doctor")
    with st.form("doctor_form"):
        nombre_doc = st.text_input("Nombre del doctor")
        especialidad = st.text_input("Especialidad")
        submitted_doc = st.form_submit_button("Guardar Doctor")
        if submitted_doc:
            if nombre_doc and especialidad:
                st.session_state.doctores.append({"nombre": nombre_doc, "especialidad": especialidad})
                st.success("✅ Doctor registrado exitosamente")
            else:
                st.error("⚠️ Todos los campos son obligatorios.")

# REGISTRAR PACIENTE
if st.session_state.get("view") == "paciente":
    st.subheader("➕ Registrar Paciente")
    with st.form("paciente_form"):
        nombre_pac = st.text_input("Nombre completo")
        cedula = st.text_input("Número de cédula")
        fecha_nacimiento = st.date_input("Fecha de nacimiento", min_value=date(1900,1,1), max_value=date.today())
        ocupacion = st.text_input("Ocupación")
        contacto = st.text_input("Teléfono (con código país, ej: +593)")
        correo = st.text_input("Correo electrónico")
        direccion = st.text_input("Dirección de residencia")

        edad = datetime.now().year - fecha_nacimiento.year
        if datetime.now().month < fecha_nacimiento.month or (datetime.now().month == fecha_nacimiento.month and datetime.now().day < fecha_nacimiento.day):
            edad -= 1

        st.write(f"Edad calculada: **{edad} años**")

        submitted_pac = st.form_submit_button("Guardar Paciente")
        if submitted_pac:
            if nombre_pac and cedula and ocupacion and contacto and correo and direccion:
                st.session_state.pacientes.append({
                    "nombre": nombre_pac,
                    "cedula": cedula,
                    "fecha_nacimiento": fecha_nacimiento.strftime("%Y-%m-%d"),
                    "edad": edad,
                    "ocupacion": ocupacion,
                    "contacto": contacto,
                    "correo": correo,
                    "direccion": direccion
                })
                st.success("✅ Paciente registrado exitosamente")
            else:
                st.error("⚠️ Todos los campos son obligatorios.")

# AGENDAR CITA
if st.session_state.get("view") == "cita":
    st.subheader("📅 Agendar Cita")

    fecha = st.date_input("Selecciona el día para visualizar el calendario", value=date.today())
    st.markdown(f"### Calendario del día {fecha.strftime('%d-%m-%Y')}")

    # Generar calendario de 8am a 9pm en intervalos de 15 min
    start_hour = 8
    end_hour = 21
    interval_minutes = 15

    current_time = datetime.strptime(f"{start_hour}:00", "%H:%M")
    end_time = datetime.strptime(f"{end_hour}:00", "%H:%M")
    time_slots = []

    while current_time < end_time:
        time_str = current_time.strftime("%H:%M")
        ocupado = any(c['fecha'] == fecha and c['hora'].strftime("%H:%M") == time_str for c in st.session_state.citas)
        estado = "🟥 Ocupado" if ocupado else "🟩 Disponible"
        if st.button(f"{estado} - {time_str}"):
            if not ocupado:
                st.session_state.hora_seleccionada = current_time.time()
        current_time += timedelta(minutes=interval_minutes)

    if st.session_state.hora_seleccionada:
        st.success(f"Hora seleccionada: {st.session_state.hora_seleccionada.strftime('%H:%M')}")
        with st.form("form_cita"):
            paciente = st.selectbox("Seleccionar paciente", [p['nombre'] for p in st.session_state.pacientes])
            doctor = st.selectbox("Seleccionar doctor", [d['nombre'] for d in st.session_state.doctores])
            tratamiento = st.text_input("Tratamiento realizado")
            agendar = st.form_submit_button("Agendar Cita")
            if agendar:
                st.session_state.citas.append({
                    "paciente": paciente,
                    "doctor": doctor,
                    "fecha": fecha,
                    "hora": st.session_state.hora_seleccionada,
                    "tratamiento": tratamiento
                })
                st.success("✅ Cita agendada correctamente")

# PANEL DIARIO
if st.session_state.get("view") == "panel":
    st.subheader("📊 Panel Diario")
    hoy = datetime.now().date()
    citas_hoy = [c for c in st.session_state.citas if c['fecha'] == hoy]
    if citas_hoy:
        df = pd.DataFrame(citas_hoy)
        df['hora'] = df['hora'].astype(str)
        st.dataframe(df)
    else:
        st.info("No hay citas para hoy.")

# REGISTRO COMPLETO
if st.session_state.get("view") == "registro":
    st.subheader("📁 Registro completo de ingresos")
    if st.session_state.detalles:
        df_detalles = pd.DataFrame(st.session_state.detalles)
        st.dataframe(df_detalles)
        if st.button("📥 Exportar Registro General"):
            df_detalles.to_excel("registro_general.xlsx", index=False)
            with open("registro_general.xlsx", "rb") as f:
                st.download_button("Descargar Excel", f, file_name="registro_general.xlsx")
    else:
        st.info("No hay detalles financieros registrados todavía.")
