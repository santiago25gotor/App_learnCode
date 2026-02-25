EXAMS = {
    'Python Básico': {
        'id': 'exam_basico',
        'title': 'Examen: Python Básico',
        'description': 'Demuestra tu conocimiento en fundamentos de Python',
        'time_limit': 30,
        'passing_score': 70,
        'questions': [
            {
                'id': 'q1',
                'type': 'multiple_choice',
                'question': '¿Cuál es la salida de: print(type(5))?',
                'options': ["<class 'int'>", "<class 'float'>", "<class 'str'>", '5'],
                'correct': 0,
                'points': 10
            },
            {
                'id': 'q2',
                'type': 'code',
                'question': 'Escribe una función que sume dos números',
                'starter_code': 'def sumar(a, b):\n    # Tu código aquí\n    pass',
                'test_cases': [
                    {'input': [2, 3], 'expected': 5},
                    {'input': [10, 5], 'expected': 15},
                    {'input': [-1, 1], 'expected': 0}
                ],
                'points': 20
            }
        ]
    },
    'Python Intermedio': {
        'id': 'exam_intermedio',
        'title': 'Examen: Python Intermedio',
        'description': 'Evalúa tus habilidades en estructuras de datos',
        'time_limit': 45,
        'passing_score': 75,
        'questions': [
            {
                'id': 'q1',
                'type': 'code',
                'question': 'Crea una función que filtre números pares',
                'starter_code': 'def filtrar_pares(lista):\n    # Tu código aquí\n    pass',
                'test_cases': [
                    {'input': [[1,2,3,4,5,6]], 'expected': [2,4,6]}
                ],
                'points': 25
            }
        ]
    },
    'Python Avanzado': {
        'id': 'exam_avanzado',
        'title': 'Examen: Python Avanzado',
        'description': 'Demuestra dominio en programación avanzada',
        'time_limit': 60,
        'passing_score': 80,
        'questions': [
            {
                'id': 'q1',
                'type': 'code',
                'question': 'Implementa un decorador',
                'starter_code': 'def decorador(func):\n    # Tu código aquí\n    pass',
                'test_cases': [],
                'points': 30
            }
        ]
    }
}