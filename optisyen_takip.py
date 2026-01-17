import streamlit as st
import openpyxl
import io

st.set_page_config(page_title="Zayi Raporu - Hassas Düzenleyici", layout="centered")

st.title("📊 Cam Zayi Raporu - Görsel Onarıcı")
st.info("Mavi alanlar küçültüldü, üst boşluklar silindi ve sadece seçili mağazalar bırakıldı.")

# Görselde paylaştığınız tam mağaza listesi
istenen_magazalar = [
    "M38003", "M51001", "M42004", "M51002", "M38001", "M38005", 
    "M68001", "M42006", "M42002", "M46001", "M38002", "M42001", 
    "M40001", "M42005", "M38004", "M70001", "M50001"
]

uploaded_file = st.file_uploader("Orijinal Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        # 1. Dosyayı Biçimleri Koruyarak Yükle
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

        # 3. İLK İKİ SÜTUNU SİL (Bölge ve Müdür sütunları)
        # Sütun silerken birleştirilmiş hücrelere dikkat eder
        ws.delete_cols(1, 2)
        ub_col_idx -= 2 # Sütun kaydırması

        # 4. ÜSTTEKİ BOŞ SATIRLARI SİL
        # Başlık satırının üstündeki her şeyi temizler
        if header_row > 1:
            ws.delete_rows(1, header_row - 1)
            header_row = 1 # Artık başlık 1. satırda

        # 5. MAVİ BAŞLIK ALANINI KÜÇÜLT (Satır Yüksekliği Ayarı)
        # Başlık satırının yüksekliğini daraltarak alanı küçültüyoruz
        ws.row_dimensions[1].height = 40 # Örn: 40 birim (Varsayılandan daha dar)

        # 6. MAĞAZALARI FİLTRELE (İstenmeyenleri Sil)
        # Veri satırlarından başlayarak aşağıya doğru istenmeyenleri siliyoruz
        max_row = ws.max_row
        for r in range(max_row, header_row, -1):
            m_kodu = str(ws.cell(r, ub_col_idx).value).strip()
            # Eğer hücre boşsa veya mağaza listemizde yoksa satırı sil
            if m_kodu not in istenen_magazalar:
                ws.delete_rows(r)

        # 7. ÇIKTIYI HAZIRLA
        output = io.BytesIO()
        wb.save(output)
        
        st.success(f"✅ İşlem tamamlandı. {len(istenen_magazalar)} Mağaza için rapor hazır.")
        
        st.download_button(
            label="📥 Onarılmış ve Daraltılmış Excel'i İndir",
            data=output.getvalue(),
            file_name="Zayi_Raporu_Final.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")
