import requests
from bs4 import BeautifulSoup
import urllib3
from urllib.parse import urljoin

# Menonaktifkan peringatan SSL Insecure
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URL Target
base_url = "https://ahgary.com"
url = "https://ahgary.com/category/jav-sub-indo/"

# Header diperketat agar lebih mirip browser asli dan menghindari blokir basah
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.google.com/"
}

try:
    print("Sedang mengambil data dari web... Mohon tunggu.")
    response = requests.get(url, headers=headers, verify=False, timeout=15)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Mengambil semua tag <a> yang punya href
        items = soup.find_all('a', href=True)
        
        print(f"\n{'Judul Film':<50} | {'Link Video':<60} | {'Link Thumbnail'}")
        print("-" * 160)
        
        scraped_links = set()
        count = 0
        
        for item in items:
            href = item['href'].strip()
            
            # Skip jika link kosong, link janggal, atau mengarah ke halaman kategori/tag/page tersendiri
            if not href or href.startswith('#') or 'javascript:' in href or '/category/' in href or '/tag/' in href or '/page/' in href:
                continue
                
            # Gunakan urljoin untuk menggabungkan URL relatif dengan aman (mencegah double slash hancur)
            video_url = urljoin(base_url, href)
            
            # Memastikan kita tidak mengambil URL utama ahgary.com saja
            if video_url == base_url or video_url == base_url + "/":
                continue
            
            if video_url not in scraped_links:
                # Cari tag gambar di dalam atau di sekitar elemen link ini
                img_tag = item.find('img')
                img_url = "Thumbnail tidak ditemukan"
                
                if img_tag:
                    # Ambil dari data-src (lazy load) atau src biasa
                    raw_img = img_tag.get('data-src') or img_tag.get('data-lazy-src') or img_tag.get('src')
                    if raw_img:
                        img_url = urljoin(base_url, raw_img)
                
                # Mengambil judul film dari alt gambar atau text link
                title = item.get('title') or (img_tag.get('alt') if img_tag else None) or item.text.strip()
                title = " ".join(title.split()) if title else "Video Konten"
                
                # Batasi hanya memproses link yang tampaknya seperti postingan film tunggal
                # Ciri-cirinya biasanya mengandung karakter judul atau tidak berakhir dengan ekstensi aneh
                scraped_links.add(video_url)
                count += 1
                
                # Merapikan tampilan judul agar tidak merusak kolom
                display_title = title[:47] + "..." if len(title) > 47 else title
                print(f"{display_title:<50} | {video_url:<60} | {img_url}")
                
        if count == 0:
            print("\n[!] Tidak ada video yang berhasil di-parsing. Kemungkinan halaman diblokir oleh Cloudflare/Proteksi Bot.")
            print("Saran: Gunakan library 'cloudscraper' menggantikan 'requests'.")
            
    else:
        print(f"Gagal mengakses situs. Status Code: {response.status_code}")
        if response.status_code in [403, 503]:
            print("Akses ditolak (Forbidden/Cloudflare). Website mendeteksi script sebagai Bot.")

except Exception as e:
    print(f"Terjadi kesalahan: {e}")