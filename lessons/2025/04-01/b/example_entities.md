Entities:

- User
  - username [Primary Key]  # PK
  - avatar
  - age
  - gender
  - created_at
  - updated_at

- Room
  - name [PK]
  - created_at
  - updated_at

- UserRoom # Relation User (N) <-> Room (M)
  - id [PK]
  - username [FK]
  - room_name [FK]
  - joined_at
  - updated_at
  - leaved_at

- UserRoomMessage # Relation User / Room (1) <-> Message (N)
  - user_room_id [FK]
  - message_id [PK]
  - updated_at
  - created_at
  - content
