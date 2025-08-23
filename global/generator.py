"""
Gerador de Formulários Baseado em JSON
Sistema universal para gerar formulários educacionais a partir de arquivos JSON
"""

import sys
import os
import json

# Adicionar pasta global ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'global'))

from config import get_authenticated_service, get_drive_service


def validar_json_schema(data):
    """
    Valida se o JSON está no formato correto.
    """
    required_fields = ['metadata', 'content', 'questions']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Campo obrigatório '{field}' não encontrado no JSON")
    
    # Validar metadata
    metadata_required = ['title', 'description', 'subject', 'grade', 'topic']
    for field in metadata_required:
        if field not in data['metadata']:
            raise ValueError(f"Campo obrigatório 'metadata.{field}' não encontrado")
    
    # Validar questões
    if not isinstance(data['questions'], list) or len(data['questions']) == 0:
        raise ValueError("O campo 'questions' deve ser uma lista não vazia")
    
    for i, question in enumerate(data['questions']):
        required_q_fields = ['id', 'section', 'question', 'options', 'correct_answer']
        for field in required_q_fields:
            if field not in question:
                raise ValueError(f"Campo obrigatório '{field}' não encontrado na questão {i+1}")
    
    return True


def carregar_configuracao_quiz(caminho_json):
    """
    Carrega e valida a configuração do quiz a partir do arquivo JSON.
    """
    try:
        with open(caminho_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        validar_json_schema(data)
        print(f"✅ Configuração carregada: {data['metadata']['title']}")
        return data
    
    except FileNotFoundError:
        print(f"❌ Arquivo JSON não encontrado: {caminho_json}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar JSON: {e}")
        return None
    except ValueError as e:
        print(f"❌ Erro de validação: {e}")
        return None


def criar_formulario_do_json(caminho_json):
    """
    Cria ou atualiza um formulário do Google Forms baseado no arquivo JSON.
    Se um formulário com o mesmo nome já existir, ele será atualizado.
    """
    try:
        print("🚀 Iniciando criação/atualização de formulário baseado em JSON...")
        
        # 1. Carregar configuração
        config = carregar_configuracao_quiz(caminho_json)
        if not config:
            return None
        
        # 2. Extrair nome do arquivo JSON (sem extensão) para usar como nome do formulário
        json_filename = os.path.splitext(os.path.basename(caminho_json))[0]
        form_name = json_filename  # Nome do arquivo será o nome do formulário no Drive
        
        print(f"📄 Nome do formulário: {form_name}")
        print(f"📋 Título: {config['metadata']['title']}")
        
        # 3. Verificar se já existe um formulário com esse nome
        from config import find_existing_form_by_name, update_form_title, get_drive_service
        
        existing_form_id = find_existing_form_by_name(form_name)
        
        if existing_form_id:
            print("🔄 Formulário existente encontrado! Preparando para atualização...")
            
            # Atualizar formulário existente
            form_id = existing_form_id
            
            # Atualizar título no Drive e no Forms
            update_form_title(form_id, form_name)
            
            # Limpar todas as questões existentes
            print("🗑️ Removendo questões existentes...")
            service = get_authenticated_service()
            if not service:
                print("❌ Erro na autenticação!")
                return None
            
            # Obter formulário atual para ver itens existentes
            form_info = service.forms().get(formId=form_id).execute()
            
            # Remover todos os itens existentes
            if 'items' in form_info and len(form_info['items']) > 0:
                delete_requests = []
                for item in form_info['items']:
                    delete_requests.append({
                        "deleteItem": {
                            "location": {"index": 0}  # Sempre remover o primeiro (a lista se reorganiza)
                        }
                    })
                
                # Executar remoções em lotes
                if delete_requests:
                    service.forms().batchUpdate(formId=form_id, body={
                        "requests": delete_requests
                    }).execute()
            
            # Atualizar descrição e ATIVAR MODO QUIZ
            print("📝 Atualizando descrição e ativando modo Quiz...")
            
            # Processar description (pode ser string ou array)
            description = config['metadata']['description']
            if isinstance(description, list):
                description_text = "\n".join(description)
            else:
                description_text = description
            
            service.forms().batchUpdate(formId=form_id, body={
                "requests": [{
                    "updateFormInfo": {
                        "info": {
                            "title": config['metadata']['title'],
                            "description": description_text
                        },
                        "updateMask": "title,description"
                    }
                }, {
                    "updateSettings": {
                        "settings": {
                            "quizSettings": {
                                "isQuiz": True
                            }
                        },
                        "updateMask": "quizSettings.isQuiz"
                    }
                }]
            }).execute()
            
            print("✅ Formulário existente atualizado com nova configuração!")
            
        else:
            print("📋 Criando novo formulário...")
            
            # 4. Obter serviço autenticado
            service = get_authenticated_service()
            if not service:
                print("❌ Erro na autenticação!")
                return None
            
            print("✅ Autenticado com sucesso!")
            
            # 5. Criar formulário básico (apenas título)
            form_result = service.forms().create(body={
                "info": {
                    "title": config['metadata']['title']
                }
            }).execute()
            
            form_id = form_result.get('formId')
            print(f"✅ Formulário criado! ID: {form_id}")
            
            # 6. Adicionar descrição e ATIVAR MODO QUIZ
            print("📝 Adicionando descrição e ativando modo Quiz...")
            
            # Processar description (pode ser string ou array)
            description = config['metadata']['description']
            if isinstance(description, list):
                description_text = "\n".join(description)
            else:
                description_text = description
            
            service.forms().batchUpdate(formId=form_id, body={
                "requests": [{
                    "updateFormInfo": {
                        "info": {
                            "title": config['metadata']['title'],
                            "description": description_text
                        },
                        "updateMask": "title,description"
                    }
                }, {
                    "updateSettings": {
                        "settings": {
                            "quizSettings": {
                                "isQuiz": True
                            }
                        },
                        "updateMask": "quizSettings.isQuiz"
                    }
                }]
            }).execute()
            
            # 7. Definir nome do arquivo no Google Drive
            drive_service = get_drive_service()
            if drive_service:
                drive_service.files().update(
                    fileId=form_id,
                    body={'name': form_name}
                ).execute()
                print(f"📝 Nome do arquivo definido: {form_name}")
            
            # 8. Remover item padrão que é criado automaticamente
            print("🗑️ Removendo item padrão...")
            try:
                # Obter informações do formulário para ver os itens
                form_info = service.forms().get(formId=form_id).execute()
                if 'items' in form_info and len(form_info['items']) > 0:
                    # Remover o primeiro item padrão
                    first_item_id = form_info['items'][0]['itemId']
                    service.forms().batchUpdate(formId=form_id, body={
                        "requests": [{
                            "deleteItem": {
                                "location": {"index": 0}
                            }
                        }]
                    }).execute()
            except Exception as e:
                print(f"⚠️ Não foi possível remover item padrão: {e}")
        
        # 8. Adicionar seção de instruções
        instructions = config.get('content', {}).get('instructions', [])
        if instructions:
            print("Adicionando seção de instruções...")
            
            # Converter array de instruções em texto formatado (sem quebras de linha)
            if isinstance(instructions, list):
                instructions_text = " ".join(instructions)  # Usar espaço ao invés de \n
            else:
                instructions_text = instructions
            
            instructions_request = {
                "createItem": {
                    "item": {
                        "title": instructions_text,
                        "textItem": {}
                    },
                    "location": {"index": 0}
                }
            }
            
            try:
                service.forms().batchUpdate(formId=form_id, body={"requests": [instructions_request]}).execute()
                print("Instruções adicionadas!")
            except Exception as e:
                print(f"Erro ao adicionar instruções: {e}")
        
        # 9. Adicionar questões COM respostas corretas (modo Quiz simplificado)
        print(f"📝 Adicionando {len(config['questions'])} questões em modo Quiz...")
        
        for i, question_data in enumerate(config['questions']):
            print(f"   Questão {i+1}/{len(config['questions'])}...")
            
            # Preparar opções
            options_clean = question_data['options'].copy()
            correct_answer_index = question_data['correct_answer']
            
            # Obter o número atual de itens no formulário para calcular o índice correto
            form_info = service.forms().get(formId=form_id).execute()
            current_items_count = len(form_info.get('items', []))
            
            # Criar questão com configuração de Quiz diretamente
            create_request = {
                "createItem": {
                    "item": {
                        "title": f"{question_data['id']}: {question_data['question']}",
                        "description": f"Seção: {question_data['section']}",
                        "questionItem": {
                            "question": {
                                "required": True,
                                "choiceQuestion": {
                                    "type": "RADIO",
                                    "options": [{"value": opcao} for opcao in options_clean],
                                    "shuffle": False
                                },
                                "grading": {
                                    "pointValue": 1,
                                    "correctAnswers": {
                                        "answers": [{"value": question_data['options'][correct_answer_index]}]
                                    }
                                }
                            }
                        }
                    },
                    "location": {"index": current_items_count}
                }
            }
            
            try:
                service.forms().batchUpdate(formId=form_id, body={"requests": [create_request]}).execute()
                print(f"   ✅ Questão {i+1} criada com resposta correta!")
            except Exception as e:
                print(f"   ⚠️ Erro na questão {i+1}: {e}")
                # Fallback: criar sem grading
                fallback_request = {
                    "createItem": {
                        "item": {
                            "title": f"{question_data['id']}: {question_data['question']}",
                            "description": f"Seção: {question_data['section']}",
                            "questionItem": {
                                "question": {
                                    "required": True,
                                    "choiceQuestion": {
                                        "type": "RADIO",
                                        "options": [{"value": opcao} for opcao in options_clean],
                                        "shuffle": False
                                    }
                                }
                            }
                        },
                        "location": {"index": i}
                    }
                }
                service.forms().batchUpdate(formId=form_id, body={"requests": [fallback_request]}).execute()
                print(f"   ✅ Questão {i+1} criada (sem grading)")
        
        print("✅ Todas as questões foram criadas!")
        
        # 6. Adicionar questões de avaliação (se habilitado)
        if config.get('evaluation', {}).get('include_evaluation', False):
            print("📊 Adicionando seção de avaliação...")
            
            eval_questions = config.get('evaluation', {}).get('evaluation_questions', [
                {
                    "question": "Como você avalia a dificuldade deste quiz?",
                    "options": ["Muito fácil", "Fácil", "Médio", "Difícil", "Muito difícil"]
                },
                {
                    "question": "O que você achou das questões?",
                    "options": ["Muito interessantes", "Interessantes", "Normais", "Chatas", "Muito chatas"]
                },
                {
                    "question": "Você recomendaria este quiz para seus colegas?",
                    "options": ["Sim, com certeza", "Sim", "Talvez", "Não", "Definitivamente não"]
                }
            ])
            
            for i, eval_q in enumerate(eval_questions):
                print(f"   Avaliação {i+1}/{len(eval_questions)}...")
                
                # Obter índice atual atualizado
                form_info = service.forms().get(formId=form_id).execute()
                current_items_count = len(form_info.get('items', []))
                
                request = {
                    "createItem": {
                        "item": {
                            "title": f"Avaliação {i+1}: {eval_q['question']}",
                            "questionItem": {
                                "question": {
                                    "choiceQuestion": {
                                        "type": "RADIO",
                                        "options": [{"value": opcao} for opcao in eval_q['options']]
                                    }
                                }
                            }
                        },
                        "location": {"index": current_items_count}
                    }
                }
                
                service.forms().batchUpdate(formId=form_id, body={"requests": [request]}).execute()
        
        # 7. Aplicar configurações de settings do JSON
        form_settings = config.get('settings', {})
        if form_settings:
            print("⚙️ Aplicando configurações de settings...")
            
            settings_updates = {}
            update_mask_parts = []
            
            # Configurar se deve coletar email e limitar respostas
            require_login = form_settings.get('require_login', False)
            collect_email = form_settings.get('collect_email', False) 
            allow_multiple_responses = form_settings.get('allow_multiple_responses', True)
            
            # Se require_login for True, automaticamente ativar collect_email
            if require_login:
                collect_email = True
                print("🔐 Login obrigatório ativado - coleta de email habilitada")
            
            # Se allow_multiple_responses for False, limitar a uma resposta
            if not allow_multiple_responses:
                print("📊 Limitando a uma resposta por usuário")
            
            # Aplicar configurações
            if collect_email is not None:
                settings_updates["collectEmail"] = collect_email
                update_mask_parts.append("collectEmail")
            
            # Aplicar as configurações se houver alguma
            if settings_updates and update_mask_parts:
                try:
                    service.forms().batchUpdate(formId=form_id, body={
                        "requests": [{
                            "updateSettings": {
                                "settings": settings_updates,
                                "updateMask": ",".join(update_mask_parts)
                            }
                        }]
                    }).execute()
                    print("✅ Configurações de settings aplicadas!")
                    
                    # Informar sobre limitações da API
                    if not allow_multiple_responses or require_login:
                        print("📝 IMPORTANTE: Para garantir uma resposta por usuário, você precisa:")
                        print("   1. Acessar o formulário no Google Forms")
                        print("   2. Ir em Configurações (ícone de engrenagem)")
                        print("   3. Marcar 'Limitar a uma resposta'")
                        print("   4. Verificar se 'Coletar endereços de email' está ativado")
                        print(f"   🔗 Acesse: {edit_url}")
                    
                except Exception as e:
                    print(f"⚠️ Erro ao aplicar configurações de settings: {e}")
            else:
                print("📝 Nenhuma configuração de settings para aplicar")
        
        # Sistema Quiz Google - não precisamos de arquivo gabarito separado
        print("Formulário criado em MODO QUIZ com respostas corretas configuradas!")
        print("O Google Forms calculará automaticamente as pontuações")
        
        # URLs do formulário
        edit_url = f"https://docs.google.com/forms/d/{form_id}/edit"
        public_url = f"https://docs.google.com/forms/d/{form_id}/viewform"
        
        # Estatísticas por seção
        secoes_stats = {}
        for q in config['questions']:
            secao = q['section']
            if secao not in secoes_stats:
                secoes_stats[secao] = 0
            secoes_stats[secao] += 1
        
        print("\n" + "="*60)
        print("🎉 FORMULÁRIO QUIZ CRIADO COM SUCESSO!")
        print("="*60)
        print(f"📝 Título: {config['metadata']['title']}")
        print(f"📚 Matéria: {config['metadata']['subject']} - {config['metadata']['topic']}")
        print(f"🎓 Série: {config['metadata']['grade']}")
        print(f"📊 Total de questões: {len(config['questions'])}")
        print(f"🎯 Modo: Quiz Google (cálculo automático de pontuação)")
        
        # Informações sobre configurações de autenticação
        form_settings = config.get('settings', {})
        if form_settings.get('require_login', False):
            print(f"🔐 Autenticação: Login obrigatório")
            print(f"📧 Coleta de email: Ativada")
            print(f"📊 Respostas: Uma por usuário logado")
        elif not form_settings.get('allow_multiple_responses', True):
            print(f"📊 Respostas: Uma por usuário")
            if form_settings.get('collect_email', False):
                print(f"📧 Coleta de email: Ativada")
        elif form_settings.get('collect_email', False):
            print(f"📧 Coleta de email: Ativada")
        else:
            print(f"🌐 Acesso: Público (sem restrições)")
        
        print(f"🔗 Link do editor: {edit_url}")
        print(f"🌐 Link público: {public_url}")
        print("\n📚 Distribuição por seção:")
        for secao, quantidade in secoes_stats.items():
            print(f"   • {secao}: {quantidade} questões")
        
        if config.get('evaluation', {}).get('include_evaluation', False):
            eval_count = len(config.get('evaluation', {}).get('evaluation_questions', []))
            print(f"   • Avaliação: {eval_count} questões")
        
        print("\n✅ Formulário Quiz criado/atualizado e pronto para uso!")
        print("🎓 Os alunos receberão pontuação automática após responder!")
        
        # 10. Organizar formulário na pasta específica no Google Drive
        print("📁 Organizando formulário na pasta do Google Drive...")
        from config import find_or_create_folder, move_form_to_folder, GOOGLE_DRIVE_FOLDER_NAME
        
        folder_id = find_or_create_folder(GOOGLE_DRIVE_FOLDER_NAME)
        if folder_id:
            # Verificar se já está na pasta correta
            drive_service = get_drive_service()
            if drive_service:
                file_info = drive_service.files().get(fileId=form_id, fields='parents').execute()
                current_parents = file_info.get('parents', [])
                
                if folder_id not in current_parents:
                    print(f"📦 Movendo para pasta '{GOOGLE_DRIVE_FOLDER_NAME}'...")
                    if move_form_to_folder(form_id, folder_id):
                        print(f"✅ Formulário organizado na pasta '{GOOGLE_DRIVE_FOLDER_NAME}'")
                    else:
                        print("⚠️ Formulário criado mas não foi possível mover para a pasta")
                else:
                    print(f"✅ Formulário já está na pasta '{GOOGLE_DRIVE_FOLDER_NAME}'")
        else:
            print("⚠️ Formulário criado mas não foi possível encontrar/criar a pasta")
        
        print("="*60)
        
        return {
            'form_id': form_id,
            'edit_url': edit_url,
            'public_url': public_url,
            'total_questions': len(config['questions']),
            'sections': secoes_stats,
            'config': config
        }
        
    except Exception as e:
        print(f"❌ Erro ao criar formulário: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """
    Função principal que pode ser chamada diretamente ou via linha de comando.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerar formulário do Google Forms a partir de JSON')
    parser.add_argument('json_file', nargs='?', default='quiz_config.json',
                        help='Caminho para o arquivo JSON de configuração')
    
    args = parser.parse_args()
    
    # Se não foi passado argumento, usar o arquivo padrão na pasta atual
    if not os.path.isabs(args.json_file):
        json_path = os.path.join(os.path.dirname(__file__), args.json_file)
    else:
        json_path = args.json_file
    
    resultado = criar_formulario_do_json(json_path)
    
    if resultado:
        print(f"\n🎯 Formulário criado com sucesso!")
        print(f"📋 Use este link para visualizar: {resultado['public_url']}")
        return resultado
    else:
        print("\n❌ Falha ao criar o formulário!")
        return None


if __name__ == "__main__":
    main()
