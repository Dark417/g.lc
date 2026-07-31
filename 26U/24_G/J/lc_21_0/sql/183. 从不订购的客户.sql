SELECT c.Name Customers FROM Customers c
WHERE c.id not in (
    select o.CustomerId from Orders as o
    )