MPStats-Sync

Проект для синхронизации данных с MPStats и записи их в Google Таблицу через REST API, написанный на Go + Python. Использует Docker для деплоя.

📦 Структура проекта

```
mpstats-sync/
├── mpstats-sync/        # Python: main.py, main_reels.py, sheets_client.py и т.д.
├── rest-go/             # Go-сервер (main.go)
├── .env                 # Переменные окружения (не публикуется)
├── Dockerfile           # Инструкция сборки контейнера
├── requirements.txt     # Python зависимости
└── mpstats-sync-*.json  # JSON-токен для Google Sheets API
```

🚀 Быстрый старт (локально)

```
docker build -t mpstats-rest .
docker run -d \
  -p 8080:8080 \
  --env-file .env \
  --name mpstats-rest \
  mpstats-rest
```

Проверка:

```
curl http://localhost:8080/health
```

🔗 REST API эндпоинты

```bash
curl -i -X POST http://your_server_ip/sync/lines
```
Синхронизация лески

```bash
curl -i -X POST http://your_server_ip/sync/reels
```
Синхронизация катушек

```bash
curl -v http://localhost:8080/health
```
Проверка статуса

🧾 .env (пример)
```
MPSTATS_API_TOKEN=...
SPREADSHEET_ID=...
GOOGLE_APPLICATION_CREDENTIALS=...json
```
🖱 Интеграция с Google Таблицей

В таблице добавлены две кнопки, которые запускают синхронизацию данных с MPStats. Кнопки используют следующий Apps Script:
```js
function runSyncLines() {
  UrlFetchApp.fetch("http://your.server.ip:8080/sync/lines", {
    method: "post"
  });
}

function runSyncReels() {
  UrlFetchApp.fetch("http://your.server.ip:8080/sync/reels", {
    method: "post"
  });
}
```
Это позволяет инициировать обновление данных напрямую из интерфейса Google Таблицы, без необходимости обращаться к серверу вручную.


#💼 Бизнес-контекст

Этот проект был реализован под задачу заказчика по автоматизации сбора данных о товарах (леска и катушки) из сервиса MPStats и загрузке их в Google Таблицу.

До автоматизации сотрудникам приходилось вручную собирать данные и заполнять таблицу, что занимало до 10 часов в неделю. Благодаря реализации:

синхронизация стала запускаться одной кнопкой в Google Таблице;

данные автоматически парсятся по SKU из MPStats;

таблица может использоваться для глобального анализа, прогнозирования и принятия управленческих решений;

код обернут в REST API и деплоится в Docker на удалённый сервер.

Проект помог сократить ручной труд, ускорить обновление данных и повысить их точность.

