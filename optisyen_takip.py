import streamlit as st
import openpyxl
import io

# Sayfa Yapılandırması
st.set_page_config(page_title="Zayi Raporu - Birebir Görünüm", layout="wide")

st.title("📊 Cam Zayi Raporu - Tam Biçim ve İsim Koruma")
st.info("✅ Mağaza isimleri kodların yanına sabitlendi, renkli gruplar ve dikey yazılar korundu.")

# Mağaza Kodları ve İsimleri (Görsellerinizden birebir eşleştirildi)
magaza_sozlugu = {
    "M38001": "KAYSERI PARK AVM",
    "M38002": "KAYSERI MEYSU OUTLET AVM",
    "M38003": "FORUM KAYSERI AVM",
    "M38004": "KAYSERI KUMSMALL AVM",
    "M38005": "KAYSERI TUNALIFE AVM",
    "M42001": "NOVADA KONYA OUTLET AVM",
    "M42002": "KONYA KENT PLAZA AVM",
    "M42004": "M1 KONYA AVM",
    "M42005": "KONYA KAZIMKARABEKIR CADDE",
    "M42006": "KONYA ENNTEPE AVM",
    "M51001": "NIGDE CADDE",
    "M51002": "NIGDE TEMA PARK AVM",
    "M68001": "AKSARAY NORA CITY AVM",
    "M40001": "KIRSEHIR CADDE",
    "M46001": "MARAS PIAZZA AVM",
    "M70001": "PARK KARAMAN AVM",
    "M50001": "NEVSEHIR NISSARA AVM"
}

uploaded_file = st.file_uploader("Orijinal Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        # 1. Dosyayı TÜM biçim özellikleriyle yükle (data_only=False)
        wb = openpyxl.load_workbook(uploaded_file, data_only=False)
        ws = wb.active

        # 2. SOLDAKİ GRUPLANDIRMA (OUTLINE) YAPISINI SIFIRLA
        ws.sheet_format.outlineLevelRow = 0
        ws.sheet_format.outlineLevelCol = 0
        for r in range(1, ws.max_row + 1):
            ws.row_dimensions[r].outline_level = 0
            ws.row_dimensions[r].hidden = False

        # 3. BAŞLIK VE ÜST BİRİM TESPİTİ
        header_row, ub_col_idx = 1, 1
        found = False
        for r in range(1, 30):
            for c in range(1, 15):
                val = str(ws.cell(r, c).value).strip().upper()
                if "ÜST BIRIM" in val:
                    header_row, ub_col_idx, found = r, c, True
                    break
            if found: break

        # 4. SOLDAKİ GEREKSİZ SÜTUNLARI SİL (Bölge/Müdür)
        # Sadece Üst Birim'in solundakileri sileriz ki Kod ve İsim yapısı bozulmasın
        if ub_col_idx > 1:
            ws.delete_cols(1, ub_col_idx - 1)
        
        # 5. ÜSTTEKİ BOŞ SATIRLARI SİL
        if header_row > 1:
            ws.delete_rows(1, header_row - 1)
            header_row = 1

        # 6. MAĞAZALARI FİLTRELE VE İSİMLERİ KONTROL ET
        # Artık A sütunu KOD, B sütunu İSİM oldu (veya öyle olmalı)
        max_row = ws.max_row
        for r in range(max_row, header_row, -1):
            m_kodu = str(ws.cell(r, 1).value).strip()
            
            if m_kodu in magaza_sozlugu:
                # Mağaza ismini yanındaki hücreye (B sütunu) zorla yazdırıyoruz
                ws.cell(row=r, column=2).value = magaza_sozlugu[m_kodu]
            elif m_kodu != "None" and len(m_kodu) >= 5:
                # Listede olmayan mağaza satırlarını sil
                ws.delete_rows(r)
            elif m_kodu == "None" or m_kodu == "":
                # Tamamen boş satırları (alt toplamlar hariç) temizle
                if r > header_row:
                    ws.delete_rows(r)

        # 7. GÖRSEL DÜZENLEME (Birebir Görünüm İçin)
        ws.row_dimensions[1].height = 65  # Mavi başlık yüksekliği
        ws.column_dimensions['A'].width = 12 # Kod sütunu genişliği
        ws.column_dimensions['B'].width = 30 # İsim sütunu genişliği (Sığması için)

        # 8. ÇIKTIYI HAZIRLA
        output = io.BytesIO()
        wb.save(output)
        
        st.success("✅ Mağaza isimleri kodların yanına getirildi ve biçimler korundu.")
        
        st.download_button(
            label="📥 Birebir Görünümlü Excel'i İndir",
            data=output.getvalue(),
            file_name="Zayi_Raporu_Final_Uyumlu.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Sistem Hatası: {e}")
