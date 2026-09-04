# Toolshed CLI

Toolshed adalah CLI open source untuk developer sehari-hari — berisi kumpulan perintah cepat seputar **git** dan **manajemen file lokal**, dibangun dengan Python + [Click](https://click.palletsprojects.com/).

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
