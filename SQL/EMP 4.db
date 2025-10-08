CREATE TABLE employee (
    eid INTEGER,
    ename text(20),
    gender text(8),
    email text(50),
    age INTEGER,
    salary INTEGER,
    deptid text(20),
    designation text(20),
    city text(20)
);

INSERT INTO employee VALUES (1, 'Rahul Verma', 'Male', 'rahul.verma@gmail.com', 28, 50000, 'D01', 'Developer', 'Delhi');
INSERT INTO employee VALUES (2, 'Anjali Singh', 'Female', 'anjali.singh@yahoo.com', 25, 45000, 'D02', 'Designer', 'Mumbai');
INSERT INTO employee VALUES (3, 'Amit Kumar', 'Male', 'amit.kumar@outlook.com', 30, 60000, 'D01', 'Developer', 'Bangalore');
INSERT INTO employee VALUES (4, 'Pooja Mehta', 'Female', 'pooja.mehta@gmail.com', 27, 52000, 'D03', 'HR', 'Pune');
INSERT INTO employee VALUES (5, 'Suresh Rao', 'Male', 'suresh.rao@yahoo.com', 35, 75000, 'D04', 'Manager', 'Hyderabad');
INSERT INTO employee VALUES (6, 'Neha Sharma', 'Female', 'neha.sharma@rediff.com', 26, 47000, 'D02', 'Designer', 'Mumbai');
INSERT INTO employee VALUES (7, 'Manoj Yadav', 'Male', 'manoj.yadav@gmail.com', 29, 56000, 'D01', 'Tester', 'Delhi');
INSERT INTO employee VALUES (8, 'Sneha Patil', 'Female', 'sneha.patil@yahoo.com', 24, 43000, 'D02', 'Intern', 'Pune');
INSERT INTO employee VALUES (9, 'Deepak Jain', 'Male', 'deepak.jain@outlook.com', 32, 68000, 'D03', 'HR', 'Delhi');
INSERT INTO employee VALUES (10, 'Kavita Rani', 'Female', 'kavita.rani@gmail.com', 31, 65000, 'D04', 'Team Lead', 'Chennai');
INSERT INTO employee VALUES (11, 'Ravi Shankar', 'Male', 'ravi.shankar@gmail.com', 29, 57000, 'D01', 'Developer', 'Bangalore');
INSERT INTO employee VALUES (12, 'Divya Bhatt', 'Female', 'divya.bhatt@yahoo.com', 28, 51000, 'D03', 'HR', 'Mumbai');
INSERT INTO employee VALUES (13, 'Nikhil Das', 'Male', 'nikhil.das@rediffmail.com', 33, 70000, 'D04', 'Manager', 'Kolkata');
INSERT INTO employee VALUES (14, 'Priya Kaur', 'Female', 'priya.kaur@gmail.com', 26, 46000, 'D02', 'Designer', 'Delhi');
INSERT INTO employee VALUES (15, 'Arjun Nair', 'Male', 'arjun.nair@outlook.com', 34, 73000, 'D01', 'Team Lead', 'Chennai');
INSERT INTO employee VALUES (16, 'Swati Mishra', 'Female', 'swati.mishra@gmail.com', 27, 50000, 'D03', 'HR', 'Bangalore');
INSERT INTO employee VALUES (17, 'Vivek Tiwari', 'Male', 'vivek.tiwari@yahoo.com', 31, 62000, 'D04', 'Manager', 'Pune');
INSERT INTO employee VALUES (18, 'Meena Joshi', 'Female', 'meena.joshi@gmail.com', 25, 20000, 'D02', 'Intern', 'Delhi');
INSERT INTO employee VALUES (19, 'Ankur Bansal', 'Male', 'ankur.bansal@rediff.com', 30, 15000, 'D01', 'Tester', 'Mumbai');
INSERT INTO employee VALUES (20, 'Isha Kapoor', 'Female', 'isha.kapoor@gmail.com', 53, 14000, 'D03', 'HR', 'Kolkata');
INSERT INTO employee VALUES (20, 'Isha Kapoor', 'Female', 'isha.kapoor@gmail.com', 53, 14000, 'D03', 'HR', 'Kolkata');


update employee set salary = salary + 3000 where salary <= 25000;
delete from employee where designation = 'HR' and age > 50;
update employee set city = 'Pune' where city = 'Mumbai';
delete from employee where gender = 'Female' and designation = 'HR';
update employee set city = 'Banglore' where email = 'rahul.verma@gmail.com';
select distinct ename from employee;('Only retrive Unique there is no duplication')
select eid,ename ,salary + 3000 as 'Net Salary' from employee;
select * from employee where ename like '%a%';
select * from employee where ename like '___i%';
select * from employee where salary between 20000 and 50000;
