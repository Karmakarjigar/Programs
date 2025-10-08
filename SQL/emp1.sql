create table emp
(
	Id interger,
	first_name text,
	last_name text
);

insert into emp values(1,'Jigar','Karmakar');
insert into emp values(2,'Ved','Rana');
insert into emp values(3,'Mark','Bruce');
insert into emp values(4,'Rohit','Ghosh');

select * from emp;
select * from emp where id = 1;
