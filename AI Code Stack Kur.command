#!/usr/bin/env bash
# Double-click launcher for macOS. Thin wrapper: delegates to install.sh / global-install.sh.
set -uo pipefail
ROOT="$(cd "${BASH_SOURCE[0]%/*}" && pwd)"
cd "$ROOT"

echo "=== AI Code Stack kurulumu ==="
echo "Depo: $ROOT"
echo

echo "--- 1/2: Repo-local kurulum (manifests + adapters) ---"
if ! ./install.sh; then
  echo
  echo "HATA: repo-local kurulum başarısız oldu. Yukarıdaki çıktıyı kontrol et."
  read -r -p "Kapatmak için Enter'a bas..." _
  exit 1
fi

echo
echo "--- 2/2: Global kurulum (Codex / Claude Code / Cursor) ---"
echo "Bu adım sadece bu bilgisayarda kurulu olan platformlara, sadece bu araç tarafından"
echo "üretilmiş dosyaları yazar. Elle yazdığın mevcut dosyaların üzerine asla yazmaz."
echo
read -r -p "Global kurulumu şimdi uygula? [e/H] " REPLY
case "$REPLY" in
  [eE]*)
    ./global-install.sh --apply
    ;;
  *)
    echo "Global kurulum atlandı. İstediğinde: ./global-install.sh --apply"
    ;;
esac

echo
echo "=== Bitti ==="
read -r -p "Kapatmak için Enter'a bas..." _
