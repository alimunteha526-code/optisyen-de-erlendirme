import streamlit as st
import openpyxl
import io

# Sayfa yapılandırması
st.set_page_config(page_title="Zayi Raporu - Tam Uyumlu", layout="wide")

st.title("📊 Cam Zayi Raporu - Mağaza & İsim Düzenleyici")
st.info("✅ Mağaza isimleri kodların yanına sabitlendi ve görsel yapı korundu.")

# Tam Mağaza Listesi (Eşleştirme için)
istenen_magazalar = {
    "M38003": "FORUM KAYSERI AVM", "M51001": "NIGDE CADDE", 
    "M42004": "M1 KONYA AVM", "M51002": "NIGDE TEMA PARK AVM",
    "M38001": "KAYSERI PARK AVM", "M38005": "KAYSERI TUNALIFE AVM",
    "M68001": "AKSARAY NORA CITY AVM", "M42006": "KONYA ENNTEPE AVM",
    "M42002": "KONYA KENT PLAZA AVM", "M46001": "MARAS PIAZZA AVM",
    "M38002": "KAYSERI MEYSU OUTLET AVM", "M42001": "NOVADA KONYA OUTLET AVM",
    "M40001": "KIRSEHIR CADDE", "M42005": "KONYA KAZIMKARABEKIR CADDE",
    "M38004": "KAYSERI KUMSMALL AVM", "M70001": "PARK KARAMAN AVM",
    "M50001": "NEVSEHIR NISSARA AVM"
}

uploaded_file = st.file_uploader("Orijinal Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        wb = openpyxl.load_workbook(uploaded_file, data_only=False)
        ws = wb.active

        # 1. Gruplandırma (+/-) butonlarını temizle
        ws.sheet_format.outlineLevelRow = 0
        for r in range(1, ws.max_row + 1):
            ws.row_dimensions[r].outline_level = 0

        # 2. Başlık ve Sütun Tespiti
        header_row, ub_col_idx = 1, 1
        found = False
        for r in range(1, 25):
            for c in range(1, 15):
                if "ÜST BIRIM" in str(ws.cell(r, c).value).upper():
                    header_row, ub_col_idx, found = r, c, True
                    break
            if found: break

        # 3. Gereksiz sol sütunları ve üst satırları temizle
        if ub_col_idx > 1: ws.delete_cols(1, ub_col_idx - 1)
        if header_row > 1: ws.delete_rows(1, header_row - 1)
        
        # 4. Mağaza Kodlarını ve İsimlerini Eşleştir (Kritik Bölüm)
        # Sütunları sildiğimiz için Üst Birim artık A sütunu (1) oldu.
        # İsimleri B sütununa (2) yazacağız.
        max_row = ws.max_row
        for r in range(max_row, 1, -1):
            kod = str(ws.cell(r, 1).value).strip()
            
            if kod in istenen_magazalar:
                # İsmi hemen yanındaki (B) hücresine yaz
                ws.cell(row=r, column=2).value = istenen_magazalar[kod]
            elif kod != "None" and len(kod) >= 5:
                # Listede olmayan diğer mağaza satırlarını sil
                ws.delete_rows(r)
            elif kod == "None" or kod == "":
                # Boş satırları temizle
                ws.delete_rows(r)

        # 5. Görsel Ayarlar
        ws.row_dimensions[1].height = 65  # Başlık yüksekliği
        ws.column_dimensions['A'].width = 10 # Kod sütunu
        ws.column_dimensions['B'].width = 30 # İsim sütunu

        output = io.BytesIO()
        wb.save(output)
        
        st.success("✅ Mağaza isimleri başarıyla yan yana getirildi.")
        st.download_button(
            label="📥 Düzenlenmiş Excel'i İndir",
            data=output.getvalue(),
            file_name="Zayi_Raporu_Magaza_Uyumlu.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"Hata: {e}")
