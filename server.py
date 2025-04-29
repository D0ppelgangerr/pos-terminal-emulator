import socket
import iso8583
from iso8583.specs import default_ascii as spec

# Константные параметры
SERVER_IP = "0.0.0.0"
SERVER_PORT = 12345

# Карты для тестирования
POSITIVE_CARD = "4111111111111111"  # Карта с положительным балансом
NEGATIVE_CARD = "4222222222222222"  # Карта с нулевым балансом

# Формирование ответа ISO8583
def create_response(decoded_request):
    response = {}
    response["t"] = "0210"  # Response Message Type Indicator (MTI)
    response["2"] = decoded_request["2"]  # Номер карты
    response["3"] = decoded_request["3"]  # Код обработки
    response["4"] = decoded_request["4"]  # Сумма
    response["11"] = decoded_request["11"]  # Уникальный номер

    # Анализ номера карты для определения статуса
    if decoded_request["2"] == POSITIVE_CARD:
        response["39"] = "00"  # Успешное завершение транзакции
    elif decoded_request["2"] == NEGATIVE_CARD:
        response["39"] = "51"  # Недостаточно средств
    else:
        response["39"] = "14"  # Неверный номер карты

    return response

# Основная функция сервера
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((SERVER_IP, SERVER_PORT))
        server_socket.listen(5)
        print(f"Сервер запущен и слушает порт {SERVER_PORT}...")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Подключен клиент: {client_address}")
            with client_socket:
                try:
                    # Принимаем данные от клиента
                    encoded_request = client_socket.recv(1024)
                    print(f"Получено сообщение от клиента (raw): {encoded_request}")

                    # Декодируем сообщение клиента
                    decoded_request, _ = iso8583.decode(encoded_request, spec)
                    print("Декодированное сообщение от клиента:")
                    iso8583.pp(decoded_request, spec)

                    # Формируем ответное сообщение
                    decoded_response = create_response(decoded_request)
                    encoded_response, _ = iso8583.encode(decoded_response, spec)

                    # Отправляем ответ клиенту
                    client_socket.sendall(encoded_response)
                    print("Ответ отправлен клиенту.")
                    iso8583.pp(decoded_response, spec)

                except iso8583.DecodeError as e:
                    print(f"Ошибка декодирования сообщения: {e}")
                    client_socket.close()
                except Exception as e:
                    print(f"Общая ошибка: {e}")
                    client_socket.close()

if __name__ == "__main__":
    start_server()
