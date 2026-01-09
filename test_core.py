import unittest
from unittest.mock import patch, MagicMock
import app

class TestMoneyLayerLogic(unittest.TestCase):

    # Teste: A matemática dos 5% está correta?
    @patch('app.get_db_connection') 
    def test_calculo_social(self, mock_db_conn):
        
        # Configura o "Banco de Mentira"
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db_conn.return_value = mock_conn
        
        # EXECUTAR: Simula uma venda de R$ 100,00
        print("⚡ Simulando venda de R$ 100,00...")
        app.registrar_pagamento_real(100.00, "cliente_teste@email.com")
        
        # VERIFICAR: O sistema tentou gravar R$ 5,00 no Social?
        chamadas = mock_cursor.execute.call_args_list
        
        # A segunda chamada ao banco deve ser a do Social
        # args_social pega os argumentos da query SQL
        args_social = chamadas[1][0] 
        # valores_social pega os valores passados (%s)
        valores_social = args_social[1] 
        
        valor_calculado = valores_social[0]
        
        self.assertEqual(valor_calculado, 5.00)
        print(f"✅ SUCESSO: Venda de 100.00 gerou Social de {valor_calculado} (Esperado: 5.0)")

if __name__ == '__main__':
    unittest.main()
