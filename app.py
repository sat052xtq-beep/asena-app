import streamlit as st
import google.generativeai as genai
import os
import random

st.set_page_config(page_title="ASENA", page_icon="💙", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background-color: #FAFAF8; }
    section[data-testid="stSidebar"] { background-color: #F5F4EF; border-right: 1px solid #E5E4DF; }
    .stButton button { border-radius: 8px; border: 1px solid #E5E4DF; background-color: white; }
    .stButton button:hover { background-color: #F0EFE9; border-color: #D97757; }
    h1 { font-weight: 600; color: #2D2D2A; }
    .stChatInput textarea { border-radius: 20px; }
    .sos-button button {
        background-color: #E63946 !important;
        color: white !important;
        font-size: 22px !important;
        font-weight: bold !important;
        border-radius: 50px !important;
        height: 70px !important;
        border: none !important;
    }
    .sos-button button:hover { background-color: #C1121F !important; }
    .aac-button button { font-size: 26px !important; height: 90px !important; }
</style>
""", unsafe_allow_html=True)

api_key = os.environ.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

ASENA_SYSTEM_PROMPT = """
Sen ASENA adli, hertarefli bir suni intellekt komekcisisen - ders, gundelik suallar, meslehet, umumi sohbet - ISTENILEN MOVZUDA komek ede bilersen.
AMMA senin ferqin budur: sen bunu HEMISE xususi bir hessasliqla edirsen, cunki istifadecilerinin arasinda autizm spektrinde olanlar, ADHD yasayanlar, panik atak/anksiyete kecirenler ve gundelik stresli insanlar var.
Qaydalar:
1. Sade, aydin, birbasa dilden istifade et.
2. Metafora ve ikimenali ifadeleri diqqetle izah et.
3. Hemise sebirli, destekleyici, MUHAKIMESIZ ton saxla.
4. Narahatliq/stress elameti gorsen, evvelce sakitlesdir.
5. Ders suallarinda deqiq, addim-addim izah ver.
6. Sohbetin gedisatini xatirla.
7. HEC VAXT "neceysen" kimi suallari tekrarlama.
8. Cavablarini QISA saxla.
9. Istifadeci hansi dilde yazirsa, EYNI DILDE cavab ver.
Sen tibbi diaqnoz qoymursan, amma her movzuda semimi destek verirsen.
"""

@st.cache_resource
def get_model():
    return genai.GenerativeModel(
        model_name="gemini-3.5-flash-lite",
        system_instruction=ASENA_SYSTEM_PROMPT,
        generation_config=genai.GenerationConfig(max_output_tokens=300, temperature=0.8)
    )

if "chats" not in st.session_state:
    st.session_state.chats = {}
    st.session_state.current_chat_id = None
if "profile" not in st.session_state:
    st.session_state.profile = {"movzular": "", "ses_tonu": "", "qorxular": ""}
if "sos_active" not in st.session_state:
    st.session_state.sos_active = False
if "oyun_sual" not in st.session_state:
    st.session_state.oyun_sual = None
if "ses_lang" not in st.session_state:
    st.session_state.ses_lang = "tr-TR"
if "ses_sureti" not in st.session_state:
    st.session_state.ses_sureti = 0.9

def yeni_sohbet_yarat():
    model = get_model()
    chat_id = "chat_" + str(len(st.session_state.chats) + 1)
    st.session_state.chats[chat_id] = {"title": "Yeni Sohbet", "messages": [], "chat_obj": model.start_chat(history=[])}
    st.session_state.current_chat_id = chat_id

if not st.session_state.chats:
    yeni_sohbet_yarat()

with st.sidebar:
    st.markdown("## ASENA")
    if st.button("Yeni Sohbet", use_container_width=True):
        yeni_sohbet_yarat()
        st.rerun()
    st.markdown("---")
    st.caption("SOHBETLERIM")
    for cid, chat_data in reversed(list(st.session_state.chats.items())):
        is_active = (cid == st.session_state.current_chat_id)
        label = chat_data["title"]
        if st.button(label, key="btn_" + cid, use_container_width=True):
            st.session_state.current_chat_id = cid
            st.rerun()

st.title("ASENA")
st.caption("Senin destek dostun - ne desen, men buradayam")

st.markdown('<div class="sos-button">', unsafe_allow_html=True)
if st.button("SOS - Komek Lazimdir", use_container_width=True):
    st.session_state.sos_active = True
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.sos_active:
    st.error("SOS AKTIV EDILDI")
    st.write("Aileye zeng edilir... (simulyasiya)")
    st.write("GPS koordinatlarin paylasilir... (simulyasiya)")
    st.write("Sakit ol, komek yoldadir. Derin nefes al.")
    if st.button("Yaxsiyam, SOS-u sondur"):
        st.session_state.sos_active = False
        st.rerun()

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["Sohbet", "Danisiq Lovhesi", "Profil", "Diqqet Oyunu"])

with tab1:
    current = st.session_state.chats[st.session_state.current_chat_id]

    for msg in current["messages"]:
        with st.chat_message(msg["role"]):
            if isinstance(msg["content"], dict) and msg["content"].get("type") == "image":
                st.image(msg["content"]["data"], width=250)
            else:
                st.write(msg["content"])

    col_upload, col_input = st.columns([1, 8])
    with col_upload:
        yuklenen_foto = st.file_uploader("+", type=["jpg", "jpeg", "png"], label_visibility="collapsed", key="upload_" + st.session_state.current_chat_id)

    with col_input:
        yazili_mesaj = st.chat_input("Ne demek isteyirsen?")

    if yuklenen_foto is not None:
        current["messages"].append({"role": "user", "content": {"type": "image", "data": yuklenen_foto.getvalue()}})
        with st.chat_message("user"):
            st.image(yuklenen_foto, width=250)
        with st.chat_message("assistant"):
            with st.spinner("ASENA sekle baxir..."):
                try:
                    vision_model = genai.GenerativeModel("gemini-3.5-flash-lite")
                    response = vision_model.generate_content([
                        "Bu sekilde ne var? Sade, aydin dilde izah et. Metn varsa oxu.",
                        {"mime_type": "image/jpeg", "data": yuklenen_foto.getvalue()}
                    ])
                    st.write(response.text)
                    current["messages"].append({"role": "assistant", "content": response.text})
                except Exception:
                    st.error("Sekli emal ede bilmedim.")
        st.rerun()

    if yazili_mesaj:
        current["messages"].append({"role": "user", "content": yazili_mesaj})
        if current["title"] == "Yeni Sohbet":
            current["title"] = yazili_mesaj[:30]
        with st.chat_message("user"):
            st.write(yazili_mesaj)
        with st.chat_message("assistant"):
            with st.spinner("ASENA yazir..."):
                try:
                    response = current["chat_obj"].send_message(yazili_mesaj)
                    cavab_metni = response.text
                except Exception:
                    cavab_metni = "Uzr isteyirem, bu sualı indi cavablandira bilmirem."
                st.write(cavab_metni)
        current["messages"].append({"role": "assistant", "content": cavab_metni})
        st.rerun()

with tab2:
    with st.expander("Ses Ayarlari"):
        dil_secimi = st.selectbox(
            "Ses dili:",
            ["tr-TR (Turkce)", "en-US (Ingilis)", "ru-RU (Rus)"],
            index=0
        )
        st.session_state.ses_lang = dil_secimi.split(" ")[0]
        st.session_state.ses_sureti = st.slider("Ses sureti:", 0.5, 1.5, st.session_state.ses_sureti, 0.1)
        st.caption("Qeyd: Azerbaycan dili brauzerlerde birbasa desteklenmir, en yaxin sesler bunlardir.")

    st.subheader("Sozle demek cetindirse, buradan sec:")
    aac_simvollar = {
        "Su isteyirem": "Men su isteyirem",
        "Ac oldum": "Men acam, yemek isteyirem",
        "Tualet": "Tualete getmek isteyirem",
        "Kederliyem": "Ozumu kederli hiss edirem",
        "Esebiyem": "Ozumu esebi hiss edirem",
        "Qorxuram": "Qorxuram, narahatam",
        "Sarilmaq isteyirem": "Mene sarilmaq isteyirem",
        "Sessizlik isteyirem": "Ses-kuyden yorulmusam, sakit yer isteyirem",
        "Seni sevirem": "Seni sevirem",
        "Dayan": "Zehmet olmasa dayan",
        "Beli": "Beli",
        "Xeyr": "Xeyr"
    }
    cols = st.columns(4)
    for i, (label, mesaj) in enumerate(aac_simvollar.items()):
        with cols[i % 4]:
            st.markdown('<div class="aac-button">', unsafe_allow_html=True)
            if st.button(label, key="aac_" + str(i), use_container_width=True):
                current = st.session_state.chats[st.session_state.current_chat_id]
                current["messages"].append({"role": "user", "content": mesaj})
                st.components.v1.html(
                    "<script>"
                    "var msg = new SpeechSynthesisUtterance('" + mesaj + "');"
                    "msg.lang = '" + st.session_state.ses_lang + "';"
                    "msg.rate = " + str(st.session_state.ses_sureti) + ";"
                    "var voices = window.speechSynthesis.getVoices();"
                    "var match = voices.find(v => v.lang === '" + st.session_state.ses_lang + "');"
                    "if(match) msg.voice = match;"
                    "window.speechSynthesis.cancel();"
                    "window.speechSynthesis.speak(msg);"
                    "</script>",
                    height=0
                )
                st.success("Gonderildi: " + mesaj)
            st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.subheader("Valideyn/Qeyyum Profili")
    st.write("Bu melumatlar ASENA-nin usaqinizla daha yaxsi unsiyyet qurmasina komek edecek.")
    movzular = st.text_input("Usaginizin sevdiyi movzular:", value=st.session_state.profile["movzular"])
    ses_tonu = st.selectbox("Sakitlesdirici ses tonu:", ["Secin...", "Piciltili", "Hezin/yumsaq", "Aydin/deqiq"], index=0)
    qorxular = st.text_input("Qorxdugu amiller:", value=st.session_state.profile["qorxular"])
    if st.button("Profili Saxla"):
        st.session_state.profile = {"movzular": movzular, "ses_tonu": ses_tonu, "qorxular": qorxular}
        st.success("Profil saxlanildi!")

with tab4:
    st.subheader("Blok Tapmacasi")
    st.write("Fiquru sec, sonra sebekede yer sec. Cergeni doldursan, o cerge silinir ve xal qazanirsan.")
    block_game_html = """
<div id="game-wrap" style="font-family:sans-serif; text-align:center;">
  <div id="score" style="font-size:22px; font-weight:bold; margin-bottom:10px;">Xal: 0</div>
  <div id="grid" style="display:grid; grid-template-columns:repeat(8, 36px); grid-template-rows:repeat(8, 36px); gap:2px; justify-content:center; margin:0 auto;"></div>
  <div id="tray" style="display:flex; justify-content:center; gap:20px; margin-top:20px;"></div>
  <div id="msg" style="margin-top:10px; color:#E63946; font-weight:bold;"></div>
</div>
<script>
(function(){
  const SIZE = 8;
  const CELL = 36;
  let grid = Array.from({length: SIZE}, () => Array(SIZE).fill(0));
  let score = 0;
  let selectedPiece = null;

  const shapes = [
    {cells:[[0,0]], color:"#F4A261"},
    {cells:[[0,0],[0,1]], color:"#2A9D8F"},
    {cells:[[0,0],[1,0]], color:"#2A9D8F"},
    {cells:[[0,0],[0,1],[0,2]], color:"#E76F51"},
    {cells:[[0,0],[1,0],[2,0]], color:"#E76F51"},
    {cells:[[0,0],[1,0],[1,1]], color:"#457B9D"},
    {cells:[[0,0],[0,1],[1,0]], color:"#457B9D"},
    {cells:[[0,0],[0,1],[1,1]], color:"#457B9D"},
    {cells:[[0,1],[1,0],[1,1]], color:"#457B9D"},
    {cells:[[0,0],[0,1],[1,0],[1,1]], color:"#9B5DE5"}
  ];

  let tray = [];

  function randomPiece(){
    let s = shapes[Math.floor(Math.random()*shapes.length)];
    return {cells: s.cells, color: s.color, used:false};
  }

  function fillTray(){
    tray = [randomPiece(), randomPiece(), randomPiece()];
    renderTray();
  }

  function renderGrid(){
    const g = document.getElementById("grid");
    g.innerHTML = "";
    for(let r=0;r<SIZE;r++){
      for(let c=0;c<SIZE;c++){
        const cell = document.createElement("div");
        cell.style.width = CELL+"px";
        cell.style.height = CELL+"px";
        cell.style.background = grid[r][c] ? grid[r][c] : "#EFEFEF";
        cell.style.border = "1px solid #ddd";
        cell.style.borderRadius = "4px";
        cell.onclick = () => tryPlace(r,c);
        g.appendChild(cell);
      }
    }
  }

  function renderTray(){
    const t = document.getElementById("tray");
    t.innerHTML = "";
    tray.forEach((piece, idx) => {
      if(piece.used){
        const empty = document.createElement("div");
        empty.style.width = "80px"; empty.style.height="80px";
        t.appendChild(empty);
        return;
      }
      const wrap = document.createElement("div");
      wrap.style.display = "grid";
      wrap.style.gridTemplateColumns = "repeat(3, 20px)";
      wrap.style.gridTemplateRows = "repeat(3, 20px)";
      wrap.style.gap = "2px";
      wrap.style.cursor = "pointer";
      wrap.style.padding = "5px";
      wrap.style.border = (selectedPiece===idx) ? "3px solid #333" : "3px solid transparent";
      wrap.style.borderRadius = "8px";
      for(let r=0;r<3;r++){
        for(let c=0;c<3;c++){
          const cell = document.createElement("div");
          const has = piece.cells.some(([pr,pc]) => pr===r && pc===c);
          cell.style.width="18px"; cell.style.height="18px";
          cell.style.background = has ? piece.color : "transparent";
          cell.style.borderRadius = "3px";
          wrap.appendChild(cell);
        }
      }
      wrap.onclick = () => { selectedPiece = idx; renderTray(); };
      t.appendChild(wrap);
    });
  }

  function tryPlace(r,c){
    if(selectedPiece===null) { showMsg("Once bir fiqur sec!"); return; }
    const piece = tray[selectedPiece];
    if(piece.used) return;
    for(const [pr,pc] of piece.cells){
      const rr=r+pr, cc=c+pc;
      if(rr<0||rr>=SIZE||cc<0||cc>=SIZE||grid[rr][cc]){
        showMsg("Bura yerlesmir, basqa yer sec.");
        return;
      }
    }
    for(const [pr,pc] of piece.cells){
      grid[r+pr][c+pc] = piece.color;
    }
    piece.used = true;
    selectedPiece = null;
    score += piece.cells.length;
    clearLines();
    renderGrid();
    renderTray();
    document.getElementById("score").innerText = "Xal: " + score;
    showMsg("");
    if(tray.every(p=>p.used)) fillTray();
  }

  function clearLines(){
    let rowsToClear=[], colsToClear=[];
    for(let r=0;r<SIZE;r++) if(grid[r].every(v=>v)) rowsToClear.push(r);
    for(let c=0;c<SIZE;c++){
      let full=true;
      for(let r=0;r<SIZE;r++) if(!grid[r][c]) full=false;
      if(full) colsToClear.push(c);
    }
    rowsToClear.forEach(r => { for(let c=0;c<SIZE;c++) grid[r][c]=0; score+=10; });
    colsToClear.forEach(c => { for(let r=0;r<SIZE;c++) grid[r][c]=0; score+=10; });
  }

  function showMsg(t){ document.getElementById("msg").innerText = t; }

  renderGrid();
  fillTray();
})();
</script>
"""
    st.components.v1.html(block_game_html, height=560)
