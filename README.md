# Аниме Торрент-Трекер

Веб-приложение для размещения и распространения торрент-файлов.

## Технологии

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL
- **Frontend:** Jinja2, Bootstrap 5
- **Tracker:** OpenTracker (HTTP/UDP)
- **Deployment:** Docker, Docker Compose

## Архитектура

### Диаграмма компонентов

```mermaid
flowchart TB
    subgraph Client["Клиент"]
        Browser[Веб-браузер]
        TorrentClient[Торрент-клиент<br/>qBittorrent/Transmission]
    end
    
    subgraph Frontend["Frontend Layer"]
        Templates[Jinja2 Templates]
        Static[Static Files<br/>CSS/JS/Images]
    end
    
    subgraph Backend["Backend Layer FastAPI"]
        API[REST API<br/>Endpoints]
        Auth[Authentication<br/>JWT/Session]
        TorrentParser[Torrent Parser<br/>.torrent файлы]
        SearchEngine[Search Service<br/>SQL поиск]
        FileStorage[File Storage Service<br/>Работа с файлами]
    end
    
    subgraph Database["Data Layer"]
        PostgreSQL[(PostgreSQL<br/>База данных)]
        Redis[(Redis<br/>Кеш/Сессии)]
    end
    
    subgraph Storage["File Storage"]
        TorrentFiles[Директория<br/>/storage/torrents/]
    end
    
    subgraph Tracker["Tracker Layer"]
        OpenTracker[OpenTracker<br/>HTTP/UDP трекер]
    end
    
    subgraph External["External Services"]
        SMTP[SMTP Server<br/>Email уведомления]
    end
    
    Browser --> API
    Browser --> Templates
    Browser --> Static
    TorrentClient -.-> OpenTracker
    
    Templates -.-> API
    API --> Auth
    API --> TorrentParser
    API --> SearchEngine
    API --> FileStorage
    
    Auth --> PostgreSQL
    Auth --> Redis
    TorrentParser -.-> TorrentFiles
    SearchEngine --> PostgreSQL
    FileStorage --> TorrentFiles
    FileStorage --> PostgreSQL
    
    API -.-> SMTP
    OpenTracker --> PostgreSQL
    OpenTracker -.-> TorrentFiles
    
    style Client fill:#E8F4F8
    style Frontend fill:#FFF4E6
    style Backend fill:#E8F5E9
    style Database fill:#F3E5F5
    style Storage fill:#FFF9C4
    style Tracker fill:#FFE0B2
    style External fill:#FFEBEE
```

### Модель данных

```mermaid
classDiagram
    class User {
        +int id
        +string username
        +string email
        +string password_hash
        +datetime created_at
        +boolean is_active
        +boolean is_moderator
        +int upload_count
        +int download_count
        +register()
        +login()
        +uploadTorrent()
        +downloadTorrent()
    }

    class Torrent {
        +int id
        +string title
        +string description
        +int category_id
        +int uploader_id
        +string info_hash
        +int file_size
        +datetime created_at
        +int seeders
        +int leechers
        +int downloads
        +string torrent_file_path
        +getTorrentFile()
        +updateStats()
        +delete()
    }

    class Category {
        +int id
        +string name
        +string slug
        +string description
        +getTorrents()
    }

    class Tag {
        +int id
        +string name
        +string slug
    }

    class TorrentTag {
        +int torrent_id
        +int tag_id
    }

    class Comment {
        +int id
        +int torrent_id
        +int user_id
        +string text
        +datetime created_at
        +edit()
        +delete()
    }

    class TorrentFile {
        +int id
        +int torrent_id
        +string file_path
        +int file_size
    }

    class PeerStats {
        +int id
        +int torrent_id
        +string peer_id
        +string ip_address
        +int port
        +int uploaded
        +int downloaded
        +int left
        +datetime last_announce
        +updateStats()
    }

    Torrent "1" *-- "0..*" TorrentFile : содержит
    Torrent "1" *-- "0..*" PeerStats : отслеживает
    User "1" o-- "0..*" Torrent : загружает
    User "1" o-- "0..*" Comment : пишет
    Torrent "1" -- "0..*" Comment : имеет
    Torrent "0..*" --> "1" Category : принадлежит
    Torrent "0..*" -- "0..*" Tag : имеет
    TorrentTag "1" -- "1" Torrent : связывает
    TorrentTag "1" -- "1" Tag : связывает

    note for User "Пользователь системы<br/>Может быть обычным<br/>или модератором"
    note for Torrent "Метаданные торрента<br/>info_hash - уникальный<br/>идентификатор SHA1"
    note for TorrentFile "Список файлов<br/>внутри торрента"
    note for PeerStats "Статистика пиров<br/>Обновляется трекером<br/>через announce"
```

## Бизнес-процессы

### Процесс загрузки торрента

```mermaid
graph TD
    Start([Пользователь хочет загрузить торрент]) --> Login{Авторизован?}
    Login -->|Нет| LoginPage[Страница входа]
    LoginPage --> LoginSuccess{Успешный вход?}
    LoginSuccess -->|Да| UploadForm
    LoginSuccess -->|Нет| LoginPage
    Login -->|Да| UploadForm[Форма загрузки торрента]
    
    UploadForm --> FillForm[Заполнение формы:<br/>- Название<br/>- Описание<br/>- Категория<br/>- Теги<br/>- .torrent файл]
    FillForm --> ValidateForm{Валидация<br/>формы}
    ValidateForm -->|Ошибка| ShowError[Показать ошибки]
    ShowError --> UploadForm
    
    ValidateForm -->|Успех| ParseTorrent[Парсинг .torrent файла]
    ParseTorrent --> ExtractInfo[Извлечение:<br/>- info_hash<br/>- список файлов<br/>- размер]
    ExtractInfo --> CheckDuplicate{Проверка<br/>дубликата}
    
    CheckDuplicate -->|Дубликат найден| ShowDupError[Ошибка: торрент уже существует]
    ShowDupError --> End1([Конец])
    
    CheckDuplicate -->|Уникальный| SaveToDB[(Сохранение в БД:<br/>- Torrent<br/>- TorrentFile<br/>- Tags)]
    SaveToDB --> SaveFile[Сохранение .torrent<br/>файла на диск]
    SaveFile --> UpdateTracker[Добавление info_hash<br/>в трекер whitelist]
    UpdateTracker --> Success[Успешно:<br/>редирект на страницу торрента]
    Success --> End2([Конец])
    
    style Start fill:#2E7D32,color:#fff
    style End1 fill:#C62828,color:#fff
    style End2 fill:#2E7D32,color:#fff
    style SaveToDB fill:#1565C0,color:#fff
    style UpdateTracker fill:#EF6C00,color:#fff
```

### Процесс скачивания торрента

```mermaid
graph TD
    Start([Пользователь хочет скачать торрент]) --> ViewPage[Просмотр страницы торрента]
    ViewPage --> ClickDownload[Клик на Download]
    ClickDownload --> CheckAuth{Авторизован?}
    
    CheckAuth -->|Нет| LoginRequired[Требуется вход]
    LoginRequired --> End1([Конец])
    
    CheckAuth -->|Да| ServeTorrent[Отдача .torrent файла]
    ServeTorrent --> IncrementCounter[Инкремент счетчика downloads]
    IncrementCounter --> UserDownloads[Открытие в<br/>торрент-клиенте]
    
    UserDownloads --> ClientConnect[Торрент-клиент<br/>подключается к трекеру]
    ClientConnect --> AnnounceRequest[Отправка announce запроса:<br/>- info_hash<br/>- peer_id<br/>- uploaded/downloaded/left]
    
    AnnounceRequest --> TrackerValidate{Валидация<br/>трекером}
    TrackerValidate -->|Неверный info_hash| RejectPeer[Отклонение пира]
    RejectPeer --> End2([Конец])
    
    TrackerValidate -->|Валидный| UpdatePeerStats[(Обновление PeerStats в БД)]
    UpdatePeerStats --> ReturnPeerList[Возврат списка пиров]
    ReturnPeerList --> StartDownload[Начало загрузки/раздачи]
    
    StartDownload --> PeriodicAnnounce[Периодические announce<br/>каждые 30-60 мин]
    PeriodicAnnounce --> UpdateStats[Обновление статистики<br/>seeders/leechers]
    UpdateStats --> Complete{Загрузка<br/>завершена?}
    
    Complete -->|Нет| PeriodicAnnounce
    Complete -->|Да| FinalAnnounce[Финальный announce<br/>event=completed]
    FinalAnnounce --> UpdateComplete[(Обновление:<br/>downloads++<br/>seeders++)]
    UpdateComplete --> End3([Конец])
    
    style Start fill:#2E7D32,color:#fff
    style End1 fill:#C62828,color:#fff
    style End2 fill:#C62828,color:#fff
    style End3 fill:#2E7D32,color:#fff
    style UpdatePeerStats fill:#1565C0,color:#fff
    style UpdateComplete fill:#1565C0,color:#fff
    style AnnounceRequest fill:#EF6C00,color:#fff
```

## Основной функционал

- Регистрация и авторизация пользователей
- Загрузка торрент-файлов с метаданными
- Поиск по названию, категориям, тегам
- Скачивание .torrent файлов
- Отслеживание статистики (seeders/leechers/downloads)
- Комментарии к раздачам

## Структура проекта

    anime-tracker/
    ├── app/
    │   ├── api/              # API endpoints
    │   ├── core/             # Бизнес-логика
    │   ├── models/           # SQLAlchemy модели
    │   ├── schemas/          # Pydantic схемы
    │   ├── services/         # Сервисный слой
    │   ├── templates/        # Jinja2 шаблоны
    │   └── static/           # CSS/JS/Images
    ├── alembic/              # Миграции БД
    ├── storage/              # .torrent файлы
    ├── docker-compose.yml
    ├── Dockerfile
    └── requirements.txt

---

**Учебный проект МФТИ**
