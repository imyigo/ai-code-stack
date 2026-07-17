#!/usr/bin/env bash
# Double-click launcher for macOS. Thin wrapper: delegates to install.sh / global-install.sh / replace-skills.sh.
set -uo pipefail
ROOT="$(cd "${BASH_SOURCE[0]%/*}" && pwd)"
cd "$ROOT"

echo "=== AI Code Stack kurulumu ==="
echo "Depo: $ROOT"
echo

echo "--- 1/3: Repo-local kurulum (manifests + adapters, eksik submodule fetch) ---"
if ! ./install.sh; then
  echo
  echo "HATA: repo-local kurulum başarısız oldu. Yukarıdaki çıktıyı kontrol et."
  read -r -p "Kapatmak için Enter'a bas..." _
  exit 1
fi

echo
echo "--- 2/3: Global config (Codex AGENTS.md/MCP, Claude Code agent'ları, Cursor kuralı) ---"
echo "Bu adım sadece bu bilgisayarda kurulu olan platformlara, sadece bu araç tarafından"
echo "üretilmiş dosyaları yazar. Elle yazdığın mevcut dosyaların üzerine asla yazmaz."
echo
read -r -p "Global config'i şimdi uygula? [e/H] " REPLY
case "$REPLY" in
  [eE]*) ./global-install.sh --apply ;;
  *) echo "Atlandı. İstediğinde: ./global-install.sh --apply" ;;
esac

echo
echo "--- 3/3: Skill'leri değiştir (~/.claude/skills, ~/.codex/skills) ---"
echo "DİKKAT: mevcut skills/ klasörü SİLİNMEZ, kenara taşınır (skills.backup-<tarih>),"
echo "ardından bu repodaki skill setiyle TAMAMEN değiştirilir. Önce plan:"
echo
./replace-skills.sh
echo
read -r -p "Skill'leri yukarıdaki plana göre değiştir? [e/H] " REPLY
case "$REPLY" in
  [eE]*) ./replace-skills.sh --apply ;;
  *) echo "Atlandı. İstediğinde: ./replace-skills.sh --apply" ;;
esac

echo
echo "=== Bitti ==="
read -r -p "Kapatmak için Enter'a bas..." _
