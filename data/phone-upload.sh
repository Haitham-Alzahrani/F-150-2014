#!/data/data/com.termux/files/usr/bin/bash
#
# Bulk-upload screenshots from an Android phone into the repo.
# Run this in TERMUX (not inside proot Debian - Termux has the storage access).
#
#   bash data/phone-upload.sh                 # everything from today
#   bash data/phone-upload.sh 2026-09-05      # everything from that date
#   bash data/phone-upload.sh 2026-09-05 idle # ... and tag them 'idle'
#
set -euo pipefail

REPO="${REPO:-$HOME/F-150-2014}"
SINCE="${1:-$(date +%Y-%m-%d)}"
TAG="${2:-}"
INBOX="$REPO/data/screenshots/inbox"

echo "==> repo   $REPO"
echo "==> since  $SINCE"
[ -n "$TAG" ] && echo "==> tag    $TAG"

if [ ! -d "$REPO" ]; then
  echo "Repo not found at $REPO"
  echo "Clone it first:"
  echo "  git clone https://github.com/Haitham-Alzahrani/F-150-2014.git \"$REPO\""
  exit 1
fi

# Termux needs storage permission once: termux-setup-storage
for d in "$HOME/storage/pictures/Screenshots" \
         /sdcard/Pictures/Screenshots \
         /sdcard/DCIM/Screenshots \
         "$HOME/storage/dcim/Screenshots"; do
  [ -d "$d" ] && SHOTS="$d" && break
done

if [ -z "${SHOTS:-}" ]; then
  echo "Could not find the screenshots folder."
  echo "Run 'termux-setup-storage' first, then check where your phone puts them:"
  echo "  ls ~/storage/pictures/"
  exit 1
fi
echo "==> source $SHOTS"

mkdir -p "$INBOX"
n=0
while IFS= read -r -d '' f; do
  base="$(basename "$f")"
  dest="$INBOX/${TAG:+${TAG}_}$base"
  cp -n "$f" "$dest" && n=$((n+1))
done < <(find "$SHOTS" -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) \
           -newermt "$SINCE" -print0)

echo "==> copied $n file(s) into data/screenshots/inbox/"
[ "$n" -eq 0 ] && { echo "Nothing new. Done."; exit 0; }

cd "$REPO"
git add data/screenshots/inbox
git commit -q -m "Add $n screenshot(s) from the phone, captured on or after $SINCE${TAG:+ (tag: $TAG)}

Uploaded from the phone into the inbox for filing. The condition each capture
was taken under is not recoverable from the file and must be stated separately."
echo "==> committed. Pushing..."
git push origin HEAD
echo
echo "Done. Now tell Claude what condition these were taken under:"
echo "  gear (P/N/D/R), load (idle / held rpm / cruise), warm or cold, A/C on or off."
