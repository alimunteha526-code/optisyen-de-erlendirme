import streamlit as st
import pandas as pd
import random
import io
import base64

# PDF kütüphanesi (Hata vermemesi için alternatif yöntemle entegre edildi)
def create_pdf_link(df_dict, sube_adlari):
    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: DejaVu Sans, Arial; font-size: 12px; }}
            h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; page-break-inside: avoid; }}
            th, td {{ border: 1px solid #bdc3c7; padding: 8px; text-align: center; }}
            th {{ background-color: #f2f2f2; font-weight: bold; }}
            .izinli {{ background-color: #fff9c4; font-weight: bold; color: #d32f2f; }}
        </style>
    </head>
    <body>
        <h1 style="text-align: center;">Haftalık Şube Vardiya Çizelgesi</h1>
    """
    for isim in sube_adlari:
        if isim in df_dict:
            html_content += f"<h2>📍 {isim} Şubesi</h2>"
            # Tabloyu oluştururken İZİNLİ olan hücreleri renklendir
            table_html = df_dict[isim].to_html().replace("<td>İZİNLİ</td>", "<td class='izinli'>İZİNLİ</td>")
            html_content += table_html
            html_content += "<div style='page-break-after: always;'></div>"
    
    html_content += "</body></html>"
    return html_content

st.set_page_config(page_title="Niğde Vardiya Paneli", layout="wide")

st.title("📅 Profesyonel Vardiya Yönetimi")
st.markdown("**Kural:** Hafta sonu tam mesai, hafta içi her personel 1 gün izinli.")

# --- YAN MENÜ ---
st.sidebar.header("🏢 Şube ve Personel")
s1_isim = st.sidebar.text_input("1. Şube Adı:", "Niğde 1")
s1_p = st.sidebar.text_area(f"{s1_isim} Personelleri:", "Ahmet, Ayşe, Mehmet, Fatma")

s2_isim = st.sidebar.text_input("2. Şube Adı:", "Niğde 2")
s2_p = st.sidebar.text_area(f"{s2_isim} Personelleri:", "Can, Ece, Ali, Zeynep")

s3_isim = st.sidebar.text_input("3. Şube Adı:", "Niğde 3")
s3_p = st.sidebar.text_area(f"{s3_isim} Personelleri:", "Burak, Deniz, Selin, Mert")

gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
mesai_saatleri = ["05:30 - 14:00", "07:30 - 16:00", "13:30 - 22:00", "14:30 - 23:00"]

def vardiya_motoru(p_listesi):
    personeller = [p.strip() for p in p_listesi.split(",") if p.strip()]
    if len(personeller) < 4: return pd.DataFrame(columns=gunler)
    
    matris = {p: {g: "" for g in gunler} for p in personeller}
    is_gunleri = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
    random.shuffle(is_gunleri)
    
    for idx, p in enumerate(personeller):
        matris[p][is_gunleri[idx % 5]] = "İZİNLİ"
        
    for g in gunler:
        aktifler = [p for p in personeller if matris[p][g] != "İZİNLİ"]
        random.shuffle(aktifler)
        for m_idx, p in enumerate(aktifler):
            matris[p][g] = mesai_saatleri[m_idx % 4]
    return pd.DataFrame(matris).T

if st.sidebar.button("🚀 Vardiyaları Oluştur"):
    st.session_state['s1'] = vardiya_motoru(s1_p)
    st.session_state['s2'] = vardiya_motoru(s2_p)
    st.session_state['s3'] = vardiya_motoru(s3_p)

if 's1' in st.session_state:
    tabs = st.tabs([f"📍 {s1_isim}", f"📍 {s2_isim}", f"📍 {s3_isim}"])
    
    with tabs[0]:
        df1 = st.data_editor(st.session_state['s1'], key="e1", use_container_width=True)
    with tabs[1]:
        df2 = st.data_editor(st.session_state['s2'], key="e2", use_container_width=True)
    with tabs[2]:
        df3 = st.data_editor(st.session_state['s3'], key="e3", use_container_width=True)

    # PDF ve Excel Hazırlığı
    st.sidebar.markdown("---")
    
    # PDF Butonu için HTML çıktısı
    full_html = create_pdf_link({s1_isim: df1, s2_isim: df2, s3_isim: df3}, [s1_isim, s2_isim, s3_isim])
    b64 = base64.b64encode(full_html.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="vardiya_listesi.html" style="text-decoration:none;"><button style="width:100%; height:40px; background-color:#d32f2f; color:white; border:none; border-radius:5px; cursor:pointer;">📄 PDF Taslağını İndir</button></a>'
    st.sidebar.markdown(href, unsafe_allow_html=True)
    st.sidebar.caption("Not: İndirdiğiniz dosyayı açıp Yazdır (CTRL+P) -> PDF Kaydet diyerek PDF alabilirsiniz.")

    # Excel İndirme
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df1.to_excel(writer, sheet_name=s1_isim[:30])
        df2.to_excel(writer, sheet_name=s2_isim[:30])
        df3.to_excel(writer, sheet_name=s3_isim[:30])
    
    st.sidebar.download_button("📥 Excel Olarak İndir", buffer.getvalue(), "vardiya.xlsx", "application/vnd.ms-excel")
