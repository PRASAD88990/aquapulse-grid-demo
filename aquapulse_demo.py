import streamlit as st
import numpy as np
import pandas as pd

# ---------------------------------------------------------
# PAGE CONFIG & CLEAN STYLING
# ---------------------------------------------------------
st.set_page_config(
    page_title="AquaPulse Grid | Indigenous Acoustic Leak Intelligence",
    page_icon="💧",
    layout="wide",
)

st.markdown(
    """
    <style>
    .hero-box {
        padding: 1.5rem;
        border-radius: 10px;
        background: linear-gradient(135deg, #0f2942 0%, #164e63 100%);
        color: #ffffff;
        margin-bottom: 1.2rem;
    }
    .hero-box h1 {
        color: #ffffff;
        margin-bottom: 0.3rem;
        font-size: 2.1rem;
    }
    .badge {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        border-radius: 999px;
        background-color: #0ea5e9;
        color: #ffffff;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# HERO SECTION
# ---------------------------------------------------------
st.markdown(
    """
    <div class="hero-box">
        <span class="badge">TRL-3/4 PROTOTYPE • PATENT-PENDING ARCHITECTURE • MAKE IN INDIA</span>
        <h1>AquaPulse Grid</h1>
        <p style="font-size:1.08rem; margin-bottom:0.4rem;">
            Indigenous Non-Invasive Acoustic Leak Logger & Cloud AI Platform for Intermittent Municipal & Industrial Water Networks
        </p>
        <p style="font-size:0.9rem; color:#cbd5e1; margin-bottom:0;">
            Zero road digging • Zero drinking-water contact • Built for 4-day rotational water supply • 1–2m Cloud ML leak pinpointing
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# TOP METRICS
# ---------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)
m1.metric("Installation Time", "3 Mins / Valve", "Non-invasive magnetic mount")
m2.metric("Daily Packet Payload", "40–64 Bytes", "LoRaWAN / NB-IoT (<2s TX)")
m3.metric("Battery Endurance", "7–10+ Years", "Li-SOCl₂ primary cell")
m4.metric("Burst Pinpoint Accuracy", "1–2 Meters", "Cross-valve Cloud ML")

st.divider()

# ---------------------------------------------------------
# INTERACTIVE LIVE CLOUD ML & 32-BIN FFT TELEMETRY SIMULATOR
# ---------------------------------------------------------
st.subheader("Live Prototype Demo: 4-Day Intermittent Supply & 32-Bin FFT Leak Analyzer")
st.caption(
    "Simulated telemetry from a Wardha/Vidarbha District Metered Area (DMA) pipeline segment "
    "(Valve V-101 to Valve V-102, 200 m Ductile Iron main)."
)

ctrl_col, viz_col = st.columns([1, 2.2])

with ctrl_col:
    st.markdown("**1. Supply Cycle Phase**")
    supply_phase = st.selectbox(
        "Select Hydraulic State",
        [
            "Phase 1: Empty Pipe (Dry / Pre-Supply)",
            "Phase 2: Initial 10-Min Air-Purging Surge (Gated Out)",
            "Phase 3: Pressurized Steady Flow — Healthy Pipe",
            "Phase 4: Pressurized Steady Flow — Subsurface Leak (142 m)",
        ],
        index=3,
    )

    pipe_material = st.radio(
        "Pipe Material Profile",
        ["Metal (CI / DI / MS — 400–2,500 Hz)", "Polymer (PVC / HDPE — 100–600 Hz)"],
        index=0,
    )

    traffic_noise = st.slider(
        "Surface Manhole Traffic Noise Level (dB)",
        min_value=30,
        max_value=95,
        value=72,
        help="10th-percentile minimum noise floor rejects transient passing vehicles.",
    )

    st.info(
        "**Intermittent Supply Gating:**\n"
        "Passive pipe-fill state verification skips dry hours and the initial 10-minute "
        "air-slug turbulence before capturing a 15-minute acoustic window."
    )

with viz_col:
    rng = np.random.default_rng(42)
    is_metal = "Metal" in pipe_material
    freqs = (
        np.linspace(100, 2600, 32) if is_metal else np.linspace(50, 1200, 32)
    )

    # Generate 32-bin FFT spectral magnitudes (dB)
    base_floor = np.full(32, 18.0) + rng.normal(0, 1.2, 32)
    traffic_component = (
        (traffic_noise - 30) * 0.28 * np.exp(-((freqs - 180) ** 2) / (2 * 110**2))
    )

    if "Phase 1" in supply_phase:
        raw_spectrum = base_floor * 0.6
        filtered_spectrum = raw_spectrum
        status_label = "SLEEP MODE — Dry Pipe Verified (0.0 mA Active Compute)"
        leak_prob = 2
        est_distance = None
    elif "Phase 2" in supply_phase:
        raw_spectrum = base_floor + 38 * np.exp(-((freqs - 500) ** 2) / (2 * 450**2)) + traffic_component
        filtered_spectrum = base_floor + 4.0  # Gated out by hardware air-purge timer
        status_label = "AIR-PURGE GATED — Skipping 10-Min Air Surge Artifacts"
        leak_prob = 5
        est_distance = None
    elif "Phase 3" in supply_phase:
        raw_spectrum = base_floor + 6 * np.exp(-((freqs - 300) ** 2) / (2 * 200**2)) + traffic_component
        filtered_spectrum = base_floor + 5 * np.exp(-((freqs - 300) ** 2) / (2 * 200**2))
        status_label = "NORMAL — Pressurized Supply Verified, No Leak Signature"
        leak_prob = 8
        est_distance = None
    else:
        leak_center = 1350 if is_metal else 320
        leak_width = 260 if is_metal else 95
        leak_peak = 34 * np.exp(-((freqs - leak_center) ** 2) / (2 * leak_width**2))
        raw_spectrum = base_floor + leak_peak + traffic_component
        filtered_spectrum = base_floor + leak_peak  # 10th-percentile floor removes truck transient
        status_label = "LEAK DETECTED — High-Confidence Acoustic Anomaly"
        leak_prob = 94
        est_distance = 142.3

    chart_df = pd.DataFrame(
        {
            "Frequency (Hz)": np.round(freqs, 0),
            "Raw Manhole Capture (dB)": np.round(raw_spectrum, 2),
            "10th-Percentile Filtered 32-Bin FFT (dB)": np.round(filtered_spectrum, 2),
        }
    ).set_index("Frequency (Hz)")

    st.line_chart(chart_df, height=310)

    r1, r2, r3 = st.columns(3)
    r1.metric("Node Telemetry State", "64-Byte Packet Ready")
    r2.metric("Cloud ML Leak Confidence", f"{leak_prob}%")
    r3.metric(
        "Triangulated Leak Location",
        f"{est_distance} m from V-101" if est_distance else "No Excavation Needed",
    )

    if leak_prob > 80:
        st.error(f"**Status:** {status_label} — Pinpointed at **142.3 m** downstream of Valve V-101 (±1.5 m).")
    elif "GATED" in status_label or "SLEEP" in status_label:
        st.warning(f"**Status:** {status_label}")
    else:
        st.success(f"**Status:** {status_label}")

st.divider()

# ---------------------------------------------------------
# SYSTEM ARCHITECTURE & DEPLOYMENT OVERVIEW
# ---------------------------------------------------------
st.subheader("System Architecture & Engineering Moat")
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("### 1. Couplant-Free Valve Node")
    st.write(
        "- IP68 submersible puck snaps onto street gate valves in 3 minutes.\n"
        "- Passive acoustic listening (zero ultrasonic emission into drinking water).\n"
        "- Viscoelastic damping isolates pipe vibrations from surface street noise."
    )

with c2:
    st.markdown("### 2. Intermittent Grid Firmware")
    st.write(
        "- Designed for 4-day rotational municipal supply schedules.\n"
        "- Discriminates empty air vs. pressurized water before waking MCU.\n"
        "- Compresses waveform into a 32-bin FFT packet (40–64 bytes/day)."
    )

with c3:
    st.markdown("### 3. Cloud ML & Security")
    st.write(
        "- Cross-correlates neighboring valve FFT signatures + GIS pipe maps.\n"
        "- Hardware root-of-trust key provisioning & encrypted telemetry.\n"
        "- 100% Indian data localization for municipal & industrial SLAs."
    )

st.divider()

# ---------------------------------------------------------
# CONTACT / INCUBATION FOOTER
# ---------------------------------------------------------
st.markdown(
    "**Project Lead:** Prasad Rajendra Warkal (B.E./B.Tech CSE) • Wardha / Nagpur / Pune, Maharashtra  \n"
    "**Stage:** Prototype Validation & Patent Filing • **Deployment Model:** B2B2G EPC & Industrial Water Networks"
)
