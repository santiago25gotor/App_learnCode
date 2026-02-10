/* =====================================================================
   PLATAFORMA LEARNING PYTHON - MySQL
===================================================================== */

-- ============================================
-- 1. USUARIOS Y ROLES
-- ============================================
CREATE TABLE alumno (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 2. ESTRUCTURA DEL CURSO
-- ============================================
CREATE TABLE temario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    nivel VARCHAR(20) CHECK (nivel IN ('Basico', 'Intermedio', 'Avanzado')),
    orden INT NOT NULL
);

-- ============================================
-- 3. CONTENIDO TEÓRICO
-- ============================================
CREATE TABLE teoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    temario_id INT NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    contenido TEXT NOT NULL,
    FOREIGN KEY (temario_id) REFERENCES temario(id) ON DELETE CASCADE
);

-- ============================================
-- 4. DEFINICIÓN DE ACTIVIDADES
-- ============================================
CREATE TABLE actividad_def (
    id INT AUTO_INCREMENT PRIMARY KEY,
    temario_id INT NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    enunciado_md TEXT NOT NULL,
    respuesta_alumno TEXT,
    respuesta_ia TEXT NOT NULL,
    puntos_maximos DECIMAL(5,2) DEFAULT 10.0,
    FOREIGN KEY (temario_id) REFERENCES temario(id) ON DELETE CASCADE
);

-- ============================================
-- 5. DEFINICIÓN DE EXÁMENES
-- ============================================
CREATE TABLE examen_def (
    id INT AUTO_INCREMENT PRIMARY KEY,
    temario_id INT NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    duracion_minutos INT NOT NULL,
    nota_aprobatoria DECIMAL(5,2) DEFAULT 5.0,
    FOREIGN KEY (temario_id) REFERENCES temario(id) ON DELETE CASCADE
);

-- ============================================
-- 6. PROGRESO GLOBAL
-- ============================================
CREATE TABLE progreso_global (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alumno_id INT NOT NULL,
    temario_id INT NOT NULL,
    estado VARCHAR(20) CHECK (estado IN ('BLOQUEADO', 'EN CURSO', 'COMPLETADO', 'CONVALIDADO')),
    fecha_convalidacion TIMESTAMP NULL,
    progreso INT,
    UNIQUE KEY unique_alumno_temario (alumno_id, temario_id),
    FOREIGN KEY (alumno_id) REFERENCES alumno(id) ON DELETE CASCADE,
    FOREIGN KEY (temario_id) REFERENCES temario(id) ON DELETE CASCADE
);

-- ============================================
-- 7. INTENTOS DE ACTIVIDAD
-- ============================================
CREATE TABLE intento_actividad (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alumno_id INT NOT NULL,
    actividad_def_id INT NOT NULL,
    codigo_alumno_snapshot TEXT NOT NULL,
    actividad_completada BOOLEAN NOT NULL,
    output_consola TEXT,
    nota_obtenida DECIMAL(5,2),
    fecha_intento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alumno_id) REFERENCES alumno(id) ON DELETE CASCADE,
    FOREIGN KEY (actividad_def_id) REFERENCES actividad_def(id) ON DELETE CASCADE
);

-- ============================================
-- 8. REGISTRO DE EXAMEN
-- ============================================
CREATE TABLE registro_examen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alumno_id INT NOT NULL,
    examen_def_id INT NOT NULL,
    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TIMESTAMP NULL,
    nota_final DECIMAL(5,2),
    estado VARCHAR(20) CHECK (estado IN ('EN_PROGRESO', 'FINALIZADO', 'EXPIRADO')),
    FOREIGN KEY (alumno_id) REFERENCES alumno(id) ON DELETE CASCADE,
    FOREIGN KEY (examen_def_id) REFERENCES examen_def(id) ON DELETE CASCADE
);
