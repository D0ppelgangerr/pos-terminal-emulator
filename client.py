import socket
import datetime
import pyDes  # Для работы с TripleDES
import iso8583
from iso8583.specs import default_ascii as spec

# Константные параметры
SERVER_IP = "127.0.0.1"  # IP-адрес сервера
SERVER_PORT = 12345      # Порт сервера
TERMINAL_ID = "12345678"
TERMINAL_TYPE = "POS"
ENCRYPTION_KEY = bytes.fromhex("0123456789ABCDEFFEDCBA98765432100123456789ABCDEF")

# Функция для формирования PIN-блока (ISO Format 2)
def generate_pin_block(pin, card_number):
    pin_data = f"0{len(pin)}{pin}" + "F" * (14 - len(pin))
    pan_data = card_number[-13:-1].zfill(16)
    pin_block = bytes([int(pin_data[i:i + 2], 16) ^ int(pan_data[i:i + 2], 16) for i in range(0, 16, 2)])
    des = pyDes.triple_des(ENCRYPTION_KEY, pyDes.ECB, pad=None, padmode=pyDes.PAD_NORMAL)
    return des.encrypt(pin_block)

# Формирование ISO8583 сообщения
def create_iso8583(amount, currency, card_number, expiry_date, cvv, pin):
    message = {
        "t": "0200",  # Message Type Indicator (MTI)
        "2": card_number,  # Номер карты
        "3": "000000",     # Код обработки (платеж)
        "4": f"{int(amount * 100):012}",  # Сумма в минимальных единицах
        "7": datetime.datetime.now().strftime("%m%d%H%M%S"),  # Дата/время транзакции
        "11": "000001",    # Уникальный номер
        "14": expiry_date,  # Срок действия карты
        "22": TERMINAL_TYPE,  # Тип терминала
        "35": cvv,  # Track2
        "41": TERMINAL_ID,  # Номер терминала
        "52": generate_pin_block(pin, card_number).hex(),  # PIN-блок
    }
    return message

# Основная функция клиента
def terminal_client():
    amount = float(input("Введите сумму платежа: "))
    currency = input("Введите валюту платежа (например, RUB): ")
    card_number = input("Введите номер карты: ")
    expiry_date = input("Введите срок действия карты (MMYY): ")
    cvv = input("Введите CVV1 (Track2): ")
    pin = input("Введите PIN-код карты: ")

    try:
        # Создаем и кодируем ISO8583 сообщение
        iso_message = create_iso8583(amount, currency, card_number, expiry_date, cvv, pin)
        encoded_message, encoded_data = iso8583.encode(iso_message, spec)
        print("Сформированное сообщение ISO8583:")
        iso8583.pp(iso_message, spec)
    except iso8583.DecodeError as e:
        print(f"Ошибка при формировании ISO8583 сообщения: {e}")
        return

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((SERVER_IP, SERVER_PORT))
        print("Соединение с сервером установлено.")
        client_socket.sendall(encoded_message)  # Отправляем закодированное сообщение
        response = client_socket.recv(1024)    # Получаем ответ
        try:
            decoded_response, _ = iso8583.decode(response, spec)
            print("Ответ сервера:")
            iso8583.pp(decoded_response, spec)
        except iso8583.DecodeError as e:
            print(f"Ошибка декодирования ответа сервера: {e}")

if __name__ == "__main__":
    terminal_client()
