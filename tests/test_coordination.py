import unittest
from AppGUI import BotAPI
import RewardsCore

class TestBotCoordination(unittest.TestCase):
    def test_checar_fim_geral_waits_for_both(self):
        bot = BotAPI()
        logs = []
        bot.log_ui = lambda msg, tipo="info": logs.append((msg, tipo))

        # Cenário 1: Bing termina mas Discord continua rodando
        bot.rodando = True
        bot.bing_rodando = False
        bot.discord_rodando = True
        bot.checar_fim_geral()

        # O bot ainda deve permanecer rodando e não deve emitir a mensagem final verde
        self.assertTrue(bot.rodando)
        self.assertNotIn(("FARM COMPLETED SUCCESSFULLY!", "success"), logs)

        # Cenário 2: Discord também termina
        bot.discord_rodando = False
        bot.checar_fim_geral()

        # Agora sim deve finalizar e emitir FARM COMPLETED SUCCESSFULLY!
        self.assertFalse(bot.rodando)
        self.assertIn(("FARM COMPLETED SUCCESSFULLY!", "success"), logs)

    def test_checar_fim_geral_discord_first(self):
        bot = BotAPI()
        logs = []
        bot.log_ui = lambda msg, tipo="info": logs.append((msg, tipo))

        # Cenário: Discord termina mas Bing continua rodando
        bot.rodando = True
        bot.bing_rodando = True
        bot.discord_rodando = False
        bot.checar_fim_geral()

        self.assertTrue(bot.rodando)
        self.assertNotIn(("FARM COMPLETED SUCCESSFULLY!", "success"), logs)

        # Bing termina depois
        bot.bing_rodando = False
        bot.checar_fim_geral()

        self.assertFalse(bot.rodando)
        self.assertIn(("FARM COMPLETED SUCCESSFULLY!", "success"), logs)

if __name__ == '__main__':
    unittest.main()
