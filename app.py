
import streamlit as st
import pandas as pd
from datetime import datetime, date
import urllib.parse

st.set_page_config(page_title="Gestor Dental IA", layout="wide")

# Inicializar estructuras de datos
if "doctores" not in st.session_state:
    st.session_state.doctores = []

if "pacientes" not in st.session_state:
    st.session_state.pacientes = []

if "citas" not in st.session_state:
    st.session_state.citas = []

if "detalles" not in st.session_state:
    st.session_state.detalles = []

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
    if st.session_state.pacientes and st.session_state.doctores:
        paciente = st.selectbox("Seleccionar paciente", [p['nombre'] for p in st.session_state.pacientes])
        doctor = st.selectbox("Seleccionar doctor", [d['nombre'] for d in st.session_state.doctores])
        fecha = st.date_input("Seleccionar fecha", value=date.today())
        hora = st.time_input("Seleccionar hora")
        tratamiento = st.text_input("Tratamiento realizado")

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
                    "tratamiento": tratamiento
                })
                st.success("✅ Cita guardada.")

    else:
        st.warning("Debe registrar al menos un paciente y un doctor para agendar citas.")

    st.markdown("---")
    st.markdown(f"#### 📆 Agenda para el {fecha.strftime('%d-%m-%Y')}")
    citas_dia = [c for c in st.session_state.citas if c['fecha'] == fecha]
    if citas_dia:
        df_citas = pd.DataFrame(citas_dia)
        df_citas['hora'] = df_citas['hora'].astype(str)
        st.dataframe(df_citas)

        selected_cita = st.selectbox("Selecciona una cita para registrar detalles financieros", [f"{c['paciente']} ({c['hora']})" for c in citas_dia])
        if selected_cita:
            with st.form("detalles_form"):
                precio = st.number_input("Precio original", min_value=0.0, step=1.0)
                descuento = st.number_input("Descuento aplicado", min_value=0.0, step=1.0)
                cuotas = st.number_input("Número de cuotas", min_value=1, step=1)

                monto_final = precio - descuento
                st.write(f"💰 **Total a pagar con descuento:** ${monto_final:.2f}")
                estado_pago = "Pagado completo" if cuotas == 1 else f"Pendiente: {cuotas} cuotas"

                agregar = st.form_submit_button("Guardar Detalles")
                if agregar:
                    nombre_paciente = selected_cita.split(" (")[0]
                    st.session_state.detalles.append({
                        "paciente": nombre_paciente,
                        "fecha": fecha,
                        "precio_original": precio,
                        "descuento": descuento,
                        "monto_final": monto_final,
                        "cuotas": cuotas,
                        "estado_pago": estado_pago
                    })
                    st.success("✅ Detalles financieros guardados")

            # Botón de recordatorio por WhatsApp
            paciente_data = next((p for p in st.session_state.pacientes if p['nombre'] == nombre_paciente), None)
            if paciente_data:
                mensaje = f"Hola {nombre_paciente}, te recordamos tu cita dental el {fecha.strftime('%d/%m/%Y')} a las {hora.strftime('%H:%M')}. ¡Te esperamos!"
                numero = paciente_data['contacto'].replace("+", "")
                url = f"https://wa.me/{numero}?text={urllib.parse.quote(mensaje)}"
                st.markdown(f"[📩 Enviar recordatorio por WhatsApp]({url})", unsafe_allow_html=True)
    else:
        st.info("No hay citas para esta fecha.")

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
