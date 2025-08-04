# Sistema de Formulários Educacionais

Sistema completo para criar formulários educacionais no Google Forms com modo Quiz e pontuação automática.

## 📋 Formulários Criados

Acesse os formulários já criados e funcionais em nossa pasta pública do Google Drive:

**🔗 [Pasta Pública dos Formulários](https://drive.google.com/drive/folders/1GTXIcWBu-cQwot0arZe6qW921R4I-Hk7)**

Esta pasta contém todos os formulários educacionais criados pelo sistema, incluindo:
- ✍️ Quiz sobre Verbos e Tempos Verbais
- 📝 Quiz sobre Pronomes
- 🏛️ Quiz sobre Cidadania, Diversidade, Nação e Luta por Direitos
- E muitos outros conteúdos educacionais

## 🤖 Sobre o Desenvolvimento

Este software foi integralmente gerado por uma sequência de diferentes Inteligências Artificiais, demonstrando o poder da colaboração entre humanos e IA para criar ferramentas educacionais eficientes e funcionais.

## Estrutura do Projeto

```
personal-studying/
├── global/                     # Arquivos globais
│   ├── config.py              # Configurações centralizadas
│   ├── generator.py           # Gerador de formulários  
│   ├── schema.json            # Schema de validação JSON
│   └── credentials.json       # Credenciais Google
│
├── forms/                     # Formulários por tema
│   ├── pronomes.json          # Configuração do quiz de pronomes
│   └── [outros_temas]/        # Futuros temas
│
├── credentials_oauth.json     # Credenciais OAuth2
├── token.json                 # Token de autenticação
├── form.py                    # Script principal
└── README.md                  # Esta documentação
```

## Requisitos

- Python 3.8+
- Google API Client Library
- Conta Google com acesso ao Google Forms

## Instalação

1. **Clone o projeto:**
```bash
git clone [seu-repositorio]
cd personal-studying
```

2. **Instale dependências:**
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

3. **Configure credenciais Google:**
   - Acesse [Google Cloud Console](https://console.cloud.google.com/)
   - Crie um projeto e ative Google Forms API
   - Baixe `credentials.json` para a pasta raiz

## Uso Básico

### Criar Formulário

```bash
python form.py [nome_do_arquivo_json]
```

**Exemplo:**
```bash
python form.py pronomes
```

### Estrutura do JSON

Os formulários são definidos em arquivos JSON na pasta `forms/`:

```json
{
  "metadata": {
    "title": "Quiz: Tipos de Pronomes - 5ª Série",
    "description": ["Linha 1", "Linha 2", "Linha 3"],
    "subject": "Português",
    "grade": "5ª série",
    "topic": "Pronomes"
  },
  "content": {
    "instructions": ["Instrução 1", "Instrução 2", "Instrução 3"]
  },
  "questions": [
    {
      "id": 1,
      "section": "Pronomes Pessoais",
      "question": "Qual é o pronome correto?",
      "options": ["eu", "mim", "para mim", "comigo"],
      "correct_answer": 0
    }
  ]
}
```

## Funcionalidades

### Modo Quiz
- **Pontuação automática** pelo Google Forms
- **Respostas corretas** configuradas no JSON
- **Feedback imediato** para estudantes
- **Relatórios automáticos** de desempenho

### Formatação Avançada
- **Arrays para textos** - melhor formatação com quebras de linha
- **Seções organizadas** - agrupamento lógico de questões
- **Validação automática** - schema JSON para consistência

### Integração Google Drive
- **Organização automática** em pasta específica
- **Nomes padronizados** para fácil localização
- **Backup automático** na nuvem

## Arquivos Principais

### `global/config.py`
Configurações centralizadas:
- Autenticação Google APIs
- Funções auxiliares
- Constantes do sistema

### `global/generator.py`
Motor de criação:
- Processamento de JSON
- Criação de formulários
- Modo Quiz automático
- Integração com Google Drive

### `global/schema.json`
Validação de estrutura:
- Schema JSON completo
- Suporte a arrays
- Validação automática

## Exemplos de Uso

### 1. Quiz de Pronomes (Existente)
```bash
python form.py pronomes
```

### 2. Criar Novo Tema
1. Crie `forms/novo_tema.json`
2. Siga o schema em `global/schema.json`
3. Execute: `python form.py novo_tema`

### 3. Atualizar Formulário Existente
- O sistema detecta automaticamente formulários existentes
- Atualiza o conteúdo mantendo o mesmo ID
- Preserva respostas já coletadas

## Configuração Avançada

### Personalizar Avaliação
```json
{
  "evaluation": {
    "include_evaluation": true,
    "evaluation_questions": [
      {
        "question": "Como você avalia este quiz?",
        "options": ["Muito fácil", "Fácil", "Médio", "Difícil"]
      }
    ]
  }
}
```

### Configurações do Formulário
```json
{
  "settings": {
    "public": true,
    "allow_multiple_responses": false,
    "show_progress_bar": true,
    "collect_email": true,
    "require_login": true
  }
}
```

### Configurações de Autenticação

Para garantir que apenas usuários logados possam responder e limitar a uma resposta por usuário:

```json
{
  "settings": {
    "require_login": true,
    "collect_email": true,
    "allow_multiple_responses": false
  }
}
```

**Funcionalidades:**
- `require_login: true` - Exige que o usuário esteja logado no Google (implica em `collect_email: true`)
- `allow_multiple_responses: false` - Limita a uma resposta por usuário
- `collect_email: true` - Coleta o email do usuário (necessário para controle)

**Nota:** A API do Google Forms tem limitações. Algumas configurações precisam ser ajustadas manualmente na interface web para garantir o controle completo de uma resposta por usuário logado.

## Troubleshooting

### Problemas Comuns

**Erro de autenticação:**
- Verifique `credentials_oauth.json`
- Execute novamente para reautenticar
- Confirme permissões do Google Forms API

**Erro de validação JSON:**
- Verifique estrutura com `global/schema.json`
- Confirme todos os campos obrigatórios
- Valide sintaxe JSON

**Formulário não aparece:**
- Verifique Google Drive para organização automática
- Confirme permissões de criação
- Verifique logs de erro no terminal

## Desenvolvimento

### Adicionar Nova Funcionalidade
1. Edite `global/generator.py` para nova feature
2. Atualize `global/schema.json` se necessário
3. Teste com formulário de exemplo

### Contribuição
1. Mantenha código em inglês
2. Siga padrões PEP 8
3. Adicione type hints
4. Documente funções importantes

## 🤖 Processo de Desenvolvimento por IA

Este projeto é um exemplo notável de como a Inteligência Artificial pode ser utilizada para criar software educacional completo e funcional. O desenvolvimento envolveu:

### Colaboração Humano-IA
- **Conceito e Requisitos**: Definidos pelo usuário humano
- **Arquitetura e Código**: Gerados por diferentes modelos de IA
- **Validação e Testes**: Refinados através de iterações colaborativas
- **Conteúdo Educacional**: Criado automaticamente por IA especializada em educação

### Tecnologias de IA Utilizadas
- **Geração de Código**: Para a criação da estrutura Python e integração com APIs Google
- **Criação de Conteúdo**: Para gerar questionários educacionais apropriados por nível escolar
- **Validação de Dados**: Para garantir consistência e qualidade do conteúdo
- **Documentação**: Para criar guias completos de uso e instalação

### Benefícios da Abordagem IA
- ⚡ **Desenvolvimento Rápido**: Projeto completo criado em sessões iterativas
- 🎯 **Precisão Técnica**: Código seguindo boas práticas e padrões estabelecidos
- 📚 **Conteúdo Educacional Rico**: Questionários alinhados com currículos escolares
- 🔄 **Iteração Contínua**: Correções e melhorias aplicadas em tempo real

Este projeto demonstra o potencial transformador da IA na criação de ferramentas educacionais, combinando eficiência técnica com qualidade pedagógica.

## Licença

Este projeto é para fins educacionais.

---

**Desenvolvido para criar formulários educacionais de forma rápida e eficiente.**
