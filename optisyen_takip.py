import streamlit as st
import openpyxl
import io

st.set_page_config(page_title="Zayi Raporu - Final Düzenleme", layout="centered")

st.title("📊 Cam Zayi Raporu - Görsel Onarıcı")
st.info("✅ Sol taraftaki gruplandırma çubukları (+/-) tamamen temizlendi.")

# Tam Mağaza Listesi
istenen_magazalar = [
    "M38003", "M51001", "M42004", "M51002", "M38001", "M38005", 
    "M68001", "M42006", "M42002", "M46001", "M38002", "M42001", 
    "M40001", "M42005", "M38004", "M70001", "M50001"
]

uploaded_file = st.file_uploader("Orijinal Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        # 1. Dosyayı Biçimleriyle Birlikte Yükle
        wb = openpyxl.load_workbook(uploaded_file, data_only=False)
        ws = wb.active

        # 2. SOLDAKİ GRUPLANDIRMA (OUTLINE) YAPISINI SIFIRLA
        # Bu kısım o istemediğiniz +/- butonlarını ve sol çizgileri yok eder
        ws.sheet_format.outlineLevelRow = 0
        ws.sheet_format.outlineLevelCol = 0
        for r in range(1, ws.max_row + 1):
            ws.row_dimensions[r].outline_level = 0
            ws.row_dimensions[r].hidden = False # Gizli satır varsa açar

        # 3. Başlık ve "Üst Birim" Sütununu Tespit Et
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

        # 4. SOLDAKİ GEREKSİZ SÜTUNLARI SİL (Bölge/Müdür kısımları)
        if ub_col_idx > 1:
            ws.delete_cols(1, ub_col_idx - 1)
        
        # 5. ÜSTTEKİ BOŞ SATIRLARI SİL
        if header_row > 1:
            ws.delete_rows(1, header_row - 1)
            header_row = 1 

        # 6. MAĞAZALARI FİLTRELE (İstenmeyenleri Budama)
        max_row = ws.max_row
        # Sondan başa doğru silmek Excel yapısını (merge cells dahil) korur
        for r in range(max_row, header_row, -1):
            m_kodu = str(ws.cell(r, 1).value).strip()
            
            # Eğer hücredeki mağaza kodu listede yoksa satırı sil
            if m_kodu not in istenen_magazalar:
                # Toplam satırlarını korumak isterseniz ek şart gerekebilir.
                # Şimdilik sadece mağaza kodu içeren ama listede olmayanları siliyoruz.
                if m_kodu != "None" and len(m_kodu) > 2:
                    ws.delete_rows(r)

        # 7. GÖRSEL AYARLAR (Mavi Başlığı Daraltma)
        ws.row_dimensions[1].height = 55 # Başlık yüksekliğini görsele uydurur
        ws.column_dimensions['A'].width = 15 # Üst Birim sütun genişliği

        # 8. ÇIKTIYI HAZIRLA
        output = io.BytesIO()
        wb.save(output)
        
        st.success("✅ Rapor Hazır! Renkler korundu ve gruplandırmalar kaldırıldı.")
        
        st.download_button(
            label="📥 Onarılmış Excel'i İndir",
            data=output.getvalue(),
            file_name="Zayi_Raporu_Temiz.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Sistem Hatası: {e}")
