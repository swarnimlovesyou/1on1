"""DBMS study guides for the CS fundamentals track (orders 1 to 6)."""

GUIDES = [
    dict(
        id='guide-cs-fundamentals-dbms-er-modelling', kind='guide', track='cs-fundamentals', subject='DBMS',
        title='ER modelling', order=1,
        summary="Learn to sketch a database as entities, attributes and relationships, then turn that sketch into tables.",
        sections=[
            dict(title='What an ER model is for', text=(
                "Before you write a single CREATE TABLE, you need a picture of the things your system stores and how they connect. "
                "An entity relationship (ER) model is that picture. It has three building blocks: entities, attributes and relationships.\n\n"
                "An entity is a real thing you want to remember, like one particular student. An entity set is the collection of all similar things, like every student. "
                "Attributes describe an entity, such as roll number, name and date of birth. A relationship connects entities, such as a student enrolling in a course.\n\n"
                "Picture a small college system. You have Student and Course entity sets and an Enrolls relationship between them. "
                "This is simple enough to draw on a napkin, yet it already tells you there will be at least three tables. "
                "Interviewers like ER questions because they show whether you think about data before you think about code."
            )),
            dict(title='Kinds of attributes', text=(
                "Not every attribute is a plain single value, and the ER notation makes the difference visible.\n\n"
                "A simple attribute cannot be split further, like a roll number. A composite attribute is made of parts, like an address made of street, city and pin code. "
                "A single valued attribute holds one value per entity, while a multivalued attribute can hold several, like a student with two phone numbers. "
                "A derived attribute can be computed from others, like age from date of birth, so you usually do not store it. "
                "A key attribute uniquely identifies each entity in its set, and is underlined in the diagram.\n\n"
                "These labels matter when you build tables. A composite attribute usually becomes several columns. "
                "A multivalued attribute cannot live in a single column without breaking first normal form, so it becomes its own table, for example StudentPhone(roll_no, phone)."
            )),
            dict(title='Cardinality and participation', text=(
                "Cardinality tells you how many entities on one side can link to entities on the other side. "
                "One to one means each side links to at most one, like a person and a passport. "
                "One to many means one entity links to many, like one department with many employees, while each employee has one department. "
                "Many to many means both sides can have many, like students and courses.\n\n"
                "Participation is a separate question: must every entity take part? "
                "If every employee must belong to some department, Employee has total participation in WorksIn, drawn with a double line. "
                "If a department may exist with no employees yet, Department has partial participation.\n\n"
                "Do not mix these up. Cardinality is about the maximum number of partners, participation is about the minimum, that is, whether zero is allowed."
            )),
            dict(title='Weak entities', text=(
                "Some entities cannot be identified on their own. Think of an employee's dependents, stored by name. "
                "Two different employees might both have a child called Asha, so the name alone does not identify a dependent.\n\n"
                "Such an entity set is called weak. It depends on an owner entity, here Employee, through an identifying relationship. "
                "The weak entity has a partial key, also called a discriminator, which is unique only among the dependents of one owner. "
                "The full identity is the owner's key plus the partial key, for example (emp_id, dependent_name).\n\n"
                "A weak entity always has total participation in its identifying relationship, since a dependent without an employee makes no sense. "
                "In diagrams it is drawn with a double rectangle, and the partial key is underlined with a dashed line."
            )),
            dict(title='Turning the diagram into tables', text=(
                "Mapping an ER diagram to tables follows a few reliable rules.\n\n"
                "Each strong entity set becomes a table whose primary key is the key attribute. "
                "For a one to many relationship, put a foreign key on the many side: Employee gets a dept_id column. "
                "For a one to one relationship, put the foreign key on either side, preferably the side with total participation so the column is never empty. "
                "For a many to many relationship, create a new table holding both keys, such as Enrollment(roll_no, course_id), with the pair as its primary key. "
                "Any attribute of the relationship itself, like a grade, lives in that new table, because it belongs to the pairing and not to either entity alone.\n\n"
                "A weak entity becomes a table whose primary key combines the owner's key with the partial key, and the owner's key is also a foreign key. "
                "Multivalued attributes get their own tables, as described earlier."
            )),
        ],
        keyPoints=[
            "Entities are things, attributes describe them, relationships connect them.",
            "Cardinality is the maximum number of partners; participation says whether zero partners is allowed.",
            "A weak entity is identified by its owner's key plus its own partial key.",
            "One to many: foreign key on the many side. Many to many: a separate table keyed by both sides.",
            "Multivalued attributes become their own tables; derived attributes are usually not stored.",
        ],
        challenges=[
            dict(id='challenge-dbms-er-modelling-q1', kind='prediction', title='Where does the grade go',
                 prompt="Student and Course have a many to many Enrolls relationship, and each enrollment has a grade. When you build tables, where should the grade column live?",
                 options=["In the Student table", "In the Course table", "In a separate Enrollment table keyed by (roll_no, course_id)", "In whichever of Student or Course has fewer rows"],
                 answer=2,
                 explanation="A grade belongs to a specific pairing of student and course, not to either one alone. A student has a different grade in each course, and a course gives different grades to each student, so neither entity table can hold it without repeating rows. The many to many relationship becomes its own table, and the grade sits there.",
                 hint="Ask yourself: is the grade a fact about the student, the course, or the pair?"),
            dict(id='challenge-dbms-er-modelling-q2', kind='prediction', title='Key of a weak entity',
                 prompt="Dependent is a weak entity owned by Employee, with dependent_name as its partial key. What is the primary key of the Dependent table?",
                 options=["dependent_name alone", "(emp_id, dependent_name)", "emp_id alone", "A surrogate id is always required; no natural key is possible"],
                 answer=1,
                 explanation="The partial key is unique only within one owner, so dependent_name alone can repeat across employees. emp_id alone fails because one employee can have several dependents. Combining the owner's key with the partial key gives a unique identifier, which is exactly how weak entities are mapped. A surrogate is optional, not required.",
                 hint="Two employees can each have a dependent with the same name."),
            dict(id='challenge-dbms-er-modelling-q3', kind='prediction', title='Foreign key placement',
                 prompt="Department to Employee is one to many: a department has many employees, each employee has exactly one department. Using the fewest tables, where does the foreign key go?",
                 options=["dept_id as a column in Employee", "emp_id as a column in Department", "A separate WorksIn table is mandatory"],
                 answer=0,
                 explanation="Each employee has exactly one department, so a single dept_id column in Employee captures the link with no repetition. Putting emp_id in Department would need many values in one cell, or one department row per employee. A separate table works but is not needed for one to many, so it is not the fewest tables.",
                 hint="Which side has only one partner per row?"),
            dict(id='challenge-dbms-er-modelling-q4', kind='prediction', title='Age and date of birth',
                 prompt="A Person entity stores date_of_birth. The diagram also shows age, drawn with a dashed oval. What kind of attribute is age?",
                 options=["Composite", "Multivalued", "Key", "Derived"],
                 answer=3,
                 explanation="Age can be computed from date_of_birth and today's date, which makes it derived, and that is what the dashed oval means. It is not composite because it has no parts, not multivalued because a person has one age, and not a key because many people share an age.",
                 hint="Recall what a dashed oval means in ER notation."),
            dict(id='challenge-dbms-er-modelling-q5', kind='prediction', title='Reading total participation',
                 prompt="The diagram shows a double line between Employee and the WorksIn relationship. What does it tell you?",
                 options=["Every department must have at least one employee", "Every employee must be linked to at least one department", "The relationship is one to one", "dept_id is the primary key of Employee"],
                 answer=1,
                 explanation="A double line marks total participation of the entity on that side, here Employee, so no employee can exist without a department. It says nothing about departments, which are on the other side. Participation is about the minimum, not the maximum, so it does not make the relationship one to one, and it has nothing to do with primary keys.",
                 hint="Participation is about the entity whose side the double line touches."),
        ],
    ),
    dict(
        id='guide-cs-fundamentals-dbms-relational-model-and-keys', kind='guide', track='cs-fundamentals', subject='DBMS',
        title='Relational model and keys', order=2,
        summary="Understand relations, the difference between super, candidate, primary and foreign keys, and the integrity rules they enforce.",
        sections=[
            dict(title='Relations, tuples and attributes', text=(
                "In the relational model, data lives in relations, which you know as tables. Each row is a tuple and each column is an attribute. "
                "Every attribute draws its values from a domain, the set of allowed values, such as integers from 1 to 100 or strings of up to 50 characters.\n\n"
                "Two counts come up in interviews. The degree of a relation is the number of attributes, and the cardinality is the number of tuples. "
                "A Student table with roll_no, name and email has degree 3; if it holds 200 students, its cardinality is 200.\n\n"
                "In theory a relation is a set, so row order does not matter and no two tuples are identical. "
                "Real SQL tables are a little looser: they allow duplicate rows unless you declare a key. "
                "That gap is one reason keys are so important."
            )),
            dict(title='Super keys and candidate keys', text=(
                "A super key is any set of attributes whose values are different for every tuple. "
                "Take Student(roll_no, email, name, phone), where roll_no and email are each unique. "
                "Then {roll_no} is a super key, and so are {roll_no, name}, {email, phone} and the set of all four columns. Adding columns to a super key always gives another super key.\n\n"
                "A candidate key is a minimal super key: remove any attribute and it stops being unique. "
                "Here {roll_no} and {email} are candidate keys. {roll_no, name} is a super key but not a candidate key, because roll_no alone already works.\n\n"
                "Minimal does not mean smallest. A table can have one candidate key with one column and another with two columns, and both are candidates as long as neither contains a smaller unique set. "
                "An attribute that appears in any candidate key is called a prime attribute, a term you will need for normalization."
            )),
            dict(title='Primary, alternate and composite keys', text=(
                "Out of the candidate keys, you choose one to be the primary key. The rest are called alternate keys. "
                "In the Student example you might pick roll_no as primary, which leaves email as an alternate key, usually enforced with a UNIQUE constraint.\n\n"
                "The primary key carries the entity integrity rule: no part of it may be NULL. "
                "This makes sense, because a missing value cannot identify anything. Each table has at most one primary key.\n\n"
                "A key made of more than one attribute is a composite key. Enrollment(roll_no, course_id, grade) uses (roll_no, course_id) as its primary key, since a student takes many courses and a course has many students, but each pairing appears once.\n\n"
                "You will also hear natural versus surrogate keys. A natural key comes from real data, like email. A surrogate key is an artificial id, such as an auto increment number, used when natural keys are long or may change."
            )),
            dict(title='Foreign keys and referential integrity', text=(
                "A foreign key is a column, or set of columns, whose values must match a key in another table, usually its primary key. "
                "In Orders(order_id, customer_id, amount), customer_id can be a foreign key referencing Customers(id).\n\n"
                "Referential integrity says every non NULL foreign key value must point to a row that exists. "
                "You cannot insert an order for customer 42 if there is no customer 42. A foreign key column may hold NULL, meaning the row references nothing, unless you also declare it NOT NULL.\n\n"
                "What happens when you delete a referenced customer depends on the rule you declare. "
                "With NO ACTION, the default in standard SQL, or with RESTRICT, the delete is refused while orders still point at that customer. "
                "With CASCADE, the matching orders are deleted too. With SET NULL, their customer_id becomes NULL.\n\n"
                "A foreign key can even point to its own table, like Employee.manager_id referencing Employee.emp_id."
            )),
        ],
        keyPoints=[
            "Super key: any set of attributes that uniquely identifies tuples.",
            "Candidate key: a super key with no proper subset that is also a super key.",
            "Primary key: the candidate key you pick; it can never be NULL. The others are alternate keys.",
            "Foreign key values must match an existing referenced row or be NULL.",
            "Prime attributes are those that appear in at least one candidate key.",
        ],
        challenges=[
            dict(id='challenge-dbms-relational-model-and-keys-q1', kind='prediction', title='Counting candidate keys',
                 prompt="In R(A, B, C), A is unique on its own. B alone repeats and C alone repeats, but the pair (B, C) never repeats. How many candidate keys does R have?",
                 options=["1", "2", "3", "4"],
                 answer=1,
                 explanation="{A} is a candidate key because it is unique and has one attribute. {B, C} is also a candidate key: it is unique, and neither B nor C alone is. Sets such as {A, B} are super keys but not minimal, because they contain A. So there are exactly two.",
                 hint="Look for unique sets that do not contain a smaller unique set."),
            dict(id='challenge-dbms-relational-model-and-keys-q2', kind='prediction', title='What makes a key candidate',
                 prompt="Which statement about candidate keys is correct?",
                 options=["It is always the key with the fewest attributes", "It must be a single column", "Adding any attribute to it gives another candidate key", "No proper subset of it is a super key"],
                 answer=3,
                 explanation="Minimality is the defining property: drop any attribute and uniqueness breaks. A table can have candidate keys of different sizes, so it need not be the smallest, and composite candidate keys are common, so it need not be one column. Adding an attribute to a candidate key gives a super key, but it is no longer minimal, so it is not a candidate key.",
                 hint="Think about what separates a candidate key from a super key."),
            dict(id='challenge-dbms-relational-model-and-keys-q3', kind='prediction', title='Counting super keys',
                 prompt="R(A, B, C, D) has exactly one candidate key, {A}. How many super keys does R have?",
                 options=["1", "4", "8", "15"],
                 answer=2,
                 explanation="A set is a super key exactly when it contains A. You must include A, and each of B, C and D can be in or out, giving 2 x 2 x 2 = 8 super keys. 15 counts every non empty subset, including those without A, which are not unique.",
                 hint="Every super key must include A; the other three columns are free choices."),
            dict(id='challenge-dbms-relational-model-and-keys-q4', kind='prediction', title='Deleting a referenced row',
                 prompt="Orders.customer_id is a foreign key to Customers.id with no ON DELETE clause, so the standard default applies. You delete a customer who still has orders. What happens?",
                 options=["The delete is rejected", "The customer's orders are deleted too", "The orders' customer_id is set to NULL", "The delete succeeds and the orders keep pointing at a missing id"],
                 answer=0,
                 explanation="Without an explicit rule, standard SQL uses NO ACTION, which refuses any change that would leave orders referencing a customer who no longer exists. CASCADE and SET NULL only happen when you declare them. Leaving dangling references is exactly what referential integrity forbids.",
                 hint="Recall which referential action standard SQL applies when you declare none, and what it does."),
            dict(id='challenge-dbms-relational-model-and-keys-q5', kind='prediction', title='Where NULL is allowed',
                 prompt="Which of these columns can legally contain NULL?",
                 options=["A single column primary key", "One column of a composite primary key", "No column in a table that has a primary key", "A foreign key column declared without NOT NULL"],
                 answer=3,
                 explanation="Entity integrity bans NULL in every part of a primary key, single or composite. Other columns in a keyed table can be NULL, so the third option is too strict. A foreign key without NOT NULL may be NULL, which simply means the row references nothing.",
                 hint="Entity integrity applies to one kind of key only."),
        ],
    ),
    dict(
        id='guide-cs-fundamentals-dbms-normalization', kind='guide', track='cs-fundamentals', subject='DBMS',
        title='Normalization (1NF to BCNF)', order=3,
        summary="Use functional dependencies to spot redundancy and decompose tables step by step through 1NF, 2NF, 3NF and BCNF.",
        sections=[
            dict(title='Why normalize: the three anomalies', text=(
                "Imagine one table Enrollment(roll_no, student_name, course_id, course_title, grade). It works, but it repeats a lot. "
                "Every student's name appears once per course they take, and every course title appears once per student enrolled.\n\n"
                "That repetition causes three classic problems. An update anomaly: if a course is renamed, you must change many rows, and missing one leaves the data contradicting itself. "
                "An insertion anomaly: you cannot record a new course until some student enrolls, because there is no row to put it in. "
                "A deletion anomaly: if the last student drops a course, deleting that row also erases the only record of the course title.\n\n"
                "Normalization is the process of splitting such tables so each fact is stored once. "
                "The normal forms are checkpoints that tell you how much of this redundancy is left."
            )),
            dict(title='Functional dependencies', text=(
                "A functional dependency X -> Y means that whenever two rows agree on X, they must agree on Y. "
                "In the Enrollment table, course_id -> course_title, because one course has one title, and (roll_no, course_id) -> grade.\n\n"
                "To find keys, compute the closure of a set of attributes: start with the set and keep adding anything the dependencies let you derive. "
                "If the closure of X contains every attribute, X is a super key. "
                "Here the closure of (roll_no, course_id) reaches every column, so it is a key.\n\n"
                "Two shapes of dependency cause trouble. A partial dependency is when a non prime attribute depends on only part of a candidate key, like course_title depending on course_id alone. "
                "A transitive dependency is when a non prime attribute depends on the key through another non key attribute, as in emp_id -> dept_id -> dept_name. "
                "2NF removes the first pattern and 3NF removes the second."
            )),
            dict(title='First and second normal form', text=(
                "A table is in first normal form (1NF) when every cell holds a single atomic value and there are no repeating groups. "
                "A phones column holding '98200, 99300' breaks 1NF; you fix it by moving phones to their own table with one phone per row.\n\n"
                "A table is in second normal form (2NF) when it is in 1NF and no non prime attribute is partially dependent on any candidate key. "
                "In plain words, every non key column must depend on the whole key, not just part of it.\n\n"
                "Our Enrollment table fails 2NF, since course_title depends on course_id alone and student_name depends on roll_no alone. "
                "Split it into Student(roll_no, student_name), Course(course_id, course_title) and Enrollment(roll_no, course_id, grade). "
                "Notice that partial dependency needs a composite key. A table whose candidate keys are all single columns, and which is in 1NF, is automatically in 2NF."
            )),
            dict(title='Third normal form and BCNF', text=(
                "A table is in third normal form (3NF) if, for every non trivial dependency X -> A, either X is a super key or A is a prime attribute. "
                "This removes transitive dependencies of non prime attributes on the key. "
                "Employee(emp_id, dept_id, dept_name) fails, because dept_id -> dept_name, dept_id is not a super key, and dept_name is not prime. Move dept_name into a Department table.\n\n"
                "Boyce Codd normal form (BCNF) drops the escape clause: for every non trivial X -> A, X must be a super key. Every BCNF table is in 3NF, but not the other way round.\n\n"
                "The classic gap: Teaching(student, subject, teacher), where each teacher teaches one subject, so teacher -> subject, and (student, subject) -> teacher. "
                "Candidate keys are (student, subject) and (student, teacher), so all three columns are prime. "
                "teacher -> subject is allowed in 3NF because subject is prime, but it breaks BCNF because teacher is not a super key."
            )),
            dict(title='Good decompositions', text=(
                "Splitting a table is only safe if you can put it back together. "
                "A decomposition is lossless if joining the pieces gives exactly the original rows, with no extra rows. "
                "For a split into two tables, a simple test works: the shared columns must be a super key of at least one of the pieces. "
                "Splitting R(A, B, C) with A -> B into (A, B) and (A, C) is lossless, because A is a key of (A, B).\n\n"
                "A decomposition is dependency preserving if every original dependency can still be checked inside a single table, without joins.\n\n"
                "Here is the trade-off interviewers like. You can always reach 3NF with a decomposition that is both lossless and dependency preserving. "
                "BCNF can always be reached losslessly, but sometimes only by losing a dependency, as in the Teaching example. "
                "In practice, many systems stop at 3NF, and some read heavy systems deliberately denormalize to avoid joins."
            )),
        ],
        keyPoints=[
            "Redundancy causes update, insertion and deletion anomalies.",
            "2NF: no non prime attribute depends on part of a candidate key.",
            "3NF: for every non trivial X -> A, X is a super key or A is prime.",
            "BCNF: for every non trivial X -> A, X is a super key.",
            "3NF is always reachable losslessly with dependencies preserved; BCNF may lose a dependency.",
        ],
        challenges=[
            dict(id='challenge-dbms-normalization-q1', kind='prediction', title='Composite key with a partial dependency',
                 prompt="R(A, B, C, D) has candidate key (A, B) and dependencies AB -> C and B -> D. What is the highest normal form R satisfies?",
                 options=["1NF", "2NF", "3NF", "BCNF"],
                 answer=0,
                 explanation="D is non prime and depends on B alone, which is only part of the key (A, B). That is a partial dependency, so R fails 2NF and therefore also 3NF and BCNF. Assuming atomic values, it is in 1NF only.",
                 hint="Does every non key column depend on the whole key?"),
            dict(id='challenge-dbms-normalization-q2', kind='prediction', title='A chain through a non key column',
                 prompt="R(A, B, C) has key A and dependencies A -> B and B -> C. What is the highest normal form R satisfies?",
                 options=["1NF", "2NF", "3NF", "BCNF"],
                 answer=1,
                 explanation="The key is a single attribute, so there can be no partial dependency and R is in 2NF. But B -> C has a left side that is not a super key and a right side, C, that is not prime, which is a transitive dependency. So R fails 3NF, and with it BCNF.",
                 hint="With a single column key, 2NF is easy. Check B -> C against the 3NF rule."),
            dict(id='challenge-dbms-normalization-q3', kind='prediction', title='3NF but not BCNF',
                 prompt="In Teaching(student, subject, teacher), teacher -> subject and (student, subject) -> teacher. The table is in 3NF but not BCNF. Why?",
                 options=["Because subject depends on part of the key (student, subject)", "Because there are no candidate keys with two columns", "Because teacher -> subject has a left side that is not a super key, but subject is prime", "Because the table has a transitive dependency on a non prime attribute"],
                 answer=2,
                 explanation="3NF allows X -> A when A is prime, and subject belongs to the candidate key (student, subject), so 3NF holds. BCNF has no such exception and requires teacher to be a super key, which it is not. There is no non prime attribute here at all, so neither partial nor transitive dependency of a non prime attribute applies.",
                 hint="Which escape clause does 3NF have that BCNF lacks?"),
            dict(id='challenge-dbms-normalization-q4', kind='prediction', title='Is the split lossless',
                 prompt="R(A, B, C) has the dependency A -> B. You split it into R1(A, B) and R2(A, C). Is the decomposition lossless?",
                 options=["Lossy, because C does not appear in R1", "Lossless only if B -> C also holds", "You cannot tell without looking at the data", "Lossless, because the shared column A is a key of R1"],
                 answer=3,
                 explanation="The shared attribute is A, and A -> B makes A a key of R1(A, B). Each row of R2 then joins with exactly one row of R1, so no extra rows appear. Not every column needs to be in every piece, B -> C is irrelevant to this test, and the dependency guarantees the result for any valid data.",
                 hint="Check whether the common columns determine everything in one of the pieces."),
            dict(id='challenge-dbms-normalization-q5', kind='prediction', title='Naming the anomaly',
                 prompt="In an unnormalized Enrollment table, the last student taking 'Compilers' drops it. Deleting that row also wipes out the course's title. Which anomaly is this?",
                 options=["Insertion anomaly", "Deletion anomaly", "Update anomaly"],
                 answer=1,
                 explanation="Removing one fact, the enrollment, unintentionally removed another fact, the course title. That is a deletion anomaly. An insertion anomaly is being unable to add a fact without an unrelated one, and an update anomaly is having to change the same fact in many rows.",
                 hint="Which operation caused the loss?"),
        ],
    ),
    dict(
        id='guide-cs-fundamentals-dbms-transactions-and-acid', kind='guide', track='cs-fundamentals', subject='DBMS',
        title='Transactions and ACID', order=4,
        summary="See how a database groups work into transactions and keeps the ACID promises, including the isolation levels and the anomalies each one allows.",
        sections=[
            dict(title='What a transaction is', text=(
                "A transaction is a group of operations the database treats as one unit of work. "
                "The usual example is moving 500 rupees from account A to account B: subtract 500 from A, then add 500 to B. "
                "If the system stops between those two steps, money has vanished. A transaction makes sure that cannot be the final state.\n\n"
                "You start a transaction with BEGIN, do your reads and writes, then end with COMMIT to make the changes permanent or ROLLBACK to throw them away.\n\n"
                "A transaction moves through states. It is active while running, partially committed after its last statement, and committed once the commit is safely recorded. "
                "If something goes wrong it becomes failed, and after rollback it is aborted. "
                "The four promises a database makes about transactions are summed up as ACID: atomicity, consistency, isolation and durability."
            )),
            dict(title='Atomicity and durability', text=(
                "Atomicity means all or nothing. Either every change in the transaction takes effect or none does. "
                "If the transfer fails after debiting A, the database undoes that debit.\n\n"
                "Durability means that once the database says committed, the change survives crashes, power cuts and restarts.\n\n"
                "Both are usually built on a log. With write ahead logging, the database writes a description of each change to the log before the changed data page reaches disk. "
                "A transaction counts as committed once its commit record is flushed to stable storage, even if the data pages are still only in memory.\n\n"
                "After a crash, recovery reads the log. It redoes the changes of committed transactions whose pages never reached disk, which gives durability, "
                "and undoes changes of transactions that never committed, which gives atomicity. This is why committing can be fast: only the log must be flushed, not every page."
            )),
            dict(title='Consistency and isolation', text=(
                "Consistency means a transaction takes the database from one valid state to another. "
                "Valid means all declared rules hold: keys, foreign keys, CHECK constraints, and business rules like the total money across accounts staying the same during a transfer. "
                "The database enforces the rules you declare, but the application must write transactions that make sense. "
                "That is why consistency is often called the property the application shares responsibility for.\n\n"
                "Isolation means concurrent transactions should not see each other's half finished work. "
                "The gold standard is serializability: running transactions together gives the same result as running them one after another in some order.\n\n"
                "Full serializability costs performance, so databases offer weaker isolation levels. "
                "Each level allows certain anomalies in exchange for more concurrency, which is the topic of the next section."
            )),
            dict(title='Isolation levels and their anomalies', text=(
                "The SQL standard names three read anomalies. "
                "A dirty read is reading data another transaction wrote but has not committed, which might be rolled back. "
                "A non repeatable read is reading the same row twice and getting different values because another transaction updated it and committed in between. "
                "A phantom read is running the same query twice and getting a different set of rows because another transaction inserted or deleted matching rows.\n\n"
                "Read uncommitted allows all three. Read committed prevents dirty reads only. "
                "Repeatable read prevents dirty and non repeatable reads, but the standard still allows phantoms. "
                "Serializable prevents all three and behaves like some serial order.\n\n"
                "Real systems differ in detail. PostgreSQL and Oracle default to read committed, and MySQL InnoDB defaults to repeatable read, where snapshot reads avoid most phantoms. "
                "In an interview, state the standard table first, then mention that engines may be stricter."
            )),
        ],
        keyPoints=[
            "A transaction is one unit of work that ends in COMMIT or ROLLBACK.",
            "Atomicity is all or nothing; durability means committed changes survive crashes.",
            "Write ahead logging supports both: undo for atomicity, redo for durability.",
            "Read committed stops dirty reads, repeatable read also stops non repeatable reads, serializable also stops phantoms.",
            "Consistency depends on both declared constraints and correct application logic.",
        ],
        challenges=[
            dict(id='challenge-dbms-transactions-and-acid-q1', kind='prediction', title='Reading a value that disappears',
                 prompt="T1 updates a row's price to 90 but has not committed. T2 reads the row and sees 90. Then T1 rolls back. What anomaly did T2 experience?",
                 options=["Dirty read", "Phantom read", "Non repeatable read", "Lost update"],
                 answer=0,
                 explanation="T2 read a value written by a transaction that never committed, which is the definition of a dirty read. A non repeatable read involves committed changes between two reads of the same row, a phantom involves a changing set of rows, and a lost update involves two writers overwriting each other.",
                 hint="Was the value T2 saw ever committed?"),
            dict(id='challenge-dbms-transactions-and-acid-q2', kind='prediction', title='Lowest level that fixes it',
                 prompt="Under the SQL standard, what is the lowest isolation level that prevents non repeatable reads?",
                 options=["Read uncommitted", "Read committed", "Repeatable read", "Serializable"],
                 answer=2,
                 explanation="Read committed only stops dirty reads, so a row can still change between your two reads. Repeatable read is the first level that guarantees rows you read stay the same. Serializable also prevents it but is not the lowest such level.",
                 hint="List what each level prevents beyond the one below it."),
            dict(id='challenge-dbms-transactions-and-acid-q3', kind='prediction', title='Crash right after commit',
                 prompt="A transaction commits and the database confirms success. The power fails before the changed data pages are written to disk, but the commit record was flushed to the log. What do you see after restart?",
                 options=["The change is lost, because the data pages never reached disk", "The change is present, because recovery redoes it from the log", "The database keeps half the change and flags the row as corrupt"],
                 answer=1,
                 explanation="Durability is guaranteed by the log, not by the data pages. Because the commit record and change records were flushed, recovery replays them, so the committed change reappears. Losing it would break durability, and a half applied change would break atomicity.",
                 hint="What exactly must be on disk for a commit to count?"),
            dict(id='challenge-dbms-transactions-and-acid-q4', kind='prediction', title='Which property is shared',
                 prompt="A transfer running alone debits A by 500 but, due to a coding bug, credits B by 50, then commits. No constraint is violated. Which ACID property did the application break?",
                 options=["Atomicity", "Isolation", "Durability", "Consistency"],
                 answer=3,
                 explanation="All the steps ran and committed together, so atomicity held, no concurrency was involved, so isolation is not the issue, and the result was saved, so durability held. The broken business rule, that total money is unchanged, is a consistency problem, which depends on the application writing correct transactions.",
                 hint="The database did everything it was told to do."),
            dict(id='challenge-dbms-transactions-and-acid-q5', kind='prediction', title='The count changed',
                 prompt="T1 counts employees with salary over 50000 and gets 10. T2 inserts a new employee with salary 60000 and commits. T1 runs the same count again and gets 11. What anomaly is this?",
                 options=["Dirty read", "Non repeatable read", "Phantom read"],
                 answer=2,
                 explanation="No existing row changed; a new row appeared in the set matching T1's condition. That is a phantom read. It is not dirty, because T2 committed first, and it is not a non repeatable read, which is about an existing row's values changing.",
                 hint="Did a row change, or did the set of rows change?"),
        ],
    ),
    dict(
        id='guide-cs-fundamentals-dbms-indexing', kind='guide', track='cs-fundamentals', subject='DBMS',
        title='Indexing', order=5,
        summary="Learn how indexes speed up lookups, how B+ trees work, and the difference between clustered, non-clustered, dense and sparse indexes.",
        sections=[
            dict(title='Why indexes exist', text=(
                "Without an index, finding a row means reading the whole table and checking each row, which is a full table scan. "
                "For ten rows that is fine. For ten million it is painfully slow.\n\n"
                "An index is a separate structure that maps values of a column, the search key, to where the matching rows live. "
                "It works like the index at the back of a book: instead of reading every page to find 'deadlock', you look it up and jump to the right page.\n\n"
                "Indexes are not free. Each one takes disk space, and every INSERT, UPDATE or DELETE that touches the indexed column must also update the index. "
                "So a table with many indexes reads fast but writes slower. "
                "The art is to index the columns your queries actually filter, join or sort on, and not every column just in case."
            )),
            dict(title='B+ trees and hash indexes', text=(
                "Most database indexes are B+ trees. A B+ tree is balanced, so every leaf is at the same depth, and each node holds many keys, often hundreds, because a node fills a disk page. "
                "That high fanout keeps the tree shallow: three or four levels can cover millions of rows, so a lookup reads only a handful of pages.\n\n"
                "Internal nodes only guide the search. All actual entries sit in the leaves, which are kept in key order and linked to their neighbours. "
                "That link is what makes range queries fast: find the first key, then walk sideways along the leaves.\n\n"
                "A hash index instead hashes the key to a bucket. It is excellent for equality, like WHERE id = 42, with roughly constant cost. "
                "But hashing scatters neighbouring values, so it cannot help with ranges, sorting or prefix searches. That is why B+ trees are the default."
            )),
            dict(title='Clustered and non-clustered indexes', text=(
                "A clustered index decides the physical order in which rows are stored. In engines like MySQL InnoDB, the table itself is the B+ tree of the primary key, with full rows in the leaves. "
                "Because rows can be stored in only one order, a table has at most one clustered index.\n\n"
                "A non-clustered, or secondary, index is a separate structure. Its leaves hold the key plus a pointer to the row, either a physical row address or the row's primary key value. "
                "A table can have many of these.\n\n"
                "The difference shows up in cost. A range query on the clustered key reads rows that sit next to each other. "
                "A lookup through a secondary index finds the pointer first, then makes a second trip to fetch the row, and a wide range can mean many scattered trips.\n\n"
                "If a secondary index already contains every column a query needs, the second trip is skipped. That is called a covering index."
            )),
            dict(title='Dense, sparse and multilevel indexes', text=(
                "Textbooks also classify indexes by how many entries they keep.\n\n"
                "A dense index has an entry for every search key value in the data file. You can answer 'does key 57 exist?' from the index alone.\n\n"
                "A sparse index has entries for only some values, typically one per data block, holding the first key in that block. "
                "To find key 57, you locate the largest index entry not greater than 57 and scan that block. "
                "This only works if the data file is sorted on the search key, so a sparse index must be on the ordering column. "
                "A secondary index on an unsorted column has to be dense.\n\n"
                "When an index itself grows too large to search quickly, you can build a sparse index on top of it, and another on top of that. "
                "That is a multilevel index, and a B+ tree is essentially a self balancing version of this idea."
            )),
            dict(title='Composite indexes and when indexes do not help', text=(
                "A composite index covers several columns in a fixed order, such as (city, age). Entries are sorted by city first and by age within each city.\n\n"
                "This gives the leftmost prefix rule. The index helps WHERE city = 'Pune', and WHERE city = 'Pune' AND age > 25. "
                "In general it does not help a seek on WHERE age = 30 alone, just as a phone book sorted by surname then first name cannot find everyone named Ravi quickly. Some engines, such as Oracle, MySQL 8.0 and PostgreSQL 18, can do a skip scan, one seek per distinct city, but that only pays off when the leading column has few distinct values.\n\n"
                "Indexes also go unused in other common cases. Wrapping the column in a function, like WHERE YEAR(created_at) = 2024, hides the raw values the index is sorted on, unless you build an expression (function based) index on that exact expression. "
                "A pattern with a leading wildcard, like LIKE '%son', cannot use the sorted order. "
                "And when a condition matches a large share of rows, such as a status column with two values, the optimizer may decide a full scan is cheaper than thousands of index lookups."
            )),
        ],
        keyPoints=[
            "Indexes trade extra storage and slower writes for faster reads.",
            "B+ trees keep entries in sorted, linked leaves, so they handle equality and range queries.",
            "Hash indexes handle equality only.",
            "A table has at most one clustered index; it can have many non-clustered ones.",
            "Sparse indexes need the data sorted on the key; composite indexes follow the leftmost prefix rule.",
        ],
        challenges=[
            dict(id='challenge-dbms-indexing-q1', kind='prediction', title='How many clustered indexes',
                 prompt="How many clustered indexes can a single table have?",
                 options=["At most one", "One per column", "As many as you like", "Exactly two: primary and secondary"],
                 answer=0,
                 explanation="A clustered index defines the physical order of the rows, and rows can only be stored in one order at a time. Additional indexes must be non-clustered structures that point back to the rows.",
                 hint="Think about what a clustered index controls."),
            dict(id='challenge-dbms-indexing-q2', kind='prediction', title='Leftmost prefix',
                 prompt="A table has a composite B+ tree index on (city, age). Which query can use the index to seek directly to matching rows?",
                 options=["WHERE age = 30", "WHERE city = 'Pune' AND age > 25", "WHERE age BETWEEN 20 AND 30"],
                 answer=1,
                 explanation="The index is sorted by city first, then age within each city. Fixing city lets the engine jump to the Pune section and then use the age order inside it. Conditions on age alone skip the leading column, and ages are scattered across every city, so there is no single place to seek to.",
                 hint="Entries are sorted by the first column before the second."),
            dict(id='challenge-dbms-indexing-q3', kind='prediction', title='Range on a hash index',
                 prompt="You need to run WHERE price BETWEEN 100 AND 200 frequently. Which index type suits this best?",
                 options=["A hash index, because lookups are constant time", "Either one, they perform the same on ranges", "Neither; ranges always need a full scan", "A B+ tree, because its leaves are in key order and linked"],
                 answer=3,
                 explanation="A B+ tree finds 100 and then walks along the linked leaves until it passes 200. A hash index scatters nearby prices into unrelated buckets, so it only helps exact matches. A full scan is not required when a sorted index exists.",
                 hint="Which structure keeps neighbouring values next to each other?"),
            dict(id='challenge-dbms-indexing-q4', kind='prediction', title='Requirement for a sparse index',
                 prompt="What must be true for a sparse index on column K to work?",
                 options=["The index must fit entirely in memory", "Every value of K must be unique", "The data file must be sorted on K", "Column K must not contain NULLs"],
                 answer=2,
                 explanation="A sparse index stores one entry per block and relies on scanning forward inside that block. That only finds the right rows if they are physically ordered by K. Uniqueness, NULLs and memory size do not change how the lookup works.",
                 hint="How do you find a key that has no entry of its own in the index?"),
            dict(id='challenge-dbms-indexing-q5', kind='prediction', title='Index everything',
                 prompt="A teammate proposes adding an index on every column of a busy orders table that receives thousands of inserts per second. What is the main problem?",
                 options=["Queries would get slower because the optimizer gets confused", "Every insert must also update every index, slowing writes and using more storage", "Databases forbid more than one index per table", "Indexes stop working once a table has many rows"],
                 answer=1,
                 explanation="Each index is a structure that must be kept in sync, so every insert does extra work per index, and each takes disk space. Optimizers handle many indexes fine, databases allow many non-clustered indexes, and indexes matter most on large tables.",
                 hint="What has to happen to each index when a row is added?"),
        ],
    ),
    dict(
        id='guide-cs-fundamentals-dbms-concurrency-control', kind='guide', track='cs-fundamentals', subject='DBMS',
        title='Concurrency control', order=6,
        summary="Understand how databases run transactions at the same time safely, using serializability, locks, two-phase locking, deadlock handling and MVCC.",
        sections=[
            dict(title='Why interleaving goes wrong', text=(
                "A database runs many transactions at once to stay fast. The order in which their operations interleave is called a schedule. "
                "A serial schedule runs one transaction fully before the next, which is always safe but slow.\n\n"
                "Interleaving can break things. Suppose a balance is 100. T1 reads 100 and plans to add 10. T2 also reads 100 and plans to add 20. "
                "T1 writes 110, then T2 writes 120. The final value is 120, but it should be 130. T1's update has been lost.\n\n"
                "The goal of concurrency control is to allow interleaving while guaranteeing the result matches some serial order. "
                "A schedule with that property is called serializable. "
                "The rest of this guide covers how databases check for it and enforce it: conflict analysis, locking, and versioning."
            )),
            dict(title='Conflict serializability', text=(
                "Two operations conflict if they belong to different transactions, touch the same data item, and at least one of them is a write. "
                "Read and read never conflict. Read and write, write and read, and write and write do.\n\n"
                "A schedule is conflict serializable if you can swap neighbouring non conflicting operations until it becomes a serial schedule. "
                "The practical test is the precedence graph. Draw one node per transaction. "
                "Whenever an operation of Ti conflicts with a later operation of Tj, draw an edge from Ti to Tj, meaning Ti must come first.\n\n"
                "If the graph has no cycle, the schedule is conflict serializable, and any topological order of the graph is an equivalent serial order. "
                "If there is a cycle, such as T1 -> T2 -> T1, no serial order can satisfy both edges, so the schedule is not conflict serializable. "
                "In the lost update example, both reads come before both writes, giving edges in both directions."
            )),
            dict(title='Locks and two-phase locking', text=(
                "Locks are the most common way to enforce serializability. A shared (S) lock lets a transaction read an item, and several transactions can hold shared locks together. "
                "An exclusive (X) lock lets a transaction write, and no other lock of either kind can coexist with it. A request that is not compatible waits.\n\n"
                "Locking alone is not enough; you also need a rule about when locks are taken and released. "
                "Two-phase locking (2PL) splits each transaction into a growing phase, where it may acquire locks but not release any, "
                "and a shrinking phase, which starts at the first release, where it may release locks but not acquire new ones. "
                "2PL guarantees conflict serializable schedules.\n\n"
                "Basic 2PL still allows cascading aborts: if T1 releases an X lock early and T2 reads that value, T1 aborting forces T2 to abort too. "
                "Strict 2PL fixes this by holding all exclusive locks until commit or abort. Rigorous 2PL holds every lock until then. Neither prevents deadlocks."
            )),
            dict(title='Deadlocks', text=(
                "A deadlock happens when transactions wait for each other in a circle. T1 holds a lock on A and wants B, while T2 holds B and wants A. Neither can move.\n\n"
                "Databases usually detect deadlocks with a wait-for graph, where an edge from T1 to T2 means T1 is waiting on a lock T2 holds. "
                "A cycle means deadlock, and the system aborts one transaction, the victim, so the others can continue. Timeouts are a cruder alternative.\n\n"
                "Prevention schemes use transaction timestamps, where an older transaction has a smaller timestamp. "
                "In wait-die, an older transaction may wait for a younger one, but a younger transaction that requests a lock held by an older one is aborted, or dies, and restarts later with its original timestamp. "
                "In wound-wait, an older transaction that requests a lock held by a younger one wounds it, forcing the younger to abort, while a younger requester simply waits. "
                "Keeping the original timestamp means a restarted transaction eventually becomes the oldest and cannot starve."
            )),
            dict(title='Timestamps, optimistic control and MVCC', text=(
                "Locking is pessimistic: it blocks in case a conflict happens. Other approaches exist.\n\n"
                "Timestamp ordering gives each transaction a timestamp and forces conflicting operations to happen in timestamp order. "
                "If a transaction tries to read an item a younger transaction has already written, or write an item a younger transaction has already read or written, it is aborted and restarted with a new timestamp rather than made to wait. Thomas's write rule relaxes the last case: an outdated write over a younger write is simply ignored.\n\n"
                "Optimistic concurrency control lets transactions run freely on private copies, then validates at commit time that nothing they read was changed by others. "
                "It works well when conflicts are rare.\n\n"
                "Multiversion concurrency control (MVCC) keeps several versions of each row. A reader sees a consistent snapshot of committed data as of some point, while writers create new versions. "
                "The big win is that readers do not block writers and writers do not block readers. "
                "PostgreSQL, Oracle and MySQL InnoDB all use MVCC, usually combined with locks for write-write conflicts."
            )),
        ],
        keyPoints=[
            "Two operations conflict when they are from different transactions, on the same item, and at least one writes.",
            "A schedule is conflict serializable if its precedence graph has no cycle.",
            "2PL: a growing phase then a shrinking phase; it guarantees conflict serializability but not freedom from deadlock.",
            "Strict 2PL holds exclusive locks until commit or abort, which avoids cascading aborts.",
            "Wait-die and wound-wait prevent deadlocks using timestamps; MVCC lets readers and writers avoid blocking each other.",
        ],
        challenges=[
            dict(id='challenge-dbms-concurrency-control-q1', kind='prediction', title='Shared then exclusive',
                 prompt="T1 holds a shared lock on row R. T2 requests an exclusive lock on R. What happens under standard locking?",
                 options=["T2 gets the lock immediately", "T2 waits until T1 releases its lock", "T1's lock is silently upgraded to exclusive", "T1 is always aborted to make room"],
                 answer=1,
                 explanation="An exclusive lock is incompatible with any other lock, including shared, so T2 must wait. Shared locks only coexist with other shared locks. No upgrade happens to T1 unless T1 asks for it, and aborting is a deadlock or prevention decision, not the default response to a conflict.",
                 hint="Check the lock compatibility rules."),
            dict(id='challenge-dbms-concurrency-control-q2', kind='prediction', title='Locking after a release',
                 prompt="Under basic two-phase locking, transaction T has locked A and B, then released its lock on A. Can T now acquire a lock on C?",
                 options=["Yes, because C is unrelated to A", "Yes, but only a shared lock", "No, because releasing A started its shrinking phase"],
                 answer=2,
                 explanation="The first release ends the growing phase. From then on, 2PL allows releases only, whatever the item or lock mode. That rule is exactly what produces the serializability guarantee.",
                 hint="What marks the boundary between the two phases?"),
            dict(id='challenge-dbms-concurrency-control-q3', kind='prediction', title='What strict 2PL adds',
                 prompt="What does strict two-phase locking add on top of basic two-phase locking?",
                 options=["Exclusive locks are held until commit or abort, so no one reads uncommitted writes and cascading aborts are avoided", "It prevents deadlocks entirely", "It allows new locks after the first release", "It removes the need for shared locks"],
                 answer=0,
                 explanation="Holding exclusive locks until the end means other transactions cannot read data that might still be rolled back, so one abort never forces others to abort. Strict 2PL can still deadlock, it is stricter rather than looser about acquiring locks, and it still uses shared locks for reads.",
                 hint="Think about when the write locks are released."),
            dict(id='challenge-dbms-concurrency-control-q4', kind='prediction', title='Reading a precedence graph',
                 prompt="A schedule's precedence graph has edges T1 -> T2, T2 -> T3 and T3 -> T1. What can you conclude?",
                 options=["It is equivalent to the serial order T1, T2, T3", "It is equivalent to the serial order T3, T1, T2", "A deadlock must have occurred", "It is not conflict serializable"],
                 answer=3,
                 explanation="The edges form a cycle, so any serial order would break at least one of them; for example T1, T2, T3 violates T3 -> T1. That means the schedule is not conflict serializable. A precedence graph describes conflict order, not waiting, so it says nothing about deadlock.",
                 hint="Look for a cycle."),
            dict(id='challenge-dbms-concurrency-control-q5', kind='prediction', title='Wait-die in action',
                 prompt="Using wait-die, T1 has timestamp 5 and holds a lock on X. T2, with timestamp 10, requests a conflicting lock on X. What happens?",
                 options=["T2 waits for T1 to finish", "T2 is aborted and later restarts with timestamp 10", "T1 is aborted so T2 can proceed", "T2 is restarted with a fresh, larger timestamp"],
                 answer=1,
                 explanation="T2 is younger, with a larger timestamp. In wait-die only older transactions may wait, so the younger requester dies. It restarts with its original timestamp so it ages and cannot starve. Aborting the holder is what wound-wait does when an older transaction requests, which is not this case.",
                 hint="In wait-die, who is allowed to wait: the older or the younger?"),
        ],
    ),
]
