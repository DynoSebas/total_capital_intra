#!/usr/bin/env python3
"""Genera un hash bcrypt para usar en credentials.yaml."""

import sys

try:
    import streamlit_authenticator as stauth
except ImportError:
    print("Instala streamlit-authenticator: pip install streamlit-authenticator")
    sys.exit(1)

if len(sys.argv) < 2:
    print("Uso: python scripts/generate_password_hash.py TU_CONTRASEÑA")
    print("Ejemplo: python scripts/generate_password_hash.py MiPass123")
    sys.exit(1)

password = sys.argv[1]
hashed = stauth.Hasher().hash(password)
print(f"\nHash generado (copia en credentials.yaml):\n{hashed}\n")
