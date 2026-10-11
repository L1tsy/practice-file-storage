CREATE DATABASE file_storage;

\c file_storage

DROP TABLE IF EXISTS files CASCADE;
DROP TABLE IF EXISTS folders CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), login VARCHAR(50) NOT NULL, password_hash VARCHAR(255) NOT NULL, first_name VARCHAR(100) NOT NULL, last_name VARCHAR(100) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, CONSTRAINT uq_users_login UNIQUE (login), CONSTRAINT chk_users_login_not_empty CHECK (length(trim(login)) > 0));

CREATE TABLE folders (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), user_id UUID NOT NULL, name VARCHAR(255) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, CONSTRAINT fk_folders_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE, CONSTRAINT chk_folders_name_not_empty CHECK (length(trim(name)) > 0), CONSTRAINT uq_user_folder_name UNIQUE (user_id, name));

CREATE TABLE files (id UUID PRIMARY KEY DEFAULT gen_random_uuid(), user_id UUID NOT NULL, folder_id UUID NOT NULL, name VARCHAR(255) NOT NULL, size_bytes BIGINT NOT NULL, mime_type VARCHAR(127) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, CONSTRAINT fk_files_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE, CONSTRAINT fk_files_folder FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE CASCADE, CONSTRAINT chk_files_size_positive CHECK (size_bytes >= 0), CONSTRAINT chk_files_name_not_empty CHECK (length(trim(name)) > 0));

CREATE INDEX idx_users_search_name ON users (lower(first_name), lower(last_name));
CREATE INDEX idx_folders_user_id ON folders (user_id);
CREATE INDEX idx_files_folder_id ON files (folder_id);
CREATE INDEX idx_files_user_id_name ON files (user_id, lower(name));