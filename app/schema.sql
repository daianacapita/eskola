-- ============================================================
-- schema.sql (SQLite) - Plataforma de gestão escolar
-- ============================================================
-- Nota: Em SQLite, as Foreign Keys só funcionam se estiver activo:
PRAGMA foreign_keys = ON;

-- ============================================================
-- DROP (ordem inversa das dependências)
-- ============================================================
DROP TABLE IF EXISTS Anuncios;
DROP TABLE IF EXISTS Presencas;
DROP TABLE IF EXISTS Aulas;
DROP TABLE IF EXISTS Notas;
DROP TABLE IF EXISTS Avaliacoes;
DROP TABLE IF EXISTS Docencia;
DROP TABLE IF EXISTS TurmaDisciplinas;
DROP TABLE IF EXISTS Matriculas;
DROP TABLE IF EXISTS Turmas;
DROP TABLE IF EXISTS Disciplinas;
DROP TABLE IF EXISTS Cursos;
DROP TABLE IF EXISTS AlunoEncarregado;
DROP TABLE IF EXISTS Encarregados;
DROP TABLE IF EXISTS Usuarios;
DROP TABLE IF EXISTS Professores;
DROP TABLE IF EXISTS Alunos;
DROP TABLE IF EXISTS AnoLectivo;

-- ============================================================
-- Tabelas base
-- ============================================================

CREATE TABLE AnoLectivo (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ano INTEGER NOT NULL UNIQUE CHECK(ano >= 2000)
);

CREATE TABLE Cursos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nome TEXT NOT NULL UNIQUE,
  descricao TEXT,
  carga_horaria INTEGER NOT NULL CHECK(carga_horaria > 0)
);

CREATE TABLE Alunos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nome TEXT NOT NULL,
  data_nascimento DATE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  telefone TEXT,
  endereco TEXT,
  data_matricula TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  numero_bilhete TEXT UNIQUE NOT NULL,
  genero TEXT CHECK(genero IN ('M','F','Outro')),
  nome_pai TEXT,
  nome_mae TEXT,
  telefone_encarregado TEXT,
  curso_preferido_id INTEGER REFERENCES Cursos(id),
  ano_preferido INTEGER CHECK(ano_preferido >= 1 AND ano_preferido <= 13)
);

CREATE TABLE Professores (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nome TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  telefone TEXT,
  departamento TEXT,
  data_contratacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  numero_bilhete TEXT UNIQUE NOT NULL,
  especialidade TEXT,
  endereco TEXT,
  genero TEXT CHECK(genero IN ('M','F','Outro'))
);

-- Usuarios (login)
-- Pode estar ligado a um Professor OU a um Aluno (ou nenhum, no caso de admin/secretaria)
CREATE TABLE Usuarios (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL, -- guardar hash (ex: scrypt/pbkdf2/bcrypt), nunca password em texto simples
  email TEXT UNIQUE NOT NULL,
  papel TEXT NOT NULL CHECK(papel IN ('admin','secretaria','professor','aluno')),
  status TEXT NOT NULL DEFAULT 'ativo' CHECK(status IN ('ativo','pendente')),
  professor_id INTEGER REFERENCES Professores(id) ON DELETE SET NULL,
  aluno_id INTEGER REFERENCES Alunos(id) ON DELETE SET NULL,
  data_criacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CHECK (
    (professor_id IS NULL AND aluno_id IS NULL)
    OR (professor_id IS NOT NULL AND aluno_id IS NULL)
    OR (professor_id IS NULL AND aluno_id IS NOT NULL)
  )
);

-- ============================================================
-- Anúncios e Comunicados
-- ============================================================

CREATE TABLE Anuncios (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  titulo TEXT NOT NULL,
  conteudo TEXT NOT NULL,
  data_publicacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  admin_id INTEGER NOT NULL REFERENCES Usuarios(id) ON DELETE CASCADE
);

-- ============================================================
-- Estrutura académica
-- ============================================================

CREATE TABLE Disciplinas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  curso_id INTEGER NOT NULL REFERENCES Cursos(id) ON DELETE CASCADE,
  ano INTEGER NOT NULL CHECK(ano >= 10 AND ano <= 12),
  nome TEXT NOT NULL,
  descricao TEXT,
  UNIQUE (curso_id, ano, nome)
);

CREATE TABLE Turmas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  curso_id INTEGER NOT NULL REFERENCES Cursos(id) ON DELETE RESTRICT,
  ano_lectivo_id INTEGER NOT NULL REFERENCES AnoLectivo(id) ON DELETE RESTRICT,
  ano INTEGER NOT NULL CHECK(ano >= 10 AND ano <= 12),
  sala_aula TEXT,
  designacao TEXT NOT NULL DEFAULT '', -- ex: "10A", "12B" (opcional)
  UNIQUE (curso_id, ano_lectivo_id, ano, designacao)
);


-- Matrículas: ponte Aluno <-> Turma
CREATE TABLE Matriculas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  aluno_id INTEGER NOT NULL REFERENCES Alunos(id) ON DELETE CASCADE,
  turma_id INTEGER NOT NULL REFERENCES Turmas(id) ON DELETE CASCADE,
  data_matricula TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status TEXT NOT NULL DEFAULT 'ativa' CHECK(status IN ('ativa','suspensa','anulada','concluida')),
  UNIQUE (aluno_id, turma_id)
);

-- Disciplinas dadas numa turma (a grelha da turma)
CREATE TABLE TurmaDisciplinas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  turma_id INTEGER NOT NULL REFERENCES Turmas(id) ON DELETE CASCADE,
  disciplina_id INTEGER NOT NULL REFERENCES Disciplinas(id) ON DELETE RESTRICT,
  UNIQUE (turma_id, disciplina_id)
);

-- Quem lecciona o quê (professor por disciplina/turma)
CREATE TABLE Docencia (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  turma_disciplina_id INTEGER NOT NULL
    REFERENCES TurmaDisciplinas(id) ON DELETE CASCADE,
  professor_id INTEGER NOT NULL
    REFERENCES Professores(id) ON DELETE RESTRICT,
  data_inicio DATE NOT NULL DEFAULT CURRENT_DATE,
  data_fim DATE,
  UNIQUE (turma_disciplina_id, professor_id, data_inicio)
);


-- ============================================================
-- Avaliações e Notas
-- ============================================================

CREATE TABLE Avaliacoes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  turma_disciplina_id INTEGER NOT NULL REFERENCES TurmaDisciplinas(id) ON DELETE CASCADE,
  tipo TEXT NOT NULL CHECK(tipo IN ('teste','trabalho','prova','exame','oral','participacao')),
  titulo TEXT,                 -- ex: "Teste 1"
  data DATE NOT NULL,
  peso REAL NOT NULL DEFAULT 1.0 CHECK(peso > 0),
  nota_max REAL NOT NULL DEFAULT 20 CHECK(nota_max > 0)
);

CREATE TABLE Notas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  avaliacao_id INTEGER NOT NULL REFERENCES Avaliacoes(id) ON DELETE CASCADE,
  matricula_id INTEGER NOT NULL REFERENCES Matriculas(id) ON DELETE CASCADE,
  nota REAL NOT NULL CHECK(nota >= 0),
  observacao TEXT,
  criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (avaliacao_id, matricula_id)
);

-- ============================================================
-- Aulas e Presenças (faltas)
-- ============================================================

CREATE TABLE Aulas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  turma_disciplina_id INTEGER NOT NULL REFERENCES TurmaDisciplinas(id) ON DELETE CASCADE,
  data DATE NOT NULL,
  conteudo TEXT,
  UNIQUE (turma_disciplina_id, data)
);

CREATE TABLE Presencas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  aula_id INTEGER NOT NULL REFERENCES Aulas(id) ON DELETE CASCADE,
  matricula_id INTEGER NOT NULL REFERENCES Matriculas(id) ON DELETE CASCADE,
  estado TEXT NOT NULL CHECK(estado IN ('presente','falta','justificada','atraso')),
  observacao TEXT,
  UNIQUE (aula_id, matricula_id)
);

-- ============================================================
-- Encarregados de educação
-- ============================================================

CREATE TABLE Encarregados (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nome TEXT NOT NULL,
  telefone TEXT,
  email TEXT
);

CREATE TABLE AlunoEncarregado (
  aluno_id INTEGER NOT NULL REFERENCES Alunos(id) ON DELETE CASCADE,
  encarregado_id INTEGER NOT NULL REFERENCES Encarregados(id) ON DELETE CASCADE,
  parentesco TEXT, -- ex: "pai", "mãe", "tio", "encarregado"
  principal INTEGER NOT NULL DEFAULT 0 CHECK(principal IN (0,1)),
  PRIMARY KEY (aluno_id, encarregado_id)
);

-- ============================================================
-- Índices (performance)
-- ============================================================

CREATE INDEX idx_turmas_curso_id ON Turmas(curso_id);
CREATE INDEX idx_turmas_ano_lectivo_id ON Turmas(ano_lectivo_id);

CREATE INDEX idx_matriculas_aluno_id ON Matriculas(aluno_id);
CREATE INDEX idx_matriculas_turma_id ON Matriculas(turma_id);

CREATE INDEX idx_disciplinas_curso_id ON Disciplinas(curso_id);
CREATE INDEX idx_disciplinas_curso_ano ON Disciplinas(curso_id, ano);

CREATE INDEX idx_turma_disciplinas_turma_id ON TurmaDisciplinas(turma_id);
CREATE INDEX idx_turma_disciplinas_disciplina_id ON TurmaDisciplinas(disciplina_id);

CREATE INDEX idx_docencia_professor_id ON Docencia(professor_id);
CREATE INDEX idx_docencia_turma_disciplina_id ON Docencia(turma_disciplina_id);

CREATE INDEX idx_avaliacoes_turma_disciplina_id ON Avaliacoes(turma_disciplina_id);
CREATE INDEX idx_notas_avaliacao_id ON Notas(avaliacao_id);
CREATE INDEX idx_notas_matricula_id ON Notas(matricula_id);

CREATE INDEX idx_aulas_turma_disciplina_id ON Aulas(turma_disciplina_id);
CREATE INDEX idx_presencas_aula_id ON Presencas(aula_id);
CREATE INDEX idx_presencas_matricula_id ON Presencas(matricula_id);

CREATE INDEX idx_usuarios_papel ON Usuarios(papel);
CREATE INDEX idx_usuarios_professor_id ON Usuarios(professor_id);
CREATE INDEX idx_usuarios_aluno_id ON Usuarios(aluno_id);

-- ============================================================
-- Seed (opcional): AnoLectivo e admin
-- ============================================================

INSERT INTO AnoLectivo (ano) VALUES (2025), (2026), (2027);

-- Cursos comuns em Angola (Ensino Básico e Secundário)
INSERT INTO Cursos (nome, descricao, carga_horaria) VALUES 
  ('CFB', 'Ciências Físicas e Biológicas', 800),
  ('CEJ', 'Ciências Económicas e Jurídicas', 900),
  ('CHu', 'Ciências Humanas', 1000),
  ('AVi', 'Artes Visuais', 1200);

-- Disciplinas comuns
INSERT INTO Disciplinas (curso_id, ano, nome, descricao) VALUES 
  (1, 10, 'Língua Portuguesa', 'Leitura e escrita'),
  (1, 10, 'Matemática', 'Números e operações básicas'),
  (1, 10, 'Ciências Naturais', 'Natureza e ambiente'),
  (2, 10, 'Língua Portuguesa', 'Gramática e literatura'),
  (2, 10, 'Matemática', 'Geometria e frações'),
  (2, 10, 'História', 'História de Angola'),
  (3, 10, 'Língua Portuguesa', 'Análise textual'),
  (3, 10, 'Matemática', 'Álgebra e estatística'),
  (3, 10, 'Física', 'Conceitos básicos'),
  (3, 10, 'Química', 'Matéria e reações'),
  (3, 10, 'Biologia', 'Vida e ecologia'),
  (3, 10, 'História', 'História mundial'),
  (3, 10, 'Geografia', 'Geografia de Angola'),
  (4, 10, 'Língua Portuguesa', 'Literatura angolana'),
  (4, 10, 'Matemática', 'Cálculo avançado'),
  (4, 10, 'Física', 'Mecânica e eletricidade'),
  (4, 10, 'Química', 'Química orgânica'),
  (4, 10, 'Biologia', 'Genética e evolução'),
  (4, 10, 'História', 'História contemporânea'),
  (4, 10, 'Geografia', 'Geografia mundial'),
  (4, 10, 'Inglês', 'Língua estrangeira'),
  (4, 10, 'Educação Física', 'Saúde e desporto');

INSERT INTO Usuarios (username, password, email, papel)
VALUES (
  'daiana',
  'scrypt:32768:8:1$KmDCCXwjs8XLcZFl$d9ad7c4f0370417298a96798d95e0c3aafa64760b38a1e666fb5676b83f7cfa1a2b7d5c25184f3709d979b16f224096d7420d98ba7cdefb584c6f17a0e29883c',
  'daiana02@gmail.com',
  'admin'
);
