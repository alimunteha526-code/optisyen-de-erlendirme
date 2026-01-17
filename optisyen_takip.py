import streamlit as st
import openpyxl
import io

# Sayfa Yapılandırması
st.set_page_config(page_title="Zayi Raporu - Tam Temizlik", layout="wide")

st.title("📊 Cam Zayi Raporu - Saf ve Görünür Veri")
st.info("✅ Gizli satır/sütunlar silindi, birleştirmeler kaldırıldı ve mağaza isimleri sabitlendi.")

# Mağaza Kodları ve İsimleri
magaza_sozlugu = {
    "M38001": "KAYSERI PARK AVM", "M38002": "KAYSERI MEYSU OUTLET AVM",
    "M38003": "FORUM KAYSERI AVM", "M38004": "KAYSERI KUMSMALL AVM",
    "M38005": "KAYSERI TUNALIFE AVM", "M42001": "NOVADA KONYA OUTLET AVM",
    "M42002": "KONYA KENT PLAZA AVM", "M42004": "M1 KONYA AVM",
    "M42005": "KONYA KAZIMKARABEKIR CADDE", "M42006": "KONYA ENNTEPE AVM",
    "M51001": "NIGDE CADDE", "M51002": "NIGDE TEMA PARK AVM",
    "M68001": "AKSARAY NORA CITY AVM", "M40001": "KIRSEHIR CADDE",
    "M46001": "MARAS PIAZZA AVM", "M70001": "PARK KARAMAN AVM",
    "M50001": "NEVSEHIR NISSARA AVM"
}

uploaded_file = st.file_uploader("Orijinal Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        # 1. Dosyayı Yükle
        wb = openpyxl.load_workbook(uploaded_file, data_only=False)
        ws = wb.active

        # 2. TÜM GİZLİ SATIR VE SÜTUNLARI SİL
        # Gizli satırları temizle
        for row_idx in range(ws.max_row, 0, -1):
            if ws.row_dimensions[row_idx].hidden:
                ws.delete_rows(row_idx)
        
        # Gizli sütunları temizle
        for col_idx in range(ws.max_column, 0, -1):
            col_letter = openpyxl.utils.get_column_letter(col_idx)
            if ws.column_dimensions[col_letter].hidden:
                ws.delete_cols(col_idx)

        # 3. BİRLEŞTİRİLMİŞ HÜCRELERİ ÇÖZ (Unmerge)
        merged_ranges = list(ws.merged_cells.ranges)
        for m_range in merged_ranges:
            ws.unmerge_cells(str(m_range))

        # 4. GRUPLANDIRMA (OUTLINE) SEVİYELERİNİ SIFIRLA
        ws.sheet_format.outlineLevelRow = 0
        ws.sheet_format.outlineLevelCol = 0

        # 5. BAŞLIK TESPİTİ VE TEMİZLİK
        header_row, ub_col_idx = 1, 1
        found = False
        for r in range(1, 20):
            for c in range(1, 15):
                if "ÜST BIRIM" in str(ws.cell(r, c).value).upper():
                    header_row, ub_col_idx, found = r, c, True
                    break
            if found: break

        # Sol sütunları ve üst boşluğu sil (Üst Birim A1'e gelene kadar)
        if ub_col_idx > 1: ws.delete_cols(1, ub_col_idx - 1)
        if header_row > 1: ws.delete_rows(1, header_row - 1)
        header_row = 1

        # 6. MAĞAZALARI FİLTRELE VE İSİMLERİ YAZ
        max_row = ws.max_row
        for r in range(max_row, header_row, -1):
            m_kodu = str(ws.cell(r, 1).value).strip()
            
            if m_kodu in magaza_sozlugu:
                ws.cell(row=r, column=2).value = magaza_sozlugu[m_kodu]
            elif m_kodu != "None" and len(m_kodu) >= 5:
                ws.delete_rows(r)
            elif m_kodu == "None" or m_kodu == "":
                if r > header_row: ws.delete_rows(r)

        # 7. GÖRSEL AYARLAR (Başlıkları Düzenle)
        ws.row_dimensions[1].height = 60
        ws.column_dimensions['A'].width = 12
        ws.column_dimensions['B'].width = 30
        
        # Hizalamayı düzelt (Birleştirme kalktığı için bağımsız hücreleri ortala)
        for cell in ws[1]:
            cell.alignment = openpyxl.styles.Alignment(horizontal='center', vertical='center', wrapText=True)

        # 8. ÇIKTIYI HAZIRLA
        output = io.BytesIO()
        wb.save(output)
        
        st.success("✅ Gizli hücreler ve birleştirmeler temizlendi. Rapor hazır!")
        st.download_button(
            label="📥 Tam Temizlenmiş Excel'i İndir",
            data=output.getvalue(),
            file_name="Zayi_Raporu_Gizlisiz.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Hata: {e}")
