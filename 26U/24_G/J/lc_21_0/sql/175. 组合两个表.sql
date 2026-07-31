-- 175. 组合两个表

select FirstName, LastName, City, State
from Person left join Address
on Person.PersonId = Address.PersonId



-- 577. 员工奖金
select Employee.name, bonus
from Employee left join Bonus
on Employee.empId = Bonus.empId
where bonus is null or bonus < 1000