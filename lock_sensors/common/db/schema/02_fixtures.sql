INSERT INTO clients (client_id, name, notification_url) VALUES
  (1, 'Alex', 'http://postconsumer/alex'),
  (2, 'Bob', 'http://postconsumer/bob');

INSERT INTO sensors (sensor_id, address, owner) VALUES
  ('sensor_1', 'Address 1', NULL),
  ('sensor_2', 'Address 1', 1),
  ('sensor_3', 'Address 2', 2),
  ('sensor_4', 'Address 4', 2);
