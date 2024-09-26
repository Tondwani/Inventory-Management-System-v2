-- database: ../inventory.db
PRAGMA table_info(Products);
ALTER TABLE Products ADD COLUMN CategoryID INTEGER;
ALTER TABLE Products ADD CONSTRAINT fk_category
FOREIGN KEY (CategoryID) REFERENCES Categories(ID);
SELECT c.Name, COUNT(*) as ProductCount
FROM Products p
JOIN Categories c ON p.CategoryID = c.ID
GROUP BY c.ID;
