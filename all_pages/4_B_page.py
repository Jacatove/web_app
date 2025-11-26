import streamlit as st
import pandas as pd
from datetime import datetime
from services.auth_service import AuthService

st.title("Equipo B - Dashboard Financiero")

# Verificar que el usuario esté autenticado
if 'is_authenticated' not in st.session_state or not st.session_state.is_authenticated:
    st.error("❌ No estás autenticado. Por favor inicia sesión.")
    st.stop()

if 'token' not in st.session_state or not st.session_state.token:
    st.error("❌ Token no encontrado. Por favor inicia sesión.")
    st.stop()

# Cargar datos desde CSV
@st.cache_data
def cargar_datos():
    clientes = pd.read_csv('data/clientes.csv')
    cuentas = pd.read_csv('data/cuentas_debito.csv')
    historial = pd.read_csv('data/historial_alertas.csv')
    scoring = pd.read_csv('data/scoring_crediticio.csv')
    return clientes, cuentas, historial, scoring

# Función para extraer UUID del mensaje de whoami
def extraer_uuid_del_whoami(mensaje_whoami):
    """
    Extrae el UUID del usuario del mensaje que viene de whoami
    Formato esperado: "Yo soy c4f45cd0-1412-44be-b8b0-658322c5da84 y mi email es mafe@gmail.com"
    o un JSON con estructura {"id": "uuid", ...}
    """
    import re
    
    # Si es un diccionario/JSON, intentar extraer directamente
    if isinstance(mensaje_whoami, dict):
        return mensaje_whoami.get('id') or mensaje_whoami.get('user_id') or mensaje_whoami.get('uuid')
    
    # Si es un string, buscar patrón UUID
    # Patrón UUID v4: 8-4-4-4-12 caracteres hexadecimales
    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    match = re.search(uuid_pattern, str(mensaje_whoami))
    return match.group(0) if match else None

llamada_whoiam = AuthService.whoami(st.session_state.token)
try:
    clientes_df, cuentas_df, historial_df, scoring_df = cargar_datos()
    
    # Extraer UUID del mensaje de whoami
    id_usuario = extraer_uuid_del_whoami(llamada_whoiam)
    
    if not id_usuario:
        st.error("❌ No se pudo extraer el ID del usuario del mensaje whoami.")
        st.info("Respuesta whoami recibida: " + str(llamada_whoiam))
        st.stop()
    
    # Buscar el cliente por UUID directamente en el CSV
    cliente_match = clientes_df[clientes_df['id_cliente'] == id_usuario]
    
    if len(cliente_match) == 0:
        st.error(f"❌ No se encontró información financiera para el usuario ID: {id_usuario}")
        st.info("💡 Contacta a soporte para registrar tus datos financieros.")
        st.stop()
    
    # Obtener datos del cliente
    cliente = cliente_match.iloc[0]
    id_cliente = cliente['id_cliente']
    email_usuario = cliente['email']
    
    # Determinar membership desde el CSV (es_cliente_premium)
    es_premium = bool(cliente['es_cliente_premium'])
    st.session_state.membership = 'PREMIUM' if es_premium else 'FREE'
    
    # Mostrar info de sesión
    st.info(
        f"Usuario: {email_usuario} | ID: {id_cliente[:8]}... | Membresía: {st.session_state.membership}"
    )
    
    # Filtrar datos del cliente
    cliente = clientes_df[clientes_df['id_cliente'] == id_cliente].iloc[0]
    cuentas_cliente = cuentas_df[cuentas_df['id_cliente'] == id_cliente]
    historial_cliente = historial_df[historial_df['id_cliente'] == id_cliente]
    scoring_cliente = scoring_df[scoring_df['id_cliente'] == id_cliente].iloc[0] if len(scoring_df[scoring_df['id_cliente'] == id_cliente]) > 0 else None
    
    st.divider()
    
    # Información del cliente
    st.header(f"👤 {cliente['nombres']} {cliente['apellidos']}")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Cédula", cliente['cedula'])
    with col2:
        st.metric("Ciudad", cliente['ciudad'])
    with col3:
        st.metric("Ingresos Mensuales", f"${cliente['ingresos_mensuales']:,.0f}")
    with col4:
        # Mostrar score solo para usuarios PREMIUM
        if st.session_state.membership == 'PREMIUM' and scoring_cliente is not None:
            st.metric("Score Crediticio", int(scoring_cliente['puntaje_credito']))
        elif st.session_state.membership == 'FREE':
            st.metric("Score Crediticio", "🔒 Premium")
    
    st.divider()
    
    # VISUALIZACIÓN SEGÚN MEMBRESÍA
    if st.session_state.membership == 'FREE':
        # ========== VERSIÓN FREE ==========
        st.warning("⚠️ Plan FREE - Acceso limitado")
        
        # Mostrar cuentas limitadas (máximo 2)
        st.markdown("### 💳 Cuentas de Débito")
        cuentas_limitadas = cuentas_cliente.head(2)
        total_cuentas = len(cuentas_cliente)
        
        # Calcular saldo total solo de cuentas visibles
        saldo_visible = cuentas_limitadas['saldo_actual'].sum()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💰 Saldo Visible", f"${saldo_visible:,.0f}")
        with col2:
            st.metric("📊 Cuentas Visibles", f"{len(cuentas_limitadas)} de {total_cuentas}")
        
        st.divider()
        
        # Mostrar las 2 cuentas permitidas
        for idx, cuenta in cuentas_limitadas.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.markdown(f"**🏦 {cuenta['entidad_financiera']}**")
                    st.caption(f"_{cuenta['tipo_cuenta']}_")
                with col2:
                    st.write(f"**${cuenta['saldo_actual']:,.0f}**")
                    st.caption("Saldo actual")
                with col3:
                    st.write(f"****{str(cuenta['numero_cuenta'])[-4:]}")
                    st.caption("Número")
                with col4:
                    estado_emoji = "✅" if cuenta['estado'] == "Activa" else "⚠️"
                    st.write(f"{estado_emoji} {cuenta['estado']}")
                st.divider()
        
        # Si tiene más de 2 cuentas, mostrar publicidad
        if total_cuentas > 2:
            st.markdown("---")
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 25px; border-radius: 10px; color: white; text-align: center;">
                <h2 style="color: white; margin-bottom: 15px;">🔒 Tienes {total_cuentas - 2} cuenta(s) más bloqueada(s)</h2>
                <p style="font-size: 18px; margin-bottom: 20px;">
                    Desbloquea todas tus cuentas bancarias con PREMIUM
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("")
        
        st.divider()
        
        # Score Crediticio BLOQUEADO para FREE
        st.markdown("### 🔒 Score Crediticio - Solo PREMIUM")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("""
            <div style="background-color: #f0f0f0; padding: 30px; border-radius: 10px; 
                        text-align: center; position: relative; filter: blur(3px); opacity: 0.6;">
                <h1 style="font-size: 72px; margin: 0;">750</h1>
                <p style="font-size: 24px; margin: 0;">Muy Bueno</p>
                <p style="margin-top: 20px;">📈 Tendencia: Mejorando</p>
                <p>🎯 Percentil: Top 15%</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
            <div style="position: relative; margin-top: -150px; text-align: center; z-index: 100;">
                <h2>🔒</h2>
                <p style="font-weight: bold; font-size: 18px; color: #667eea;">
                    Contenido Premium Bloqueado
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.warning("**⚠️ Función Bloqueada**")
            st.markdown("""
            El **Score Crediticio** está disponible solo para usuarios **PREMIUM**.
            
            Con PREMIUM puedes ver:
            - 📊 Puntaje crediticio actualizado
            - 📈 Tendencias y predicciones
            - 💡 Factores de riesgo
            - 🎯 Recomendaciones personalizadas
            """)
        
        st.divider()
        
        # Movimientos limitados
        st.markdown("### 📊 Últimos Movimientos (Limitado a 5)")
        entidades_limitadas = cuentas_limitadas['entidad_financiera'].tolist()
        movimientos_free = historial_cliente[
            historial_cliente['entidad_financiera'].isin(entidades_limitadas)
        ].head(5)
        
        if len(movimientos_free) > 0:
            for idx, mov in movimientos_free.iterrows():
                monto = mov['pago_realizado'] if pd.notna(mov['pago_realizado']) else 0
                categoria = mov['categoria_gasto'] if pd.notna(mov['categoria_gasto']) else 'Sin categoría'
                color = "🔴" if mov['tipo_operacion'] == 'Debito' else "🟢"
                
                with st.expander(f"{color} {str(mov['fecha_registro'])[:10]} - {mov['entidad_financiera']} - ${monto:,.0f}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Tipo:** {mov['tipo_operacion']}")
                        st.write(f"**Categoría:** {categoria}")
                    with col2:
                        if pd.notna(mov['canal_transaccion']):
                            st.write(f"**Canal:** {mov['canal_transaccion']}")
                        if pd.notna(mov['tipo_registro']):
                            st.write(f"**Registro:** {mov['tipo_registro']}")
        else:
            st.info("No hay movimientos recientes disponibles.")
        
        st.info("🔒 **Historial limitado.** Actualiza a PREMIUM para ver el historial completo con análisis detallado.")
        
        # CTA de upgrade mejorado
        st.divider()
        st.markdown("---")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 30px; border-radius: 15px; color: white; text-align: center; margin: 20px 0;">
            <h1 style="color: white; margin-bottom: 10px;">✨ Desbloquea Todo con PREMIUM ✨</h1>
            <p style="font-size: 20px; margin-bottom: 25px;">
                Accede a todas las funciones y maximiza tu control financiero
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 🏦 Todas tus Cuentas")
            st.write("Visualiza todas tus cuentas bancarias sin límites")
        
        with col2:
            st.markdown("#### 📊 Score Crediticio")
            st.write("Conoce tu puntaje y recibe recomendaciones personalizadas")
        
        with col3:
            st.markdown("#### 📈 Análisis Completo")
            st.write("Historial detallado y análisis de gastos por categoría")
        
        st.markdown("")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 ACTUALIZAR A PREMIUM AHORA", type="primary", use_container_width=True):
                st.balloons()
                st.success("🎉 ¡Gracias por tu interés! Contacta a soporte para actualizar tu plan.")
                st.info("📧 Email: soporte@dashboard.com | 📞 WhatsApp: +57 300 123 4567")
    
    else:
        # ========== VERSIÓN PREMIUM ==========
        st.success("⭐ Plan PREMIUM - Acceso completo")
        
        # Todas las cuentas
        st.markdown("### 💳 Todas tus Cuentas de Débito")
        
        total_saldo = cuentas_cliente['saldo_actual'].sum()
        st.metric("💰 Saldo Total", f"${total_saldo:,.2f}", 
                 delta=f"{len(cuentas_cliente)} cuenta(s) activa(s)")
        
        # Mostrar cuentas en columnas
        num_cuentas = len(cuentas_cliente)
        cols = st.columns(min(num_cuentas, 4))
        
        for idx, cuenta in enumerate(cuentas_cliente.iterrows()):
            _, cuenta_data = cuenta
            col_idx = idx % 4
            with cols[col_idx]:
                st.markdown(f"**{cuenta_data['entidad_financiera']}**")
                st.write(f"_{cuenta_data['tipo_cuenta']}_")
                st.metric("Saldo", f"${cuenta_data['saldo_actual']:,.0f}")
                st.caption(f"Cuenta: ****{str(cuenta_data['numero_cuenta'])[-4:]}")
                st.caption(f"Estado: {cuenta_data['estado']}")
        
        st.divider()
        
        # Score Crediticio (solo PREMIUM)
        if scoring_cliente is not None:
            st.markdown("### 📊 Score Crediticio")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Puntaje", int(scoring_cliente['puntaje_credito']), 
                         delta=f"+{int(scoring_cliente['cambio_puntaje_mes'])}")
            with col2:
                st.metric("Categoría", scoring_cliente['categoria_riesgo'])
            with col3:
                st.metric("Tendencia", scoring_cliente['tendencia_score'])
            with col4:
                st.metric("Percentil Nacional", f"{int(scoring_cliente['percentil_nacional'])}%")
            
            # Detalles del score
            with st.expander("📈 Ver análisis detallado"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Deuda total:** ${scoring_cliente['deuda_total']:,.0f}")
                    st.write(f"**Ratio deuda/ingreso:** {scoring_cliente['ratio_deuda_ingreso']:.1%}")
                    st.write(f"**Utilización de crédito:** {scoring_cliente['utilizacion_credito_promedio']:.1f}%")
                    st.write(f"**Cuentas activas:** {int(scoring_cliente['numero_cuentas_activas'])}")
                with col2:
                    st.write(f"**Pagos puntuales:** {scoring_cliente['porcentaje_pagos_puntuales']:.1f}%")
                    st.write(f"**Días mora máximos:** {int(scoring_cliente['dias_mora_maximos'])}")
                    st.write(f"**Probabilidad default:** {scoring_cliente['probabilidad_default']:.1f}%")
                    st.write(f"**Score predicción 6m:** {int(scoring_cliente['score_prediccion_6meses'])}")
                
                st.divider()
                st.write(f"**⚠️ Factor negativo:** {scoring_cliente['principal_factor_negativo']}")
                st.write(f"**💡 Oportunidad de mejora:** {scoring_cliente['principal_oportunidad_mejora']}")
        
        st.divider()
        
        # Historial completo de movimientos
        st.markdown("### 📊 Historial Completo de Movimientos")
        
        if len(historial_cliente) > 0:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Movimientos", len(historial_cliente))
            with col2:
                debitos = historial_cliente[historial_cliente['tipo_operacion'] == 'Debito']
                total_debitos = debitos['pago_realizado'].sum() if len(debitos) > 0 else 0
                st.metric("Total Débitos", f"${total_debitos:,.0f}")
            with col3:
                creditos = historial_cliente[historial_cliente['tipo_operacion'] == 'Credito']
                total_creditos = creditos['pago_realizado'].sum() if len(creditos) > 0 else 0
                st.metric("Total Créditos", f"${total_creditos:,.0f}")
            
            # Filtros
            col1, col2 = st.columns(2)
            with col1:
                tipo_filtro = st.multiselect(
                    "Filtrar por tipo de operación",
                    options=historial_cliente['tipo_operacion'].unique(),
                    default=historial_cliente['tipo_operacion'].unique()
                )
            with col2:
                entidad_filtro = st.multiselect(
                    "Filtrar por entidad",
                    options=historial_cliente['entidad_financiera'].unique(),
                    default=historial_cliente['entidad_financiera'].unique()
                )
            
            # Aplicar filtros
            historial_filtrado = historial_cliente[
                (historial_cliente['tipo_operacion'].isin(tipo_filtro)) &
                (historial_cliente['entidad_financiera'].isin(entidad_filtro))
            ].sort_values('fecha_registro', ascending=False)
            
            # Tabla de movimientos
            for idx, mov in historial_filtrado.head(10).iterrows():
                color = "🔴" if mov['tipo_operacion'] == 'Debito' else "🟢"
                monto = mov['pago_realizado'] if pd.notna(mov['pago_realizado']) else 0
                categoria = mov['categoria_gasto'] if pd.notna(mov['categoria_gasto']) else 'Sin categoría'
                
                with st.expander(f"{color} {str(mov['fecha_registro'])[:10]} - {mov['entidad_financiera']} - ${monto:,.0f}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Tipo:** {mov['tipo_operacion']}")
                        st.write(f"**Categoría:** {categoria}")
                        st.write(f"**Tipo de registro:** {mov['tipo_registro']}")
                        if pd.notna(mov['canal_transaccion']):
                            st.write(f"**Canal:** {mov['canal_transaccion']}")
                    with col2:
                        if pd.notna(mov['saldo_anterior']):
                            st.write(f"**Saldo anterior:** ${mov['saldo_anterior']:,.2f}")
                        if pd.notna(mov['saldo_posterior']):
                            st.write(f"**Saldo posterior:** ${mov['saldo_posterior']:,.2f}")
                        if pd.notna(mov['estado_cuenta']):
                            st.write(f"**Estado:** {mov['estado_cuenta']}")
                    
                    # Mostrar alertas si existen
                    if pd.notna(mov['titulo_alerta']):
                        st.warning(f"**{mov['titulo_alerta']}**")
                        st.write(mov['mensaje_alerta'])
                        if pd.notna(mov['accion_recomendada']):
                            st.info(f"💡 **Recomendación:** {mov['accion_recomendada']}")
            
            if len(historial_filtrado) > 10:
                st.info(f"Mostrando 10 de {len(historial_filtrado)} movimientos. Ajusta los filtros para ver más.")
        else:
            st.info("No hay movimientos registrados para este cliente.")
        
        st.divider()
        
        # Análisis premium
        st.markdown("### 📈 Análisis Financiero PREMIUM")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Gastos por Categoría:**")
            gastos_categoria = historial_cliente[
                (historial_cliente['tipo_operacion'] == 'Debito') & 
                (pd.notna(historial_cliente['categoria_gasto']))
            ].groupby('categoria_gasto')['pago_realizado'].sum().sort_values(ascending=False)
            
            if len(gastos_categoria) > 0:
                for cat, monto in gastos_categoria.items():
                    st.write(f"• {cat}: ${monto:,.0f}")
            else:
                st.write("Sin datos de gastos")
        
        with col2:
            st.write("**Distribución de Saldos:**")
            for idx, cuenta in cuentas_cliente.iterrows():
                porcentaje = (cuenta['saldo_actual'] / total_saldo * 100) if total_saldo > 0 else 0
                st.write(f"• {cuenta['entidad_financiera']}: {porcentaje:.1f}%")
        
        with col3:
            balance = cliente['ingresos_mensuales'] - cliente['gastos_mensuales']
            st.metric("Balance Mensual", f"${balance:,.0f}", 
                     delta="Positivo" if balance > 0 else "Negativo")
            capacidad_ahorro = (balance / cliente['ingresos_mensuales'] * 100) if cliente['ingresos_mensuales'] > 0 else 0
            st.write(f"**Capacidad de ahorro:** {capacidad_ahorro:.1f}%")
            st.write(f"**Personas a cargo:** {int(cliente['personas_a_cargo'])}")
            st.write(f"**Estrato:** {int(cliente['estrato_socioeconomico'])}")
    
    st.divider()
    st.caption("© 2024 Equipo B - Sistema de Gestión Financiera")

except FileNotFoundError as e:
    st.error(f"❌ Error al cargar los datos: {e}")
    st.info("Asegúrate de que los archivos CSV estén en la carpeta 'data/'")
except Exception as e:
    st.error(f"❌ Error inesperado: {e}")
    st.info("Verifica que los archivos CSV tengan el formato correcto")