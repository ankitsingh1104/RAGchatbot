import os
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import subprocess
from app.pipeline import Pipeline
from app.config import VECTOR_STORE_DIR, DATA_DOCS_DIR

st.set_page_config(
    page_title="DevOps Assistant v1.0",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS + ANIMATIONS + SOUNDS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=VT323&family=Share+Tech+Mono&display=swap');

* { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background-color: #008080 !important;
    font-family: 'Share Tech Mono', monospace !important;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stMainBlockContainer"] {
    background: #c0c0c0 !important;
    padding: 4px 8px 60px 8px !important;
    max-width: 100% !important;
}
[data-testid="stSidebar"] { background: #c0c0c0 !important; border-right: 2px solid #808080 !important; }
[data-testid="stSidebar"] > div { background: #c0c0c0 !important; padding: 6px !important; }

/* ── Boot screen overlay ── */
#boot-screen {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: #000080;
    z-index: 99999;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    font-family: 'VT323', monospace;
    color: #ffffff;
    animation: bootFadeOut 0.5s ease 3.5s forwards;
}
@keyframes bootFadeOut {
    from { opacity: 1; pointer-events: all; }
    to   { opacity: 0; pointer-events: none; display: none; }
}
.boot-logo {
    font-size: 72px; margin-bottom: 20px;
    animation: bootPulse 0.8s ease-in-out infinite alternate;
}
@keyframes bootPulse {
    from { transform: scale(1); }
    to   { transform: scale(1.05); }
}
.boot-title {
    font-size: 52px; color: #ffffff; margin-bottom: 8px; letter-spacing: 4px;
}
.boot-subtitle {
    font-size: 24px; color: #c0c0c0; margin-bottom: 40px;
}
.boot-bar-container {
    width: 400px; height: 28px;
    border: 2px solid #ffffff;
    background: #000040;
    overflow: hidden;
    position: relative;
}
.boot-bar {
    height: 100%;
    background: repeating-linear-gradient(
        90deg, #c0c0c0 0px, #c0c0c0 18px, #000040 18px, #000040 22px
    );
    width: 0%;
    animation: bootLoad 3s ease forwards;
}
@keyframes bootLoad {
    0%   { width: 0%; }
    20%  { width: 25%; }
    50%  { width: 60%; }
    80%  { width: 85%; }
    100% { width: 100%; }
}
.boot-status {
    font-size: 18px; color: #c0c0c0; margin-top: 10px;
    animation: bootStatus 3s steps(1) forwards;
}
@keyframes bootStatus {
    0%   { content: ''; }
}
.boot-version {
    position: absolute; bottom: 20px;
    font-size: 16px; color: #808080;
}

/* ── Win95 components ── */
.win95-titlebar {
    background: linear-gradient(90deg, #000080, #1084d0);
    color: white; font-family: 'VT323', monospace; font-size: 20px;
    padding: 3px 8px; display: flex; align-items: center; justify-content: space-between;
}
.win95-btns { display: flex; gap: 2px; }
.win95-btn {
    width: 18px; height: 16px; background: #c0c0c0;
    border-top: 2px solid #fff; border-left: 2px solid #fff;
    border-right: 2px solid #808080; border-bottom: 2px solid #808080;
    font-size: 10px; text-align: center; line-height: 13px;
    color: #000; font-weight: bold; font-family: monospace; display: inline-block;
}
.win95-menu {
    background: #c0c0c0; border-bottom: 1px solid #808080;
    padding: 2px 8px; font-size: 13px; font-family: 'Share Tech Mono', monospace;
}
.win95-menu span { margin-right: 14px; cursor: pointer; }
.win95-toolbar {
    background: #c0c0c0; border-top: 1px solid #fff; border-bottom: 2px solid #808080;
    padding: 3px 8px; font-size: 12px; font-family: 'Share Tech Mono', monospace;
    color: #555; display: flex; justify-content: space-between;
}
.win95-label {
    font-family: 'VT323', monospace; font-size: 19px; color: #000080;
    border-bottom: 1px solid #808080; margin: 6px 0 3px 0;
}
.win95-infobox {
    background: #fff;
    border-top: 2px solid #808080; border-left: 2px solid #808080;
    border-right: 2px solid #fff; border-bottom: 2px solid #fff;
    padding: 5px 8px; font-size: 12px; font-family: 'Share Tech Mono', monospace; margin: 3px 0;
}
.dot-green { display:inline-block; width:10px; height:10px; background:#00c800; border:1px solid #006400; margin-right:4px; }
.dot-red   { display:inline-block; width:10px; height:10px; background:#ff0000; border:1px solid #800000; margin-right:4px; }

/* ── Buttons ── */
.stButton > button {
    background: #c0c0c0 !important; color: #000 !important;
    border-top: 2px solid #fff !important; border-left: 2px solid #fff !important;
    border-right: 2px solid #808080 !important; border-bottom: 2px solid #808080 !important;
    border-radius: 0 !important; font-family: 'Share Tech Mono', monospace !important;
    font-size: 12px !important; padding: 3px 10px !important; box-shadow: none !important;
}
.stButton > button:active {
    border-top: 2px solid #808080 !important; border-left: 2px solid #808080 !important;
    border-right: 2px solid #fff !important; border-bottom: 2px solid #fff !important;
}
.stCheckbox label { font-family: 'Share Tech Mono', monospace !important; font-size: 13px !important; color: #000 !important; }

/* ── Chat ── */
[data-testid="stChatMessage"] { background: transparent !important; border: none !important; padding: 2px 0 !important; }
.user-bubble {
    background: #000080; color: #fff;
    font-family: 'VT323', monospace; font-size: 20px;
    padding: 6px 12px; display: inline-block;
    border-top: 2px solid #4444ff; border-left: 2px solid #4444ff;
    border-right: 2px solid #000040; border-bottom: 2px solid #000040;
    max-width: 75%; word-wrap: break-word;
}
.user-bubble::before { content: "C:\\USER>  "; color: #00ff88; font-weight: bold; }
.assistant-bubble {
    background: #fff; color: #000;
    border-top: 2px solid #808080; border-left: 2px solid #808080;
    border-right: 2px solid #fff; border-bottom: 2px solid #fff;
    max-width: 90%; word-wrap: break-word;
}
.assistant-header {
    background: linear-gradient(90deg, #000080, #1084d0);
    color: #fff; font-family: 'VT323', monospace; font-size: 16px; padding: 2px 8px;
}
.assistant-body {
    padding: 10px 14px; font-family: 'VT323', monospace;
    font-size: 20px; line-height: 1.7; white-space: pre-wrap; color: #000;
}

/* ── Typing cursor animation ── */
.typing-cursor {
    display: inline-block;
    width: 12px; height: 20px;
    background: #000;
    margin-left: 2px;
    vertical-align: middle;
    animation: blink 0.7s step-end infinite;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0; }
}

/* ── Win95 error dialog ── */
.win95-dialog-overlay {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0,0,0,0.3);
    z-index: 9998;
    display: flex; align-items: center; justify-content: center;
}
.win95-dialog {
    background: #c0c0c0;
    border-top: 2px solid #fff; border-left: 2px solid #fff;
    border-right: 2px solid #808080; border-bottom: 2px solid #808080;
    width: 400px; font-family: 'Share Tech Mono', monospace;
    box-shadow: 4px 4px 0 #000;
}
.win95-dialog-title {
    background: linear-gradient(90deg, #800000, #c00000);
    color: #fff; font-family: 'VT323', monospace; font-size: 18px;
    padding: 3px 8px; display: flex; justify-content: space-between; align-items: center;
}
.win95-dialog-body {
    padding: 16px 16px 8px 16px;
    display: flex; align-items: flex-start; gap: 12px;
}
.win95-dialog-icon {
    font-size: 36px; flex-shrink: 0;
}
.win95-dialog-msg {
    font-size: 13px; color: #000; line-height: 1.5;
}
.win95-dialog-footer {
    padding: 8px 16px 12px;
    display: flex; justify-content: center; gap: 8px;
}
.win95-dialog-btn {
    background: #c0c0c0; color: #000;
    border-top: 2px solid #fff; border-left: 2px solid #fff;
    border-right: 2px solid #808080; border-bottom: 2px solid #808080;
    padding: 3px 24px; font-family: 'Share Tech Mono', monospace;
    font-size: 13px; cursor: pointer; min-width: 80px; text-align: center;
}

/* ── Source cards ── */
.src-card {
    background: #c0c0c0;
    border-top: 1px solid #fff; border-left: 1px solid #fff;
    border-right: 1px solid #808080; border-bottom: 1px solid #808080;
    padding: 4px 8px; margin: 3px 0;
    font-family: 'Share Tech Mono', monospace; font-size: 12px; color: #000;
}
.src-card-title {
    background: linear-gradient(90deg, #000080, #1084d0);
    color: #fff; font-family: 'VT323', monospace;
    font-size: 15px; padding: 1px 6px; margin-bottom: 3px;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] { background: #c0c0c0 !important; }
[data-testid="stFileUploader"] > div {
    background: #fff !important;
    border-top: 2px solid #808080 !important; border-left: 2px solid #808080 !important;
    border-right: 2px solid #fff !important; border-bottom: 2px solid #fff !important;
    border-radius: 0 !important; padding: 8px !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: #fff !important; border: 2px dashed #000080 !important;
    border-radius: 0 !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 12px !important; color: #000080 !important;
}
.uploaded-file {
    background: #c0c0c0;
    border-top: 1px solid #fff; border-left: 1px solid #fff;
    border-right: 1px solid #808080; border-bottom: 1px solid #808080;
    padding: 3px 6px; margin: 2px 0;
    font-family: 'Share Tech Mono', monospace; font-size: 11px;
}

/* ── Chat input ── */
.stChatInput > div {
    background: #c0c0c0 !important;
    border-top: 2px solid #808080 !important; border-left: 2px solid #808080 !important;
    border-right: 2px solid #fff !important; border-bottom: 2px solid #fff !important;
    border-radius: 0 !important;
}
.stChatInput textarea {
    background: #fff !important; color: #000 !important;
    font-family: 'Share Tech Mono', monospace !important; font-size: 13px !important;
    border-radius: 0 !important; height: 40px !important;
    min-height: 40px !important; max-height: 40px !important; resize: none !important;
}

details > summary {
    background: #c0c0c0 !important;
    border-top: 2px solid #fff !important; border-left: 2px solid #fff !important;
    border-right: 2px solid #808080 !important; border-bottom: 2px solid #808080 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 12px !important; color: #000 !important;
    border-radius: 0 !important; padding: 4px 8px !important;
}
code, pre {
    background: #000 !important; color: #00ff00 !important;
    font-family: 'Share Tech Mono', monospace !important;
    border: 1px solid #004400 !important; border-radius: 0 !important;
}
hr { border: none !important; border-top: 1px solid #808080 !important; border-bottom: 1px solid #fff !important; margin: 6px 0 !important; }

/* ── Taskbar ── */
.taskbar {
    position: fixed; bottom: 0; left: 0; right: 0;
    background: #c0c0c0; border-top: 2px solid #fff;
    padding: 2px 6px; display: flex; align-items: center; gap: 6px;
    font-family: 'VT323', monospace; font-size: 17px; z-index: 9999;
}
.start-btn {
    background: #c0c0c0;
    border-top: 2px solid #fff; border-left: 2px solid #fff;
    border-right: 2px solid #808080; border-bottom: 2px solid #808080;
    padding: 1px 10px; font-weight: bold; cursor: pointer;
}
.taskbar-clock {
    margin-left: auto;
    border-top: 1px solid #808080; border-left: 1px solid #808080;
    border-right: 1px solid #fff; border-bottom: 1px solid #fff;
    padding: 1px 8px; font-size: 15px;
}

/* ── Sound toggle ── */
.sound-btn {
    background: #c0c0c0;
    border-top: 2px solid #808080; border-left: 2px solid #808080;
    border-right: 2px solid #fff; border-bottom: 2px solid #fff;
    padding: 1px 8px; font-size: 14px; cursor: pointer;
    font-family: 'Share Tech Mono', monospace;
}
/* Hide audio players — sounds play but UI stays clean */
[data-testid="stAudio"] {
    display: none !important;
    height: 0 !important;
    overflow: hidden !important;
}            
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# JAVASCRIPT — Boot screen + Sounds + Click SFX
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<script>
// ── Audio context for retro sounds ────────────────────────────────────────────
const AudioCtx = window.AudioContext || window.webkitAudioContext;
let audioCtx = null;
let soundEnabled = true;

function getAudioCtx() {
    if (!audioCtx) audioCtx = new AudioCtx();
    return audioCtx;
}

function playBeep(freq, duration, type='square', vol=0.15) {
    if (!soundEnabled) return;
    try {
        const ctx = getAudioCtx();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.type = type;
        osc.frequency.setValueAtTime(freq, ctx.currentTime);
        gain.gain.setValueAtTime(vol, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
        osc.start(ctx.currentTime);
        osc.stop(ctx.currentTime + duration);
    } catch(e) {}
}

function playStartup() {
    if (!soundEnabled) return;
    setTimeout(() => playBeep(523, 0.12), 0);
    setTimeout(() => playBeep(659, 0.12), 130);
    setTimeout(() => playBeep(784, 0.12), 260);
    setTimeout(() => playBeep(1047, 0.25), 390);
}

function playClick() {
    playBeep(800, 0.05, 'square', 0.08);
}

function playError() {
    if (!soundEnabled) return;
    setTimeout(() => playBeep(220, 0.15, 'sawtooth', 0.2), 0);
    setTimeout(() => playBeep(180, 0.15, 'sawtooth', 0.2), 160);
    setTimeout(() => playBeep(150, 0.3,  'sawtooth', 0.2), 320);
}

function playSuccess() {
    if (!soundEnabled) return;
    setTimeout(() => playBeep(523, 0.1), 0);
    setTimeout(() => playBeep(784, 0.15), 120);
}

// ── Toggle sound ──────────────────────────────────────────────────────────────
window.toggleSound = function() {
    soundEnabled = !soundEnabled;
    const btn = document.getElementById('sound-toggle');
    if (btn) btn.textContent = soundEnabled ? '🔊 Sound: ON' : '🔇 Sound: OFF';
    playBeep(440, 0.1);
}

// ── Add click sounds to all Win95 buttons ─────────────────────────────────────
function attachClickSounds() {
    document.querySelectorAll('button, .win95-dialog-btn').forEach(btn => {
        if (!btn.dataset.soundAttached) {
            btn.addEventListener('click', () => playClick());
            btn.dataset.soundAttached = 'true';
        }
    });
}

// ── Boot screen logic ─────────────────────────────────────────────────────────
window.addEventListener('load', function() {
    // Only show boot screen on first load
    const booted = sessionStorage.getItem('win95_booted');
    const bootEl = document.getElementById('boot-screen');

    if (!booted && bootEl) {
        bootEl.style.display = 'flex';
        playStartup();

        // Animate boot messages
        const messages = [
            'Loading DEVOPS.SYS...',
            'Initializing FAISS Engine...',
            'Loading Ollama Driver...',
            'Starting RAG Services...',
            'Welcome to DevOps Assistant v1.0'
        ];
        const statusEl = document.getElementById('boot-status');
        messages.forEach((msg, i) => {
            setTimeout(() => {
                if (statusEl) statusEl.textContent = msg;
            }, i * 600);
        });

        setTimeout(() => {
            if (bootEl) {
                bootEl.style.opacity = '0';
                bootEl.style.transition = 'opacity 0.5s';
                setTimeout(() => bootEl.style.display = 'none', 500);
            }
            sessionStorage.setItem('win95_booted', '1');
            playSuccess();
        }, 3500);
    } else if (bootEl) {
        bootEl.style.display = 'none';
    }

    // Attach click sounds
    attachClickSounds();
    // Re-attach on DOM changes (Streamlit re-renders)
    const observer = new MutationObserver(attachClickSounds);
    observer.observe(document.body, { childList: true, subtree: true });
});

// ── Win95 error dialog ────────────────────────────────────────────────────────
window.showWin95Error = function(title, message) {
    playError();
    const overlay = document.createElement('div');
    overlay.className = 'win95-dialog-overlay';
    overlay.id = 'win95-error-overlay';
    overlay.innerHTML = `
        <div class="win95-dialog">
            <div class="win95-dialog-title">
                <span>⛔ ${title}</span>
                <span style="cursor:pointer" onclick="closeWin95Error()">✕</span>
            </div>
            <div class="win95-dialog-body">
                <div class="win95-dialog-icon">⛔</div>
                <div class="win95-dialog-msg">${message}</div>
            </div>
            <div class="win95-dialog-footer">
                <div class="win95-dialog-btn" onclick="closeWin95Error()">OK</div>
                <div class="win95-dialog-btn" onclick="closeWin95Error()">Cancel</div>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
}

window.closeWin95Error = function() {
    const overlay = document.getElementById('win95-error-overlay');
    if (overlay) overlay.remove();
    playClick();
}

// ── Expose sound functions globally ──────────────────────────────────────────
window.playSuccess = playSuccess;
window.playError = playError;
window.playClick = playClick;
</script>
""", unsafe_allow_html=True)

# ── Boot Screen HTML ───────────────────────────────────────────────────────────
st.markdown("""
<div id="boot-screen">
    <div class="boot-logo">🖥️</div>
    <div class="boot-title">DevOps Assistant</div>
    <div class="boot-subtitle">RAG Knowledge System v1.0</div>
    <div class="boot-bar-container">
        <div class="boot-bar"></div>
    </div>
    <div class="boot-status" id="boot-status">Loading DEVOPS.SYS...</div>
    <div class="boot-version">© 2025 DevOps RAG Systems. All rights reserved.</div>
</div>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
def is_index_ready():
    return os.path.exists(os.path.join(VECTOR_STORE_DIR, "faiss_index", "index.faiss"))


@st.cache_resource
def get_pipeline():
    return Pipeline()


def consume_stream(stream):
    parts = []
    try:
        for chunk in stream:
            if hasattr(chunk, 'content'):
                parts.append(chunk.content)
            elif isinstance(chunk, str):
                parts.append(chunk)
    except Exception:
        pass
    return "".join(parts)


def play_sound(sound_name: str):
    sound_file = os.path.join(PROJECT_ROOT, "ui", "static", f"{sound_name}.wav")
    if os.path.exists(sound_file):
        with open(sound_file, "rb") as f:
            st.audio(f.read(), format="audio/wav", autoplay=True)


def save_uploaded_file(uploaded_file):
    os.makedirs(DATA_DOCS_DIR, exist_ok=True)
    dest = os.path.join(DATA_DOCS_DIR, uploaded_file.name)
    with open(dest, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return dest


def list_docs():
    if not os.path.exists(DATA_DOCS_DIR):
        return []
    return [f for f in os.listdir(DATA_DOCS_DIR) if f.endswith((".pdf", ".txt", ".md"))]


def show_error_dialog(title, message):
    """Render a Win95-style error dialog via JS."""
    safe_msg = message.replace("'", "\\'").replace("\n", "<br>")[:300]
    st.markdown(
        f"<script>window.showWin95Error('{title}', '{safe_msg}');</script>",
        unsafe_allow_html=True
    )


# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "domain_filters" not in st.session_state:
    st.session_state.domain_filters = ["kubernetes", "docker", "cicd", "terraform", "helm", "gitops"]
if "sound_on" not in st.session_state:
    st.session_state.sound_on = True


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="win95-titlebar" style="margin-bottom:8px;">
        <span>📁 Control Panel</span>
        <div class="win95-btns">
            <div class="win95-btn">_</div>
            <div class="win95-btn">□</div>
            <div class="win95-btn">✕</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Status
    st.markdown('<div class="win95-label">⚙ System Status</div>', unsafe_allow_html=True)
    if is_index_ready():
        st.markdown('<div class="win95-infobox"><span class="dot-green"></span>KB: <b>READY</b></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="win95-infobox"><span class="dot-red"></span>KB: <b>NOT READY</b></div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Sound toggle
    st.markdown('<div class="win95-label">🔊 Sound</div>', unsafe_allow_html=True)
    st.markdown("""
    <div onclick="toggleSound()" id="sound-toggle"
         style="background:#c0c0c0; border-top:2px solid #fff; border-left:2px solid #fff;
                border-right:2px solid #808080; border-bottom:2px solid #808080;
                padding:3px 10px; font-family:'Share Tech Mono',monospace; font-size:12px;
                cursor:pointer; display:inline-block; margin:4px 0;">
        🔊 Sound: ON
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # PDF Upload
    st.markdown('<div class="win95-label">📂 Upload Documents</div>', unsafe_allow_html=True)
    st.markdown('<div class="win95-infobox" style="font-size:11px;">Drop PDF, TXT, or MD files.<br>Click Ingest after uploading.</div>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Drop files here",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        saved = []
        for f in uploaded_files:
            save_uploaded_file(f)
            saved.append(f.name)
        st.markdown(f'<div class="win95-infobox" style="color:#006400;">✓ Saved: {", ".join(saved)}</div>', unsafe_allow_html=True)

        if st.button("▶ Ingest Uploaded Files", use_container_width=True):
            with st.spinner("Indexing..."):
                r = subprocess.run([sys.executable, "ingest.py", "--local-only"],
                                   capture_output=True, text=True, cwd=PROJECT_ROOT)
                if r.returncode == 0:
                    st.success("✓ Files indexed!")
                    st.cache_resource.clear()
                else:
                    show_error_dialog("Ingestion Error", r.stderr[-300:])

    docs = list_docs()
    if docs:
        st.markdown('<div class="win95-label">📋 Indexed Files</div>', unsafe_allow_html=True)
        for doc in docs[:6]:
            icon = "📄" if doc.endswith(".pdf") else "📝"
            st.markdown(f'<div class="uploaded-file">{icon} {doc}</div>', unsafe_allow_html=True)
        if len(docs) > 6:
            st.markdown(f'<div class="win95-infobox" style="font-size:11px;">+ {len(docs)-6} more</div>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # Data management
    st.markdown('<div class="win95-label">💾 Data Management</div>', unsafe_allow_html=True)

    if st.button("▶ Run Ingestion (Local)", use_container_width=True):
        with st.spinner("Reading local files..."):
            r = subprocess.run([sys.executable, "ingest.py", "--local-only"],
                               capture_output=True, text=True, cwd=PROJECT_ROOT)
            if r.returncode == 0:
                st.success("✓ Done!")
                st.cache_resource.clear()
            else:
                show_error_dialog("Ingestion Failed", r.stderr[-300:])

    if st.button("▶ Full Ingestion (Web)", use_container_width=True):
        with st.spinner("Scraping web docs..."):
            r = subprocess.run([sys.executable, "ingest.py"],
                               capture_output=True, text=True, cwd=PROJECT_ROOT)
            if r.returncode == 0:
                st.success("✓ Done!")
                st.cache_resource.clear()
            else:
                show_error_dialog("Ingestion Failed", r.stderr[-300:])

    if st.button("⟳ Rebuild Index", use_container_width=True):
        with st.spinner("Rebuilding..."):
            r = subprocess.run([sys.executable, "ingest.py", "--rebuild"],
                               capture_output=True, text=True, cwd=PROJECT_ROOT)
            if r.returncode == 0:
                st.success("✓ Rebuilt!")
                st.cache_resource.clear()
            else:
                show_error_dialog("Rebuild Failed", r.stderr[-300:])

    st.markdown("<hr>", unsafe_allow_html=True)

    # Domain filters
    st.markdown('<div class="win95-label">🗂 Domain Filters</div>', unsafe_allow_html=True)
    icons = {"kubernetes": "☸", "docker": "🐳", "cicd": "⚙", "terraform": "🏗", "helm": "⛵", "gitops": "🔄"}
    selected = []
    for d in ["kubernetes", "docker", "cicd", "terraform", "helm", "gitops"]:
        if st.checkbox(f"{icons[d]} {d.upper()}", value=True, key=f"chk_{d}"):
            selected.append(d)
    st.session_state.domain_filters = selected or list(icons.keys())

    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div class="win95-infobox">
        <b>ENGINE:</b> Ollama<br>
        <b>LLM:</b> llama3.2<br>
        <b>EMBED:</b> nomic-embed-text<br>
        <b>VECTOR:</b> FAISS<br>
        <b>RERANK:</b> ms-marco
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ══════════════════════════════════════════════════════════════════════════════
ready = is_index_ready()

if 'startup_played' not in st.session_state:
    play_sound('startup')
    st.session_state.startup_played = True

st.markdown(f"""
<div class="win95-titlebar">
    <span>🖥️ DevOps Expert Assistant v1.0 — [RAG-SYSTEM]</span>
    <div class="win95-btns">
        <div class="win95-btn">_</div>
        <div class="win95-btn">□</div>
        <div class="win95-btn">✕</div>
    </div>
</div>
<div class="win95-menu">
    <span>File</span><span>Edit</span><span>View</span><span>Query</span><span>Help</span>
</div>
<div class="win95-toolbar">
    <span>📂 Open &nbsp;|&nbsp; 💾 Save &nbsp;|&nbsp; 🔍 Search</span>
    <span>Ollama: Active &nbsp;|&nbsp; FAISS: {'Ready' if ready else 'Not Ready'} &nbsp;|&nbsp; llama3.2</span>
</div>
""", unsafe_allow_html=True)

if not ready:
    st.markdown("""
    <div style="background:#ffff00;border:2px solid #808000;padding:8px;margin:6px 0;
                font-family:'Share Tech Mono',monospace;font-size:13px;">
        ⚠ WARNING: Knowledge base not found. Click "Run Ingestion" in the Control Panel sidebar.
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Chat history ───────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="💻"):
            st.markdown(f'<div class="user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        with st.chat_message("assistant", avatar="🖥️"):
            st.markdown(
                f'<div class="assistant-bubble">'
                f'<div class="assistant-header">🖥 DEVOPS.EXE — Output:</div>'
                f'<div class="assistant-body">{msg["content"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            if msg.get("sources"):
                with st.expander("📁 View Source Files"):
                    for src in msg["sources"]:
                        fname = os.path.basename(src.get("source_file") or src.get("source_url") or "unknown")
                        st.markdown(f"""
                        <div class="src-card">
                            <div class="src-card-title">📄 {fname}</div>
                            <b>Domain:</b> {src.get('domain','N/A').upper()} &nbsp;|&nbsp;
                            <b>Score:</b> {src.get('score',0):.4f}<br>
                            <small style="color:#444">{src.get('text','')[:200]}...</small>
                        </div>
                        """, unsafe_allow_html=True)

# ── New message ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("C:\\DEVOPS>  Ask a DevOps question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar="💻"):
        st.markdown(f'<div class="user-bubble">{prompt}</div>', unsafe_allow_html=True)
        play_sound('click')

    with st.chat_message("assistant", avatar="🖥️"):
        answer = ""
        sources = []

        if not ready:
            answer = "ERROR: Knowledge base not found. Run ingestion from Control Panel."
            show_error_dialog("System Error", answer)
        else:
            # Show typing animation while processing
            typing_placeholder = st.empty()
            typing_placeholder.markdown(
                '<div class="assistant-bubble">'
                '<div class="assistant-header">🖥 DEVOPS.EXE — Output:</div>'
                '<div class="assistant-body">█<span class="typing-cursor"></span></div>'
                '</div>',
                unsafe_allow_html=True
            )

            try:
                pipeline = get_pipeline()
                history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[:-1]
                ]
                result = pipeline.query(
                    user_question=prompt,
                    chat_history=history,
                    domain_filter=st.session_state.domain_filters
                )
                sources = result.get("sources", [])
                raw = result.get("answer", "")
                answer = raw if isinstance(raw, str) else consume_stream(raw)

            except Exception as e:
                answer = f"SYSTEM ERROR: {str(e)}"
                sources = []
                show_error_dialog("Runtime Error", str(e))
                play_sound('error')

            # Replace typing animation with real answer
            typing_placeholder.markdown(
                f'<div class="assistant-bubble">'
                f'<div class="assistant-header">🖥 DEVOPS.EXE — Output:</div>'
                f'<div class="assistant-body">{answer}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

            # Play success sound
            play_sound('success')

            if sources:
                with st.expander("📁 View Source Files"):
                    for src in sources:
                        fname = os.path.basename(src.get("source_file") or src.get("source_url") or "unknown")
                        st.markdown(f"""
                        <div class="src-card">
                            <div class="src-card-title">📄 {fname}</div>
                            <b>Domain:</b> {src.get('domain','N/A').upper()} &nbsp;|&nbsp;
                            <b>Score:</b> {src.get('score',0):.4f}<br>
                            <small style="color:#444">{src.get('text','')[:200]}...</small>
                        </div>
                        """, unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })

# ── Taskbar ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="taskbar">
    <div class="start-btn" onclick="playClick()">🪟 Start</div>
    <div style="width:1px;height:20px;background:#808080;margin:0 2px;"></div>
    <span>🖥️ DevOps Assistant v1.0</span>
    <div class="taskbar-clock">⚡ OLLAMA:ON | FAISS:OK</div>
</div>
""", unsafe_allow_html=True)
