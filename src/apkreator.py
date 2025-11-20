#!/usr/bin/env python3
"""
APK Creator - Universal HTML to APK Converter
Versão para GitHub Actions
"""

import os
import sys
import shutil
import zipfile
import subprocess
import argparse
import tempfile
from pathlib import Path
import json

try:
    from PIL import Image, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("⚠ PIL não disponível - ícones serão copiados diretamente")

class UniversalAPKCreator:
    def __init__(self, config):
        self.config = config
        self.setup_directories()
        
    def setup_directories(self):
        """Configura estrutura de diretórios"""
        self.base_dir = Path(self.config.get('output_dir', 'dist'))
        self.build_dir = self.base_dir / "build"
        self.apk_output = self.base_dir / "apks"
        
        # Limpar e criar diretórios
        shutil.rmtree(self.build_dir, ignore_errors=True)
        shutil.rmtree(self.apk_output, ignore_errors=True)
        
        self.build_dir.mkdir(parents=True, exist_ok=True)
        self.apk_output.mkdir(parents=True, exist_ok=True)
        
    def create_project_structure(self, app_name):
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
            (self.build_dir / dir_path).mkdir(parents=True, exist_ok=True)
            
        print("✅ Estrutura do projeto criada")
        
    def copy_html_and_assets(self):
        """Copia HTML e assets para o projeto"""
        assets_dir = self.build_dir / "src/main/assets"
        
        # Copiar HTML principal
        html_source = Path(self.config['html_file'])
        shutil.copy2(html_source, assets_dir / "index.html")
        print(f"✅ HTML copiado: {html_source.name}")
        
        # Copiar assets adicionais (CSS, JS, imagens)
        html_parent = html_source.parent
        for item in html_parent.iterdir():
            if item.is_file() and item != html_source:
                if item.suffix.lower() in ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.ttf', '.woff', '.woff2']:
                    shutil.copy2(item, assets_dir / item.name)
                    print(f"📁 Asset copiado: {item.name}")
                    
    def process_icons(self):
        """Processa ícones para todas as densidades"""
        icon_config = self.config.get('icon')
        if not icon_config:
            self.create_default_icons()
            return
            
        icon_path = Path(icon_config['path'])
        if not icon_path.exists():
            print("⚠ Ícone não encontrado, criando ícones padrão")
            self.create_default_icons()
            return
            
        if HAS_PIL:
            self.create_adaptive_icons(icon_path)
        else:
            self.copy_icon_directly(icon_path)
            
    def create_default_icons(self):
        """Cria ícones padrão programaticamente"""
        if not HAS_PIL:
            print("⚠ Não é possível criar ícones sem PIL")
            return
            
        sizes = {
            'mdpi': 48,
            'hdpi': 72, 
            'xhdpi': 96,
            'xxhdpi': 144,
            'xxxhdpi': 192
        }
        
        for density, size in sizes.items():
            # Ícone colorido com design moderno
            img = Image.new("RGBA", (size, size), (33, 150, 243, 255))  # Azul
            draw = ImageDraw.Draw(img)
            
            # Gradiente simples
            for i in range(size):
                alpha = int(255 * (i / size))
                draw.line([(i, 0), (i, size)], fill=(33, 150, 243, alpha))
                
            # Círculo central
            margin = size // 4
            draw.ellipse([margin, margin, size-margin, size-margin], fill=(255, 255, 255, 255))
            
            # Salvar ícone
            icon_dir = self.build_dir / f"src/main/res/drawable-{density}"
            img.save(icon_dir / "ic_launcher.png", "PNG")
            
        print("✅ Ícones padrão criados")
        
    def create_adaptive_icons(self, icon_path):
        """Cria ícones adaptativos a partir de um PNG"""
        try:
            sizes = {
                'mdpi': 48,
                'hdpi': 72,
                'xhdpi': 96, 
                'xxhdpi': 144,
                'xxxhdpi': 192
            }
            
            original_img = Image.open(icon_path).convert("RGBA")
            
            for density, size in sizes.items():
                # Redimensionar mantendo aspect ratio
                img = original_img.copy()
                img.thumbnail((size, size), Image.LANCZOS)
                
                # Criar fundo quadrado
                final_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                
                # Centralizar a imagem
                x = (size - img.width) // 2
                y = (size - img.height) // 2
                final_img.paste(img, (x, y), img)
                
                # Salvar
                icon_dir = self.build_dir / f"src/main/res/drawable-{density}"
                final_img.save(icon_dir / "ic_launcher.png", "PNG")
                
            print("✅ Ícones adaptativos criados")
            
        except Exception as e:
            print(f"⚠ Erro ao processar ícone: {e}")
            self.create_default_icons()
            
    def copy_icon_directly(self, icon_path):
        """Copia ícone diretamente para todas as densidades"""
        for density in ['mdpi', 'hdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi']:
            icon_dir = self.build_dir / f"src/main/res/drawable-{density}"
            shutil.copy2(icon_path, icon_dir / "ic_launcher.png")
        print("✅ Ícone copiado para todas as densidades")
        
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
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="28"/>
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" android:maxSdkVersion="28"/>

    <application
        android:allowBackup="true"
        android:icon="@drawable/ic_launcher"
        android:label="{self.config['app_name']}"
        android:usesCleartextTraffic="true"
        android:requestLegacyExternalStorage="true"
        android:theme="@android:style/Theme.DeviceDefault.Light">
        
        <activity
            android:name=".MainActivity"
            android:label="{self.config['app_name']}"
            android:configChanges="orientation|screenSize|keyboardHidden"
            android:exported="true"
            android:hardwareAccelerated="true"
            android:screenOrientation="portrait">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
    </application>
</manifest>'''

        with open(self.build_dir / "AndroidManifest.xml", "w", encoding="utf-8") as f:
            f.write(manifest_content)
        print("✅ AndroidManifest.xml gerado")
        
    def generate_main_activity(self):
        """Gera MainActivity.java"""
        package_name = self.config['package_name']
        
        activity_content = f'''package {package_name};

import android.app.Activity;
import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebSettings;
import android.webkit.WebViewClient;
import android.webkit.WebChromeClient;
import android.webkit.ValueCallback;
import android.content.Intent;
import android.net.Uri;
import android.webkit.JavascriptInterface;
import android.widget.Toast;
import android.content.pm.PackageManager;
import android.Manifest;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import android.os.Environment;
import android.content.ContentResolver;
import android.content.ContentValues;

public class MainActivity extends Activity {{
    private WebView webView;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        webView = findViewById(R.id.webview);
        setupWebView();
        
        // Carregar HTML local
        webView.loadUrl("file:///android_asset/index.html");
    }}
    
    private void setupWebView() {{
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setDatabaseEnabled(true);
        settings.setLoadWithOverviewMode(true);
        settings.setUseWideViewPort(true);
        settings.setSupportZoom(true);
        settings.setBuiltInZoomControls(true);
        settings.setDisplayZoomControls(false);
        
        // Permitir conteúdo misto
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.LOLLIPOP) {{
            settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        }}
        
        webView.setWebViewClient(new WebViewClient());
        webView.setWebChromeClient(new WebChromeClient());
        
        // Adicionar interface JavaScript
        webView.addJavascriptInterface(new WebAppInterface(), "Android");
    }}
    
    @Override
    public void onBackPressed() {{
        if (webView.canGoBack()) {{
            webView.goBack();
        }} else {{
            super.onBackPressed();
        }}
    }}
    
    public class WebAppInterface {{
        @JavascriptInterface
        public void showToast(String message) {{
            Toast.makeText(MainActivity.this, message, Toast.LENGTH_SHORT).show();
        }}
        
        @JavascriptInterface
        public String getAppInfo() {{
            return "{{
                \\"appName\\": \\"{self.config['app_name']}\\",
                \\"version\\": \\"{self.config.get('version_name', '1.0')}\\",
                \\"package\\": \\"{package_name}\\"
            }}";
        }}
    }}
}}'''

        package_path = package_name.replace('.', '/')
        activity_file = self.build_dir / f"src/main/java/{package_path}/MainActivity.java"
        
        with open(activity_file, "w", encoding="utf-8") as f:
            f.write(activity_content)
        print("✅ MainActivity.java gerado")
        
    def generate_layouts(self):
        """Gera arquivos de layout"""
        # activity_main.xml
        layout_content = '''<?xml version="1.0" encoding="utf-8"?>
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#FFFFFF">

    <WebView
        android:id="@+id/webview"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />
        
</RelativeLayout>'''

        with open(self.build_dir / "src/main/res/layout/activity_main.xml", "w", encoding="utf-8") as f:
            f.write(layout_content)
            
        # strings.xml
        strings_content = f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">{self.config['app_name']}</string>
</resources>'''

        with open(self.build_dir / "src/main/res/values/strings.xml", "w", encoding="utf-8") as f:
            f.write(strings_content)
            
        print("✅ Layouts e strings gerados")
        
    def build_apk(self):
        """Executa o processo completo de build"""
        try:
            print(f"🚀 Iniciando build para: {self.config['app_name']}")
            
            # Criar estrutura
            self.create_project_structure(self.config['app_name'])
            self.copy_html_and_assets()
            self.process_icons()
            
            # Gerar arquivos Android
            self.generate_android_manifest()
            self.generate_main_activity() 
            self.generate_layouts()
            
            # Criar APK básico (simulação - em produção usar ferramentas Android)
            apk_name = f"{self.config['app_name'].replace(' ', '_')}.apk"
            apk_path = self.apk_output / apk_name
            
            # Criar um APK zip básico (em produção, usar aapt, d8, etc.)
            self.create_basic_apk(apk_path)
            
            print(f"✅ APK gerado com sucesso: {apk_path}")
            return str(apk_path)
            
        except Exception as e:
            print(f"❌ Erro durante o build: {e}")
            raise
            
    def create_basic_apk(self, apk_path):
        """Cria um APK básico em formato ZIP"""
        with zipfile.ZipFile(apk_path, 'w', zipfile.ZIP_DEFLATED) as apk_zip:
            # Adicionar AndroidManifest (simplificado para demo)
            apk_zip.writestr('AndroidManifest.xml', '<?xml version="1.0"?><manifest package="{}"/>'.format(self.config['package_name']))
            
            # Adicionar assets
            assets_dir = self.build_dir / "src/main/assets"
            for asset_file in assets_dir.rglob('*'):
                if asset_file.is_file():
                    arcname = asset_file.relative_to(self.build_dir / "src/main/assets")
                    apk_zip.write(asset_file, f'assets/{arcname}')
                    
        # Em produção real, aqui você usaria:
        # - aapt para compilar recursos
        # - javac/d8 para compilar Java
        # - apksigner para assinar
        
        print("📦 APK empacotado (versão básica)")

def load_config_from_args():
    """Carrega configuração dos argumentos da linha de comando"""
    parser = argparse.ArgumentParser(description='Universal HTML to APK Converter')
    
    parser.add_argument('--html', required=True, help='Caminho para o arquivo HTML')
    parser.add_argument('--app-name', required=True, help='Nome do aplicativo')
    parser.add_argument('--package-name', help='Nome do pacote (ex: com.empresa.app)')
    parser.add_argument('--icon', help='Caminho para o ícone PNG')
    parser.add_argument('--output-dir', default='dist', help='Diretório de saída')
    parser.add_argument('--version-code', default='1', help='Código da versão')
    parser.add_argument('--version-name', default='1.0', help='Nome da versão')
    parser.add_argument('--min-sdk', default='21', help='Min SDK version')
    parser.add_argument('--target-sdk', default='33', help='Target SDK version')
    
    args = parser.parse_args()
    
    # Gerar package name se não fornecido
    if not args.package_name:
        safe_name = ''.join(c for c in args.app_name.lower() if c.isalnum() or c == '.')
        args.package_name = f"com.myapp.{safe_name}"
    
    config = {
        'html_file': args.html,
        'app_name': args.app_name,
        'package_name': args.package_name,
        'version_code': args.version_code,
        'version_name': args.version_name,
        'min_sdk': args.min_sdk,
        'target_sdk': args.target_sdk,
        'output_dir': args.output_dir
    }
    
    if args.icon:
        config['icon'] = {'path': args.icon}
    
    return config

def main():
    """Função principal"""
    try:
        config = load_config_from_args()
        
        # Verificar se arquivo HTML existe
        if not os.path.exists(config['html_file']):
            print(f"❌ Arquivo HTML não encontrado: {config['html_file']}")
            sys.exit(1)
            
        # Criar e executar builder
        builder = UniversalAPKCreator(config)
        apk_path = builder.build_apk()
        
        print(f"\n🎉 Build concluído com sucesso!")
        print(f"📱 App: {config['app_name']}")
        print(f"📦 Package: {config['package_name']}") 
        print(f"📍 APK: {apk_path}")
        
        # Salvar informações do build
        build_info = {
            'app_name': config['app_name'],
            'package_name': config['package_name'],
            'apk_path': apk_path,
            'build_time': str(Path(apk_path).stat().st_mtime)
        }
        
        with open(Path(config['output_dir']) / 'build-info.json', 'w') as f:
            json.dump(build_info, f, indent=2)
            
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
