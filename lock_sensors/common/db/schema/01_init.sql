CREATE TABLE clients (
  client_id INTEGER PRIMARY KEY,
  name VARCHAR(256) NOT NULL,
  notification_url VARCHAR(512) NOT NULL
);

CREATE TABLE sensors (
  sensor_id VARCHAR(256) PRIMARY KEY,
  address VARCHAR(512) NOT NULL,
  owner INTEGER REFERENCES clients(client_id) ON DELETE RESTRICT
);