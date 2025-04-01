Entities:

- User
  - username [Primary Key]  # PK
  - avatar
  - age
  - gender
  - timestamp_creation   (created_at)
  - timestamp_update     (updated_at)

- Room
  - name [PK]
  - timestamp_creation   (created_at)
  - timestamp_update     (updated_at)

- Message
  - timestamp     (created_at)
  - updated_at
  - content

- UserRoom
  - username
  - room_name
  - timestamp_join   (joined_at)
  - timestamp_update  (updated_at)
  - leaved_at


FacebookUser
  ...
  ...
  ...
  deleted [Boolean]
