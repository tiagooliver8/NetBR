
# NetBR

**NetBR** é um aplicativo em Python com interface gráfica (PySide6) para diagnosticar a conectividade de estações de trabalho com servidores da nuvem TOTVS, testando:

- Conexão com servidores e portas específicas
- Velocidade de download e upload
- Ping e jitter
- Fallback visual com medidor alternativo de velocidade

---

## 📦 Requisitos

- Python 3.10+  
- Ambiente virtual (`venv`)  
- Navegador interno com suporte a `QWebEngineView`

---

## 🔧 Instalação e Execução

```bash
# Clone o repositório
git clone https://github.com/tiagooliver8/NetBR.git
cd NetBR

# Crie e ative o ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # No Windows

# Instale as dependências
pip install -r requirements.txt

# Execute o aplicativo
python main.py
```

---

## ⚙️ Configuração via `config/conf.json`

Exemplo:

```json
{
  "speed_requirements": {
    "download_min_mbps": 10,
    "upload_min_mbps": 10,
    "ping_max_ms": 20,
    "jitter_max_ms": 200,
    "required": true
  },
  "tests": [
    {
      "host": "exemplo1.cloudtotvs.com.br",
      "port": 491,
      "required": true,
      "description": "Servidor principal"
    },
    {
      "host": "exemplo2.cloudtotvs.com.br",
      "port": 495,
      "required": false,
      "description": "Servidor secundário"
    }
  ],
  "speedtest_fallback_url": "https://librespeed.org",
  "speedtest_timeout": 30
}
```

- Os testes TCP são executados em sequência.
- O teste de velocidade usa a API do [speedtest-cli](https://github.com/sivel/speedtest-cli).
- Se o teste de velocidade falhar ou expirar, o app abre o `fallback_url` como alternativa visual.

---

## 🗂 Estrutura do projeto

```
NetBR/
├── config/                # Arquivo conf.json
├── logs/                  # Arquivos de log
├── nuvem/                 # Módulos do app
│   ├── speedtest.py
│   ├── network.py
│   ├── logger.py
│   ├── config_loader.py
│   ├── network_worker.py
│   └── alternative_speedtest.py
├── main.py
└── requirements.txt
```

---

## 📝 Licença

Projeto privado para fins de diagnóstico interno.  
Distribuição somente autorizada por Tiago Oliveira.
