CREATE TABLE Accounts
(
  acc_id INT PRIMARY KEY NOT NULL,
  login VARCHAR NOT NULL,
  password VARCHAR NOT NULL
);

CREATE TABLE myItems
(
  item_id INT PRIMARY KEY NOT NULL,
  acc_id INT NOT NULL,
  price INT NOT NULL,
  is_sold INT NOT NULL,
  is_available INT NOT NULL,
  url VARCHAR NOT NULL,
  FOREIGN KEY (acc_id) REFERENCES Accounts(acc_id) ON DELETE CASCADE
);

CREATE TABLE itemInfo
(
  item_id INT PRIMARY KEY NOT NULL,
  title VARCHAR NOT NULL,
  description VARCHAR NOT NULL,
  category VARCHAR NOT NULL,
  brand VARCHAR NOT NULL,
  size VARCHAR NOT NULL,
  state VARCHAR NOT NULL,
  color VARCHAR NOT NULL,
  real_price INT NOT NULL,
  date date NOT NULL,
  FOREIGN KEY (item_id) REFERENCES myItems(item_id) ON DELETE CASCADE
);

CREATE TABLE Photos
(
  ID INTEGER PRIMARY KEY AUTOINCREMENT,
  item_id INT NOT NULL,
  url VARCHAR NOT NULL,
  FOREIGN KEY (item_id) REFERENCES itemInfo(item_id) ON DELETE CASCADE
);
CREATE TABLE Notifications
(
  ID INTEGER PRIMARY KEY AUTOINCREMENT,
  item_id INT NOT NULL,
  acc_id INT NOT NULL,
  username VARCHAR NOT NULL,
  created date NOT NULL,
  modified date NOT NULL,
  is_available INT DEFAULT 1 NOT NULL,
  personalized BOOL DEFAULT False NOT NULL,
  discount INT,
  url VARCHAR NOT NULL
);