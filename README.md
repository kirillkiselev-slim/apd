# APD search by text 

Поисковик по текстам документов. Данные хранятся в БД sqlite, поисковый индекс в эластике.

## Основные возможности

- сервис принимает на вход произвольный текстовый запрос, ищет по тексту документа в индексе и возвращать первые 20 документов со всем полями БД, упорядоченные по дате создания;
- удаляет из БД и индекса по полю `id`.

## Начало работы

### Требования

Убедитесь, что у вас установлен Docker. 

### Установка

1. **Клонируйте репозиторий:**

   ```
   git clone https://github.com/kirillkiselev-slim/apd
   ```
2. **Перейдите в директорию:**
   ```
   cd apd

### Перенесите ваш файл posts.csv в директорию data_import для того, чтобы можно было запонить таблицу

### Соберите Docker-образ:

```bash
docker build -t apd_image .
```
### Запустите контейнер в shell:
```bash
docker run --rm -it --name apd -p 80:80 -v $(pwd)/app.db:/app/app.db apd_image:latest /bin/sh
```
***Во время запуска контейнера - мы подключаем volume, чтобы при удалении контейнера сохранялись данные.***

***Откроется shell, вам необходимо будет заполнить таблицу documents.***

### Заполните таблицу:
```bash
python3 data_import/services.py
```

В данном проекте использованы следующие технологии:

- **Python 3.9**: основной язык программирования проекта.
- **Docker**: для контейнеризации приложения.
- **SQLite**: легковесная база данных для хранения документов.
- **Elasticsearch**: система для полнотекстового поиска и анализа данных. 


#### Автор: Кирилл Киселев