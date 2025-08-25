import cv2
import numpy as np
import streamlit as st
import time

# ---------- Page Configuration ----------
st.set_page_config(page_title="Invisibility Cloak", layout="wide")

# ---------- CUSTOM CSS FOR STYLING ----------
st.markdown("""
<style>
/* Import a clean, modern font */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

/* --- Reset & Base Styles --- */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: 'Poppins', sans-serif;
    background-color: #10141F; /* A deep, dark blue-gray */
}

/* Hide Streamlit's default elements for a custom look */
#MainMenu, footer, header { visibility: hidden; }

/* --- Main App Container --- */
.block-container {
    padding: 2rem 3rem 3rem 3rem !important;
}

/* --- Main Layout (Columns) --- */
/* This ensures the columns are aligned to the top */
[data-testid="stHorizontalBlock"] {
    align-items: flex-start;
    gap: 2.5rem;
}

/* --- Column Content: Controls & Instructions --- */
h3 {
    font-weight: 600;
    color: #EAEAEA;
    margin-top: 1rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.small {
    font-size: 0.95rem;
    line-height: 1.6;
    color: #A9B1D6;
}

hr {
    background-color: rgba(255, 255, 255, 0.1);
    margin: 1.5rem 0 !important;
    border: none !important;
    height: 1px !important;
}

/* --- Gradient Buttons --- */
.stButton button {
    background: linear-gradient(90deg, #5F72BE, #9921E8);
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    font-size: 1rem;
    height: 48px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(153, 33, 232, 0.3);
}

.stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(153, 33, 232, 0.5);
}

/* --- Right Column: Camera & Placeholder --- */
[data-testid="stImage"] img {
    border-radius: 16px;
}

.placeholder-text {
    font-size: 1.5rem;
    font-weight: 500;
    color: #6C757D;
    text-align: center;
    background-color: #0E1117;
    padding: 10rem 2rem;
    border: 2px dashed #2C303B;
    border-radius: 16px;
    height: 100%;
}
</style>
""", unsafe_allow_html=True)


# ---------- State Management ----------
if "run" not in st.session_state:
    st.session_state.run = False
if "background" not in st.session_state:
    st.session_state.background = None

# ---------- LAYOUT DEFINITION (CORRECT METHOD) ----------

# 1. TITLE: At the top, centered using inline styling.
st.markdown("<h1 style='text-align: center; color: #FFFFFF; margin-bottom: 2.5rem;'>Invisibility Cloak</h1>", unsafe_allow_html=True)

# 2. COLUMNS: Created below the title for the rest of the content.
left_col, right_col = st.columns([1, 2], gap="large")

# 3. LEFT COLUMN: All controls and instructions go here.
with left_col:
    st.markdown("<h3>⚙️ Controls</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="small")
    start_btn = c1.button("▶ Start Camera", use_container_width=True)
    stop_btn  = c2.button("⏹ Stop", use_container_width=True)
    recapture_btn = st.button("🔄 Recapture Background", use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("<h3>📖 How to Use</h3>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="small">
        1) Wear a <b>bright red cloth</b> for the best effect.<br/>
        2) Click <b>Start Camera</b> and step out of view.<br/>
        3) Step back in, and the red cloth will become invisible.
        </div>
        """,
        unsafe_allow_html=True
    )

# 4. RIGHT COLUMN: The camera feed or placeholder goes here.
with right_col:
    frame_placeholder = st.empty()


# ---------- BUTTON ACTIONS & CORE LOGIC ----------
if start_btn: st.session_state.run = True
if stop_btn:  st.session_state.run = False
if recapture_btn:
    st.session_state.background = None
    if st.session_state.run:
        st.toast("Background recapture requested...")

# --- Camera Loop & Placeholder Logic ---
if st.session_state.run:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("Cannot open camera. Please check permissions.")
    else:
        time.sleep(1)
        while st.session_state.run:
            ok, frame = cap.read()
            if not ok:
                st.warning("Could not read frame from camera. Stopping.")
                st.session_state.run = False
                break

            frame = cv2.flip(frame, 1)

            if st.session_state.background is None:
                frame_placeholder.info("Capturing background... Please step out of view!")
                time.sleep(2)
                bg = None
                for _ in range(30):
                    ok_bg, f_bg = cap.read()
                    if ok_bg: bg = cv2.flip(f_bg, 1)
                st.session_state.background = bg if bg is not None else frame
                st.toast("Background captured!", icon="✅")
                continue

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_red1 = np.array([0, 120, 70])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 120, 70])
            upper_red2 = np.array([180, 255, 255])

            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask = cv2.morphologyEx(mask1 + mask2, cv2.MORPH_OPEN, np.ones((3,3), np.uint8), iterations=2)
            mask = cv2.dilate(mask, np.ones((3,3), np.uint8), iterations=1)

            inv_mask = cv2.bitwise_not(mask)
            cloak = cv2.bitwise_and(st.session_state.background, st.session_state.background, mask=mask)
            rest_of_frame  = cv2.bitwise_and(frame, frame, mask=inv_mask)
            output = cv2.add(cloak, rest_of_frame)

            frame_placeholder.image(cv2.cvtColor(output, cv2.COLOR_BGR2RGB), channels="RGB")

        cap.release()
        cv2.destroyAllWindows()
else:
    # Display a placeholder when the camera is off
    frame_placeholder.markdown("<div class='placeholder-text'>Camera is Off</div>", unsafe_allow_html=True)