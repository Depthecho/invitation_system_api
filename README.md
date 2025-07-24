## API Endpoints

- `POST /api/auth/` 
  Body: {"phone": "+79991234567"}

- `POST /api/verify/`
  Body: {"phone": "+79991234567", "code": "1234"}

- `GET /api/profile/` - текущий профиль
- `POST /api/profile/` - активация инвайт-кода
  Body: {"invite_code": "ABC123"}
