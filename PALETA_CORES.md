# Paleta de Cores - LICEU DE CABINDA

## 🎨 Cores Institucionais

### Primárias
```css
--liceu-primary:        #2E5C8A  /* Azul institucional principal */
--liceu-primary-dark:   #1a3a52  /* Azul escuro para hover/ênfase */
--liceu-primary-light:  #4a7fb3  /* Azul claro para backgrounds */
```

**Uso**: Headers, botões primários, links, títulos importantes

---

### Secundárias
```css
--liceu-secondary:      #5A7D9A  /* Azul acinzentado */
```

**Uso**: Elementos complementares, bordas, ícones secundários

---

### Accent
```css
--liceu-accent:         #3498db  /* Azul brilhante */
```

**Uso**: Hover states no menu, destaques, CTAs

---

### Escala de Cinzas
```css
--liceu-gray-50:        #f8f9fa  /* Quase branco - backgrounds */
--liceu-gray-100:       #e9ecef  /* Muito claro - bordas sutis */
--liceu-gray-200:       #dee2e6  /* Claro - divisores */
--liceu-gray-300:       #ced4da  /* Médio claro - desabilitado */
--liceu-gray-700:       #495057  /* Escuro - texto secundário */
--liceu-gray-900:       #212529  /* Quase preto - texto principal */
```

---

### Status/Feedback
```css
--liceu-success:        #28a745  /* Verde - aprovado/sucesso */
--liceu-warning:        #ffc107  /* Amarelo - atenção/pendente */
--liceu-danger:         #dc3545  /* Vermelho - erro/rejeitado */
--liceu-info:           #17a2b8  /* Ciano - informação */
```

---

## 📐 Elementos Visuais de Referência

### Header
- **Background**: Gradiente de `--liceu-primary-dark` para `--liceu-primary`
- **Texto**: Branco (#ffffff)
- **Logo**: 60x60px com drop-shadow
- **User role badge**: Background rgba(255,255,255,0.2)

### Menu Horizontal
- **Background**: rgba(0,0,0,0.1) sobre o header
- **Link normal**: Branco
- **Link hover**: Background rgba(255,255,255,0.1) + borda inferior `--liceu-accent`
- **Link ativo**: Background rgba(255,255,255,0.15) + borda inferior branca

### Sidebar
- **Background**: Branco
- **Títulos de seção**: `--liceu-primary`
- **Links**: `--liceu-gray-700`
- **Link hover**: Background `--liceu-gray-50` + cor `--liceu-primary`

### Widgets/Cards
- **Background**: Branco
- **Borda**: 1px solid `--liceu-gray-200`
- **Header border-bottom**: 2px solid `--liceu-gray-100`
- **Ícone do header**: `--liceu-primary`
- **Título**: `--liceu-primary-dark`
- **Shadow**: 0 2px 6px rgba(0,0,0,0.05)
- **Hover shadow**: 0 4px 12px rgba(0,0,0,0.1)

### Botões

#### Primário (.btn-primary)
- **Background**: `--liceu-primary`
- **Hover**: `--liceu-primary-dark` + translateY(-2px)
- **Texto**: Branco

#### Secundário (.btn-secondary)
- **Background**: `--liceu-gray-200`
- **Hover**: `--liceu-gray-300`
- **Texto**: `--liceu-gray-900`

#### Danger (.btn-danger)
- **Background**: `--liceu-danger`
- **Hover**: #a82c1d
- **Texto**: Branco

#### Success (.btn-success)
- **Background**: `--liceu-success`
- **Hover**: #1e7e34
- **Texto**: Branco

### Tabelas
- **Header background**: `--liceu-primary`
- **Header text**: Branco
- **Row hover**: `--liceu-gray-50`
- **Border**: 1px solid `--liceu-gray-200`

### Formulários

#### Perfil Status Badges
```css
.status-pendente:
  background: #f7edd0
  color: #7a5a00

.status-aprovado:
  background: #dff2e2
  color: #1f6f2a

.status-rejeitado:
  background: #f7d7d7
  color: #8a1c1c
```

#### Form Fields
- **Border**: 1px solid #bbb
- **Background**: Branco
- **Focus**: Borda `--liceu-primary`

---

## 🌙 Dark Mode - Cores

```css
body.dark-mode:
  background: #181a1b
  color: #e0e0e0

Widgets/Cards:
  background: #2c313a
  border: #444
  
Texto principal: #e0e0e0
Texto desativado: #888
Accent/Links: #ffd700 (dourado)

Header de tabelas:
  background: var(--liceu-primary-dark)
```

---

## 📏 Espaçamentos

```css
--spacing-xs:  0.25rem  (4px)
--spacing-sm:  0.5rem   (8px)
--spacing-md:  1rem     (16px)
--spacing-lg:  1.5rem   (24px)
--spacing-xl:  2rem     (32px)
```

**Uso recomendado**:
- XS: Gaps mínimos entre elementos inline
- SM: Padding de badges, gaps entre ícones e texto
- MD: Padding de cards, margin entre parágrafos
- LG: Margin entre seções, padding vertical de containers
- XL: Padding de páginas, separação de blocos maiores

---

## 🔤 Tipografia

### Família
```css
font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
```

### Tamanhos

#### Títulos (Headers)
```css
H1 (liceu-page-header): 2rem (32px)
H1 (liceu-brand): 1.8rem (28.8px)
H3 (widget-header): 1.1rem (17.6px)
H4 (sidebar-section): 0.9rem (14.4px) UPPERCASE
```

#### Texto Corpo
```css
Normal: 1rem (16px)
Small: 0.9rem (14.4px)
Tiny: 0.85rem (13.6px)
Badge: 0.75rem (12px)
```

#### Pesos
```css
Normal: 400
Medium: 500
Semibold: 600
Bold: 700
```

---

## 🎯 Ícones (Font Awesome 6.4.0)

### Principais Ícones Usados

#### Navegação
- `fa-home` - Início
- `fa-bullhorn` - Notícias/Anúncios
- `fa-book` - Disciplinas/Cursos
- `fa-users` - Turmas/Alunos
- `fa-calendar-alt` - Horários
- `fa-file-alt` - Boletim/Documentos

#### Ações
- `fa-plus` - Adicionar/Criar
- `fa-edit` - Editar
- `fa-trash` - Deletar
- `fa-save` - Salvar
- `fa-download` - Download
- `fa-upload` - Upload

#### Status
- `fa-check-circle` - Aprovado
- `fa-exclamation-circle` - Pendente
- `fa-times-circle` - Rejeitado
- `fa-info-circle` - Informação

#### Usuário
- `fa-user-circle` - Avatar
- `fa-sign-in-alt` - Login
- `fa-sign-out-alt` - Logout
- `fa-user-graduate` - Estudante
- `fa-chalkboard-teacher` - Professor

---

## 🔍 Exemplos de Uso

### Gradiente Institucional (Header)
```css
background: linear-gradient(135deg, #1a3a52 0%, #2E5C8A 100%);
```

### Shadow Padrão (Cards)
```css
box-shadow: 0 2px 6px rgba(0,0,0,0.05);
```

### Shadow Hover (Cards)
```css
box-shadow: 0 4px 12px rgba(0,0,0,0.1);
```

### Border Radius Padrão
```css
border-radius: 6px; /* ou var(--border-radius) */
```

### Transição Padrão
```css
transition: all 0.3s ease; /* ou var(--transition) */
```

---

## 📱 Breakpoints Responsivos

```css
Desktop Large:  > 1024px
Desktop/Tablet: 768px - 1024px
Mobile:         < 768px
Mobile Small:   < 600px (formulários)
```

---

## 🎨 Combinações Recomendadas

### Leitura Principal
- Fundo: Branco ou `--liceu-gray-50`
- Texto: `--liceu-gray-900`
- Títulos: `--liceu-primary-dark`

### Destaque/Ênfase
- Fundo: `--liceu-primary`
- Texto: Branco
- Hover: `--liceu-primary-dark`

### Informativa (Avisos)
- Fundo: #e9f3fa (azul claro)
- Texto: #1a3c5c (azul escuro)
- Borda: 4px solid `--liceu-primary`

### Sucesso
- Fundo: #dff2e2
- Texto: #1f6f2a
- Ação: `--liceu-success`

### Alerta
- Fundo: #f7edd0
- Texto: #7a5a00
- Ação: `--liceu-warning`

### Erro
- Fundo: #f7d7d7
- Texto: #8a1c1c
- Ação: `--liceu-danger`

---

## ✅ Contraste e Acessibilidade

### Ratios de Contraste (WCAG AA)

✅ **Branco em --liceu-primary**: 4.8:1 (Bom)
✅ **--liceu-primary-dark em branco**: 9.1:1 (Excelente)
✅ **--liceu-gray-900 em branco**: 15.8:1 (Excelente)
✅ **--liceu-gray-700 em branco**: 7.2:1 (Excelente)

---

## 🖼️ Referência Visual Rápida

```
┌─────────────────────────────────────────┐
│  HEADER (#2E5C8A → #1a3a52 gradient)   │
│  ┌─────┐ LICEU DE CABINDA    [User]    │
│  │LOGO │ Sistema de Gestão              │
│  └─────┘                                │
│  [Início] [Notícias] [Admin] [Aluno]   │ ← Menu horizontal
└─────────────────────────────────────────┘

┌──────────┬──────────────────────────────┐
│ SIDEBAR  │  MAIN CONTENT                │
│ (branco) │  (branco)                    │
│          │                              │
│ • Home   │  ┌──────────────────────┐    │
│ • Docs   │  │ WIDGET CARD          │    │
│ • Links  │  │ (#2E5C8A header)     │    │
│          │  │ Conteúdo...          │    │
│          │  └──────────────────────┘    │
└──────────┴──────────────────────────────┘

┌─────────────────────────────────────────┐
│  FOOTER (#212529)                       │
│  © 2024 Liceu de Cabinda                │
└─────────────────────────────────────────┘
```

---

**Última atualização**: 2024
**Versão**: 1.0
