CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR NOT NULL UNIQUE,
    email VARCHAR NOT NULL UNIQUE,
    name VARCHAR NOT NULL,
    surname VARCHAR NOT NULL,
    password TEXT NOT NULL,
    age SMALLINT
);


CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_name ON users(name);
CREATE INDEX IF NOT EXISTS idx_users_surname ON users(surname);
CREATE INDEX IF NOT EXISTS idx_users_name_surname ON users (name, surname);


INSERT INTO users (username, email, name, surname, password, age)
VALUES (
    'admin',
    'admin@example.com',
    'admin',
    'admin',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
    NULL
);


DO $$
DECLARE
    i INTEGER;
    first_names TEXT[] := ARRAY['Александр', 'Максим', 'Иван', 'Анна', 'Мария', 'Екатерина', 'Дмитрий', 'Сергей', 'Андрей', 'Ольга'];
    last_names TEXT[] := ARRAY['Иванов', 'Петров', 'Сидоров', 'Кузнецов', 'Попов', 'Смирнов', 'Миллер', 'Волков', 'Федоров', 'Воробьев'];

BEGIN
    FOR i IN 1..100000 LOOP
        INSERT INTO users (username, email, name, surname, password, age)
        VALUES (
            'user_' || i,
            'user' || i || '@example.com',
            first_names[(floor(random() * array_length(first_names, 1)) + 1)::int],
            last_names[(floor(random() * array_length(last_names, 1)) + 1)::int],
            '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
            (random() * 50 + 18)::int
        );
    END LOOP;
END $$;
