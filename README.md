# lock-sensors

## Done
- Инфраструктура docker контейнеров
- Инфраструктура для тестирования
- Тестовый стенд ряботы с RabbitMQ

## TODO
- Сборщик состояний от сенсоров
- Рассылка уведомлений
- История состояний

## Задача

Cервис принимает данные от датчиков закрытия дверных замков через RabbitMQ и отправляет пользователям уведомления об изменении статуса. Так-же сервис ведет историю принятых данных и отправленных уведомлений и позволяет регистрировать новые датчики, новых пользователей и настраивать связи между ними.

ID датчика представлен  циферно-буквенной строкой длинной до 16 символов (“xa7v9Dfadr7H”, “0xA”, “TestSensor”, “0123456789aBcDeF”)

Каждый датчик может принадлежать нескольким клиентам
У каждого клиента может быть несколько датчиков
У каждого датчика есть зарегистрированный адрес помещения, в котором он установлен. Пример:
    “Moscow, Russia, Svobody st. 23 fl 1 room 16”
Каждый клиент имеет один URL, на который нужно отправить POST-запрос об изменении статуса датчика.

data может принимать значения 0 и 1. Датчик отправляет данные минимум раз в час. Если приходит сообщение с полем data, содержащим то-же самое значение, что и прошлое сообщение от этого датчика, то не нужно уведомлять пользователя об этом сообщении.

Как было сказано выше, каждый датчик отправляет сообщение минимум раз в час. Если через час после последнего сообщения от датчика не пришло новое сообщение, то нужно отправить уведомление о потере связи с датчиком:

Свойства датчика:
Id
Адрес установки
Свойства клиента:
Название клиента
URL для отправки запроса

Система принимает тысячи запросов в секунду и должна быть масштабируема на большое количество клиентов, датчиков и запросов. Возможно развитие системы с изменением API

## Архитектура

![Schema](https://github.com/ekirill/lock-sensors/raw/master/locks_workflow.png)

Для хранения списка датчиков, клиентов и связей между ними использовать POSTGRESQL. Это наиболее продвинутая и динамически развивающаяся
opensource база данных с хорошей поддержкой сообщества. В этой же базе будет храниться таблица с текущими состояниями каждого датчика.
Если датчиков будет очень много, то таблицу можно партицировать по hash(sensor_id).

Для хранения истории изменения состояний используем CLICKHOUSE. База данных отлично зарекомендовала себя для хранения лого-подобных данных,
имеет шардирование из коробки, быстро производит агрегационные вычисления.

### Обработка сигналов от датчиков

Очередь из rabbit читают несколько консумеров. Консумер проверяет, изменилось ли состояние по ставнению с тем, что записано в postgresql.
Если изменилось, то в отдельную очередь rabbit отправляется задания на отправку уведомления клиентам. В clickhouse отправляется изменение состояния. Отправку в clickhouse лучше делать через простенький сервис-аггрегатор, который раз в минуту делать запись в базу пачкой.

### Рассылка уведомлений

В момент, когда мы ставим задачу на отправку уведомления клиенту, нам надо предусмотреть систему переотправки сообщений в случае ошибки отправки.
Мы сразу записываем в отдельную таблицу "повторных уведомлений" в postgresql пометку - "повторить отправку сообщения в такое-то время". Время следующей отправки - функция от логарифма номера попытки, для того, чтобы задержка между попыками увеличивалась при каждой следующей попытке.

Отдельный демон регулярно вычитывает из
таблицы попытки, которые надо повторить, отправляет в очередь задание на уведомление и сразу ставит в базу следующую запись на повторную отправку. Все записи, которые он отправил в очередь уведомлений, демон удаляет из этой таблицы.

Консумер очереди уведомлений по данным клиента считывает из базы url и пытается сделать уведомление. Мы читаем url из базы каждый раз на тот
случай, если между retry url клиента поменялся или клиент вообще перестал владеть датчиком. При успешной отправке мы удаляем все заиписи из таблицы "повторных уведомлений".

Система с предварительной записью в таблицу "повторных уведомлений" дает нам гарантию, каждый retry будет только в одном экземпляре.

Обработчик сигналов при поступлении нового сигнала от датчика должен удалить из таблицы "повторных уведомлений" все записи, связанные с изменившимся датчиком.

Таблицу "повторных уведомлений" также можно партицировать. Можно попробовать еще вариант харнения в clickhouse. Но так как там нет удаления, то придется
вместо удаления делать MergeTree таблицу с версионированием и делать запись об изменении состояния задачи уведомления, а в демоне переотправки делать
выборку из этой таблицы с ArgMax(version).

### Система проверки связи с датчиками

Обработчик сигналов отправляет историю изменений в clickhouse. Специальный heartbeat демон будет иметь у себя кеш, например в redis,
в котором будет хранить список всех датчиков, они должны влезть в память. Рядом к каждым id датчика будет храниться timestamp последнего обновления. Харнить можно, например, в sorted set с сортировкой по timestamp.

Демон на каждой итерации смотрит timestamp нижнего датчика, читает из clickhouse все записи с этого timestamp, обновляет sorted set в кеше.

Потом демон выбирает из sorted set сверху все те датчики, которые больше часа не присылали данные и отправляет в очередь уведомлений задачу на отправку уведомления о потере связи. Потерянные датчики надо удалять из sorted set и скидывать в еще один set. При чтении из clickhouse проверять, нет ни такого 
sensor_id в этом set потеряных датчиков. Если есть, то ставить задачу на отправку уведомления о восстановлении связи.

### Web API

API создает датчики и клиентов в postgresql базе.
Endpoints , связанные с историей читают данные из clickhouse.

## Blueprints
```
    SensorConsumer:
    while true:
        rabbitmq -> (sensor_id, sensor_state)
        postgres.check_state(sensor_id, sensor_state) -> (has_changed)
        if (has_changed):
            store_state(sensor_id, sensor_state, timestamp) -> postgres
            store_history(sensor_id, sensor_state, timestamp) -> clickhouse

            cancel_old_retries_for_sensor(sensor_id)
            postgres.get_clients(sensor_id) -> (clients)
            for client in clients:
                set_next_retry_time(
                    client,
                    sensor_id, 
                    message,
                    try_count=1, 
                    to_try_time=now() + f(log(1))
                ) -> postgres
                push_notify_task(client, sensor_id, message, timestamp) -> rabbitmq


RetryProducerDemon:
    while true:
        get_failed(try_count<10, to_try_time<=now()) -> tasks[:1000]
        for task in tasks:
            push_notify_task(task.client, task.sensor_id, task.message) -> rabbitmq
            set_next_retry_time(
                task.set_next_retry_time,
                task.sensor_id,
                task.message,
                try_count=task.try_count + 1,
                to_try_time=now() + f(log(task.try_count + 1))
            ) -> postgres
        delete_sent_retries(tasks) -> postgres

        sleep(_delay)


NotifyTask:Consumer
    while true:
        rabbitmq -> (task)
        get_url(task.client) -> (url)
        post(url, post_data(task.message))
        mark_done_and_cancel_retry(task.sensor_id, task.client) -> postgres
```
