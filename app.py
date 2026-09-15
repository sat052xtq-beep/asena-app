import streamlit as st
import google.generativeai as genai
import os

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
    .aac-button button { font-size: 24px !important; height: 90px !important; }
    div[data-testid="stTextInput"] input {
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        padding: 4px !important;
    }
</style>
""", unsafe_allow_html=True)

api_key = os.environ.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

BASE_PROMPT = """
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

def build_system_prompt():
    prompt = BASE_PROMPT
    p = st.session_state.get("profile", {})
    extra = []
    if p.get("movzular"):
        extra.append("Istifadecinin sevdiyi movzular: " + p["movzular"] + ". Mumkunse, misallarinda bunlardan istifade et.")
    if p.get("ses_tonu") and p["ses_tonu"] != "Secin...":
        extra.append("Yazi tonun bu sekilde olmalidir: " + p["ses_tonu"] + ".")
    if p.get("qorxular"):
        extra.append("Istifadeci bunlardan qorxur/narahat olur: " + p["qorxular"] + ". Bunlari xatirlatmaqdan qacın.")
    if extra:
        prompt += "\n\nFERDI PROFIL MELUMATLARI:\n" + "\n".join(extra)
    return prompt

def get_model():
    return genai.GenerativeModel(
        model_name="gemini-3.5-flash-lite",
        system_instruction=build_system_prompt(),
        generation_config=genai.GenerationConfig(max_output_tokens=300, temperature=0.8)
    )

if "chats" not in st.session_state:
    st.session_state.chats = {}
    st.session_state.current_chat_id = None
if "profile" not in st.session_state:
    st.session_state.profile = {"movzular": "", "ses_tonu": "Secin...", "qorxular": ""}
if "sos_active" not in st.session_state:
    st.session_state.sos_active = False
if "ses_lang" not in st.session_state:
    st.session_state.ses_lang = "tr-TR"
if "ses_sureti" not in st.session_state:
    st.session_state.ses_sureti = 0.9
if "nebz" not in st.session_state:
    st.session_state.nebz = 75
if "sudoku_board" not in st.session_state:
    st.session_state.sudoku_board = [
        [5,3,0, 0,7,0, 0,0,0],
        [6,0,0, 1,9,5, 0,0,0],
        [0,9,8, 0,0,0, 0,6,0],
        [8,0,0, 0,6,0, 0,0,3],
        [4,0,0, 8,0,3, 0,0,1],
        [7,0,0, 0,2,0, 0,0,6],
        [0,6,0, 0,0,0, 2,8,0],
        [0,0,0, 4,1,9, 0,0,5],
        [0,0,0, 0,8,0, 0,7,9]
    ]
    st.session_state.sudoku_fixed = [[v != 0 for v in row] for row in st.session_state.sudoku_board]

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
    st.caption("NEBZ MONITORINQI (simulyasiya)")
    st.session_state.nebz = st.slider("BPM", 50, 160, st.session_state.nebz)
    if st.session_state.nebz > 100:
        st.warning("Nebz yuksekdir - sakitlesdirici rejim aktivdir")
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

if st.session_state.nebz > 100:
    st.info("Nebzin yuksekdir. Gel birlikde sakitlesek: 4 saniye nefes al, 4 saniye saxla, 4 saniye burax.")

st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Sohbet", "Danisiq Lovhesi", "Profil", "Foto ile Sorus", "Sudoku"])

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
        dil_secimi = st.selectbox("Ses dili:", ["tr-TR (Turkce)", "en-US (Ingilis)", "ru-RU (Rus)"], index=0)
        st.session_state.ses_lang = dil_secimi.split(" ")[0]
        st.session_state.ses_sureti = st.slider("Ses sureti:", 0.5, 1.5, st.session_state.ses_sureti, 0.1)

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
                    "window.speechSynthesis.cancel();"
                    "window.speechSynthesis.speak(msg);"
                    "</script>",
                    height=0
                )
                st.success("Gonderildi: " + mesaj)
            st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.subheader("Valideyn/Qeyyum Profili")
    st.write("Bu melumatlar ASENA-nin sohbetlerine avtomatik tesir edecek.")
    movzular = st.text_input("Sevdiyi movzular (meselen: dinozavrlar, su sesi):", value=st.session_state.profile["movzular"])
    ton_secimleri = ["Secin...", "Piciltili", "Hezin/yumsaq", "Aydin/deqiq"]
    mevcud_ton = st.session_state.profile["ses_tonu"]
    ton_index = ton_secimleri.index(mevcud_ton) if mevcud_ton in ton_secimleri else 0
    ses_tonu = st.selectbox("Sakitlesdirici ses tonu:", ton_secimleri, index=ton_index)
    qorxular = st.text_input("Qorxdugu amiller:", value=st.session_state.profile["qorxular"])
    if st.button("Profili Saxla"):
        st.session_state.profile = {"movzular": movzular, "ses_tonu": ses_tonu, "qorxular": qorxular}
        for cid in st.session_state.chats:
            new_model = get_model()
            st.session_state.chats[cid]["chat_obj"] = new_model.start_chat(history=[])
        st.success("Profil saxlanildi ve butun sohbetlere tetbiq edildi!")

with tab4:
    st.subheader("Sekil gonder, ASENA sene izah etsin")
    foto_metod = st.radio("Nece gondermek isteyirsen?", ["Fayl yukle", "Kamera ile cek"], horizontal=True)
    foto = None
    if foto_metod == "Fayl yukle":
        foto = st.file_uploader("Sekil sec", type=["jpg", "jpeg", "png"], key="foto_tab")
    else:
        foto = st.camera_input("Sekil cek")
    if foto is not None:
        st.image(foto, width=300)
        if st.button("Bu sekli izah et"):
            with st.spinner("ASENA sekle baxir..."):
                try:
                    vision_model = genai.GenerativeModel("gemini-3.5-flash-lite")
                    response = vision_model.generate_content([
                        "Bu sekilde ne var? Sade, aydin dilde izah et. Metn varsa oxu.",
                        {"mime_type": "image/jpeg", "data": foto.getvalue()}
                    ])
                    st.success(response.text)
                except Exception:
                    st.error("Sekli emal ede bilmedim.")

with tab5:
    st.subheader("Sudoku")
    st.write("Bos xanalari 1-9 arasi reqemlerle doldur.")

    board_col, empty_col = st.columns([5, 3])
    with board_col:
        for r in range(9):
            row_cols = st.columns(9, gap="small")
            for c in range(9):
                fixed = st.session_state.sudoku_fixed[r][c]
                val = st.session_state.sudoku_board[r][c]
                border_style = ""
                if c in (2, 5):
                    border_style = "border-right: 3px solid #2D2D2A;"
                if r in (2, 5):
                    border_style += "border-bottom: 3px solid #2D2D2A;"
                with row_cols[c]:
                    if fixed:
                        st.markdown(
                            "<div style='text-align:center; font-weight:bold; font-size:16px; padding:6px 0; background:#EFEFEF; " + border_style + "'>" + str(val) + "</div>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown("<div style='" + border_style + "'>", unsafe_allow_html=True)
                        new_val = st.text_input(" ", value=str(val) if val != 0 else "", key="sud_" + str(r) + "_" + str(c), label_visibility="collapsed", max_chars=1)
                        st.markdown("</div>", unsafe_allow_html=True)
                        if new_val.isdigit() and 1 <= int(new_val) <= 9:
                            st.session_state.sudoku_board[r][c] = int(new_val)
                        elif new_val == "":
                            st.session_state.sudoku_board[r][c] = 0

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Yoxla"):
            board = st.session_state.sudoku_board
            valid = True
            for i in range(9):
                row = [x for x in board[i] if x != 0]
                col = [board[j][i] for j in range(9) if board[j][i] != 0]
                if len(row) != len(set(row)) or len(col) != len(set(col)):
                    valid = False
            if all(all(v != 0 for v in row) for row in board) and valid:
                st.success("Tebrikler! Sudoku duzgun hell edildi!")
            elif valid:
                st.info("Indiye qeder duzgundur, davam et!")
            else:
                st.warning("Bezi xanalarda tekrarlanma var.")
    with col_b:
        if st.button("Yeniden Basla"):
            del st.session_state.sudoku_board
            del st.session_state.sudoku_fixed
            st.rerun()
