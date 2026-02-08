# Sistema de Upload de Documentos - Pré-Inscrição

## 📋 Resumo da Implementação

Sistema completo de upload seguro de documentos para pré-inscrição de alunos, com aprovação apenas por admin e downloads protegidos.

---

## 🗂️ Componentes Implementados

### 1. **Banco de Dados**
- **Arquivo**: `app/schema.sql`
- **Nova Tabela**: `PreInscricoes`
  - Armazena dados completos de pré-inscrição
  - Campos: `documento_anterior_path`, `bilhete_path`
  - Status: pendente, aprovado, rejeitado
  - Controle de aprovação: `admin_id`, `data_aprovacao`
  - Acesso temporário: `username`, `password` (hash)

### 2. **Frontend - Formulário de Pré-Inscrição**
- **Arquivo**: `app/templates/auth/pre_register.html`
- **Mudanças**:
  - Adicionado atributo `enctype="multipart/form-data"` ao formulário
  - Novo fieldset "5. Documentos Obrigatórios"
  - Campo de upload: Certificado/Declaração da classe anterior
  - Campo de upload: Bilhete de Identidade
  - Validação no frontend (formatos PDF, JPG, PNG)
  - Limite de 4MB por arquivo
  - Campos marcados como obrigatórios

### 3. **Backend - Processamento de Upload**
- **Arquivo**: `app/auth.py`
- **Funcionalidades Novas**:

#### **Configurações de Upload**:
```python
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 4 * 1024 * 1024  # 4MB
```

#### **Funções Utilitárias**:
- `allowed_file()`: Valida extensão do arquivo
- `validate_file_size()`: Verifica tamanho máximo
- `save_uploaded_file()`: Salva arquivo com segurança
  - Gera UUID único para cada arquivo
  - Cria estrutura: `uploads/preinscricao/{id}/{tipo}/uuid.ext`
  - Valida tipo e tamanho antes de salvar

#### **Rota `/auth/pre_register`**:
- Processa **GET**: Exibe formulário com cursos disponíveis
- Processa **POST**:
  1. Valida dados pessoais
  2. Valida obrigatoriedade de documentos
  3. Verifica duplicatas (email, bilhete)
  4. Insere registro em PreInscricoes com status 'pendente'
  5. Processa e salva arquivos
  6. Atualiza paths dos documentos no BD
  7. Em caso de erro, remove registro criado

#### **Rota `/auth/download_documento/<id>/<tipo>`**:
- Apenas admin pode acessar
- Previne path traversal attacks
- Valida existência de arquivo
- Serve arquivo com attachement header
- Não expõe URL direta do arquivo

### 4. **Aprovação de Pré-Inscrições (Admin)**
- **Arquivo**: `app/admin.py`
- **Rota**: `/admin/aprovar_alunos`
  - Busca todas as pré-inscrições com status 'pendente'
  - Exibe documentos como links para download
  - Lista turmas disponíveis para matrícula

- **Rota**: `/admin/aprovar_aluno/<id>`
  - Cria novo registro em Alunos
  - Cria novo usuário em Usuarios (status 'ativo')
  - Matricula automaticamente em turma selecionada
  - Marca pré-inscrição como aprovada
  - Registra admin que aprovou e data

### 5. **Template de Aprovação**
- **Arquivo**: `app/templates/admin/aprovar_alunos.html`
- **Funcionalidades**:
  - Exibe cada pré-inscrição pendente
  - Links para download dos documentos (🔒 Seguros)
  - Formulário para selecionar turma e aprovar
  - Indicador visual se turmas estão disponíveis
  - Data e BI do candidato

### 6. **Diretório de Uploads**
- **Path**: `uploads/preinscricao/`
- **Estrutura**:
  ```
  uploads/
  └── preinscricao/
      ├── 1/
      │   ├── documento_anterior/
      │   │   └── abc123...pdf
      │   └── bilhete/
      │       └── def456...jpg
      ├── 2/
      │   ├── documento_anterior/
      │   │   └── ghi789...pdf
      │   └── bilhete/
      │       └── jkl012...png
  ```

---

## 🔒 Segurança

### **Validações Implementadas**:
1. ✅ Validação de tipo de arquivo (extensão)
2. ✅ Validação de tamanho (máx 4MB)
3. ✅ Nomes de arquivos únicos (UUID)
4. ✅ Prevenção de path traversal
5. ✅ Apenas admin pode acessar downloads
6. ✅ Não há URL direta para uploads
7. ✅ Diretório uploads fora do web root (recomendado)

### **Permissões**:
- Qualquer pessoa pode fazer pré-inscrição
- Apenas **admin** pode:
  - Visualizar documentos
  - Fazer download de documentos
  - Aprovar pré-inscrições

---

## 📝 Fluxo Completo

1. **Candidato** acessa `/auth/pre_register`
2. Preenche formulário com seus dados pessoais
3. Faz upload de:
   - Certificado/Declaração da classe anterior (PDF/IMG)
   - Cópia do Bilhete de Identidade (PDF/IMG)
4. Clica em "Enviar Pré-Inscrição"
5. Sistema valida e salva os arquivos
6. **Admin** recebe notificação implícita (ou monitora página)
7. Admin acessa `/admin/aprovar_alunos`
8. Visualiza documentos via links de download público
9. Seleciona turma e clica "Aprovar e Matricular"
10. Sistema cria:
    - Novo registro em `Alunos`
    - Novo usuário em `Usuarios` (status ativo)
    - Matrícula em turma selecionada
11. Candidato agora pode fazer login normalmente

---

## 🛠️ Configuração

### **Ambiente Django/Flask**:
```python
# Já configurado em app/__init__.py
SECRET_KEY = "seu-secret-key"
DATABASE = "path/to/db.sqlite"
# MAX_CONTENT_LENGTH opcional para limitar tamanho global
```

### **Diretório de Uploads**:
- Máximo recomendado: No mesmo nível da pasta `app/`
- Não expor ao web via `app.static_files` ou similar

### **Banco de Dados**:
Executar `schema.sql` para criar tabela PreInscricoes (já incluído)

---

## 📌 Pontos Importantes

1. **Nenhum acesso direto a uploads**: URLs como `http://site.com/uploads/...` não funcionam
2. **Download apenas via rota segura**: `/auth/download_documento/1/bilhete`
3. **Aprovação cria novo Aluno**: Não sobrescreve dados; pré-inscrição é apenas temporary
4. **UUID para nomes**: Previne colisão e garante nomes únicos
5. **Limite de 4MB**: Pode ser ajustado em `MAX_FILE_SIZE`

---

## 🧪 Teste Rápido

```bash
# 1. Acessar pré-inscrição
http://localhost:5000/auth/pre_register

# 2. Preencher e submeter
# - Dados: João Silva, 2005-01-15, españa@email.com, ...
# - Upload: documento.pdf, bi.jpg

# 3. Admin aprova
http://localhost:5000/admin/aprovar_alunos
# - Clicar em "Certificado/Declaração" para ver documento
# - Selecionar turma
# - Clicar "Aprovar e Matricular"

# 4. Aluno faz login normalmente
http://localhost:5000/auth/login
# - username: (username fornecido na pré-inscrição)
# - password: (password fornecido na pré-inscrição)
```

---

## 📚 Arquivos Modificados

- ✅ `app/schema.sql` - Nova tabela PreInscricoes
- ✅ `app/auth.py` - Upload e download seguro
- ✅ `app/admin.py` - Aprovação de pré-inscrições
- ✅ `app/templates/auth/pre_register.html` - Formulário com upload
- ✅ `app/templates/admin/aprovar_alunos.html` - Visualização com documentos
- ✅ `uploads/preinscricao/` - Diretório criado

---

## 📞 Suporte

Caso haja dúvidas sobre:
- **Validação**: Ver funções em `auth.py` linhas ~20-60
- **Segurança**: Ver função `download_documento` em `auth.py` linhas ~260+
- **BD**: Ver tabela PreInscricoes em `schema.sql`
- **Frontend**: Ver templates em `app/templates/`

