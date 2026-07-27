# 🚩 CAPTURE THE FLAG - CTF Framework v2.0.0

All-in-one CLI framework untuk membantu pemain **Capture The Flag (CTF)**.
Framework interaktif bergaya Metasploit dengan 90+ tools untuk berbagai kategori challenge.

> ⚠️ Tools ini digunakan untuk mempercepat proses analisis challenge CTF, bukan untuk menyerang sistem tanpa izin.

---

## ✨ Features

- 🖥️ **Interactive CLI** - Metasploit-style terminal dengan auto-completion & syntax highlighting
- 🔌 **Plugin System** - Tambahkan module baru cukup dengan menambah folder
- 🔐 **90+ Tools** - Crypto, Forensic, Reverse, PWN, Web, Stego, OSINT
- 🤖 **Automation** - Auto-detect challenge, pipeline workflow, batch processing
- 📊 **Report Generator** - HTML & Markdown reports
- 💾 **Session Management** - Save/load session
- 🎨 **Rich UI** - Colored tables, panels, progress bars

---

## 📦 Installation

### Requirements
- Python 3.10+
- WSL Ubuntu / Kali Linux (recommended)

### Install Dependencies

Di Kali Linux / Ubuntu modern:
```bash
pip3 install -r requirements.txt --break-system-packages
```
*Atau menggunakan virtual environment (`python3 -m venv venv && source venv/bin/activate`).*

### Run Framework
```bash
python3 main.py
```

---

## 🎮 Quick Start & Perintah Dasar

```
CTF > modules                    # List semua kategori module
CTF > use crypto                 # Lihat semua tools di kategori crypto
CTF > use crypto/base64          # Pilih tool Base64
CTF crypto(base64) > show options  # Lihat opsi tool yang aktif
CTF crypto(base64) > set DATA SGVsbG8gV29ybGQ=
CTF crypto(base64) > set MODE decode
CTF crypto(base64) > run         # Jalankan analisis / tool!
CTF crypto(base64) > back        # Kembali ke menu utama
CTF > search hash                # Cari tools berdasarkan kata kunci
CTF > exit                       # Keluar dari framework
```

---

## 💡 Contoh Penggunaan Nyata per Modul

Berikut adalah contoh skenario penggunaan praktis untuk masing-masing modul di soal CTF:

### 1. 🔍 Modul Forensic (File & Disk Analysis)
Skenario: Anda diberikan file `suspicious.png` atau file `dump.bin` dan dicurigai ada flag tersembunyi.

* **Cek Informasi Metadata (Exif):**
  ```
  CTF > use forensic/exiftool_wrapper
  CTF forensic(exiftool_wrapper) > set FILE /path/to/suspicious.png
  CTF forensic(exiftool_wrapper) > run
  ```

* **Cek Tipe File Asli (Magic Bytes):**
  ```
  CTF > use forensic/file_signature
  CTF forensic(file_signature) > set FILE /path/to/unknown_file
  CTF forensic(file_signature) > run
  ```

* **Bedah Structure Chunk PNG:**
  ```
  CTF > use forensic/png_chunk_parser
  CTF forensic(png_chunk_parser) > set FILE /path/to/challenge.png
  CTF forensic(png_chunk_parser) > run
  ```

* **Deteksi Data Tersembunyi Setelah EOF (End Of File):**
  ```
  CTF > use forensic/hidden_data
  CTF forensic(hidden_data) > set FILE /path/to/image.jpg
  CTF forensic(hidden_data) > run
  ```

* **Analisis Nilai Entropy File (Deteksi Enkripsi/Kompresi):**
  ```
  CTF > use forensic/entropy_analyzer
  CTF forensic(entropy_analyzer) > set FILE /path/to/dump.bin
  CTF forensic(entropy_analyzer) > run
  ```

---

### 2. 🔐 Modul Crypto (Sandi & Enkripsi)
Skenario: Anda mendapatkan ciphertext terenkripsi atau hash misterius.

* **Auto-Detect Enkripsi Berlapis:**
  ```
  CTF > use crypto/auto_detect
  CTF crypto(auto_detect) > set DATA VM1JMWVsbG9Xb3JsZA==
  CTF crypto(auto_detect) > run
  ```

* **Brute-force Caesar Cipher (Coba 26 Shift):**
  ```
  CTF > use crypto/caesar
  CTF crypto(caesar) > set DATA "KHOOR ZRUOG"
  CTF crypto(caesar) > set MODE bruteforce
  CTF crypto(caesar) > run
  ```

* **Single/Multi-byte XOR Brute-force:**
  ```
  CTF > use crypto/xor_tool
  CTF crypto(xor_tool) > set DATA 1c1b001a1e0b0e
  CTF crypto(xor_tool) > set MODE bruteforce
  CTF crypto(xor_tool) > run
  ```

* **RSA Factorization & Helper:**
  ```
  CTF > use crypto/rsa_helper
  CTF crypto(rsa_helper) > set N 143
  CTF crypto(rsa_helper) > set E 65537
  CTF crypto(rsa_helper) > set MODE factor
  CTF crypto(rsa_helper) > run
  ```

---

### 3. ⚙️ Modul Reverse Engineering (Analisis Binary)
Skenario: Diberikan binary Linux `chall` atau Windows `chall.exe`.

* **Membedah ELF Binary Header & Section:**
  ```
  CTF > use reverse/elf_parser
  CTF reverse(elf_parser) > set FILE ./chall
  CTF reverse(elf_parser) > run
  ```

* **Mencari Printable Strings dengan Filter Offset:**
  ```
  CTF > use reverse/strings_extractor
  CTF reverse(strings_extractor) > set FILE ./chall
  CTF reverse(strings_extractor) > set MIN_LENGTH 6
  CTF reverse(strings_extractor) > run
  ```

* **Mengekstrak Symbol & Function Table:**
  ```
  CTF > use reverse/symbol_parser
  CTF reverse(symbol_parser) > set FILE ./chall
  CTF reverse(symbol_parser) > run
  ```

---

### 4. 💥 Modul PWN (Binary Exploitation)
Skenario: Membedah binary soal pwn dan membuat script exploit buffer overflow.

* **Cek Proteksi Binary (NX, PIE, Canary, RELRO):**
  ```
  CTF > use pwn/checksec_wrapper
  CTF pwn(checksec_wrapper) > set FILE ./pwn_chall
  CTF pwn(checksec_wrapper) > run
  ```

* **Buat Pattern Buffer Overflow & Cari Crash Offset:**
  ```
  CTF > use pwn/cyclic_pattern
  CTF pwn(cyclic_pattern) > set LENGTH 200
  CTF pwn(cyclic_pattern) > run

  CTF > use pwn/cyclic_offset
  CTF pwn(cyclic_offset) > set VALUE 0x61616168
  CTF pwn(cyclic_offset) > run
  ```

* **Generate Template Script Pwntools Otomatis:**
  ```
  CTF > use pwn/pwntools_template
  CTF pwn(pwntools_template) > set BINARY ./pwn_chall
  CTF pwn(pwntools_template) > set HOST ctf.target.com
  CTF pwn(pwntools_template) > set PORT 1337
  CTF pwn(pwntools_template) > run
  ```

---

### 5. 🌐 Modul Web (Web Application Analysis)
Skenario: Inspeksi lalu lintas HTTP, token JWT, dan payload.

* **Decode & Analisis Structure JWT Token:**
  ```
  CTF > use web/jwt_decoder
  CTF web(jwt_decoder) > set TOKEN eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  CTF web(jwt_decoder) > run
  ```

* **Ekstraksi Elemen Tersembunyi dari HTML (Link, Comment, Hidden Form):**
  ```
  CTF > use web/html_parser
  CTF web(html_parser) > set DATA "<html><!-- flag{test} --></html>"
  CTF web(html_parser) > run
  ```

* **Format Raw Request ke Command Curl atau Script Python:**
  ```
  CTF > use web/request_formatter
  CTF web(request_formatter) > set DATA "GET /admin HTTP/1.1\r\nHost: target.com"
  CTF web(request_formatter) > set FORMAT curl
  CTF web(request_formatter) > run
  ```

---

### 6. 🖼️ Modul Stego (Steganography)
Skenario: Gambar mengandung rahasia di dalam bit tersembunyi.

* **Analisis Least Significant Bit (LSB):**
  ```
  CTF > use stego/lsb_analyzer
  CTF stego(lsb_analyzer) > set FILE /path/to/stego.png
  CTF stego(lsb_analyzer) > run
  ```

* **Bandingkan 2 Gambar Pixel-by-Pixel:**
  ```
  CTF > use stego/image_compare
  CTF stego(image_compare) > set FILE /path/to/img1.png
  CTF stego(image_compare) > set FILE2 /path/to/img2.png
  CTF stego(image_compare) > run
  ```

---

### 7. 👁️ Modul OSINT (Information Gathering)
Skenario: Pengumpulan informasi domain, sertifikat, atau email header.

* **Analisis Header Email (Tracing Pengirim):**
  ```
  CTF > use osint/email_header_parser
  CTF osint(email_header_parser) > set DATA "Received: from mail.example.com..."
  CTF osint(email_header_parser) > run
  ```

* **Inspeksi SSL/TLS Certificate:**
  ```
  CTF > use osint/cert_parser
  CTF osint(cert_parser) > set HOST google.com
  CTF osint(cert_parser) > run
  ```

---

### 8. 🤖 Modul Automation & Pipeline
Skenario: Bingung harus mulai dari mana saat mendapatkan file soal.

* **Auto-Detect Soal & Dapatkan Rekomendasi Tool:**
  ```
  CTF > use misc/auto_detect_challenge
  CTF misc(auto_detect_challenge) > set FILE /path/to/mystery_file
  CTF misc(auto_detect_challenge) > run
  ```

* **Rantai Perintah (Pipeline Workflow):**
  ```
  CTF > use misc/pipeline
  CTF misc(pipeline) > set PIPELINE "crypto/base64 -> crypto/hex"
  CTF misc(pipeline) > set DATA "SGVsbG8="
  CTF misc(pipeline) > run
  ```

* **Generate Laporan Analysis (Markdown/HTML):**
  ```
  CTF > use misc/report_generator
  CTF misc(report_generator) > set FORMAT html
  CTF misc(report_generator) > set OUTPUT my_ctf_report
  CTF misc(report_generator) > run
  ```

---

## 📁 Struktur Project

```
flag v2/
├── main.py                      # Entry point
├── requirements.txt             # Dependencies
├── setup.py                     # Package setup
├── config/
│   └── settings.yaml            # Configuration
├── core/                        # Framework core
│   ├── app.py                   # Application bootstrap
│   ├── cli.py                   # Interactive CLI
│   ├── command_handler.py       # Command routing
│   ├── base_tool.py             # Base class for tools
│   ├── registry.py              # Module registry
│   ├── plugin_manager.py        # Plugin auto-discovery
│   ├── ui.py                    # Rich UI components
│   └── ...
├── modules/
│   ├── crypto/      (22 tools)  # Encoding, ciphers, hashing
│   ├── forensic/    (16 tools)  # File analysis, carving
│   ├── reverse/     (12 tools)  # Binary analysis
│   ├── pwn/          (9 tools)  # Exploitation helpers
│   ├── web/         (13 tools)  # Web security analysis
│   ├── stego/        (8 tools)  # Steganography
│   ├── osint/        (6 tools)  # Open source intelligence
│   └── misc/         (7 tools)  # Automation & utilities
├── plugins/                     # Custom plugins
├── logs/                        # Log files
└── data/                        # Data files
```

---

## 🔌 Membuat Custom Plugin Baru

Buat file Python baru di dalam folder module, dan gunakan decorator `@register_tool`:

```python
# modules/crypto/my_tool.py
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class MyCustomTool(BaseTool):
    name = 'my_tool'
    category = 'crypto'
    description = 'Deskripsi tool kustom saya'
    tags = ['custom', 'crypto']

    def _setup_options(self):
        self.add_option('DATA', 'Input data', required=True)
        self.add_option('MODE', 'Operation mode', default='decode',
                       choices=['encode', 'decode'])

    def run(self) -> dict:
        data = self.get_option('DATA')
        mode = self.get_option('MODE')
        
        result = data.upper() if mode == 'encode' else data.lower()
        
        return {'status': 'success', 'result': result}
```

Tool baru akan otomatis terdeteksi saat framework dijalankan tanpa perlu merubah kode core!

---

## 📜 License

MIT License - For educational purposes only.
