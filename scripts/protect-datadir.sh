#!/usr/bin/env bash
# datadir/ is not encrypted by the platform.
# Encrypt an archive with age, or place the directory on a LUKS volume,
# before it leaves the research host. This helper fails closed when age
# is absent. It does not encrypt the directory by itself.
set -euo pipefail

TARGET="${1:-datadir}"

if ! command -v age >/dev/null 2>&1; then
  echo "age is not installed. ${TARGET} is not encrypted." >&2
  echo "Create a LUKS volume for the data directory, or install age and encrypt an archive:" >&2
  echo "  tar -C \"\$(dirname \"${TARGET}\")\" -cf - \"\$(basename \"${TARGET}\")\" | age -r <recipient> -o ${TARGET}.tar.age" >&2
  exit 1
fi

echo "age is available. ${TARGET} is still plaintext until you encrypt an archive or mount it on LUKS." >&2
echo "Example: tar -C \"\$(dirname \"${TARGET}\")\" -cf - \"\$(basename \"${TARGET}\")\" | age -r <recipient> -o ${TARGET}.tar.age" >&2
exit 0
