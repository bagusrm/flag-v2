# 🚩 CAPTURE THE FLAG - CTF Framework v2.0.0

All-in-one CLI framework untuk membantu pemain **Capture The Flag (CTF)**.
Framework interaktif bergaya Metasploit dengan 90+ tools untuk berbagai kategori challenge.

> ⚠️ Tools ini digunakan untuk mempercepat proses analisis challenge CTF, bukan untuk menyerang sistem tanpa izin.

---

## ✨ Features

- 🖥️ **Interactive CLI** - Metasploit-style terminal dengan auto-completion
- 🔌 **Plugin System** - Tambahkan module baru cukup dengan menambah folder
- 🔐 **90+ Tools** - Crypto, Forensic, Reverse, PWN, Web, Stego, OSINT
- 🤖 **Automation** - Auto-detect challenge, pipeline workflow, batch processing
- 📊 **Report Generator** - HTML & Markdown reports
- 💾 **Session Management** - Save/load session
- 🎨 **Rich UI** - Colored tables, panels, progress bars

## 📦 Installation

### Requirements
- Python 3.10+
- WSL Ubuntu / Kali Linux (recommended)

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run
```bash
python main.py
```

## 🎮 Quick Start

```
CTF > modules                    # List all categories
CTF > use crypto                 # Show crypto tools
CTF > use crypto/base64          # Select Base64 tool
CTF crypto(base64) > show options  # Show tool options
CTF crypto(base64) > set DATA SGVsbG8gV29ybGQ=
CTF crypto(base64) > set MODE decode
CTF crypto(base64) > run         # Execute!
CTF crypto(base64) > back        # Back to main
CTF > search hash                # Search tools
CTF > exit                       # Exit
```

## 📁 Project Structure

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

## 🔧 Commands

| Command | Description |
|---------|-------------|
| `help` | Show help information |
| `modules` | List all module categories |
| `search <keyword>` | Search for tools |
| `use <category/tool>` | Select a tool |
| `info` | Show tool information |
| `show options` | Show tool options |
| `set <option> <value>` | Set option value |
| `run` | Execute current tool |
| `back` | Deselect current tool |
| `history` | Show command history |
| `save [name]` | Save current session |
| `load <name>` | Load saved session |
| `clear` | Clear screen |
| `version` | Show version |
| `exit` | Exit framework |

## 🔐 Module: Crypto (22 tools)

Base16, Base32, Base58, Base64, Base85, Hex, Binary, ROT13, Caesar, Vigenere,
XOR, AES Helper, RSA Helper, Bacon, Morse, Rail Fence, Affine,
Frequency Analysis, Hash Identifier, MD5, SHA, Auto Detect Encoding

## 🔍 Module: Forensic (16 tools)

Exiftool Wrapper, Strings, Binwalk, Foremost, Hidden Data Detector,
Entropy Analyzer, Metadata Extractor, File Signature, Magic Bytes,
Steganography Helper, PNG Chunk Parser, ZIP Analyzer, PDF Analyzer,
Image Analyzer, Audio Analyzer, Recursive Extraction

## ⚙️ Module: Reverse (12 tools)

ELF Parser, PE Parser, Strings Extractor, Disassembler Helper,
Opcode Viewer, Section Viewer, Symbol Parser, Import/Export Parser,
Hex Viewer, Assembly Helper, Ghidra Helper, Radare2 Helper

## 💥 Module: PWN (9 tools)

Checksec Wrapper, Cyclic Pattern, Cyclic Offset, ROP Gadget Finder,
ELF Info, Libc Helper, Shellcode Viewer, Pwntools Template, Exploit Template

## 🌐 Module: Web (13 tools)

JWT Decoder, JWT Inspector, Cookie Parser, Header Analyzer,
Request Formatter, Response Beautifier, HTML Parser, JS Beautifier,
Robots.txt Parser, Sitemap Parser, URL Decoder, SQL Encoder, XSS Encoder

## 🖼️ Module: Stego (8 tools)

PNGCheck, Zsteg Wrapper, Stegsolve Helper, LSB Analyzer,
QR Decoder, Barcode Reader, Image Compare, Color Channel Splitter

## 👁️ Module: OSINT (6 tools)

WHOIS Lookup, DNS Lookup, Certificate Parser, Email Header Parser,
Metadata Extractor, IP Information

## 🤖 Module: Automation (7 tools)

Auto Detect Challenge, Auto Identify Encoding, Auto Identify File Type,
Auto Recommend Tools, Pipeline Workflow, Batch Processor, Report Generator

## 🔌 Creating Custom Plugins

Buat tool baru dengan membuat file Python di dalam folder module:

```python
# modules/crypto/my_tool.py
from core.base_tool import BaseTool, register_tool
from core.exceptions import ExecutionError

@register_tool
class MyCustomTool(BaseTool):
    name = 'my_tool'
    category = 'crypto'
    description = 'My custom tool description'
    tags = ['custom', 'crypto']

    def _setup_options(self):
        self.add_option('DATA', 'Input data', required=True)
        self.add_option('MODE', 'Operation mode', default='decode',
                       choices=['encode', 'decode'])

    def run(self) -> dict:
        data = self.get_option('DATA')
        mode = self.get_option('MODE')
        
        # Your logic here
        result = data.upper() if mode == 'encode' else data.lower()
        
        return {'status': 'success', 'result': result}
```

Tool akan otomatis terdeteksi saat framework dijalankan.

## 📜 License

MIT License - For educational purposes only.
