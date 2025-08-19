"""
Testes para a aplicação de exemplo
"""

import pytest
import sys
from pathlib import Path

# Adicionar src ao path para importar o módulo
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pkg.app import add, subtract, multiply, divide, greet, calculate_area

class TestMathFunctions:
    """Testes para funções matemáticas"""
    
    def test_add(self):
        """Testa função de adição"""
        assert add(2, 3) == 5
        assert add(-1, 1) == 0
        assert add(0, 0) == 0
    
    def test_subtract(self):
        """Testa função de subtração"""
        assert subtract(5, 3) == 2
        assert subtract(1, 1) == 0
        assert subtract(0, 5) == -5
    
    def test_multiply(self):
        """Testa função de multiplicação"""
        assert multiply(2, 3) == 6
        assert multiply(-2, 3) == -6
        assert multiply(0, 5) == 0
    
    def test_divide(self):
        """Testa função de divisão"""
        assert divide(6, 2) == 3.0
        assert divide(5, 2) == 2.5
        assert divide(0, 5) == 0.0
    
    def test_divide_by_zero(self):
        """Testa divisão por zero"""
        with pytest.raises(ValueError, match="Divisão por zero não é permitida"):
            divide(5, 0)

class TestStringFunctions:
    """Testes para funções de string"""
    
    def test_greet(self):
        """Testa função de saudação"""
        assert greet("João") == "Olá, João!"
        assert greet("Maria") == "Olá, Maria!"
        assert greet("") == "Olá, !"

class TestGeometryFunctions:
    """Testes para funções geométricas"""
    
    def test_calculate_area(self):
        """Testa cálculo de área do círculo"""
        import math
        assert calculate_area(1) == pytest.approx(math.pi)
        assert calculate_area(2) == pytest.approx(4 * math.pi)
        assert calculate_area(0) == 0.0
