"""Universal Form Generator (simplified)

This script creates or updates Google Forms from JSON quiz files located
in the project's `forms/` directory. Before publishing, it runs the
project validator `validate.py` (if present) to ensure the JSON meets the
project schema constraints (metadata, content, questions, option uniqueness,
correct answer indexes, etc.). If validation fails, the publication is
aborted.

Typical steps performed by this script:
    1. Parse command-line argument: the quiz name (file name without .json)
    2. Locate the JSON file under `forms/<quiz_name>.json`
    3. If `validate.py` exists in project root, run it as:
             python validate.py <quiz_name>
         Abort if validation fails.
    4. Load the JSON and call the internal generator to create or update
         the corresponding Google Form.
    5. Save a brief history in `ultimo_formulario_criado.txt` with links
         and metadata returned by the generator.

Usage examples:
    python form.py pronomes
    python form.py energia_renovavel_nao_renovavel

Note:
    - The script expects the `global` package and generator utilities to be
        available in `global/` (project folder). In normal execution the
        existing project structure resolves these imports.
    - The validator is optional but recommended; keep `validate.py` at the
        project root to enable automatic validation before publishing.
"""

import sys
import os
import json
import argparse
from datetime import datetime

# Adicionar pasta global ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
global_dir = os.path.join(current_dir, 'global')
sys.path.append(global_dir)

# Usar o novo generator
from generator import criar_formulario_do_json
import subprocess

def main():
    """
    Função principal simplificada que usa o form_generator.
    """
    parser = argparse.ArgumentParser(
        description='Criar ou atualizar formulário do Google Forms a partir de JSON'
    )
    parser.add_argument(
        'nome_quiz', 
        help='Nome do quiz (arquivo JSON na pasta forms/)'
    )
    
    args = parser.parse_args()
    nome_quiz = args.nome_quiz
    
    print(f"🚀 Criando/atualizando formulário: {nome_quiz}")
    print("=" * 50)
    
    # Definir caminho do arquivo JSON
    json_path = os.path.join(current_dir, 'forms', f'{nome_quiz}.json')
    
    if not os.path.exists(json_path):
        print(f"❌ Arquivo não encontrado: {json_path}")
        print(f"📁 Arquivos disponíveis na pasta forms/:")
        forms_dir = os.path.join(current_dir, 'forms')
        if os.path.exists(forms_dir):
            files = [f[:-5] for f in os.listdir(forms_dir) if f.endswith('.json')]
            for file in files:
                print(f"   • {file}")
        return None
    
    print(f"✅ Configuração carregada: ", end='')
    
    # Carregar título para mostrar
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(config['metadata']['title'])
    except:
        print("(título não disponível)")
    
    print(f"📁 Arquivo: {json_path}")

    # Run validator before publishing
    validate_script = os.path.join(current_dir, 'validate.py')
    if os.path.exists(validate_script):
        print("🔎 Validando o arquivo antes da publicação...")
        try:
            # Use lista de argumentos para evitar problemas de shell
            completed = subprocess.run(
                [sys.executable, validate_script, nome_quiz], 
                check=False, 
                capture_output=True, 
                text=True,
                encoding='utf-8'
            )
            if completed.stdout:
                print(completed.stdout)
            if completed.returncode != 0:
                print("❌ Validação falhou. Abortando publicação.")
                if completed.stderr:
                    print(completed.stderr)
                return None
            else:
                print("✅ Validação OK. Prosseguindo com a publicação...")
        except Exception as e:
            print(f"Erro ao executar validador: {e}")
            return None
    else:
        print("⚠️ Validador 'validate.py' não encontrado. Pulando validação.")
    
    # Usar o form_generator (com sistema de atualização)
    resultado = criar_formulario_do_json(json_path)
    
    if resultado:
        print(f"\n🎯 Formulário criado/atualizado com sucesso!")
        
        # Salvar histórico simplificado
        historico_file = os.path.join(current_dir, 'ultimo_formulario_criado.txt')
        with open(historico_file, 'w', encoding='utf-8') as f:
            f.write(f"Último formulário criado/atualizado:\n")
            f.write(f"Nome: {nome_quiz}\n")
            f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Título: {resultado['config']['metadata']['title']}\n")
            f.write(f"ID: {resultado['form_id']}\n")
            f.write(f"Link público: {resultado['public_url']}\n")
            f.write(f"Link de edição: {resultado['edit_url']}\n")
            f.write(f"Total de questões: {resultado['total_questions']}\n")
            f.write(f"Arquivo fonte: {json_path}\n")
            f.write(f"Seções:\n")
            for secao, qtd in resultado['sections'].items():
                f.write(f"  - {secao}: {qtd} questões\n")
        
        return resultado
    else:
        print(f"\n❌ Falha ao criar/atualizar o formulário '{nome_quiz}'!")
        return None

if __name__ == "__main__":
    main()
