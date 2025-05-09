# Эмулятор платежного терминала
Клиент-серверный эмулятор для демонстрации ISO8583 на основе локальных сокетных соединений.
Клиент обеспечивает ввод следующих данных:
1. Сумма платежа
2. Валюта платежа
3. Номер карты, осуществляющей платеж
4. Срок окончания действия карты
5. CVV1 (Track2)
6. ПИН-код карты

Клиент автоматически получает текущую дату/время транзакции, для формирования сообщения ISO8583.
В качестве константных параметров используются: IP-адрес и порт сервера, ID и тип терминала.

Сервер в качестве константных параметров использует номера карт с положительным и нулевым балансом.

ПИН-блок формируется по ISO Format 2, в качестве ключа шифрования ПИН-блока используется стандартный ключ ```0123456789ABCDEFFEDCBA98765432100123456789ABCDEF```, алгоритм шифрования 3DES.
