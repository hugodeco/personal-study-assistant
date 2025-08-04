"""
Configuração Global do Sistema de Formulários Educativos
Este arquivo centraliza as configurações e imports necessários para todos os formulários.
"""

import os
import sys

# Adicionar pasta global ao path para importações
GLOBAL_PATH = os.path.dirname(os.path.abspath(__file__))
if GLOBAL_PATH not in sys.path:
    sys.path.insert(0, GLOBAL_PATH)

# Importações globais
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

# Configurações padrão
DEFAULT_SCOPES = [
    'https://www.googleapis.com/auth/forms.body',
    'https://www.googleapis.com/auth/drive.file'
]
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

# Configuração da pasta no Google Drive
GOOGLE_DRIVE_FOLDER_NAME = 'Personal study assistant'
GOOGLE_DRIVE_FOLDER_ID = '1GTXIcWBu-cQwot0arZe6qW921R4I-Hk7'  # ID da pasta para otimização

def get_authenticated_service():
    """
    Retorna um serviço autenticado do Google Forms API.
    Esta função centraliza a autenticação para todos os formulários.
    """
    creds = None
    
    # Possíveis caminhos para os arquivos
    possible_paths = ['.', '../global', '../../global']
    
    # Procurar token existente
    token_path = None
    for path in possible_paths:
        full_path = os.path.join(path, TOKEN_FILE)
        if os.path.exists(full_path):
            token_path = full_path
            break
    
    if token_path:
        creds = Credentials.from_authorized_user_file(token_path, DEFAULT_SCOPES)
    
    # Se não há credenciais válidas, solicitar autorização
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Procurar arquivo de credenciais
            credentials_path = None
            for path in possible_paths:
                full_path = os.path.join(path, CREDENTIALS_FILE)
                if os.path.exists(full_path):
                    credentials_path = full_path
                    break
            
            if not credentials_path:
                print(f"❌ Arquivo de credenciais '{CREDENTIALS_FILE}' não encontrado!")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, DEFAULT_SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Salvar credenciais (tentar na pasta global primeiro)
        save_path = TOKEN_FILE
        for path in ['../../global', '../global', '.']:
            try:
                test_path = os.path.join(path, TOKEN_FILE)
                os.makedirs(os.path.dirname(os.path.abspath(test_path)), exist_ok=True)
                save_path = test_path
                break
            except:
                continue
                
        with open(save_path, 'w') as token:
            token.write(creds.to_json())
    
    return build('forms', 'v1', credentials=creds)

def create_base_form(title, description):
    """
    Cria um formulário básico com título e descrição.
    
    Args:
        title (str): Título do formulário
        description (str): Descrição do formulário
    
    Returns:
        dict: Resultado da criação do formulário
    """
    try:
        service = get_authenticated_service()
        
        # Criar formulário básico
        form_result = service.forms().create(body={
            "info": {
                "title": title
            }
        }).execute()
        
        form_id = form_result.get('formId')
        
        # Adicionar descrição
        service.forms().batchUpdate(formId=form_id, body={
            "requests": [{
                "updateFormInfo": {
                    "info": {
                        "title": title,
                        "description": description
                    },
                    "updateMask": "description"
                }
            }]
        }).execute()
        
        return form_result, service
        
    except Exception as e:
        print(f"❌ Erro ao criar formulário base: {e}")
        return None, None

def add_multiple_choice_question(service, form_id, question_text, options, required=True):
    """
    Adiciona uma questão de múltipla escolha ao formulário.
    
    Args:
        service: Serviço autenticado do Google Forms
        form_id (str): ID do formulário
        question_text (str): Texto da pergunta
        options (list): Lista de opções
        required (bool): Se a pergunta é obrigatória
    """
    try:
        service.forms().batchUpdate(formId=form_id, body={
            "requests": [{
                "createItem": {
                    "item": {
                        "title": question_text,
                        "questionItem": {
                            "question": {
                                "required": required,
                                "choiceQuestion": {
                                    "type": "RADIO",
                                    "options": [{"value": option} for option in options]
                                }
                            }
                        }
                    },
                    "location": {"index": 0}
                }
            }]
        }).execute()
        return True
    except Exception as e:
        print(f"❌ Erro ao adicionar questão: {e}")
        return False

def add_text_question(service, form_id, question_text, required=True, paragraph=False):
    """
    Adiciona uma questão de texto ao formulário.
    
    Args:
        service: Serviço autenticado do Google Forms
        form_id (str): ID do formulário
        question_text (str): Texto da pergunta
        required (bool): Se a pergunta é obrigatória
        paragraph (bool): Se permite texto longo
    """
    try:
        service.forms().batchUpdate(formId=form_id, body={
            "requests": [{
                "createItem": {
                    "item": {
                        "title": question_text,
                        "questionItem": {
                            "question": {
                                "required": required,
                                "textQuestion": {"paragraph": paragraph}
                            }
                        }
                    },
                    "location": {"index": 0}
                }
            }]
        }).execute()
        return True
    except Exception as e:
        print(f"❌ Erro ao adicionar questão de texto: {e}")
        return False

def add_standard_evaluation_questions(service, form_id, topic_name):
    """
    Adiciona questões padrão de autoavaliação no final do formulário.
    
    Args:
        service: Serviço autenticado do Google Forms
        form_id (str): ID do formulário
        topic_name (str): Nome do tema do formulário
    """
    # Questão de autoavaliação sobre dificuldade
    add_multiple_choice_question(
        service, form_id,
        f"Como você se sentiu fazendo esta atividade sobre {topic_name.lower()}?",
        [
            "😊 Muito fácil e divertida",
            "🙂 Fácil",
            "😐 Nem fácil nem difícil",
            "😅 Um pouco difícil",
            "😰 Muito difícil"
        ],
        required=False
    )
    
    # Questão sobre o que mais gostou
    add_multiple_choice_question(
        service, form_id,
        f"Você gostou de aprender sobre {topic_name.lower()}?",
        [
            "❤️ Adorei!",
            "😊 Gostei muito",
            "🙂 Gostei",
            "😐 Foi ok",
            "😞 Não gostei muito"
        ],
        required=False
    )
    
    # Espaço para dúvidas
    add_text_question(
        service, form_id,
        f"Tem alguma dúvida sobre {topic_name.lower()}? Escreva aqui (opcional):",
        required=False,
        paragraph=True
    )

def print_form_summary(form_result, total_questions, topic_categories=None):
    """
    Imprime um resumo do formulário criado.
    
    Args:
        form_result (dict): Resultado da criação do formulário
        total_questions (int): Total de questões
        topic_categories (dict): Categorias de questões por tema
    """
    form_id = form_result.get('formId')
    
    print("\n" + "=" * 70)
    print("🎉 FORMULÁRIO CRIADO COM SUCESSO!")
    print("=" * 70)
    print(f"📋 Título: {form_result.get('info', {}).get('title', 'Não informado')}")
    print(f"📊 Total de questões: {total_questions}")
    print(f"🔗 Link para os alunos: {form_result.get('responderUri')}")
    print(f"⚙️ Link para editar: https://docs.google.com/forms/d/{form_id}/edit")
    
    if topic_categories:
        print("\n📚 CONTEÚDO ABORDADO:")
        for category, count in topic_categories.items():
            print(f"• {category} ({count} questões)")


def get_drive_service():
    """
    Retorna um serviço autenticado do Google Drive API.
    """
    creds = None
    
    # Possíveis caminhos para os arquivos
    possible_paths = ['.', '../global', '../../global', 'Z:/Desenvolvimento/personal-studying/global']
    
    # Procurar token existente
    token_path = None
    for path in possible_paths:
        full_path = os.path.join(path, TOKEN_FILE)
        if os.path.exists(full_path):
            token_path = full_path
            break
    
    if token_path:
        creds = Credentials.from_authorized_user_file(token_path, DEFAULT_SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Buscar arquivo de credenciais
            credentials_path = None
            for path in possible_paths:
                full_path = os.path.join(path, CREDENTIALS_FILE)
                if os.path.exists(full_path):
                    credentials_path = full_path
                    break
            
            if not credentials_path:
                print(f"❌ Arquivo de credenciais '{CREDENTIALS_FILE}' não encontrado!")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, DEFAULT_SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Salvar credenciais
        save_path = TOKEN_FILE
        for path in ['../../global', '../global', '.']:
            try:
                test_path = os.path.join(path, TOKEN_FILE)
                os.makedirs(os.path.dirname(os.path.abspath(test_path)), exist_ok=True)
                save_path = test_path
                break
            except:
                continue
                
        with open(save_path, 'w') as token:
            token.write(creds.to_json())
    
    return build('drive', 'v3', credentials=creds)


def find_or_create_folder(folder_name):
    """
    Encontra ou cria uma pasta no Google Drive.
    
    Args:
        folder_name (str): Nome da pasta
    
    Returns:
        str: ID da pasta
    """
    try:
        drive_service = get_drive_service()
        if not drive_service:
            return None
        
        # Se temos o ID salvo para a pasta padrão, usar diretamente
        if folder_name == GOOGLE_DRIVE_FOLDER_NAME and 'GOOGLE_DRIVE_FOLDER_ID' in globals():
            try:
                # Verificar se a pasta ainda existe
                drive_service.files().get(fileId=GOOGLE_DRIVE_FOLDER_ID).execute()
                print(f"📁 Pasta '{folder_name}' encontrada (ID salvo)")
                return GOOGLE_DRIVE_FOLDER_ID
            except:
                print(f"⚠️ Pasta com ID salvo não encontrada, procurando...")
        
        # Procurar pasta existente
        results = drive_service.files().list(
            q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        items = results.get('files', [])
        
        if items:
            print(f"📁 Pasta '{folder_name}' encontrada no Google Drive")
            return items[0]['id']
        
        # Criar nova pasta
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        folder = drive_service.files().create(
            body=folder_metadata,
            fields='id'
        ).execute()
        
        print(f"📁 Nova pasta '{folder_name}' criada no Google Drive")
        return folder.get('id')
        
    except Exception as e:
        print(f"❌ Erro ao encontrar/criar pasta: {e}")
        return None


def move_form_to_folder(form_id, folder_id):
    """
    Move um formulário para uma pasta específica no Google Drive.
    
    Args:
        form_id (str): ID do formulário
        folder_id (str): ID da pasta de destino
    
    Returns:
        bool: True se movido com sucesso
    """
    try:
        drive_service = get_drive_service()
        if not drive_service:
            return False
        
        # Obter pais atuais do arquivo
        file = drive_service.files().get(
            fileId=form_id,
            fields='parents'
        ).execute()
        
        previous_parents = ",".join(file.get('parents', []))
        
        # Mover arquivo para nova pasta
        if previous_parents:
            # Remover das pastas antigas e adicionar na nova
            drive_service.files().update(
                fileId=form_id,
                addParents=folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
        else:
            # Apenas adicionar na pasta (sem remover de outras)
            drive_service.files().update(
                fileId=form_id,
                addParents=folder_id,
                fields='id, parents'
            ).execute()
        
        print(f"📁 Formulário movido para a pasta '{GOOGLE_DRIVE_FOLDER_NAME}'")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao mover formulário para pasta: {e}")
        import traceback
        traceback.print_exc()
        return False


def find_existing_form_by_name(form_name):
    """
    Procura um formulário existente com o nome específico na pasta configurada.
    Verifica também na lixeira e restaura se necessário.
    
    Args:
        form_name (str): Nome do formulário (baseado no arquivo JSON)
    
    Returns:
        str or None: ID do formulário se encontrado, None se não encontrado
    """
    try:
        drive_service = get_drive_service()
        if not drive_service:
            return None
        
        # 1. Primeiro, procurar formulários ativos na pasta específica
        query = f"name='{form_name}' and mimeType='application/vnd.google-apps.form' and parents in '{GOOGLE_DRIVE_FOLDER_ID}'"
        
        results = drive_service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        items = results.get('files', [])
        
        if items:
            print(f"📋 Formulário existente encontrado: {items[0]['name']} (ID: {items[0]['id']})")
            return items[0]['id']
        
        # 2. Se não encontrou na pasta, verificar na lixeira
        print(f"🗑️ Verificando se o formulário '{form_name}' está na lixeira...")
        
        query_trash = f"name='{form_name}' and mimeType='application/vnd.google-apps.form' and trashed=true"
        
        results_trash = drive_service.files().list(
            q=query_trash,
            spaces='drive',
            fields='files(id, name, trashed)'
        ).execute()
        
        items_trash = results_trash.get('files', [])
        
        if items_trash:
            form_id = items_trash[0]['id']
            print(f"♻️ Formulário '{form_name}' encontrado na lixeira! Restaurando...")
            
            # Restaurar da lixeira
            try:
                drive_service.files().update(
                    fileId=form_id,
                    body={'trashed': False}
                ).execute()
                
                print(f"✅ Formulário restaurado da lixeira!")
                
                # Mover para a pasta correta após restaurar
                folder_id = find_or_create_folder(GOOGLE_DRIVE_FOLDER_NAME)
                if folder_id:
                    move_form_to_folder(form_id, folder_id)
                    print(f"📁 Formulário movido para a pasta '{GOOGLE_DRIVE_FOLDER_NAME}'")
                
                return form_id
                
            except Exception as e:
                print(f"❌ Erro ao restaurar formulário da lixeira: {e}")
                return None
        
        # 3. Se não encontrou nem ativo nem na lixeira
        print(f"📋 Nenhum formulário '{form_name}' encontrado (ativo ou na lixeira)")
        return None
        
    except Exception as e:
        print(f"❌ Erro ao procurar formulário existente: {e}")
        import traceback
        traceback.print_exc()
        return None


def update_form_title(form_id, new_title):
    """
    Atualiza o título do formulário existente.
    
    Args:
        form_id (str): ID do formulário
        new_title (str): Novo título
    
    Returns:
        bool: True se atualizado com sucesso
    """
    try:
        # Renomear no Google Drive
        drive_service = get_drive_service()
        if drive_service:
            drive_service.files().update(
                fileId=form_id,
                body={'name': new_title}
            ).execute()
            print(f"📝 Nome do arquivo atualizado no Drive: {new_title}")
        
        # Atualizar título no Google Forms
        forms_service = get_authenticated_service()
        if forms_service:
            forms_service.forms().batchUpdate(formId=form_id, body={
                "requests": [{
                    "updateFormInfo": {
                        "info": {
                            "title": new_title
                        },
                        "updateMask": "title"
                    }
                }]
            }).execute()
            print(f"📋 Título do formulário atualizado: {new_title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar título: {e}")
        return False
