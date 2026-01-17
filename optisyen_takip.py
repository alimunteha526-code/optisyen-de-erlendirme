import streamlit as st
import openpyxl
from openpyxl.utils import get_column_letter
import io

st.set_page_config(page_title="Zayi Raporu - Birebir Görünüm", layout="centered")

st.title("📊 Cam Zayi Raporu - Görsel Onarıcı")
st.info("✅ En soldaki bölümler kaldırıldı. Rapor doğrudan 'Üst Birim' ile başlıyor.")

# Tam Mağaza Listesi (Filtreleme için)
istenen_magazalar = [
    "M38003", "M51001", "M42004", "M51002", "M38001", "M38005", 
    "M68001", "M42006", "M42002", "M46001", "M38002", "M42001", 
    "M40001", "M42005", "M38004", "M70001", "M50001"
]

uploaded_file = st.file_uploader("Orijinal Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        # 1. Dosyayı tüm biçim özellikleriyle yükle (Formülleri değil biçimi koru)
        wb = openpyxl.load_workbook(uploaded_file, data_only=False)
        ws = wb.active

        # 2. Üst Birim Sütununu ve Başlık Satırını Dinamik Bul
        header_row = 1
        ub_col_idx = 1
        found = False
        for r in range(1, 20):
            for c in range(1, 10):
                val = str(ws.cell(r, c).value).strip().upper()
                if "ÜST BIRIM" in val:
                    header_row = r
                    ub_col_idx = c
                    found = True
                    break
            if found: break

        # 3. SOLDAKİ BÖLÜMÜ SİL (Üst Birim'in solundaki tüm sütunlar gider)
        # Eğer Üst Birim 3. sütundaysa (C), 1 ve 2. sütunları (A ve B) siler.
        if ub_col_idx > 1:
            ws.delete_cols(1, ub_col_idx - 1)
        
        # Sütunlar silindiği için artık "Üst Birim" 1. sütun (A sütunu) oldu.
        new_ub_idx = 1 

        # 4. ÜSTTEKİ BOŞLUKLARI VE GEREKSİZ SATIRLARI SİL
        if header_row > 1:
            ws.delete_rows(1, header_row - 1)
            header_row = 1 # Başlık artık 1. satıra taşındı

        # 5. MAĞAZALARI FİLTRELE (İstenmeyen satırları temizle)
        # Sondan başa doğru silmek kaymaları ve biçim bozulmalarını önler
        max_row = ws.max_row
        for r in range(max_row, header_row, -1):
            m_kodu = str(ws.cell(r, new_ub_idx).value).strip()
            
            # Eğer hücredeki değer listede yoksa satırı sil
            if m_kodu not in istenen_magazalar:
                # Toplam satırlarını korumak isterseniz ek şart gerekebilir
                # Şimdilik sadece listede olmayan mağaza satırlarını siliyoruz
                if m_kodu != "None" and len(m_kodu) > 2:
                    ws.delete_rows(r)

        # 6. MAVİ ALANI (BAŞLIK) DARALT
        # Başlık satırının yüksekliğini görsele uygun hale getiriyoruz
        ws.row_dimensions[1].height = 50 
        
        # Üst Birim sütununu (A) biraz genişletelim
        ws.column_dimensions['A'].width = 12

        # 7. ÇIKTIYI HAZIRLA
        output = io.BytesIO()
        wb.save(output)
        
        st.success(f"✅ İşlem tamamlandı. Rapor doğrudan Üst Birim ile başlıyor.")
        
        st.download_button(
            label="📥 Onarılmış Raporu İndir",
            data=output.getvalue(),
            file_name="Zayi_Raporu_Temiz.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")
