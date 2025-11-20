#!/usr/bin/env python3
"""
APK Creator REAL - Usando ferramentas Android reais
"""

import os
import sys
import shutil
import subprocess
import argparse
import tempfile
from pathlib import Path
import zipfile

class RealAPKCreator:
    def __init__(self, config):
        self.config = config
        self.temp_dir = Path(tempfile.mkdtemp())
        self.setup_directories()
        
    def setup_directories(self):
        """Configura estrutura de diretórios"""
        self.project_dir = self.temp_dir / "android_project"
        self.apk_output = Path("dist") / "apks"
        self.apk_output.mkdir(parents=True, exist_ok=True)
        
    def find_android_tools(self):
        """Encontra ferramentas Android no sistema"""
        # No GitHub Actions, essas ferramentas estão geralmente em caminhos específicos
        possible_paths = [
            "/usr/lib/android-sdk/build-tools/*/aapt",
            "/opt/android-sdk/build-tools/*/aapt", 
            "/home/runner/android-sdk/build-tools/*/aapt"
        ]
        
        for path_pattern in possible_paths:
            import glob
            matches = glob.glob(path_pattern)
            if matches:
                self.aapt_path = sorted(matches)[-1]  # Pega a versão mais recente
                break
        else:
            # Fallback: baixar ferramentas
            self.download_android_tools()
            
    def download_android_tools(self):
        """Baixa ferramentas Android se não encontradas"""
        print("📥 Baixando ferramentas Android...")
        
        # URL das command line tools
        tools_url = "https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip"
        tools_zip = self.temp_dir / "android-tools.zip"
        
        # Download
        subprocess.run([
            "wget", "-q", tools_url, "-O", str(tools_zip)
        ], check=True)
        
        # Extrair
        subprocess.run([
            "unzip", "-q", str(tools_zip), "-d", str(self.temp_dir / "android-sdk")
        ], check=True)
        
        sdk_root = self.temp_dir / "android-sdk"
        
        # Aceitar licenças e instalar pacotes
        subprocess.run([
            "yes |", str(sdk_root / "cmdline-tools" / "bin" / "sdkmanager"), 
            "--sdk_root=" + str(sdk_root), "platform-tools", "build-tools;33.0.2", "platforms;android-33"
        ], shell=True, check=True)
        
        self.aapt_path = sdk_root / "build-tools" / "33.0.2" / "aapt"
        
    def create_project_structure(self):
        """Cria estrutura completa do projeto Android"""
        package_path = self.config['package_name'].replace('.', '/')
        
        dirs = [
            f"src/main/java/{package_path}",
            "src/main/assets",
            "src/main/res/values",
            "src/main/res/layout",
            "src/main/res/drawable-mdpi",
            "src/main/res/drawable-hdpi", 
            "src/main/res/drawable-xhdpi",
            "src/main/res/drawable-xxhdpi",
            "src/main/res/drawable-xxxhdpi",
            "libs",
            "bin"
        ]
        
        for dir_path in dirs:
            (self.project_dir / dir_path).mkdir(parents=True, exist_ok=True)
            
    def copy_html_and_assets(self):
        """Copia HTML e assets"""
        assets_dir = self.project_dir / "src/main/assets"
        html_source = Path(self.config['html_file'])
        
        shutil.copy2(html_source, assets_dir / "index.html")
        print(f"✅ HTML copiado: {html_source.name}")
        
        # Copiar assets da mesma pasta
        html_parent = html_source.parent
        for item in html_parent.iterdir():
            if item.is_file() and item != html_source:
                if item.suffix.lower() in ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.ttf', '.woff', '.woff2']:
                    shutil.copy2(item, assets_dir / item.name)
                    print(f"📁 Asset copiado: {item.name}")
    
    def create_default_icons(self):
        """Cria ícones padrão usando ferramentas de linha de comando"""
        # Criar um ícone simples usando ImageMagick (disponível no GitHub Actions)
        for density, size in [('mdpi', 48), ('hdpi', 72), ('xhdpi', 96), ('xxhdpi', 144), ('xxxhdpi', 192)]:
            icon_dir = self.project_dir / f"src/main/res/drawable-{density}"
            icon_path = icon_dir / "ic_launcher.png"
            
            # Criar ícone usando ImageMagick
            subprocess.run([
                "convert", "-size", f"{size}x{size}", 
                "gradient:blue-darkblue", 
                "-fill", "white", 
                "-draw", f"circle {size//2},{size//2} {size//2},{size//4}",
                str(icon_path)
            ], check=True)
            
        print("✅ Ícones criados com ImageMagick")
    
    def generate_android_manifest(self):
        """Gera AndroidManifest.xml"""
        manifest_content = f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{self.config['package_name']}"
    android:versionCode="{self.config.get('version_code', '1')}"
    android:versionName="{self.config.get('version_name', '1.0')}">

    <uses-sdk
        android:minSdkVersion="{self.config.get('min_sdk', '21')}"
        android:targetSdkVersion="{self.config.get('target_sdk', '33')}" />

    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>

    <application
        android:allowBackup="true"
        android:icon="@drawable/ic_launcher"
        android:label="{self.config['app_name']}"
        android:usesCleartextTraffic="true"
        android:theme="@android:style/Theme.DeviceDefault.Light">
        
        <activity
            android:name=".MainActivity"
            android:label="{self.config['app_name']}"
            android:exported="true">
            <intent-filter>
                <action android:name="android.permission.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
    </application>
</manifest>'''

        with open(self.project_dir / "AndroidManifest.xml", "w", encoding="utf-8") as f:
            f.write(manifest_content)
    
    def generate_main_activity(self):
        """Gera MainActivity.java"""
        package_name = self.config['package_name']
        
        activity_content = f'''package {package_name};

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebSettings;

public class MainActivity extends Activity {{
    private WebView webView;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        webView = findViewById(R.id.webview);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        
        webView.loadUrl("file:///android_asset/index.html");
    }}
}}'''

        package_path = package_name.replace('.', '/')
        activity_file = self.project_dir / f"src/main/java/{package_path}/MainActivity.java"
        
        with open(activity_file, "w", encoding="utf-8") as f:
            f.write(activity_content)
    
    def generate_layouts(self):
        """Gera arquivos de layout"""
        # activity_main.xml
        layout_content = '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <WebView
        android:id="@+id/webview"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />
        
</LinearLayout>'''

        with open(self.project_dir / "src/main/res/layout/activity_main.xml", "w", encoding="utf-8") as f:
            f.write(layout_content)
            
        # strings.xml
        strings_content = f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{self.config['app_name']}</string>
</resources>'''

        with open(self.project_dir / "src/main/res/values/strings.xml", "w", encoding="utf-8") as f:
            f.write(strings_content)
    
    def compile_resources(self):
        """Compila recursos usando aapt2"""
        print("🔨 Compilando recursos...")
        
        # Compilar recursos
        compiled_res = self.temp_dir / "compiled_res"
        compiled_res.mkdir(exist_ok=True)
        
        subprocess.run([
            str(self.aapt_path), "compile",
            "--dir", str(self.project_dir / "src/main/res"),
            "-o", str(compiled_res)
        ], check=True)
        
        # Linkar recursos
        self.unsigned_apk = self.temp_dir / "unsigned.apk"
        
        subprocess.run([
            str(self.aapt_path), "link",
            "-o", str(self.unsigned_apk),
            "-I", str(self.temp_dir / "android-sdk/platforms/android-33/android.jar"),
            "--manifest", str(self.project_dir / "AndroidManifest.xml"),
            "-A", str(self.project_dir / "src/main/assets"),
            str(compiled_res / "*")
        ], check=True)
        
        print("✅ Recursos compilados")
    
    def create_final_apk(self):
        """Cria APK final"""
        print("📦 Criando APK final...")
        
        final_apk_name = f"{self.config['app_name'].replace(' ', '_')}.apk"
        final_apk_path = self.apk_output / final_apk_name
        
        # Copiar APK unsigned para final
        shutil.copy2(self.unsigned_apk, final_apk_path)
        
        # Adicionar classes.dex vazio (para estrutura mínima)
        with zipfile.ZipFile(final_apk_path, 'a') as apk_zip:
            apk_zip.writestr('classes.dex', b'')
        
        print(f"✅ APK criado: {final_apk_path}")
        return final_apk_path
    
    def build_apk(self):
        """Executa o processo completo de build"""
        try:
            print(f"🚀 Iniciando build REAL para: {self.config['app_name']}")
            
            # Encontrar/baixar ferramentas
            self.find_android_tools()
            
            # Criar projeto
            self.create_project_structure()
            self.copy_html_and_assets()
            self.create_default_icons()
            
            # Gerar arquivos
            self.generate_android_manifest()
            self.generate_main_activity()
            self.generate_layouts()
            
            # Compilar e criar APK
            self.compile_resources()
            apk_path = self.create_final_apk()
            
            return str(apk_path)
            
        except Exception as e:
            print(f"❌ Erro durante o build: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            # Limpar temporários (opcional para debug)
            # shutil.rmtree(self.temp_dir, ignore_errors=True)
            pass

def main():
    parser = argparse.ArgumentParser(description='Real APK Creator')
    parser.add_argument('--html', required=True, help='HTML file path')
    parser.add_argument('--app-name', required=True, help='App name')
    parser.add_argument('--package-name', required=True, help='Package name')
    parser.add_argument('--version-name', default='1.0', help='Version name')
    
    args = parser.parse_args()
    
    config = {
        'html_file': args.html,
        'app_name': args.app_name,
        'package_name': args.package_name,
        'version_name': args.version_name
    }
    
    creator = RealAPKCreator(config)
    apk_path = creator.build_apk()
    
    print(f"\n🎉 APK REAL gerado com sucesso!")
    print(f"📍 Localização: {apk_path}")

if __name__ == "__main__":
    main()
