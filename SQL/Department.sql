/*
Display all departments ordered by DEPT_NAME in ascending order.
List all departments ordered by LOCATION in descending order.
Show all department details sorted by MANAGER_ID.
Retrieve departments ordered by the length of the DEPT_NAME.
Display departments in alphabetical order of LOCATION, then by DEPT_NAME.
List departments ordered by DEPT_ID in reverse (highest to lowest).
Sort departments by the last character of their DEPT_NAME.
Show all departments ordered by MANAGER_ID, then LOCATION.
List departments located in 'New York', ordered by DEPT_NAME.
Display the top 3 departments with the smallest DEPT_ID values.
*/

CREATE TABLE Depart
(
  DEPT_ID INTEGER,
  DEPT_NAME TEXT,
  LOCATION TEXT,
  MANAGER_ID INTEGER
);

INSERT INTO Depart VALUES (10, 'HR', 'New York', 101);
INSERT INTO Depart VALUES (20, 'IT', 'San Francisco', 102);
INSERT INTO Depart VALUES (30, 'Finance', 'Chicago', 103);
INSERT INTO Depart VALUES (40, 'Marketing', 'Los Angeles', 104);
INSERT INTO Depart VALUES (50, 'Operations', 'New York', 105);

select * from Depart order by DEPT_NAME;
select * from Depart order by LOCATION DESC;
