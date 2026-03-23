# Conversor de Documentos (Python 3.13.7)

Sistema robusto de conversão de documentos e planilhas com suporte a monitoramento de pastas em tempo real (**Watchdog**). Ideal para fluxos de trabalho automatizados, geração de documentação técnica e migração de dados para ambientes baseados em Markdown.

## 🛠️ Funcionalidades Principais

* [cite_start]**Modo Watchdog**: Monitora uma pasta específica e converte automaticamente qualquer arquivo novo[cite: 5].
* **Suporte Multi-formato**:
    * [cite_start]**Documentos**: PDF, DOCX, ODT, RTF, TXT, HTML -> Markdown[cite: 1, 2].
    * [cite_start]**Planilhas**: XLSX, XLS, CSV, ODS -> Tabelas Markdown[cite: 3].
    * **Exportação**: Arquivos `.md` na entrada geram automaticamente versões em **PDF** e **DOCX** na saída.
* [cite_start]**Extração de Mídia Inteligente**: Fotos e gráficos são extraídos para uma subpasta `media` dentro do diretório de saída, garantindo links relativos funcionais no Markdown[cite: 4, 15].

---

## 📦 Requisitos e Instalação

O script é compatível com **Windows, Linux e MacOS**.

### 1. Dependências do Sistema

O motor de conversão depende do **Pandoc** e do **WeasyPrint** (para PDFs).

* **macOS**:
    ```bash
    brew install pandoc weasyprint
    ```
* **Linux (Ubuntu/Debian)**:
    ```bash
    sudo apt-get update
    sudo apt-get install pandoc weasyprint
    ```
* **Windows**:
    1.  Instale o Pandoc via instalador `.msi` em [pandoc.org](https://pandoc.org/installing.html).
    2.  Instale o [GTK3 for Windows](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases) (necessário para o WeasyPrint gerar PDFs).

### 2. Bibliotecas Python

Instale as dependências necessárias no seu ambiente virtual:

```bash
pip install pandas openpyxl xlrd odfpy tabulate pypandoc pymupdf4llm watchdog weasyprint
```

## 💻 Como Usar
**A. Execução via IDE (PyCharm / VS Code)**
Para rodar o modo de monitoramento contínuo:

1. Vá em **Run > Edit Configurations**.
2. No campo **Parameters**, configure: _--watch -i ./entrada -o ./saida_.
3. Certifique-se de que as pastas _entrada_ e _saida_ existem na raiz do seu projeto.
4. Clique em **Run**. O console exibirá: _👀 Aguardando novos arquivos...._

**B. Execução via Script (Terminal/Prompt)**
Navegue até a pasta do projeto e execute os comandos conforme seu sistema:

**Modo Monitoramento (Watchdog)**
* **Windows:** _python converter.py --watch -i ./entrada -o ./saida_
* **Linux/macOS:** _python3 converter.py --watch -i ./entrada -o ./saida_

**Modo Conversão Única**
* **Converter Documento:** _python3 converter.py -i manual.docx -o manual.md_
* **Converter Planilha:** _python3 converter.py -i dados.xlsx -o dados.md_

## 📂 Estrutura de Pastas Sugerida
* _/entrada:_ Onde você joga seus arquivos originais (PDF, Excel, Word).
* _/saida:_ Onde o script salvará os arquivos convertidos.
* _/saida/media:_ Subpasta criada automaticamente onde as imagens extraídas dos documentos ficarão armazenadas para o Markdown ler.

## 📝 Notas de Versão e Estabilidade
* Ajuste de Tempo: O script utiliza _time.sleep(1.5)_ para garantir que o sistema operacional terminou de escrever o arquivo antes de iniciar a conversão, evitando erros de "arquivo em uso".
* Compatibilidade de Texto: Arquivos _.txt_ são processados como markdown para preservar a formatação simples sem erros de motor de entrada.
* Links de Imagem: O script corrige automaticamente os caminhos de imagem para formatos relativos, tornando a pasta de saída portátil entre diferentes máquinas.
