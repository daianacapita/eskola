/* Esquema SQL para a tabela de Alunos */
CREATE Table Alunos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    data_nascimento DATE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telefone VARCHAR(15),
    endereco TEXT,
    data_matricula TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    numero_bilhete VARCHAR(20) UNIQUE NOT NULL
);

/* Esquema SQL para a tabela de Professores */
CREATE Table Professores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telefone VARCHAR(15),
    departamento VARCHAR(100),
    data_contratacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    numero_bilhete VARCHAR(20) UNIQUE NOT NULL,
    especialidade VARCHAR(100),
    endereco TEXT
);

/* Esquema SQL para a tabela de Cursos */
CREATE Table Cursos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    carga_horaria INT NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    professor_id INT REFERENCES Professores(id)
);

/* Esquema SQL para a tabela de Turmas */
CREATE Table Turmas (
    id SERIAL PRIMARY KEY,
    curso_id INT REFERENCES Cursos(id),
    trimestre VARCHAR(20) NOT NULL,
    ano INT NOT NULL,
    sala_aula VARCHAR(50)
);