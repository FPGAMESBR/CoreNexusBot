import unittest
from AppGUI import BotAPI, OrquestradorTickets
import RewardsCore

class TestBotCoordination(unittest.TestCase):
    def test_orquestrador_waits_for_both_tickets(self):
        bot = BotAPI()
        logs = []
        bot.log_ui = lambda msg, tipo="info": logs.append((msg, tipo))

        # Inicia ciclo com 2 tickets
        bot.rodando = True
        bot.orquestrador.iniciar_ciclo()
        bot.orquestrador.registrar_ticket_entrada("bing")
        bot.orquestrador.registrar_ticket_entrada("discord")

        # Bing entrega ticket de saída com sucesso
        bot.orquestrador.registrar_ticket_saida("bing", status="sucesso")

        # Bot deve permanecer rodando pois Discord ainda está em andamento
        self.assertTrue(bot.rodando)
        self.assertNotIn(("FARM COMPLETED SUCCESSFULLY!", "success"), logs)

        # Discord entrega ticket de saída com sucesso
        bot.orquestrador.registrar_ticket_saida("discord", status="sucesso")

        # Agora sim deve finalizar e emitir o aviso de sucesso global
        self.assertFalse(bot.rodando)
        self.assertIn(("FARM COMPLETED SUCCESSFULLY!", "success"), logs)

    def test_orquestrador_handles_error_ticket(self):
        bot = BotAPI()
        logs = []
        bot.log_ui = lambda msg, tipo="info": logs.append((msg, tipo))

        bot.rodando = True
        bot.orquestrador.iniciar_ciclo()
        bot.orquestrador.registrar_ticket_entrada("bing")
        bot.orquestrador.registrar_ticket_entrada("discord")

        # Bing termina com sucesso
        bot.orquestrador.registrar_ticket_saida("bing", status="sucesso")
        self.assertTrue(bot.rodando)

        # Discord termina com erro
        bot.orquestrador.registrar_ticket_saida("discord", status="erro", erro="Conexao perdida")

        # Deve finalizar tudo, mas reportar aviso em vez de sucesso pleno
        self.assertFalse(bot.rodando)
        self.assertFalse(any(tipo == "success" and "FARM COMPLETED SUCCESSFULLY!" in msg for msg, tipo in logs))
        self.assertTrue(any(tipo == "warning" and "FARM FINALIZADO COM AVISOS" in msg for msg, tipo in logs))

    def test_orquestrador_idempotency(self):
        bot = BotAPI()
        logs = []
        bot.log_ui = lambda msg, tipo="info": logs.append((msg, tipo))

        bot.rodando = True
        bot.orquestrador.iniciar_ciclo()
        bot.orquestrador.registrar_ticket_entrada("bing")

        # Múltiplas saídas do mesmo ticket não devem re-executar a finalização
        bot.orquestrador.registrar_ticket_saida("bing", status="sucesso")
        self.assertFalse(bot.rodando)
        sucessos = [msg for msg, tipo in logs if msg == "FARM COMPLETED SUCCESSFULLY!"]
        self.assertEqual(len(sucessos), 1)

        # Segunda chamada ignorada
        bot.orquestrador.registrar_ticket_saida("bing", status="erro", erro="Inesperado")
        self.assertEqual(len([msg for msg, tipo in logs if msg == "FARM COMPLETED SUCCESSFULLY!"]), 1)

if __name__ == '__main__':
    unittest.main()
