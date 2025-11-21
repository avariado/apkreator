# apkreator
Apk creator

https://avariado.github.io/apkreator/

https://www.pwabuilder.com/



<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Organizador de Tarefas</title>
    
    <!-- PWA Meta Tags -->
    <meta name="theme-color" content="#4a6987">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="Organizador">
    <link rel="apple-touch-icon" href="icon-192x192.png">
    
    <!-- Manifest -->
    <link rel="manifest" href="manifest.json">
    
    <!-- Favicon -->
    <link rel="icon" type="image/png" href="icon-192x192.png">
    
    <style>
        /* SEU CSS EXISTENTE AQUI - mantenha todo o style que você já tem */
        :root {
            --primary-color: #4a6987;
            --secondary-color: #f0f0f0;
            /* ... todo o resto do seu CSS */
        }
        /* ... resto do seu CSS completo */
    </style>
</head>
<body>
    <!-- SEU HTML EXISTENTE AQUI - mantenha toda a estrutura HTML que você já tem -->
    <div class="container">
        <h1>Organizador de Tarefas</h1>
        <!-- ... todo o resto do seu HTML -->
    </div>

    <!-- SEU JAVASCRIPT EXISTENTE AQUI - mantenha toda a tag script -->
    <script>
        // =========================
        // ESTADO
        // =========================
        let tasks = [];
        let notes = "";
        // ... TODO O SEU JAVASCRIPT ATUAL
        
        // ADICIONE ESTA FUNÇÃO NO FINAL DO SEU SCRIPT:
        
        // Registrar Service Worker
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', function() {
                navigator.serviceWorker.register('/sw.js')
                    .then(function(registration) {
                        console.log('Service Worker registrado com sucesso:', registration.scope);
                    })
                    .catch(function(error) {
                        console.log('Falha no registro do Service Worker:', error);
                    });
            });
        }
    </script>
</body>
</html>




Seu repositório deve ter esta estrutura:

text
/
├── index.html
├── manifest.json
├── sw.js
├── icon-192x192.png
├── icon-512x512.png
└── README.md (opcional)
