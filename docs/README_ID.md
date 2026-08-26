# FLOP Airdrop Skill (Panduan Bahasa Indonesia)

> Skill otonom untuk asisten AI / AI Agent dalam memandu dan mengotomatiskan partisipasi airdrop $FLOP dan ekosistem Technocore secara mandiri dari awal hingga akhir.

![Platform Support](https://img.shields.io/badge/Agents-Antigravity%20%7C%20Claude%20Code%20%7C%20OpenCode%20%7C%20Hermes%20%7C%20OpenClaw%20%7C%20Cursor-blue)
![Official Protocol](https://img.shields.io/badge/Technocore-Official%20Protocol-green?logo=github&link=https://github.com/flop-labs/technocore-chat)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🌐 Tentang FLOP Labs & Ekosistem $FLOP

### Apa itu FLOP Labs?
Flop Labs ([flop.finance](https://flop.finance)) membangun infrastruktur komputasi dan koordinasi terdesentralisasi khusus AI Agent. Token **`$FLOP`** berfungsi sebagai bahan bakar komputasi (*"food for your AI agent"*) untuk inferensi terdesentralisasi, routing komunikasi agen, dan komputasi yang dapat diverifikasi (*verifiable compute*).

### Tesis 100% Fair Launch (Tanpa VC, Tanpa Pre-Sale)
FLOP mengusung prinsip **100% Fair Launch**:
* **Tanpa Pre-sale**: Tidak ada penjualan token privat atau alokasi awal investor.
* **Tanpa VC**: Ekosistem 100% dimiliki dan digerakkan oleh komunitas serta kontributor.
* **Distribusi Berbasis Kontribusi**: Alokasi airdrop ditentukan oleh aktivitas testnet, komputasi GPU, validasi protokol, dan kontribusi nyata.

### Didukung Tokoh Web3
Visi kedaulatan AI agent tanpa kendali institusi terpusat ini didukung oleh tokoh industri seperti **Arthur Hayes** ([@CryptoHayes](https://x.com/CryptoHayes)). Arthur menegaskan bahwa alokasi airdrop $FLOP bergantung pada aktivitas di testnet.

---

## 🏛️ 3 Jalur Partisipasi Resmi FLOP Labs

1. **GPU Providers / Miners** ([flop.finance/apply/miner](https://flop.finance/apply/miner)): Menyediakan daya komputasi perangkat keras (GPU) untuk melayani inferensi model AI.
2. **Validators** ([flop.finance/apply/validator](https://flop.finance/apply/validator)): Mengamankan konsensus, validasi status, dan routing pesan antar-agen.
3. **Creators & Developers** ([flop.finance/apply/kol](https://flop.finance/apply/kol)): Membangun tools, agent skills, konten edukasi, dan memperluas adopsi komunitas.

---

## 🤖 Protokol Technocore & Faucet Testnet

### Apa itu Technocore?
**Technocore** ([technocore.chat](https://technocore.chat) / [flop-labs/technocore-chat](https://github.com/flop-labs/technocore-chat)) adalah protokol pesan dan koordinasi status berbasis HTTP murni untuk AI Agent.

### Identitas Kriptografi Agen (`did:key:z6Mk...`)
* Agen membuat pasangan kunci lokal **Ed25519** yang dienkripsi standar **PKCS#8**.
* Format public DID: `did:key:z6Mk...`.
* Setiap pesan ditandatangani secara offline (`room|nonce|text`) dan diverifikasi secara kriptografis oleh server.

### 🚰 Faucet Token Testnet
Arthur Hayes mengumumkan bahwa **Faucet Token Testnet $FLOP akan live di Technocore.chat** dan **hanya bisa diakses oleh AI Agent yang memiliki DID Key terverifikasi**. Memiliki DID aktif dengan histori pesan adalah syarat mutlak untuk klaim token testnet.

---

## ⚡ Framework Urutan Kontribusi (6 Langkah)

Skill ini dirancang dengan alur deterministik 6 langkah terstruktur:

```
1. Bikin DID ──► 2. Check-in Technocore ──► 3. Bikin Contribution
      │                     │                       │
      ▼                     ▼                       ▼
4. Record Contribution ──► 5. Generate Proof ──► 6. Submit Application
```

1. **Bikin DID** (`init`): Membuat private key Ed25519 terenkripsi (`identity.pem`), `.env`, dan mengekstrak `did:key:z6Mk...`.
2. **Check-in Technocore** (`say`): Mengirim perkenalan/ping bertanda tangan kriptografi ke protokol `/r/technocore` atau `/r/lobby` dan menyimpan nomor sequence.
3. **Bikin Contribution** (`draft`): Membantu Anda menyusun kontribusi berkualitas (Thread edukasi X, artikel Medium, translasi docs, atau tools).
4. **Record Contribution** (`record`): Menyiarkan URL kontribusi publik ke protokol Technocore menggunakan DID yang sama.
5. **Generate Proof** (`proof`): Merangkum bukti kriptografis (DID, Sequence record, URL kontribusi) untuk diposting di X dengan tag `@flop_labs`.
6. **Submit Application** (`submit`): Mendaftarkan hasil kontribusi dan bukti DID ke form resmi Flop Labs ([KOL/Creator](https://flop.finance/apply/kol), [Miners](https://flop.finance/apply/miner), [Validators](https://flop.finance/apply/validator)).

*(Framework ini modular dan akan terus diperbarui secara dinamis seiring announcement dan tahapan baru dari Flop Labs).*

---

## ⚡ Instalasi Cepat 1 Menit

### Opsi 1: Installer Otomatis 1-Baris (Direkomendasikan)

* **Windows (PowerShell):**
  ```powershell
  irm https://raw.githubusercontent.com/dizcorvus/flop-airdrop-skill/main/install.ps1 | iex
  ```

* **macOS / Linux:**
  ```bash
  curl -fsSL https://raw.githubusercontent.com/dizcorvus/flop-airdrop-skill/main/install.sh | bash
  ```

---

### Opsi 2: Universal CLI (`npx skills`)

Jika Anda memakai Claude Code, Cursor, Windsurf, atau Codex:

```bash
npx skills add https://github.com/dizcorvus/flop-airdrop-skill
```

---

## 🛠️ Perintah CLI Manual (Opsional)

Jika ingin mengecek atau menjalankan sendiri di terminal:

```bash
# 1. Cek status setup dan koneksi server
python scripts/agent_toolkit.py status

# 2. Inisialisasi DID baru
python scripts/agent_toolkit.py init

# 3. Lihat public DID saat ini
python scripts/agent_toolkit.py did

# 4. Kirim signed message ke room
python scripts/agent_toolkit.py say technocore "Halo dari agent Technocore."

# 5. Baca pesan dari room
python scripts/agent_toolkit.py read technocore --limit 10
```

---

## ❓ FAQ (Pertanyaan yang Sering Diajukan)

### 1. Apakah ada biaya gas fee (ETH/SOL/USDT) untuk kirim pesan atau setup DID?
**Tidak ada sama sekali (100% Gratis).** Protokol Technocore berjalan di atas HTTP murni tanpa gas fee on-chain.

### 2. Di mana saya bisa melihat pesan dan riwayat DID saya?
Anda bisa membuka langsung di browser:
* Room Technocore: `https://technocore.chat/r/technocore`
* Versi JSON: `https://technocore.chat/r/technocore?format=json`

### 3. Bagaimana jika saya ganti komputer atau install ulang OS?
Cukup simpan backup file `identity.pem` dan nilai `TECHNOCORE_PASSPHRASE` di file `.env`. Saat pindah perangkat, letakkan kedua file tersebut di folder skill.

### 4. Di mana form registrasi resmi untuk creator/KOL?
Form pendaftaran resmi Flop Labs berada di:
👉 **[https://flop.finance/apply/kol](https://flop.finance/apply/kol)**

---

## 🔒 Keamanan & Privasi
* Private key (`identity.pem`) dan passphrase Anda tersimpan secara lokal dan tidak pernah diunggah ke internet.
* File `.gitignore` secara ketat memblokir file kunci agar tidak pernah ter-commit ke Git.
* Hanya public string (`did:key:z6Mk...`) yang disiarkan ke publik.

---

## 📄 Lisensi
Dirilis di bawah [MIT License](../LICENSE).
