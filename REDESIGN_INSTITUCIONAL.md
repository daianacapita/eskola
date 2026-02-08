# Redesign Institucional - LICEU DE CABINDA

## 📋 Resumo das Alterações

Este documento descreve o redesign completo da interface do sistema para refletir a identidade institucional do **LICEU DE CABINDA**.

---

## 🎨 Novo Design

### Cores Institucionais
- **Primária**: `#2E5C8A` (Azul institucional)
- **Primária Escura**: `#1a3a52`
- **Primária Clara**: `#4a7fb3`
- **Secundária**: `#5A7D9A`
- **Accent**: `#3498db`
- **Cinzas**: `#f8f9fa` até `#212529`

### Layout
O novo layout consiste em:
1. **Header Superior** - Logo + Branding + Informações do Usuário
2. **Menu Horizontal** - Navegação principal com dropdowns
3. **Sidebar Esquerda** - Links rápidos e atalhos contextuais
4. **Área de Conteúdo** - Breadcrumbs + Conteúdo principal
5. **Footer** - Informações de copyright

---

## 📁 Arquivos Modificados

### 1. `app/static/style.css` ✅
**Status**: Completamente redesenhado

**Principais mudanças**:
- CSS Variables para cores institucionais
- Classes do novo layout (`.liceu-header`, `.liceu-nav`, `.liceu-sidebar`, `.liceu-main`)
- Estilos para widgets/cards reutilizáveis
- Sistema responsivo completo
- Dark mode atualizado
- Preservados estilos de formulários, perfil, tabelas

**Estrutura**:
```css
/* Seções principais */
- Reset & Base
- Header Institucional
- Menu Horizontal (com dropdowns)
- Container Layout
- Sidebar Esquerda
- Main Content
- Footer
- Widgets/Cards
- Formulários (Pré-inscrição)
- Perfil de Estudante
- Botões
- Breadcrumbs
- Tabelas
- Toast/Flash Messages
- Old Sidebar Layout (Legacy - compatibilidade)
- Dark Mode
- Responsividade
- Utility Classes
```

### 2. `app/static/sidebar.js` ✅
**Status**: Atualizado

**Novas funcionalidades**:
- `toggleMobileNav()` - Controla menu horizontal em dispositivos móveis
- Auto-close do menu mobile ao clicar em links
- Mantidas funções originais (toasts, dark mode, filter, accordion)

### 3. `app/static/logo_liceu.svg` ✅
**Status**: Criado

Logo institucional SVG com:
- Círculo azul institucional
- Ícone de prédio escolar
- Texto "LICEU"
- Tamanho: 100x100px

### 4. `app/templates/base.html` ✅
**Status**: Completamente redesenhado

**Nova estrutura HTML**:
```html
<body class="liceu-layout">
  <header class="liceu-header">
    <div class="liceu-header-top">
      <!-- Logo + Branding + User Info -->
    </div>
    <nav class="liceu-nav">
      <!-- Menu horizontal com dropdowns -->
    </nav>
  </header>
  
  <div class="liceu-container">
    <aside class="liceu-sidebar">
      <!-- Links rápidos contextuais -->
    </aside>
    
    <main class="liceu-main">
      <div class="liceu-breadcrumbs">...</div>
      <div class="liceu-content">
        {% block content %}{% endblock %}
      </div>
    </main>
  </div>
  
  <footer class="liceu-footer">...</footer>
</body>
```

### 5. `app/templates/_widgets.html` ✅
**Status**: Criado

**Macros disponíveis**:
- `widget_card(icon, title)` - Card genérico com header
- `widget_horario(horario)` - Widget de horário de aulas
- `widget_avisos(avisos, max=5)` - Widget de notícias/avisos
- `widget_turmas(turmas)` - Widget de turmas do aluno
- `widget_stats(stats)` - Widget de estatísticas numéricas
- `widget_quick_links(links)` - Grid de links rápidos

**Uso**:
```jinja
{% from "_widgets.html" import widget_card %}

{% call widget_card('fa-book', 'Minhas Disciplinas') %}
  <p>Conteúdo aqui...</p>
{% endcall %}
```

### 6. `app/templates/index.html` ✅
**Status**: Redesenhado com widgets

Agora usa:
- `widget_avisos()` para exibir notícias
- `widget_card()` para informações do sistema
- `widget_quick_links()` para atalhos principais

---

## 📱 Responsividade

### Breakpoints
- **Desktop**: > 1024px - Layout completo com sidebar
- **Tablet**: 768px - 1024px - Sidebar vira bloco superior
- **Mobile**: < 768px - Menu hamburger, layout vertical

### Comportamentos Mobile
- Menu horizontal vira menu toggle
- Sidebar fica em bloco acima do conteúdo
- Widgets stackam verticalmente
- Logo e branding redimensionam

---

## 🔧 Como Usar

### Para Desenvolvedores

#### Criar uma nova página com o layout institucional:
```jinja
{% extends "base.html" %}

{% block title %}Minha Página{% endblock %}

{% block content %}
  <div class="liceu-page-header">
    <h1>Título da Página</h1>
  </div>
  
  <div class="liceu-content">
    <!-- Seu conteúdo aqui -->
  </div>
{% endblock %}
```

#### Usar widgets:
```jinja
{% from "_widgets.html" import widget_card, widget_avisos %}

{% call widget_card('fa-calendar', 'Meu Calendário') %}
  <p>Eventos desta semana...</p>
{% endcall %}

{{ widget_avisos(lista_noticias) }}
```

#### Adicionar links ao menu horizontal:
Edite `app/templates/base.html`, seção `<nav class="liceu-nav">`:
```html
<li><a href="{{ url_for('minha_rota') }}">
  <i class="fa fa-icon"></i> Meu Link
</a></li>
```

#### Adicionar links à sidebar:
Edite `app/templates/base.html`, seção `<aside class="liceu-sidebar">`:
```html
<li><a href="{{ url_for('rota') }}">
  <i class="fa fa-icon"></i> Link Rápido
</a></li>
```

---

## 🎯 Componentes Principais

### Botões
```html
<button class="btn btn-primary">Primário</button>
<button class="btn btn-secondary">Secundário</button>
<button class="btn btn-danger">Perigo</button>
<button class="btn btn-success">Sucesso</button>
```

### Cards/Widgets
```html
<div class="widget-card">
  <div class="widget-header">
    <i class="fa fa-icon"></i>
    <h3>Título</h3>
  </div>
  <div class="widget-body">
    Conteúdo...
  </div>
</div>
```

### Breadcrumbs (novo estilo)
```html
<div class="liceu-breadcrumbs">
  <a href="/">Início</a>
  <i class="fa fa-chevron-right"></i>
  <span>Página Atual</span>
</div>
```

---

## 🌙 Dark Mode

O dark mode está **preservado e atualizado**:
- Cores ajustadas para o novo tema institucional
- Widgets e cards com fundo escuro
- Toggle button mantido (#darkmode-toggle)
- Persistência via localStorage

---

## ✅ Checklist de Implementação

- [x] CSS institucional completo
- [x] Variáveis CSS para cores
- [x] Header com logo e branding
- [x] Menu horizontal com dropdowns
- [x] Sidebar com links rápidos
- [x] Footer institucional
- [x] Widgets/macros reutilizáveis
- [x] Responsividade mobile
- [x] Dark mode atualizado
- [x] Compatibilidade com páginas existentes (formulários, perfil)
- [x] Logo SVG institucional
- [x] JavaScript para mobile navigation
- [x] Página index redesenhada como exemplo

---

## 🔄 Compatibilidade

### Páginas que ainda usam o layout antigo:
Todas as páginas que estendem `base.html` **automaticamente** ganham o novo layout.

### Estilos preservados:
- `.form-preinscricao` - Formulários de pré-inscrição
- `.grupo-form` - Grupos de campos
- `.perfil-*` - Todos os estilos de perfil
- `.sidebar` (legacy) - Sidebar antiga para compatibilidade
- `.main-content` (legacy) - Container antigo
- Tabelas, botões, breadcrumbs

### Migração gradual:
É possível manter páginas com o layout antigo simplesmente não usando as classes `.liceu-*`.

---

## 📊 Melhorias de UX

1. **Navegação mais clara** - Menu horizontal intuitivo
2. **Identidade visual forte** - Logo e cores institucionais
3. **Informação contextual** - Sidebar com atalhos relevantes
4. **Hierarquia visual** - Headers, breadcrumbs, títulos bem definidos
5. **Responsividade** - Funciona em todos os dispositivos
6. **Widgets reutilizáveis** - Facilita criação de dashboards

---

## 🚀 Próximos Passos Sugeridos

1. **Atualizar dashboards** - Usar widgets nas áreas de Admin, Professor e Aluno
2. **Criar mais widgets** - Para gráficos, calendário, etc.
3. **Personalizar sidebar** - Conteúdo dinâmico baseado no papel do usuário
4. **Adicionar animações** - Transições suaves nos widgets
5. **Otimizar imagens** - Compressão do logo SVG
6. **Testes de acessibilidade** - ARIA labels, contraste de cores

---

## 📝 Notas Técnicas

- **Font Awesome 6.4.0** usado para ícones
- **CSS Grid e Flexbox** para layouts
- **CSS Variables** para fácil customização
- **Mobile-first approach** na responsividade
- **Sem frameworks CSS** - Código vanilla otimizado
- **Compatibilidade**: Navegadores modernos (Chrome, Firefox, Safari, Edge)

---

## 👥 Créditos

Redesign institucional implementado para refletir a identidade visual do **LICEU DE CABINDA**.

**Data de implementação**: 2024
**Versão**: 1.0

---

## 📞 Suporte

Para dúvidas ou problemas com o novo layout, consulte:
- Este documento (REDESIGN_INSTITUCIONAL.md)
- Código comentado em `style.css`
- Exemplos em `_widgets.html` e `index.html`
