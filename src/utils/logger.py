import logging
import os
from datetime import datetime

# Define o diretório base para os logs
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configuração básica do logger
def setup_logger(name="remodelacao_regioes"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Evita a duplicação de handlers se o logger já foi configurado
    if not logger.handlers:
        # Formato da mensagem de log
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Handler para arquivo
        log_file_name = datetime.now().strftime("remodelacao_regioes_%Y%m%d_%H%M%S.log")
        file_handler = logging.FileHandler(os.path.join(LOG_DIR, log_file_name))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# Exemplo de uso (pode ser removido ou adaptado para testes)
if __name__ == "__main__":
    logger = setup_logger()
    logger.info("Logger configurado com sucesso!")
    logger.debug("Esta é uma mensagem de debug.")
    logger.warning("Esta é uma mensagem de aviso.")
    logger.error("Esta é uma mensagem de erro.")
    logger.critical("Esta é uma mensagem crítica.")
