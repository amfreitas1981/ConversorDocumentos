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
        self.doc_formats = {
            '.md': 'markdown',
            '.docx': 'docx',
            '.odt': 'odt',
            '.rtf': 'rtf',
            '.txt': 'markdown',
            '.html': 'html',
            '.htm': 'html',
            '.pdf': 'pdf',
            '.pptx': 'pptx',
            '.ppt': 'pptx'
        }
        self.sheet_formats = ['.xlsx', '.xls', '.csv', '.ods']

    def convert(self, input_file, output_file):
        in_path = Path(input_file)
        out_path = Path(output_file)
        in_ext = in_path.suffix.lower()
        out_ext = out_path.suffix.lower()

        out_path.parent.mkdir(parents=True, exist_ok=True)
        media_subdir_name = "media"
        media_abs_path = out_path.parent / media_subdir_name
        media_abs_path.mkdir(exist_ok=True)

        try:
            if in_ext in self.sheet_formats and out_ext == '.md':
                self._spreadsheet_to_md(input_file, output_file)
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
                print(f"✅ PDF -> MD: {out_path.name}")
            else:
                self._run_pandoc(input_file, output_file, in_ext, out_ext, media_abs_path)
        except Exception as e:
            print(f"❌ Erro ao converter {in_path.name}: {e}")

    def _spreadsheet_to_md(self, input_file, output_file):
        df = pd.read_excel(input_file) if Path(input_file).suffix.lower() != '.csv' else pd.read_csv(input_file)
        md_table = df.to_markdown(index=False)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"## Conteúdo de: {Path(input_file).name}\n\n{md_table}")
        print(f"✅ Planilha -> MD: {Path(output_file).name}")

    def _run_pandoc(self, input_file, output_file, in_ext, out_ext, media_dir):
        extra_args = []
        if out_ext == '.pdf':
            extra_args.append('--pdf-engine=weasyprint')
        if out_ext == '.md' and in_ext in ['.docx', '.pptx']:
            extra_args.append(f'--extract-media={media_dir.parent}')

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

        if in_ext == '.md':
            self.interactive_menu(input_path)
        else:
            out = Path(self.output_dir) / f"{input_path.stem}.md"
            self.converter.convert(str(input_path), str(out))

    def interactive_menu(self, input_path):
        print(f"\n{'=' * 50}")
        print(f"📄 ARQUIVO MD DETECTADO: {input_path.name}")
        print("Escolha o destino (números separados por espaço):")
        print("1. PDF | 2. Word | 3. PPTX | 4. Todos | 0. Pular")

        try:
            escolha = input("Opção (ou Ctrl+C para sair): ").strip().split()
        except KeyboardInterrupt:
            print("\n\n👋 Encerrando o conversor com segurança...")
            sys.exit(0)  # Fecha o programa sem erro

        formatos_map = {"1": ".pdf", "2": ".docx", "3": ".pptx"}
        selecionados = []

        if "4" in escolha:
            selecionados = [".pdf", ".docx", ".pptx"]
        elif "0" in escolha or not escolha:
            print("⏭️ Arquivo pulado.")
            return
        else:
            # Filtra apenas opções válidas para evitar erros de dicionário
            selecionados = [formatos_map[opt] for opt in escolha if opt in formatos_map]

        for ext in selecionados:
            out = Path(self.output_dir) / f"{input_path.stem}{ext}"
            self.converter.convert(str(input_path), str(out))


def start_watchdog(path_to_watch, output_dir):
    converter = DocumentConverter()
    event_handler = ConversionHandler(converter, output_dir)

    print(f"🔍 Varredura inicial em {path_to_watch}...")
    for file in os.listdir(path_to_watch):
        full_path = os.path.join(path_to_watch, file)
        if os.path.isfile(full_path) and not file.startswith('.'):
            event_handler.process_file(full_path)

    observer = Observer()
    observer.schedule(event_handler, path_to_watch, recursive=False)
    observer.start()
    print(f"👀 Modo monitoramento ativo em: {path_to_watch}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def main():
    parser = argparse.ArgumentParser(description="Conversor Universal Interativo")
    parser.add_argument("-i", "--input", help="Pasta de entrada")
    parser.add_argument("-o", "--output", help="Pasta de saída")
    parser.add_argument("--watch", action="store_true", help="Ativar Watchdog")
    args = parser.parse_args()

    try:
        if args.watch and args.input and args.output:
            start_watchdog(args.input, args.output)
        elif args.input and args.output:
            DocumentConverter().convert(args.input, args.output)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print("\n\n👋 Finalizando aplicação...")
        sys.exit(0)


if __name__ == "__main__":
    main()
