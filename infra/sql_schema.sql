-- run manually on Postgres or Supabase
CREATE TABLE users (
  id serial PRIMARY KEY,
  email text UNIQUE NOT NULL,
  hashed_password text NOT NULL,
  role text DEFAULT 'user',
  created_at timestamptz DEFAULT now()
);
CREATE TABLE tickets (...);
CREATE TABLE messages (...);

