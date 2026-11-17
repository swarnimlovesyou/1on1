"""SQL guides for the CS fundamentals track (orders 1-6). Quiz results were checked by running them in SQLite;
where SQLite departs from standard SQL or PostgreSQL, the text says which behaviour it describes."""


def q(slug, n, title, prompt, options, answer, explanation, hint):
    return dict(id=f'challenge-sql-{slug}-q{n}', kind='prediction', title=title, prompt=prompt,
                options=options, answer=answer, explanation=explanation, hint=hint)


GUIDES = [
    # 1 ---------------------------------------------------------------------------------------------
    dict(
        id='guide-cs-fundamentals-sql-select-and-filtering', kind='guide', track='cs-fundamentals', subject='SQL',
        title='SELECT and filtering', order=1,
        summary="How a SELECT query is evaluated, how WHERE decides which rows survive, and why NULL breaks the usual rules of comparison.",
        sections=[
            dict(title='The order a query is evaluated in', text=(
                "A SELECT statement is written in one order but evaluated in another. Logically, the database starts with FROM to "
                "decide which tables supply rows, applies WHERE to keep only the rows that pass, forms groups with GROUP BY, filters "
                "those groups with HAVING, computes the SELECT list, and finally sorts with ORDER BY. A row limit such as LIMIT or "
                "FETCH FIRST comes last of all. Real engines reorder the physical work for speed, but the result must always match "
                "this logical order.\n\n"
                "This order explains rules that otherwise look arbitrary. Take a table students(id, name, city, year, score). In "
                "standard SQL you cannot write SELECT name, score * 2 AS doubled FROM students WHERE doubled > 100, because WHERE "
                "runs before the SELECT list has created the alias doubled. You can write ORDER BY doubled, since ORDER BY runs after "
                "SELECT. PostgreSQL, MySQL and SQL Server reject the alias in WHERE; SQLite accepts it as an extension, but interviewers "
                "expect the standard answer. When "
                "a query surprises you, walk it through the logical order and ask what exists at each step.")),
            dict(title='Filtering rows with WHERE', text=(
                "WHERE takes a condition and keeps each row for which that condition is true. You build conditions from comparisons "
                "(=, <>, <, >, <=, >=) joined with AND, OR and NOT. AND binds more tightly than OR, so city = 'Pune' OR city = 'Delhi' "
                "AND year = 2 means city = 'Pune' OR (city = 'Delhi' AND year = 2). Add parentheses whenever you mix the two; they "
                "cost nothing and remove all doubt for the next reader.\n\n"
                "A few shorthands are worth knowing well. BETWEEN 50 AND 70 is inclusive at both ends, exactly the same as score >= 50 "
                "AND score <= 70. IN ('Pune', 'Delhi') is shorthand for a chain of equalities joined by OR. LIKE matches text "
                "patterns: % stands for any run of characters, including none, and _ stands for exactly one character. So name LIKE "
                "'Ra_%' matches Ravi and Raj but not a name that is just Ra. Whether LIKE is case sensitive depends on the database "
                "and its collation: PostgreSQL's LIKE is case sensitive (ILIKE is not), SQLite's ignores case for ASCII letters by "
                "default, so 'Ra_%' also matches ravi there, and MySQL follows the column's collation, which is usually case "
                "insensitive.")),
            dict(title='NULL and three-valued logic', text=(
                "NULL means a value is missing or unknown. It is not zero and not an empty string, and it is not equal to anything, "
                "not even another NULL. Any ordinary comparison involving NULL, such as city = NULL or NULL = NULL, evaluates to "
                "unknown rather than true or false. SQL therefore works with three truth values: true, false and unknown.\n\n"
                "WHERE keeps a row only when its condition is true. Rows where the condition is false or unknown are both dropped. "
                "This is why WHERE city <> 'Pune' silently skips students whose city is NULL: for them the comparison is unknown, "
                "not true. To test for a missing value, use IS NULL or IS NOT NULL, which always give a plain true or false. If you "
                "want the NULL rows kept in the earlier filter, say so: WHERE city <> 'Pune' OR city IS NULL.\n\n"
                "NOT does not rescue you either. NOT unknown is still unknown, so wrapping a comparison in NOT never brings back rows "
                "that were lost to NULL.")),
            dict(title='Removing duplicates, sorting and limiting', text=(
                "SELECT DISTINCT removes duplicate rows from the result, comparing whole rows across every selected column. For this "
                "purpose NULLs count as equal to each other, so a city column holding Pune, NULL, Pune and NULL gives two distinct "
                "rows: Pune and NULL. GROUP BY treats NULLs the same way.\n\n"
                "ORDER BY sorts the final result. You can sort by several columns, as in ORDER BY year DESC, name, where the second "
                "column only breaks ties in the first. Where NULLs land by default depends on the database: PostgreSQL and Oracle "
                "sort NULL as if it were larger than every value, so NULLs come last ascending and first descending, while MySQL, "
                "SQLite and SQL Server sort it as smaller, so NULLs come first ascending and last descending. Standard SQL lets you "
                "write NULLS FIRST or NULLS LAST; PostgreSQL, Oracle and SQLite (from version 3.30) accept it, but MySQL and SQL "
                "Server do not, so there you put a key such as CASE WHEN city IS NULL THEN 1 ELSE 0 END ahead of the column.\n\n"
                "Without ORDER BY, the database may return rows in any order, and that order can change between runs, so never rely "
                "on it. To keep only part of a result, standard SQL uses FETCH FIRST 5 ROWS ONLY, and MySQL, PostgreSQL and SQLite "
                "also accept LIMIT 5. A limit without ORDER BY gives you some five rows, not the top five.")),
        ],
        keyPoints=[
            "Logical order: FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY, then any row limit.",
            "A SELECT alias is not visible in WHERE in standard SQL, but it is visible in ORDER BY.",
            "AND binds tighter than OR; use parentheses whenever you mix them.",
            "Any comparison with NULL is unknown, and WHERE keeps only rows that are true; test with IS NULL.",
            "BETWEEN is inclusive at both ends, and DISTINCT treats NULLs as one value.",
            "Row order is only guaranteed by ORDER BY, so a limit without it is not a top-N.",
        ],
        challenges=[
            q('select-and-filtering', 1, 'Not equal and NULL',
              "The students table has five rows whose city values are Pune, Delhi, NULL, Pune and Mumbai. What does SELECT COUNT(*) "
              "FROM students WHERE city <> 'Pune' return?",
              ['3', '2', '1', '5'], 1,
              "Delhi and Mumbai pass the test. For the NULL row, NULL <> 'Pune' is unknown, and WHERE drops anything that is not true, "
              "so the count is 2. Answering 3 assumes NULL counts as different from Pune, which SQL does not do. 1 and 5 do not match "
              "any reading of the rows.",
              "Work out the truth value of the condition for the row whose city is NULL."),
            q('select-and-filtering', 2, 'AND and OR together',
              "Rows: (Asha, Pune, year 1), (Ben, Delhi, year 1), (Chen, Delhi, year 2), (Dev, Pune, year 3). Which names does SELECT "
              "name FROM students WHERE city = 'Pune' OR city = 'Delhi' AND year = 2 return?",
              ['Chen only', 'Asha, Ben, Chen and Dev', 'Asha, Chen and Dev'], 2,
              "AND binds tighter than OR, so the condition is city = 'Pune' OR (city = 'Delhi' AND year = 2). Asha and Dev pass the "
              "first part, Chen passes the second, and Ben fails both. Chen only would be the result of (Pune OR Delhi) AND year = 2. "
              "All four would need year = 2 to be ignored entirely.",
              "Put in the parentheses SQL adds for you before evaluating each row."),
            q('select-and-filtering', 3, 'Alias in WHERE',
              "What happens in standard SQL when you run SELECT name, score * 2 AS doubled FROM students WHERE doubled > 100?",
              ["It fails, because WHERE is evaluated before the SELECT list defines doubled",
               "It works and returns students whose score is above 50",
               "It works but ignores the WHERE clause, so every student is returned"], 0,
              "WHERE is evaluated before SELECT, so the alias doubled does not exist yet and the column reference cannot be "
              "resolved. You would repeat the expression (WHERE score * 2 > 100) or wrap the query in a subquery. SQLite accepts "
              "the alias as an extension and would return students scoring above 50, but that is not standard. No database "
              "silently ignores a WHERE clause.",
              "Walk the query through the logical evaluation order and ask what exists at each step."),
            q('select-and-filtering', 4, 'BETWEEN boundaries',
              "A results table has scores 49, 50, 65, 70 and 71. How many rows does WHERE score BETWEEN 50 AND 70 keep?",
              ['1', '2', '4', '3'], 3,
              "BETWEEN includes both ends, so 50, 65 and 70 pass, giving 3. Answering 1 treats both ends as exclusive, 2 treats one "
              "end as exclusive, and 4 wrongly lets one of the outside values through.",
              "Rewrite BETWEEN as two comparisons and check each boundary value."),
            q('select-and-filtering', 5, 'DISTINCT with NULLs',
              "A city column holds Pune, NULL, Pune, NULL and Delhi. How many rows does SELECT DISTINCT city FROM students return?",
              ['3', '2', '4'], 0,
              "DISTINCT treats NULLs as duplicates of each other, so the result is Pune, Delhi and a single NULL: 3 rows. Answering 2 "
              "drops NULL entirely, and 4 keeps both NULLs as separate values, which DISTINCT does not do even though NULL = NULL is "
              "unknown in a WHERE clause.",
              "Recall how GROUP BY city would split these same five values."),
        ],
    ),
    # 2 ---------------------------------------------------------------------------------------------
    dict(
        id='guide-cs-fundamentals-sql-joins', kind='guide', track='cs-fundamentals', subject='SQL',
        title='Joins', order=2,
        summary="How inner, outer, cross and self joins combine rows, and how to predict the exact number of rows a join returns.",
        sections=[
            dict(title='What a join does', text=(
                "A join combines rows from two tables into wider rows. Use a small schema: students(id, name), courses(id, title) and "
                "enrollments(student_id, course_id), where each enrollment links one student to one course.\n\n"
                "Conceptually, an inner join considers every pairing of a row from the left table with a row from the right table and "
                "keeps the pairs for which the ON condition is true. SELECT s.name, e.course_id FROM students s INNER JOIN enrollments "
                "e ON s.id = e.student_id produces one row for each enrollment that has a matching student. Writing plain JOIN means "
                "the same thing as INNER JOIN.\n\n"
                "Two consequences matter for predicting results. First, rows multiply: a student with three enrollments appears three "
                "times, once per match. Second, rows without a match disappear: a student with no enrollments is not in the result at "
                "all. Most surprises with joins come from forgetting one of these two facts, so count matches per key before you trust "
                "a total.")),
            dict(title='Outer joins keep unmatched rows', text=(
                "A LEFT JOIN returns everything an inner join would, plus every left row that found no match, padded with NULLs in "
                "the right table's columns. SELECT s.name, e.course_id FROM students s LEFT JOIN enrollments e ON s.id = e.student_id "
                "lists every student; those with no enrollments appear once with course_id NULL. RIGHT JOIN is the mirror image, "
                "keeping every right row, and you can always rewrite it as a LEFT JOIN by swapping the tables. FULL OUTER JOIN keeps "
                "unmatched rows from both sides.\n\n"
                "The classic trap is where you put an extra condition. In a LEFT JOIN, a condition in ON decides which right rows "
                "match, and unmatched left rows survive regardless. The same condition in WHERE is applied after the join, to the "
                "padded rows too. Writing WHERE e.course_id = 10 throws away every padded row, because NULL = 10 is unknown, so the "
                "query quietly behaves like an inner join. If you want all students with their course 10 enrollment where one exists, "
                "the filter belongs in ON.")),
            dict(title='Cross joins and self joins', text=(
                "A CROSS JOIN has no condition at all: it pairs every row of one table with every row of the other, so tables with m "
                "and n rows give m times n rows. That is useful for generating combinations, such as every student paired with every "
                "available exam slot. It also means that if either table is empty, the result is empty, because there is nothing to "
                "pair with. Forgetting the ON condition in older comma-style joins (FROM a, b) produces this same explosion by "
                "accident.\n\n"
                "A self join joins a table to itself, using two aliases so you can tell the copies apart. With employees(id, name, "
                "manager_id), the query SELECT e.name, m.name FROM employees e JOIN employees m ON e.manager_id = m.id pairs each "
                "employee with their manager's row. Because it is an inner join, the person at the top, whose manager_id is NULL, is "
                "left out. Change it to LEFT JOIN employees m and that person appears with a NULL manager name.")),
            dict(title='Finding rows with no match', text=(
                "A frequent interview task is to find rows in one table that have no partner in another, such as students who have "
                "never enrolled. One standard pattern is the anti-join: SELECT s.name FROM students s LEFT JOIN enrollments e ON s.id "
                "= e.student_id WHERE e.student_id IS NULL. The LEFT JOIN keeps every student, and the WHERE then keeps only the "
                "padded rows, which are exactly the students with no match. Test a column that cannot be NULL in a real match, such "
                "as the join key itself. NOT EXISTS with a correlated subquery does the same job and is often clearer.\n\n"
                "Remember that NULL keys never match in an ordinary join. If both tables contain a NULL in the join column, a = b is "
                "unknown for that pair, so they are not joined. An enrollment row with a NULL student_id simply drops out of an inner "
                "join, and in a LEFT JOIN from enrollments it would appear with NULL student columns.")),
        ],
        keyPoints=[
            "An inner join keeps only pairs where ON is true; unmatched rows vanish and multiple matches multiply rows.",
            "LEFT JOIN keeps every left row and fills the right side with NULLs when nothing matches.",
            "In an outer join, a filter on the right table in WHERE turns it back into an inner join; put it in ON instead.",
            "CROSS JOIN returns m times n rows, so an empty table on either side gives an empty result.",
            "A self join uses two aliases of one table, such as employees and their managers.",
            "NULL join keys never match, and LEFT JOIN plus IS NULL finds rows with no partner.",
        ],
        challenges=[
            q('joins', 1, 'Counting LEFT JOIN rows',
              "students has ids 1, 2, 3 and 4. enrollments has (student_id, course_id) rows (1, 10), (1, 20) and (2, 20). How many "
              "rows does SELECT * FROM students s LEFT JOIN enrollments e ON s.id = e.student_id return?",
              ['4', '5', '3', '7'], 1,
              "Student 1 matches twice, student 2 once, and students 3 and 4 have no match, so each appears once with NULLs: 2 + 1 + "
              "1 + 1 = 5. 4 assumes a left join never adds rows beyond the left table, 3 is the inner join count, and 7 adds the two "
              "table sizes.",
              "Count the matches for each student, using one for a student with no matches."),
            q('joins', 2, 'Filter in WHERE after a LEFT JOIN',
              "Using the same data, how many rows does SELECT s.id, e.course_id FROM students s LEFT JOIN enrollments e ON s.id = "
              "e.student_id WHERE e.course_id = 10 return?",
              ['1', '4', '2'], 0,
              "The join produces 5 rows, then WHERE keeps only rows where course_id = 10 is true. Only (1, 10) qualifies; the padded "
              "rows have course_id NULL, and NULL = 10 is unknown, so they are dropped. 4 is what you get with the condition moved "
              "into ON. 2 would count student 1's two enrollments.",
              "Decide whether this filter runs before or after the NULL padding is added."),
            q('joins', 3, 'Cross join with an empty table',
              "Table a has 3 rows and table b has no rows. What does SELECT * FROM a CROSS JOIN b return?",
              ['3 rows, one per row of a, with NULLs for b', '1 row of NULLs', '0 rows'], 2,
              "A cross join returns every pairing, and 3 times 0 is 0. There is no padding in a cross join; that behaviour belongs "
              "to outer joins. A single row of NULLs is not produced by any join type here.",
              "Think about what each row of a has to be paired with."),
            q('joins', 4, 'NULL join keys',
              "Table a has x values 1, NULL and 2. Table b has x values NULL, 2 and 2. How many rows does SELECT * FROM a JOIN b ON "
              "a.x = b.x return?",
              ['3', '2', '1'], 1,
              "The value 2 in a matches both 2s in b, giving 2 rows. The NULLs never match because NULL = NULL is unknown, and 1 has "
              "no partner. Answering 3 counts the NULL pair as a match, and 1 forgets that one row can match several.",
              "Treat NULL = NULL exactly as the ON clause would."),
            q('joins', 5, 'Keeping the top of a hierarchy',
              "employees has (id, name, manager_id): (1, Ria, NULL), (2, Sam, 1), (3, Tom, 1), (4, Uma, 2). SELECT e.name, m.name "
              "FROM employees e JOIN employees m ON e.manager_id = m.id returns Sam, Tom and Uma with their managers. Which change "
              "also returns Ria with a NULL manager name?",
              ["Add WHERE e.manager_id IS NULL",
               "Change the ON clause to m.manager_id = e.id",
               "Change JOIN to LEFT JOIN"], 2,
              "Ria is lost because her manager_id is NULL, so the inner join finds no match. A LEFT JOIN keeps her and fills m.name "
              "with NULL, giving 4 rows. Adding WHERE e.manager_id IS NULL to the inner join returns nothing, since Ria was already "
              "gone. Swapping the ON columns pairs each manager with their reports instead, which answers a different question.",
              "Work out why Ria's row disappears from the original query."),
        ],
    ),
    # 3 ---------------------------------------------------------------------------------------------
    dict(
        id='guide-cs-fundamentals-sql-aggregation-and-group-by', kind='guide', track='cs-fundamentals', subject='SQL',
        title='Aggregation and GROUP BY', order=3,
        summary="How aggregate functions treat NULLs, how GROUP BY forms groups, and when to filter with WHERE versus HAVING.",
        sections=[
            dict(title='Aggregate functions and NULL', text=(
                "An aggregate function reduces many rows to one value. The common ones are COUNT, SUM, AVG, MIN and MAX. Without "
                "GROUP BY, the whole filtered table is one group, so SELECT COUNT(*) FROM enrollments returns a single row.\n\n"
                "NULL handling is where most interview questions live. COUNT(*) counts rows, whatever they contain. COUNT(score) "
                "counts only rows where score is not NULL. SUM, AVG, MIN and MAX also skip NULLs. So for scores 40, NULL, 50, NULL "
                "and 60, COUNT(*) is 5, COUNT(score) is 3 and AVG(score) is 50, because the total of 150 is divided by 3, not by 5. "
                "If you want "
                "missing scores treated as zero, say so with COALESCE(score, 0).\n\n"
                "An aggregate over no rows at all still returns one row when there is no GROUP BY. COUNT gives 0, but SUM, AVG, MIN "
                "and MAX give NULL, because there is nothing to add up or compare. Wrap them in COALESCE when you need a 0 instead. "
                "With a GROUP BY, the same empty input forms no groups, so the query returns no rows at all.")),
            dict(title='Grouping rows with GROUP BY', text=(
                "GROUP BY splits the rows into groups that share the same values in the listed columns, then produces one output row "
                "per group. SELECT course_id, COUNT(*) FROM enrollments GROUP BY course_id gives each course with its number of "
                "enrollments. Grouping by two columns, such as GROUP BY course_id, year, makes one group per distinct pair.\n\n"
                "Since each group becomes one row, every expression in the SELECT list must have one value per group. The safe rule "
                "is that each selected column is either in GROUP BY or inside an aggregate. (Newer standards, PostgreSQL and MySQL "
                "also accept a column that is fixed by the grouped columns, such as any column of a table grouped by its primary "
                "key.) Selecting student_id while grouping only by course_id is an error in PostgreSQL and SQL Server, because a "
                "course has many students. MySQL rejects it too while its default ONLY_FULL_GROUP_BY mode is on, but accepts it "
                "with that mode switched off, and SQLite always accepts it. Both then return student_id from some row of the group, "
                "which hides the bug.\n\n"
                "NULLs in the grouping column form a single group of their own. If three rows have city NULL, they become one group, "
                "where COUNT(*) is 3 but COUNT(city) is 0.")),
            dict(title='WHERE versus HAVING', text=(
                "WHERE and HAVING both filter, but at different moments. WHERE runs before grouping and removes individual rows. "
                "HAVING runs after grouping and removes whole groups. Because aggregates are only computed once groups exist, you "
                "cannot use COUNT or SUM in WHERE; that is exactly what HAVING is for.\n\n"
                "Consider this query: SELECT student_id, COUNT(*) FROM enrollments WHERE score >= 50 GROUP BY student_id HAVING "
                "COUNT(*) >= 2. Read it in logical order. WHERE first throws away every enrollment below 50. GROUP BY then collects "
                "what is left per student. HAVING keeps the students who still have at least two rows. The answer is students with "
                "at least two passing scores, which is different from students with at least two scores of any kind.\n\n"
                "A good habit: if a condition is about a single row, put it in WHERE so fewer rows reach the grouping step. Only "
                "conditions about the group as a whole belong in HAVING.")),
            dict(title='Common aggregation mistakes', text=(
                "The first mistake is aggregating after a join that multiplied rows. If you join students to enrollments and then to "
                "payments, a student with three enrollments and two payments produces six joined rows, and SUM(payments.amount) "
                "counts each payment three times. Aggregate each child table separately in a subquery, then join the totals.\n\n"
                "The second is mixing up COUNT(*), COUNT(col) and COUNT(DISTINCT col). COUNT(DISTINCT course_id) counts different "
                "courses, ignoring NULLs, while COUNT(*) counts rows. Asking how many courses a student took and how many enrollments "
                "they have are different questions.\n\n"
                "The third is expecting an empty group to appear. GROUP BY only creates groups for values present in the filtered "
                "rows. A course with no enrollments will not show up with a count of 0 unless you start from courses and LEFT JOIN "
                "enrollments, then count a column from the enrollments side, such as COUNT(e.student_id), so the padded row counts as 0.")),
        ],
        keyPoints=[
            "COUNT(*) counts rows; COUNT(col) and the other aggregates skip NULLs.",
            "Over zero rows, COUNT returns 0 while SUM, AVG, MIN and MAX return NULL.",
            "Every selected column should be grouped or aggregated; SQLite, and MySQL with ONLY_FULL_GROUP_BY off, let it slide.",
            "WHERE filters rows before grouping; HAVING filters groups after, and only HAVING can use aggregates.",
            "NULLs in a grouping column form one group of their own.",
            "Joins that multiply rows inflate SUM and COUNT, so aggregate before joining when needed.",
        ],
        challenges=[
            q('aggregation-and-group-by', 1, 'Three aggregates, one NULL',
              "A column score holds 10, NULL, 20 and 30. What does SELECT COUNT(*), COUNT(score), AVG(score) return?",
              ['4, 3, 20', '4, 4, 15', '3, 3, 20', '4, 3, 15'], 0,
              "COUNT(*) counts all 4 rows. COUNT(score) skips the NULL, giving 3. AVG also skips NULL, so it is 60 / 3 = 20. "
              "Answering 15 divides 60 by 4 as if the NULL were zero, and 3 for COUNT(*) wrongly skips the NULL row.",
              "Check which of these three functions looks at the value and which only counts rows."),
            q('aggregation-and-group-by', 2, 'Filtering on a count',
              "You want departments that offer more than two courses, from courses(id, title, dept). Which query is correct?",
              ["SELECT dept FROM courses WHERE COUNT(*) > 2 GROUP BY dept",
               "SELECT dept FROM courses GROUP BY dept HAVING COUNT(*) > 2",
               "SELECT dept, COUNT(*) > 2 FROM courses GROUP BY dept"], 1,
              "The condition is about each group's size, so it must go in HAVING, which runs after grouping. The WHERE version is an "
              "error because aggregates do not exist yet when WHERE runs. The third query returns every department with a true or "
              "false flag (1 or 0 in SQLite and MySQL) instead of filtering them.",
              "Ask whether the condition is about one row or about a whole group."),
            q('aggregation-and-group-by', 3, 'The NULL group',
              "A city column holds Pune, Pune, NULL, Delhi and NULL. SELECT city, COUNT(*), COUNT(city) FROM students GROUP BY city. "
              "What is COUNT(city) on the row for the NULL group?",
              ['2', 'NULL', '0'], 2,
              "The two NULL rows form one group, so COUNT(*) there is 2. COUNT(city) counts non-NULL values of city, and the group "
              "has none, so it is 0. COUNT never returns NULL, so that option is out, and 2 is the COUNT(*) value.",
              "Compare what COUNT(*) and COUNT(column) each count."),
            q('aggregation-and-group-by', 4, 'WHERE then HAVING',
              "enrollments has (student_id, score) rows (1, 60), (1, 80), (2, 90), (2, 30), (3, 70), (3, 75), (3, 20). How many rows "
              "does SELECT student_id, COUNT(*) FROM enrollments WHERE score >= 50 GROUP BY student_id HAVING COUNT(*) >= 2 return?",
              ['0', '1', '3', '2'], 3,
              "WHERE first removes 30 and 20. What remains is student 1 with 2 rows, student 2 with 1 and student 3 with 2. HAVING "
              "keeps students 1 and 3, so 2 rows. Answering 3 applies HAVING to the unfiltered counts, as if WHERE ran after "
              "grouping.",
              "Apply WHERE to each row first, then count what is left per student."),
            q('aggregation-and-group-by', 5, 'Summing nothing',
              "No enrollment has a score above 100. What does SELECT SUM(score) FROM enrollments WHERE score > 100 return?",
              ['No rows at all', 'One row containing NULL', 'One row containing 0'], 1,
              "Without GROUP BY, an aggregate query always returns exactly one row, even if no input rows qualify. SUM of nothing is "
              "NULL, not 0; only COUNT returns 0 for an empty input. You would write COALESCE(SUM(score), 0) to get 0.",
              "Think about how many groups exist when there is no GROUP BY."),
        ],
    ),
    # 4 ---------------------------------------------------------------------------------------------
    dict(
        id='guide-cs-fundamentals-sql-subqueries', kind='guide', track='cs-fundamentals', subject='SQL',
        title='Subqueries', order=4,
        summary="Scalar, list and table subqueries, correlated versus non-correlated ones, and why NOT IN fails when a NULL is present.",
        sections=[
            dict(title='Three shapes of subquery', text=(
                "A subquery is a SELECT nested inside another statement, and what you may do with it depends on the shape of its "
                "result.\n\n"
                "A scalar subquery returns one row and one column, so it can stand anywhere a single value can. SELECT name FROM "
                "students WHERE score > (SELECT AVG(score) FROM students) compares each student with the overall average. If a scalar "
                "subquery returns more than one row, standard SQL raises an error at run time; PostgreSQL, MySQL, SQL Server and "
                "Oracle all do. SQLite is an exception: it raises no error and quietly uses whichever row the subquery happens to "
                "produce first, so the answer can change with the data's physical order.\n\n"
                "A single-column subquery returning many rows feeds IN, ANY or ALL, as in WHERE id IN (SELECT student_id FROM "
                "enrollments).\n\n"
                "A subquery that returns a whole table can sit in FROM, where it is called a derived table. Standard SQL, MySQL, SQL "
                "Server and PostgreSQL before version 16 require it to have an alias (SQLite does not), so always give one: SELECT "
                "* FROM (SELECT course_id, COUNT(*) AS n FROM enrollments GROUP BY course_id) t WHERE t.n > 30. This is a common way "
                "to filter on an aggregate or a window result computed one level down.")),
            dict(title='Correlated and non-correlated subqueries', text=(
                "A non-correlated subquery stands on its own. You could cut it out and run it by itself, and the database can "
                "evaluate it once and reuse the result. The average in the previous section is an example.\n\n"
                "A correlated subquery refers to a column of the outer query, so its value depends on the current outer row. Using "
                "results(student, course, score), the query SELECT student FROM results r WHERE score > (SELECT AVG(score) FROM "
                "results r2 WHERE r2.course = r.course) compares each score with the average of that row's own course. The reference "
                "to r.course is what makes it correlated.\n\n"
                "Logically, a correlated subquery is evaluated once for every outer row. Optimizers frequently rewrite it into a join "
                "or a grouped computation, so it is not automatically slow, but that per-row model is the right way to reason about "
                "its result. A quick test in an interview: look inside the subquery for an alias that is only defined outside it.")),
            dict(title='IN, EXISTS and the NOT IN trap', text=(
                "EXISTS (subquery) is true if the subquery returns at least one row; the values it returns do not matter, which is why "
                "people write SELECT 1 inside it. It is usually correlated: WHERE EXISTS (SELECT 1 FROM enrollments e WHERE "
                "e.student_id = s.id). IN compares a value with a list. For positive tests, IN and EXISTS normally give the same "
                "rows.\n\n"
                "The negative forms differ when NULLs appear. x NOT IN (1, NULL) means x <> 1 AND x <> NULL. The second comparison is "
                "unknown, so the whole condition can never be true. If the subquery behind NOT IN returns even one NULL, the outer "
                "query returns no rows at all. Suppose students has ids 4, 5, 6 and 7, and enrollments.student_id holds 5, 6 and "
                "NULL. WHERE id NOT IN (SELECT student_id FROM enrollments) returns nothing, while WHERE NOT EXISTS (SELECT 1 FROM "
                "enrollments e WHERE e.student_id = s.id) returns students 4 and 7.\n\n"
                "Prefer NOT EXISTS for anti-joins, or add WHERE student_id IS NOT NULL inside the NOT IN subquery.")),
            dict(title='Subquery, join or CTE?', text=(
                "Many subqueries can be written as joins, but the two are not always equivalent. IN and EXISTS test membership, so "
                "each outer row appears at most once. A join returns one row per match. If student 1 has two enrollments, WHERE id IN "
                "(SELECT student_id FROM enrollments) returns student 1 once, while joining students to enrollments returns them "
                "twice. Pick the form whose row count matches the question.\n\n"
                "A common table expression, written with WITH, names a subquery up front: WITH course_avg AS (SELECT course, "
                "AVG(score) AS avg_score FROM results GROUP BY course) SELECT r.student FROM results r JOIN course_avg c ON c.course "
                "= r.course WHERE r.score > c.avg_score. This gives the same answer as the correlated version but reads top to "
                "bottom, and you can reference the CTE more than once.\n\n"
                "For performance, do not assume one form always wins. Modern optimizers often produce the same plan for IN, EXISTS "
                "and the equivalent join. Write the clearest correct query first, then check the plan.")),
        ],
        keyPoints=[
            "A scalar subquery must return at most one row; more than one is a run-time error in standard SQL.",
            "A correlated subquery references the outer row and is logically evaluated once per outer row.",
            "EXISTS cares only whether any row comes back, not what the row contains.",
            "NOT IN returns no rows if the subquery yields a NULL; NOT EXISTS does not have this problem.",
            "IN never duplicates outer rows, but a join returns one row per match.",
            "A CTE (WITH) names a subquery so the main query reads top to bottom.",
        ],
        challenges=[
            q('subqueries', 1, 'NOT IN meets NULL',
              "students has (1, Al), (2, Bo), (3, Cy). enrollments.student_id holds 1 and NULL. What does SELECT name FROM students "
              "WHERE id NOT IN (SELECT student_id FROM enrollments) return?",
              ['Bo and Cy', 'No rows', 'Only Cy'], 1,
              "For Bo the test is 2 <> 1 AND 2 <> NULL, which is true AND unknown, so unknown, and WHERE drops the row. The same "
              "happens for Cy, and Al fails outright. Bo and Cy is what NOT EXISTS returns. Only Cy has no basis in the data.",
              "Expand NOT IN into a chain of <> comparisons joined by AND."),
            q('subqueries', 2, 'IN does not duplicate',
              "students has (1, Al) and (2, Bo). enrollments has two rows, both with student_id 1. How many rows does SELECT name FROM "
              "students WHERE id IN (SELECT student_id FROM enrollments) return?",
              ['1 row', '2 rows', '3 rows'], 0,
              "IN asks whether each student's id is in the list, so Al qualifies once and Bo does not: 1 row. 2 rows is what an "
              "inner join of students to enrollments would return, one per matching enrollment. 3 rows has no basis.",
              "Ask what IN checks for each student, and what a join would produce instead."),
            q('subqueries', 3, 'Spot the correlated subquery',
              "Which of these queries contains a correlated subquery?",
              ["SELECT s.name FROM students s WHERE s.id IN (SELECT e.student_id FROM enrollments e WHERE e.course_id = 10)",
               "SELECT name FROM students WHERE score > (SELECT AVG(score) FROM students)",
               "SELECT * FROM (SELECT course_id, COUNT(*) AS n FROM enrollments GROUP BY course_id) t WHERE n > 5",
               "SELECT name FROM students s WHERE EXISTS (SELECT 1 FROM enrollments e WHERE e.student_id = s.id)"], 3,
              "Only the last subquery refers to s.id, a column of the outer query, so its result changes from one student to the "
              "next. The other three subqueries can each be run on their own and give the same result regardless of the outer row.",
              "Ask which subquery could not be cut out and run on its own."),
            q('subqueries', 4, 'Above the course average',
              "results has (student, course, score): (A, DB, 70), (B, DB, 90), (C, OS, 60), (D, OS, 65), (E, OS, 70). Which students "
              "does SELECT student FROM results r WHERE score > (SELECT AVG(score) FROM results r2 WHERE r2.course = r.course) "
              "return?",
              ['B only', 'B, D and E', 'B and E'], 2,
              "The subquery is correlated, so each row is compared with its own course average. DB averages 80, so B (90) passes "
              "and A fails. OS averages 65, so E (70) passes, while D (65) is equal, not greater, and C is below. B only is the "
              "answer against the overall average of 71. Including D ignores the strict greater-than.",
              "Compute one average per course, then compare each row with its own course's value."),
            q('subqueries', 5, 'Scalar subquery with many rows',
              "In standard SQL, what happens with SELECT name FROM results WHERE score = (SELECT score FROM results WHERE course = "
              "'OS') when three OS rows exist?",
              ["The query fails at run time because a scalar subquery returned more than one row",
               "It behaves like IN and keeps rows whose score matches any OS score",
               "It compares only against the first OS score"], 0,
              "Using = with a subquery treats it as a single value, and three rows cannot be one value, so PostgreSQL, MySQL, SQL "
              "Server and Oracle raise an error. To match any of them, write IN or = ANY. SQLite is the exception: run there, the "
              "query succeeds and compares only against the first OS score the subquery yields, which is nonstandard and depends on "
              "an undefined row order, so it is not a result you should rely on.",
              "Consider what = expects on its right-hand side."),
        ],
    ),
    # 5 ---------------------------------------------------------------------------------------------
    dict(
        id='guide-cs-fundamentals-sql-window-functions', kind='guide', track='cs-fundamentals', subject='SQL',
        title='Window functions', order=5,
        summary="How window functions compute across related rows without collapsing them, and how ROW_NUMBER, RANK and DENSE_RANK differ.",
        sections=[
            dict(title='Calculations that keep every row', text=(
                "GROUP BY collapses each group into a single row, so you lose the detail. A window function computes a value across "
                "a set of related rows but leaves every row in place. You recognise one by the OVER clause after the function.\n\n"
                "With results(student, course, score), SELECT student, course, score, AVG(score) OVER (PARTITION BY course) AS "
                "course_avg FROM results returns every result row, each carrying the average of its own course. Doing the same with "
                "GROUP BY would need a grouped subquery joined back to the table.\n\n"
                "Window functions are evaluated after WHERE, GROUP BY and HAVING, alongside the SELECT list, and before ORDER BY. "
                "That placement explains two things. A window sees only the rows that survived WHERE, and you can use a window "
                "function in SELECT and ORDER BY but not in WHERE, GROUP BY or HAVING. Ordinary aggregates such as SUM and COUNT "
                "become window functions when you add OVER, and there are dedicated ones such as ROW_NUMBER, RANK, LAG and LEAD.")),
            dict(title='PARTITION BY and ORDER BY inside OVER', text=(
                "PARTITION BY splits rows into independent windows, much as GROUP BY splits them into groups, except that no rows are "
                "merged. Each calculation restarts in every partition. Leave PARTITION BY out and the whole result is one window. "
                "COUNT(*) OVER (PARTITION BY course) puts the size of each course on every row of that course.\n\n"
                "ORDER BY inside OVER gives the rows within each partition an order. Ranking functions need it, and for aggregates it "
                "turns the result into a running calculation. SUM(amount) OVER (ORDER BY day) gives a running total.\n\n"
                "Watch out for ties. When ORDER BY is present and no frame is written, the default frame is RANGE BETWEEN UNBOUNDED "
                "PRECEDING AND CURRENT ROW, and RANGE includes all peers, meaning rows with the same ORDER BY value. With amounts 40 "
                "on day 1, 25 and 15 on day 2, and 30 on day 3, both day 2 rows show 80, not 65 and then 80. If you want a strict "
                "row-by-row running total, write ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW and add a tiebreaker column to the "
                "ORDER BY.")),
            dict(title='ROW_NUMBER, RANK and DENSE_RANK', text=(
                "All three number rows according to the ORDER BY in OVER. They differ only in how they treat ties. Take scores 92, "
                "85, 85, 85 and 70 ordered by score descending.\n\n"
                "ROW_NUMBER gives 1, 2, 3, 4, 5. Every row gets a unique number, so the three 85s get 2, 3 and 4, and which of them "
                "gets which is not defined unless you add a tiebreaker such as ORDER BY score DESC, student.\n\n"
                "RANK gives 1, 2, 2, 2, 5. Tied rows share a rank, and the next row's rank is one more than the number of rows "
                "ahead of it, the way a race result works: three runners tied for second means nobody is third or fourth.\n\n"
                "DENSE_RANK gives 1, 2, 2, 2, 3. Tied rows share a rank, but there are no gaps afterwards.\n\n"
                "Choose by the question. Exactly N rows per group, ties broken arbitrarily: ROW_NUMBER. Everyone in the top N "
                "positions, ties included: RANK. The Nth highest distinct value, such as the second highest salary: DENSE_RANK.")),
            dict(title='Filtering on a window result', text=(
                "A common task is the top N rows per group, such as the best two scores in each course. You cannot write WHERE "
                "ROW_NUMBER() OVER (...) <= 2, because WHERE runs before window functions are computed. Instead, compute the number "
                "one level down and filter outside: SELECT * FROM (SELECT student, course, score, ROW_NUMBER() OVER (PARTITION BY "
                "course ORDER BY score DESC) AS rn FROM results) t WHERE rn <= 2. A CTE written with WITH works the same way. Some "
                "databases add a QUALIFY clause for this, but it is not part of every engine.\n\n"
                "Two more functions are worth knowing. LAG(score) OVER (PARTITION BY student ORDER BY exam_date) returns the value "
                "from the previous row in the window, and LEAD returns the next one. On the first row there is no previous row, so "
                "LAG returns NULL unless you pass a default as its third argument. They make questions such as change since the last "
                "exam a single pass with no self join.")),
        ],
        keyPoints=[
            "A window function, marked by OVER, computes across related rows without collapsing them.",
            "PARTITION BY restarts the calculation per group; ORDER BY inside OVER gives order and running results.",
            "With ORDER BY and no explicit frame, the default RANGE frame includes tied rows, so ties share a running total.",
            "For ties: ROW_NUMBER is always unique, RANK leaves gaps, DENSE_RANK does not.",
            "Window functions run after WHERE, so filter on them in an outer query or CTE.",
            "LAG and LEAD read the previous and next row in the window.",
        ],
        challenges=[
            q('window-functions', 1, 'DENSE_RANK after a tie',
              "Scores are 95, 88, 88, 80 and 75. With DENSE_RANK() OVER (ORDER BY score DESC), what value does the 80 receive?",
              ['3', '4', '2'], 0,
              "DENSE_RANK gives 95 rank 1, both 88s rank 2, and the next value continues without a gap, so 80 is 3. 4 is what RANK "
              "would give, since it skips a number after the two-way tie. 2 would mean 80 tied with the 88s.",
              "Write out the value DENSE_RANK gives each of the five scores in turn."),
            q('window-functions', 2, 'Exactly two per course',
              "You need exactly two rows per course, the two highest scores, even when scores tie. Which function should number the "
              "rows inside each course partition?",
              ['RANK', 'DENSE_RANK', 'ROW_NUMBER'], 2,
              "ROW_NUMBER never repeats a number, so rn <= 2 gives exactly two rows per course. RANK and DENSE_RANK give tied rows "
              "the same number, so filtering on 2 or less can return three or more rows when there is a tie.",
              "Imagine the second and third highest scores in a course are equal, and apply rn <= 2 under each function."),
            q('window-functions', 3, 'Running total with a tie',
              "payments has (day, amount): (1, 10), (2, 20), (2, 5), (3, 15). Using SUM(amount) OVER (ORDER BY day) with no frame "
              "clause, what running total is shown on each day 2 row?",
              ['30', '35', '15'], 1,
              "With ORDER BY and no frame, the default is RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW, which includes every "
              "row with the same day. Both day 2 rows therefore see 10 + 20 + 5 = 35. 30 or 15 would only appear with a ROWS frame, "
              "and then which one came first would depend on the undefined order of the tied rows.",
              "Recall which frame applies when OVER has ORDER BY but no ROWS or RANGE clause."),
            q('window-functions', 4, 'Window function in WHERE',
              "Why does SELECT student FROM results WHERE ROW_NUMBER() OVER (ORDER BY score DESC) = 1 fail?",
              ["ROW_NUMBER requires a PARTITION BY clause",
               "It does not fail; it returns every row because each row is numbered 1",
               "Window functions are only allowed inside a GROUP BY query",
               "Window functions are computed after WHERE, so WHERE cannot use them"], 3,
              "Window functions are evaluated with the SELECT list, after WHERE, so WHERE cannot reference them. Compute the number "
              "in a subquery or CTE and filter in the outer query. PARTITION BY is optional, and window functions do not need GROUP "
              "BY. The query is an error, not a silent wrong result.",
              "Place WHERE and window functions in the logical order of evaluation."),
            q('window-functions', 5, 'Count per partition',
              "results has 2 rows for course DB and 3 rows for course OS. What does SELECT course, COUNT(*) OVER (PARTITION BY "
              "course) FROM results return?",
              ['2 rows, with counts 2 and 3', '5 rows, with 3 on each OS row', '5 rows, with 5 on every row'], 1,
              "A window function keeps every input row, so there are 5 rows. Each partition is counted on its own, so DB rows show "
              "2 and OS rows show 3. Two rows is what GROUP BY course would return. 5 on every row would be COUNT(*) OVER () with no "
              "partition.",
              "Work out the number of output rows first, then the value on each row."),
        ],
    ),
    # 6 ---------------------------------------------------------------------------------------------
    dict(
        id='guide-cs-fundamentals-sql-indexes-and-query-plans', kind='guide', track='cs-fundamentals', subject='SQL',
        title='Indexes and query plans', order=6,
        summary="What an index is, when the database can use one and when it cannot, and how to read a query plan to tell which happened.",
        sections=[
            dict(title='What an index is', text=(
                "Without an index, the only way to find the enrollments for student 7 is to read every row in the table and check "
                "each one. That is a full table scan, and its cost grows with the size of the table.\n\n"
                "An index is a separate structure, kept sorted by one or more columns, that points back to the rows. Most databases "
                "use a B-tree by default: a shallow, balanced tree where each step narrows the search, so finding a key takes "
                "logarithmic time. Even with millions of rows, the database reaches the right entries in a handful of page reads and "
                "then follows pointers to the matching rows. Because the entries are sorted, the same index also serves range "
                "conditions such as score BETWEEN 60 AND 80, and can deliver rows already in order for ORDER BY.\n\n"
                "Indexes are not free. Each one takes storage, and every INSERT and DELETE must also update it. Which UPDATEs touch an "
                "index depends on the engine. Changing an indexed column always does. In PostgreSQL, an update writes a new row "
                "version, and unless it qualifies as a HOT (heap-only tuple) update, which needs no indexed column to change and "
                "room on the same page, every index on the table gets a new entry, even if no indexed column changed. A table with "
                "many indexes reads faster on those columns and writes slower. "
                "Primary keys and unique constraints are usually backed by an index automatically.")),
            dict(title='When an index helps', text=(
                "An index helps most when a query asks for a small fraction of the rows by the indexed column: equality, ranges, or "
                "joins on that column. An index on enrollments(student_id) makes WHERE student_id = 7 and a join ON e.student_id = "
                "s.id cheap.\n\n"
                "A composite index on several columns is sorted by the first column, then by the second within it, like a phone book "
                "sorted by surname and then first name. On courses(dept, year), the database can seek with WHERE dept = 'CS', and "
                "with WHERE dept = 'CS' AND year > 2. It generally cannot seek with WHERE year = 2 alone, just as a phone book does "
                "not help you find everyone named Ravi. This is the leftmost prefix rule. Some engines have a skip scan that softens "
                "it, but you should not count on that.\n\n"
                "If an index contains every column a query needs, the database can answer from the index alone without visiting the "
                "table. This is a covering index: PostgreSQL shows Index Only Scan, SQLite shows USING COVERING INDEX and MySQL shows "
                "Using index. An index on enrollments(student_id, score) covers SELECT score FROM enrollments WHERE student_id = 7. "
                "PostgreSQL may still check the table for pages that VACUUM has not yet marked all-visible.")),
            dict(title='When the index is ignored', text=(
                "Having an index does not mean it will be used. The most common reason is wrapping the column in a function or "
                "expression. An index on name stores name values, not UPPER(name) values, so WHERE UPPER(name) = 'ASHA' cannot "
                "seek through it. Many databases let you create an index on the expression itself; otherwise compare the bare column. "
                "Implicit type conversion applied to the column, such as comparing a text column with a number, can have the same "
                "effect.\n\n"
                "A pattern with a leading wildcard, such as name LIKE '%son', cannot use a B-tree on name, because the sorted order "
                "is by the first characters, and those are unknown. A fixed prefix such as LIKE 'Ra%' can be turned into a range "
                "seek, but only when the index's ordering agrees with how LIKE compares text. MySQL usually manages it. PostgreSQL "
                "does with the C collation, or with an index built using text_pattern_ops under other collations. SQLite's LIKE "
                "ignores case by default, so an ordinary index on name is not used unless the index is declared COLLATE NOCASE or "
                "case_sensitive_like is switched on.\n\n"
                "Finally, the optimizer may decide a scan is cheaper. If a query matches a large share of the table, such as status = "
                "'active' when 95 percent of rows are active, jumping between index and table for each row costs more than reading "
                "the table straight through. The same is true of very small tables. That is a correct choice, not a failure.")),
            dict(title='Reading a query plan', text=(
                "A query plan is the optimizer's chosen strategy for running a statement. You ask for it with EXPLAIN in PostgreSQL "
                "and MySQL, or EXPLAIN QUERY PLAN in SQLite. PostgreSQL's EXPLAIN ANALYZE actually runs the query and reports real "
                "row counts and times next to the estimates.\n\n"
                "Start by finding how each table is accessed. A sequential scan, shown as Seq Scan in PostgreSQL or SCAN followed by "
                "the table name in SQLite, reads the whole table. Index Scan in PostgreSQL or SEARCH ... USING INDEX in SQLite means "
                "the index was used to seek. Then look at join "
                "methods, such as nested loop, hash join or merge join, and at any explicit sort step.\n\n"
                "The optimizer is cost based: it estimates how many rows each step will produce from table statistics and picks the "
                "cheapest plan. When it chooses badly, the cause is often stale statistics, so the estimate and the real count are far "
                "apart. Refreshing them (ANALYZE in PostgreSQL and SQLite, ANALYZE TABLE in MySQL) is a reasonable first step before "
                "adding indexes or rewriting the query.")),
        ],
        keyPoints=[
            "An index is a sorted structure, usually a B-tree, that finds rows in logarithmic time instead of a full scan.",
            "Indexes speed up reads on their columns but cost storage and slow inserts, deletes and many updates.",
            "A composite index helps only queries that constrain its leftmost columns.",
            "A function on the column, a leading wildcard or a low-selectivity filter usually means no index seek.",
            "A covering index answers a query from the index alone.",
            "EXPLAIN shows the plan; compare estimated and actual rows to spot stale statistics.",
        ],
        challenges=[
            q('indexes-and-query-plans', 1, 'Leftmost prefix',
              "courses has a composite index on (dept, year). Which condition can the database use that index to seek on?",
              ["WHERE year = 2",
               "WHERE year = 2 OR dept = 'CS'",
               "WHERE dept = 'CS' AND year > 2"], 2,
              "The index is sorted by dept first, then year within each dept, so fixing dept and taking a year range is a single "
              "contiguous slice. year = 2 alone does not fix the leading column, so the matches are scattered across every dept. "
              "The OR version must also return rows of any dept with year 2, so one seek on the index cannot cover it.",
              "Picture a phone book sorted by surname, then first name."),
            q('indexes-and-query-plans', 2, 'Function on an indexed column',
              "students has an index on name. Why does WHERE UPPER(name) = 'ASHA' usually not seek through that index?",
              ["The index stores name values, not UPPER(name) values, so the sorted order cannot be used for this comparison",
               "UPPER is not deterministic, so the optimizer refuses to use any index",
               "Functions are not allowed in WHERE when an index exists"], 0,
              "The index is ordered by the raw name, and the query asks about a computed value the index does not contain. The fix "
              "is an index on UPPER(name), where supported, or comparing the column directly. UPPER is deterministic, which is why "
              "an expression index on it works, and functions in WHERE are perfectly legal.",
              "Ask what values are actually stored in the index."),
            q('indexes-and-query-plans', 3, 'Low selectivity',
              "orders has an index on status, and 95 percent of rows have status = 'active'. For SELECT * FROM orders WHERE status = "
              "'active', what is the optimizer most likely to do?",
              ["Always use the index, because one exists on the filtered column",
               "Read the whole table with a sequential scan, because almost every row matches",
               "Reject the query because the index has too few distinct values"], 1,
              "When nearly every row qualifies, going through the index means an extra lookup per row in scattered order, which "
              "costs more than reading the table straight through. A cost-based optimizer chooses the scan. Having an index never "
              "forces its use, and low selectivity never makes a query invalid.",
              "Compare the work of one index lookup per row with one pass over the table."),
            q('indexes-and-query-plans', 4, 'Why not index everything',
              "Why is adding an index on every column of a busy table usually a bad idea?",
              ["Indexes are only allowed on primary key columns",
               "Too many indexes make SELECT queries return wrong results",
               "Every index makes reads slower, even on columns that are not filtered",
               "Each index costs storage and extra work on inserts, deletes and many updates"], 3,
              "The cost of an index is paid on writes and in space, so many unused indexes slow down inserts and updates for no "
              "benefit. Every INSERT and DELETE maintains every index. An UPDATE that changes an indexed column maintains that "
              "index, and in PostgreSQL an update that is not HOT adds an entry to every index, even when no indexed column "
              "changed. Any column can be indexed, indexes never change query results, and an index a query does not use adds "
              "little to its cost.",
              "Think about what has to happen to each index when a row changes."),
            q('indexes-and-query-plans', 5, 'Covering index',
              "enrollments has an index on (student_id, score). What can the database do for SELECT score FROM enrollments WHERE "
              "student_id = 7?",
              ["It must still read each matching table row to get score",
               "It can answer the query from the index alone",
               "It cannot use the index because score is not the first column"], 1,
              "The index entries already contain student_id and score, so after seeking to student_id = 7 the database reads score "
              "straight from the index. This is a covering index; SQLite's plan shows SEARCH enrollments USING COVERING INDEX, and "
              "PostgreSQL's shows Index Only Scan, though it may still check the table for pages VACUUM has not marked "
              "all-visible. The filter is on the leading column, so the leftmost prefix rule is satisfied.",
              "List the columns the query touches and compare them with the index's columns."),
        ],
    ),
]
