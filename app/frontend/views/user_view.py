import streamlit as st
import plotly.express as px
import pandas as pd

def render_user_dashboard():
    st.title("🏭 Operations Engineering Analytics Interface")
    st.subheader(f"Assigned Facility Monitors Grid: Operator [{st.session_state.get('user_name')}]")
    
    # User Target KPI Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Assigned Fleet Monitoring", "12 Active Machines")
    with col2:
        st.metric("Mean Remaining Lifespan Profile", "312.5 Hours Left")
    with col3:
        st.metric("Unresolved Action Reminders", "2 Priority Alerts", delta_color="inverse")
        
    st.markdown("---")
    
    # Analytical Distribution Plot
    st.subheader("📈 Real-time Assigned Sensor Telemetry Clusters Variance Timeline")
    
    # Constructing cleaner timeline vectors without lambda-nested pandas series
    timeline = list(range(1, 101))
    vibration_amplitudes = []
    
    for x in range(100):
        base_value = 4.2 + (x * 0.01)
        # Apply cyclical variance step spikes deterministically
        spike = 0.2 if x % 10 == 0 else -0.1
        vibration_amplitudes.append(base_value + spike)
        
    chart_data = pd.DataFrame({
        "Operating Timeline (Hours)": timeline,
        "Vibration Variance Amplitude (mm/s)": vibration_amplitudes
    })
    
    fig = px.line(chart_data, x="Operating Timeline (Hours)", y="Vibration Variance Amplitude (mm/s)")
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)