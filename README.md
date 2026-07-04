### Database Schema

```mermaid
erDiagram
    USER ||--o{ GAME : plays
    GAME ||--|| OPENING : uses

    USER {
        string id PK
        string username
        int elo_rating
        string title
    }

    GAME {
        string id PK
        string white_user_id FK
        string black_user_id FK
        string opening_eco FK
        string status
        string winner
    }

    OPENING {
        string eco PK
        string name
        string moves
    }