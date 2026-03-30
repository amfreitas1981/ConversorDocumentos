import os
import time
import argparse
import sys
import pandas as pd
import pypandoc
import pymupdf4llm
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class DocumentConverter:
    def __init__(self):
        # Mapeamento para Pandoc e identificação de formatos
        self.doc_formats = {
            '.md': 'markdown',
            '.docx': 'docx',
            '.odt': 'odt',
            '.rtf': 'rtf',
            '.txt': 'markdown',
            '.html': 'html',
            '.htm': 'html',
            '.pdf': 'pdf',
            '.pptx': 'pptx',  # Suporte a PowerPoint
            '.ppt': 'pptx'  # Pandoc utiliza o motor pptx para ler .ppt
        }
        self.sheet_formats = ['.xlsx', '.xls', '.csv', '.ods']

    def convert(self, input_file, output_file):
        in_path = Path(input_file)
        out_path = Path(output_file)
        in_ext = in_path.suffix.lower()
        out_ext = out_path.suffix.lower()

        # Define a pasta de mídia dentro da pasta de saída
        out_path.parent.mkdir(parents=True, exist_ok=True)
        media_subdir_name = "media"
        media_abs_path = out_path.parent / media_subdir_name
        media_abs_path.mkdir(exist_ok=True)

        try:
            # 1. Planilhas -> Markdown
            if in_ext in self.sheet_formats and out_ext == '.md':
                self._spreadsheet_to_md(input_file, output_file)

            # 2. PDF -> Markdown (Especializado para Imagens)
            elif in_ext == '.pdf' and out_ext == '.md':
                md_text = pymupdf4llm.to_markdown(
                    input_file,
                    write_images=True,
                    image_path=str(media_abs_path),
                    image_format="png"
                )
                md_text = md_text.replace(str(media_abs_path), media_subdir_name)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(md_text)
                print(f"✅ PDF -> MD (com imagens): {out_path.name}")

            # 3. Documentos e Apresentações (Pandoc)
            else:
                self._run_pandoc(input_file, output_file, in_ext, out_ext, media_abs_path)
        except Exception as e:
            print(f"❌ Erro ao converter {in_path.name}: {e}")

    def _spreadsheet_to_md(self, input_file, output_file):
        ext = Path(input_file).suffix.lower()
        if ext == '.csv':
            df = pd.read_csv(input_file)
        elif ext == '.ods':
            df = pd.read_excel(input_file, engine='odf')
        elif ext == '.xls':
            df = pd.read_excel(input_file, engine='xlrd')
        else:
            df = pd.read_excel(input_file, engine='openpyxl')

        md_table = df.to_markdown(index=False)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"## Tabela: {Path(input_file).stem}\n\n{md_table}")
        print(f"✅ Planilha -> MD: {Path(output_file).name}")

    def _run_pandoc(self, input_file, output_file, in_ext, out_ext, media_dir):
        extra_args = []

        # Configurações para PDF
        if out_ext == '.pdf':
            extra_args.append('--pdf-engine=weasyprint')

        # Extração de mídia para documentos ricos (Word/PPTX) quando convertidos para MD
        if out_ext == '.md' and in_ext in ['.docx', '.odt', '.html', '.pptx', '.ppt']:
            extra_args.append(f'--extract-media={media_dir.parent}')

        # Execução da conversão via Pandoc
        pypandoc.convert_file(
            input_file,
            self.doc_formats.get(out_ext, 'markdown'),
            format=self.doc_formats.get(in_ext, 'markdown'),
            outputfile=output_file,
            extra_args=extra_args
        )
        print(f"✅ {in_ext.upper()} -> {out_ext.upper()}: {Path(output_file).name}")


class ConversionHandler(FileSystemEventHandler):
    def __init__(self, converter, output_dir):
        self.converter = converter
        self.output_dir = output_dir

    def on_created(self, event):
        if not event.is_directory:
            self.process_file(event.src_path)

    def process_file(self, file_path):
        input_path = Path(file_path)
        if input_path.name.startswith(('.', '~', '$')): return

        time.sleep(1.5)
        in_ext = input_path.suffix.lower()

        # Se for Markdown, gera o "Pacote Executivo" (.pdf, .docx, .pptx)
        if in_ext == '.md':
            for t_ext in ['.pdf', '.docx', '.pptx']:
                out = Path(self.output_dir) / f"{input_path.stem}{t_ext}"
                self.converter.convert(str(input_path), str(out))
        # Para outros formatos, gera a versão de trabalho em Markdown
        else:
            out = Path(self.output_dir) / f"{input_path.stem}.md"
            self.converter.convert(str(input_path), str(out))


def start_watchdog(path_to_watch, output_dir):
    converter = DocumentConverter()
    event_handler = ConversionHandler(converter, output_dir)

    print(f"🔍 Varredura inicial em {path_to_watch}...")
    for file in os.listdir(path_to_watch):
        full_path = os.path.join(path_to_watch, file)
        if os.path.isfile(full_path):
            event_handler.process_file(full_path)

    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=False)
    observer.start()
    print(f"👀 Aguardando novos arquivos em: {path_to_watch}")
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def main():
    parser = argparse.ArgumentParser(description="Conversor Universal Automático v4.0")
    parser.add_argument("-i", "--input", help="Arquivo ou pasta de entrada")
    parser.add_argument("-o", "--output", help="Arquivo ou pasta de saída")
    parser.add_argument("--watch", action="store_true", help="Ativar modo Watchdog")
    args = parser.parse_args()

    if args.watch:
        if not args.input or not args.output:
            print("❌ Erro: No modo --watch, informe as pastas de entrada e saída.")
            sys.exit(1)
        start_watchdog(args.input, args.output)
    elif args.input and args.output:
        DocumentConverter().convert(args.input, args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
