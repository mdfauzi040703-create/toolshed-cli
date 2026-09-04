# Toolshed CLI

**Toolshed** adalah CLI open source yang mempercepat pekerjaan berulang seorang developer — hal-hal kecil yang biasanya diketik manual setiap hari, sekarang jadi satu perintah pendek.

Dibagi 2 kelompok:
- **`toolshed git ...`** — ringkas status repo, commit + push sekaligus, bersihkan branch yang sudah merged, batalkan commit terakhir, lihat daftar stash.
- **`toolshed files ...`** — cari file terbesar, bersihkan junk (`__pycache__`, `node_modules`, dll), cari & hapus file duplikat berdasarkan isi, rename banyak file sekaligus pakai pola, dan lihat struktur folder.

Contoh cepat:

```bash
toolshed git quick-commit "fix bug login" --push   # add + commit + push, satu baris
toolshed files clean-junk . --apply                # bersihkan sampah __pycache__, node_modules, dll
toolshed files dedupe .                             # cari file kembar berdasarkan isi, bukan cuma nama
```

Dibangun dengan Python + [Click](https://click.palletsprojects.com/).

## Instalasi

```bash
git clone https://github.com/yourusername/toolshed-cli.git
cd toolshed-cli
pip install -e ".[dev]"
```

Setelah terpasang, perintah `toolshed` akan tersedia di terminal.

## Perintah

### Git helper

```bash
toolshed git summary                 # ringkasan branch, perubahan, commit terakhir
toolshed git quick-commit "pesan"    # add semua perubahan + commit
toolshed git quick-commit "pesan" --push
toolshed git clean-branches          # preview branch lokal yang sudah merged
toolshed git clean-branches --apply  # hapus beneran
toolshed git undo                    # batalkan commit terakhir, perubahan tetap ada (staged)
toolshed git undo --hard             # batalkan commit terakhir SEKALIGUS buang perubahannya
toolshed git stash-list              # tampilkan semua stash dalam tabel ringkas
```

### File manager

```bash
toolshed files largest .                 # 10 file terbesar di direktori saat ini
toolshed files largest . -n 20
toolshed files clean-junk .              # preview __pycache__, node_modules, dll
toolshed files clean-junk . --apply      # hapus beneran
toolshed files tree . --depth 3          # struktur direktori
toolshed files dedupe .                  # preview file duplikat berdasarkan isi (hash)
toolshed files dedupe . --apply          # hapus duplikat, 1 salinan tetap disimpan per grup

# rename banyak file sekaligus pakai regex
toolshed files rename-bulk . --match "IMG_(\d+)\.jpg" --to "photo_\1.jpg"
toolshed files rename-bulk . --match "IMG_(\d+)\.jpg" --to "photo_\1.jpg" --apply
toolshed files rename-bulk . --match "IMG_(\d+)\.jpg" --to "photo_\1.jpg" --apply --recursive
```

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
```

## Kontribusi

Pull request dan issue sangat diterima. Ikuti langkah standar:

1. Fork repo ini
2. Buat branch fitur (`git checkout -b fitur-baru`)
3. Commit perubahan
4. Push dan buka Pull Request

## Lisensi

MIT — lihat file [LICENSE](LICENSE).
