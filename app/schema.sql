

/* Esquema SQL para a tabela de Usuários */
drop table if exists Usuarios;
CREATE Table Usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    papel VARCHAR(20) NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

insert into Usuarios (username, password, email, papel) 
    values ('daiana', 'scrypt:32768:8:1$KmDCCXwjs8XLcZFl$d9ad7c4f0370417298a96798d95e0c3aafa64760b38a1e666fb5676b83f7cfa1a2b7d5c25184f3709d979b16f224096d7420d98ba7cdefb584c6f17a0e29883c', 'daiana02@gmail.com', 'admin');   

/* Esquema SQL para a tabela de Alunos */
drop table if exists Alunos;
CREATE Table Alunos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    data_nascimento DATE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telefone VARCHAR(15),
    endereco TEXT,
    data_matricula TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    numero_bilhete VARCHAR(20) UNIQUE NOT NULL,
    genero VARCHAR(10)
);

/* Esquema SQL para a tabela de Professores */
drop table if exists Professores;
CREATE Table Professores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telefone VARCHAR(15),
    departamento VARCHAR(100),
    data_contratacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    numero_bilhete VARCHAR(20) UNIQUE NOT NULL,
    especialidade VARCHAR(100),
    endereco TEXT,
    genero
);

/* Esquema SQL para a tabela de Cursos */
drop table if exists Cursos;
CREATE Table Cursos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    carga_horaria INT NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    professor_id INT REFERENCES Professores(id)
);

/* Esquema SQL para a tabela de Turmas */
drop table if exists Turmas;
CREATE Table Turmas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    curso_id INT REFERENCES Cursos(id),
    trimestre VARCHAR(20) NOT NULL,
    ano INT NOT NULL,
    sala_aula VARCHAR(50)
);

/* Esquema SQL para a tabela de Matrículas */
drop table if exists Matriculas;
CREATE Table Matriculas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INT REFERENCES Alunos(id),
    turma_id INT REFERENCES Turmas(id),
    data_matricula TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'ativa'
);

/* Esquema SQL para a tabela de Notas */
drop table if exists Notas;
CREATE Table Notas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    matricula_id INT REFERENCES Matriculas(id),
    nota DECIMAL(5,2) NOT NULL,
    data_avaliacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo_avaliacao VARCHAR(50) NOT NULL
);

/* Esquema SQL para a tabela de Disciplinas */
drop table if exists Disciplinas;
CREATE Table Disciplinas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    curso_id INT REFERENCES Cursos(id)
);