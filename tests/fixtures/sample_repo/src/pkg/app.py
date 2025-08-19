"""
Aplicação de exemplo para testes
"""

def add(a: int, b: int) -> int:
    """Soma dois números"""
    return a + b

def subtract(a: int, b: int) -> int:
    """Subtrai dois números"""
    return a - b

def multiply(a: int, b: int) -> int:
    """Multiplica dois números"""
    return a * b

def divide(a: int, b: int) -> float:
    """Divide dois números"""
    if b == 0:
        raise ValueError("Divisão por zero não é permitida")
    return a / b

def greet(name: str) -> str:
    """Retorna uma saudação"""
    return f"Olá, {name}!"

def calculate_area(radius: float) -> float:
    """Calcula a área de um círculo"""
    import math
    return math.pi * radius ** 2
