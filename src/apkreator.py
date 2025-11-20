#!/usr/bin/env python3
"""
APK Creator Simples - Apenas para compatibilidade
"""

import os
import sys
import json
from pathlib import Path

def main():
    # Apenas cria um arquivo de build info para compatibilidade
    build_info = {
        "status": "success",
        "message": "APK criado via script shell",
        "app_name": sys.argv[2] if len(sys.argv) > 2 else "MyApp",
        "package_name": sys.argv[3] if len(sys.argv) > 3 else "com.example.app"
    }
    
    # Criar diretório de saída
    output_dir = sys.argv[5] if len(sys.argv) > 5 else "dist"
    Path(output_dir).mkdir(exist_ok=True)
    
    # Salvar info do build
    with open(Path(output_dir) / "build-info.json", "w") as f:
        json.dump(build_info, f, indent=2)
    
    print("✅ Build info criada")
    print(f"📱 App: {build_info['app_name']}")
    print(f"📦 Package: {build_info['package_name']}")

if __name__ == "__main__":
    main()
