"""
Gerador Universal de Formulários (Versão Simplificada)
Sistema global para criar/atualizar qualquer quiz a partir de arquivos JSON

USO:
    python criar_formulario.py pronomes
    python criar_formulario.py matematica
    
NOVIDADES:
- ✅ Sistema de atualização: se o formulário já existir, será atualizado
- ✅ Nome do arquivo = nome do formulário no Google Drive
- ✅ Organização automática na pasta "Personal study assistant"
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
