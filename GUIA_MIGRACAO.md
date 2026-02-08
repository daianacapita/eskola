# Guia Rápido de Migração para o Novo Design

## 🎯 Objetivo
Este guia mostra como migrar páginas existentes para o novo layout institucional do LICEU DE CABINDA de forma simples e gradual.

---

## ⚡ Migração Básica (5 minutos)

### Passo 1: Estrutura Mínima
Toda página que estende `base.html` já tem o novo layout automaticamente!

**ANTES:**
```jinja
{% extends 'base.html' %}
{% block content %}
  <h2>Minha Página</h2>
  <p>Conteúdo...</p>
{% endblock %}
```

**DEPOIS (mínimo):**
```jinja
{% extends 'base.html' %}

{% block title %}Minha Página{% endblock %}

{% block content %}
<div class="liceu-page-header">
  <h1>Minha Página</h1>
</div>

<div class="liceu-content">
  <p>Conteúdo...</p>
</div>
{% endblock %}
```

✅ **Resultado**: Página já funciona com o novo header, menu e sidebar!

---

## 🎨 Migração com Widgets (15 minutos)

### Passo 2: Usar Widgets para Organizar Conteúdo

**ANTES (HTML simples):**
```html
<div style="border:1px solid #ccc; padding:10px;">
  <h3>Notícias</h3>
  <ul>
    {% for item in items %}
      <li>{{ item.titulo }}</li>
    {% endfor %}
  </ul>
</div>
```

**DEPOIS (com widgets):**
```jinja
{% from "_widgets.html" import widget_card %}

{% call widget_card('fa-bullhorn', 'Notícias') %}
  <ul class="widget-list">
    {% for item in items %}
      <li>{{ item.titulo }}</li>
    {% endfor %}
  </ul>
{% endcall %}
```

### Widgets Disponíveis

#### 1. Widget Card Genérico
```jinja
{% call widget_card('fa-icon', 'Título do Card') %}
  <p>Qualquer conteúdo HTML aqui...</p>
{% endcall %}
```

#### 2. Widget de Avisos/Notícias
```jinja
{{ widget_avisos(lista_noticias, max=5) }}
```

#### 3. Widget de Links Rápidos
```jinja
{% set links = [
  {'url': '/rota1', 'icon': 'fa-home', 'text': 'Início'},
  {'url': '/rota2', 'icon': 'fa-book', 'text': 'Livros'}
] %}
{{ widget_quick_links(links) }}
```

#### 4. Widget de Estatísticas
```jinja
{% set stats = [
  {'icon': 'fa-users', 'label': 'Alunos', 'value': 150},
  {'icon': 'fa-book', 'label': 'Cursos', 'value': 12}
] %}
{{ widget_stats(stats) }}
```

---

## 📊 Migração de Tabelas

**ANTES:**
```html
<table>
  <tr>
    <th>Nome</th>
    <th>Nota</th>
  </tr>
  <tr>
    <td>João</td>
    <td>15</td>
  </tr>
</table>
```

**DEPOIS (usando classes do novo CSS):**
```html
<table style="width: 100%; border-collapse: collapse;">
  <thead>
    <tr style="background: var(--liceu-primary); color: white;">
      <th style="padding: var(--spacing-md);">Nome</th>
      <th style="padding: var(--spacing-md);">Nota</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border-bottom: 1px solid var(--liceu-gray-200);">
      <td style="padding: var(--spacing-md);">João</td>
      <td style="padding: var(--spacing-md);">15</td>
    </tr>
  </tbody>
</table>
```

**OU dentro de um widget:**
```jinja
{% call widget_card('fa-table', 'Tabela de Notas') %}
  <table>
    <!-- Tabela aqui -->
  </table>
{% endcall %}
```

---

## 🎨 Migração de Botões

**ANTES:**
```html
<button style="background: blue; color: white;">Salvar</button>
```

**DEPOIS:**
```html
<button class="btn btn-primary">
  <i class="fa fa-save"></i> Salvar
</button>
```

### Classes de Botões:
- `.btn .btn-primary` - Azul institucional
- `.btn .btn-secondary` - Cinza neutro
- `.btn .btn-danger` - Vermelho (ações perigosas)
- `.btn .btn-success` - Verde (sucesso)

---

## 📋 Migração de Formulários

Os formulários **já funcionam** sem alterações!

Mas você pode melhorar usando as classes existentes:

```html
<div class="form-preinscricao">
  <fieldset class="grupo-form">
    <legend>Dados Pessoais</legend>
    
    <label for="nome">Nome Completo:</label>
    <input type="text" id="nome" name="nome" required>
    
    <label for="email">Email:</label>
    <input type="email" id="email" name="email" required>
  </fieldset>
  
  <input type="submit" value="Enviar">
</div>
```

✅ Estilos `.form-preinscricao` e `.grupo-form` **já existem** e estão integrados!

---

## 🔄 Exemplo Completo de Migração

### ANTES (página antiga):
```jinja
{% extends 'base.html' %}
{% block content %}
<h2>Meus Cursos</h2>

<div style="border: 1px solid #ccc; padding: 10px;">
  <h3>Lista de Cursos</h3>
  <ul>
    {% for curso in cursos %}
      <li>{{ curso.nome }}</li>
    {% endfor %}
  </ul>
  <a href="{{ url_for('criar_curso') }}">Criar Novo</a>
</div>

<div style="margin-top: 20px; background: #f0f0f0; padding: 10px;">
  <h3>Estatísticas</h3>
  <p>Total: {{ cursos|length }}</p>
</div>
{% endblock %}
```

### DEPOIS (página nova):
```jinja
{% extends 'base.html' %}
{% from "_widgets.html" import widget_card, widget_stats %}

{% block title %}Meus Cursos{% endblock %}

{% block content %}
<div class="liceu-page-header">
  <h1>Meus Cursos</h1>
</div>

<div class="liceu-content">
  
  {# Estatísticas #}
  {% set stats = [
    {'icon': 'fa-graduation-cap', 'label': 'Total de Cursos', 'value': cursos|length}
  ] %}
  {{ widget_stats(stats) }}
  
  {# Lista de Cursos #}
  {% call widget_card('fa-list', 'Lista de Cursos') %}
    <ul class="widget-list">
      {% for curso in cursos %}
        <li>
          <a href="{{ url_for('ver_curso', id=curso.id) }}">
            {{ curso.nome }}
          </a>
        </li>
      {% endfor %}
    </ul>
    
    <a href="{{ url_for('criar_curso') }}" class="widget-link">
      <i class="fa fa-plus"></i> Criar Novo Curso
    </a>
  {% endcall %}
  
</div>
{% endblock %}
```

---

## 🎯 Classes CSS Úteis

### Variáveis CSS (use em inline styles):
```css
var(--liceu-primary)      /* Azul institucional */
var(--liceu-gray-50)      /* Cinza muito claro */
var(--liceu-gray-200)     /* Cinza claro */
var(--spacing-sm)         /* 0.5rem */
var(--spacing-md)         /* 1rem */
var(--spacing-lg)         /* 1.5rem */
var(--border-radius)      /* 6px */
```

### Utility Classes:
```html
<p class="text-center">Texto centralizado</p>
<span class="text-muted">Texto esmaecido</span>

<div class="mt-2">Margin top médio</div>
<div class="mb-3">Margin bottom grande</div>
<div class="p-2">Padding médio</div>
```

---

## 📱 Testar Responsividade

Depois de migrar, teste em:
- **Desktop** (>1024px): Sidebar ao lado
- **Tablet** (768-1024px): Sidebar acima
- **Mobile** (<768px): Menu hamburger

---

## ✅ Checklist de Migração

Para cada página:

- [ ] Adicionar `{% block title %}`
- [ ] Envolver título em `<div class="liceu-page-header"><h1>...</h1></div>`
- [ ] Envolver conteúdo em `<div class="liceu-content">...</div>`
- [ ] Substituir `<div>` simples por widgets (`widget_card`)
- [ ] Usar classes `.btn .btn-primary` nos botões
- [ ] Usar variáveis CSS em vez de cores hard-coded
- [ ] Adicionar ícones Font Awesome onde apropriado
- [ ] Testar em mobile

---

## 🚀 Dicas de Performance

1. **Widgets são macros Jinja2** - Não há overhead de performance
2. **CSS usa variáveis nativas** - Rápido e leve
3. **Minimize uso de inline styles** - Prefira classes quando possível
4. **Lazy loading** - Já implementado no CSS

---

## 📚 Referências

- **Documentação completa**: `REDESIGN_INSTITUCIONAL.md`
- **Exemplo prático**: `student_area_EXEMPLO_NOVO_DESIGN.html`
- **Widgets**: `app/templates/_widgets.html`
- **CSS**: `app/static/style.css` (procure comentários `/* === */`)

---

## ❓ FAQ

**P: Preciso migrar tudo de uma vez?**
R: Não! O layout antigo e novo coexistem. Migre gradualmente.

**P: Posso misturar estilos antigos e novos?**
R: Sim, mas evite para manter consistência visual.

**P: E se eu não quiser usar widgets?**
R: Pode usar apenas as classes `.liceu-*` diretamente no HTML.

**P: Como adiciono novos widgets?**
R: Edite `_widgets.html` e crie um novo macro seguindo os exemplos.

---

**Última atualização**: 2024
**Versão do guia**: 1.0
