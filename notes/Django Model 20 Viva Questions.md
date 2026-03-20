# 🎓 Django Models — In-Depth Viva Guide

---

### 🏛️ Architecture & Basics

#### 1. What is an ORM in Django?
**In-Depth Answer:** ORM stands for **Object-Relational Mapping**. It is a powerful technique that allows you to interact with your database using Python objects and methods instead of writing raw SQL (Structured Query Language).
- **The "Object" part:** In your code, you define Python classes (Models). Each class represents a table in the database.
- **The "Relational" part:** This refers to the Relation Database Management System (RDBMS) like SQLite, PostgreSQL, or MySQL.
- **The "Mapping" part:** Django automatically "maps" your Python attributes to database columns and your Python objects to database rows.
- **Benefits:** You don't have to worry about the specific SQL syntax of different databases (DB abstraction). It also makes your code more readable, maintainable, and protects you against SQL Injection attacks.

#### 2. What is the difference between `AbstractUser` and `AbstractBaseUser`?
**In-Depth Answer:** Django provides multiple ways to customize the User model, and the choice depends on how much of Django's built-in functionality you want to keep.
- **`AbstractUser`**: It provides a full, ready-to-use implementation of a User. It includes all the fields you expect: `username`, `first_name`, `last_name`, `email`, `is_staff`, `is_active`, `is_superuser`, etc. You use this when you want to keep the standard behavior but just add extra fields (like our `user_type`). 
- **`AbstractBaseUser`**: This is a much "thinner" model. It only provides the core authentication mechanism (password handling and hashing). It does **not** include any fields like username or email; you have to define everything yourself. You use this only if you want to completely change how authentication works (e.g., using a Phone Number instead of a Username as the primary identifier).
- **Key Takeaway:** For 99% of projects (including ClassBridge), `AbstractUser` is the way to go because it saves you from reinventing the wheel.

#### 3. Why do we use `related_name` in a ForeignKey or OneToOneField?
**In-Depth Answer:** `related_name` defines the **Reverse Relationship** name. 
- **Forward Relation:** If a `Student` has a field `user = OneToOneField(CustomUser)`, you can access the user from a student object using `student.user`. This is straightforward.
- **Reverse Relation:** What if you have a `User` object and want to see their student details? Without `related_name`, you'd have to use a default name like `user.student`. 
- **The Descriptive Power:** By setting `related_name='student_profile'`, you make your code much more readable: `user.student_profile`. It allows you to navigate the database tree from the "child" back to the "parent" using a name that makes sense in English.

#### 4. What does `on_delete=models.CASCADE` do?
**In-Depth Answer:** This is a database integrity rule. `CASCADE` means "follow the action downstream."
- **Scenario:** In our project, an `Absence` record belongs to a `Student`.
- **The Rule:** If a `Student` is deleted from the system, it makes no sense to keep their `Absence` records. They are "orphaned" data. 
- **The Action:** `models.CASCADE` tells Django that if the parent (Student) is deleted, it should automatically find and delete all associated children (Absence, Participation, etc.).
- **Alternatives:** 
    - `SET_NULL`: Keep the child but set the link to NULL (requires `null=True`).
    - `PROTECT`: Stop the deletion of the parent if it has any children.

#### 5. Explain the purpose of `models.OneToOneField`. When is it better than a ForeignKey?
**In-Depth Answer:** A `OneToOneField` is technically a `ForeignKey` with a `unique=True` constraint, but Django treats it specially.
- **The Rule:** It guarantees that for every 1 record in Table A, there is at most 1 record in Table B.
- **When to Use:** It is specifically used for **Model Extension**. Instead of cluttering the `CustomUser` table with "Roll Number", "Batch", and "Department", we split them into `Student` and `Faculty` tables. 
- **Difference from ForeignKey:** A `ForeignKey` is for "Many-to-One" (many students in one batch). A `OneToOneField` is for "One-to-One" (one user is exactly one student profile). Using it ensures that no two people can accidentally share the same student profile record.

---

### ⚙️ Fields & Logic

#### 6. What is the difference between `null=True` and `blank=True`?
**In-Depth Answer:** This is a classic interview question. One is for the database, the other is for validation.
- **`null=True` (Database level):** This tells the database (like SQLite) that it is okay for this column to have a `NULL` (empty) value. If `null=False`, the database will throw an error if you try to save an empty field.
- **`blank=True` (Validation/Template level):** This tells Django's **Forms** that the user is allowed to leave this field empty. If `blank=False`, the form will show a "This field is required" error.
- **Common Usage:** For character-based fields (`CharField`, `TextField`), Django convention is to use `blank=True` but keep `null=False` (it stores an empty string `""` instead of `NULL`). For Dates and Numbers, you usually use both: `null=True, blank=True`.

#### 7. How do choice tuples work? What is stored in the DB vs what is shown in UI?
**In-Depth Answer:** Choice tuples are a list of pairs used to limit a field to a specific set of options.
- **Syntax:** `('db_value', 'Readable Label')`
- **The DB Side:** The first element (`'student'`) is what is actually written into the SQL database. It is short, usually lowercase, and never changes. This is what you use in your Python `if` statements.
- **The UI Side:** The second element (`'Student'`) is what the user sees in the Django Admin, in dropdown menus, and on the website.
- **Why do this?** It allows you to change the "Label" (e.g., change "Student" to "Learner") without having to run a database migration or update your logic code.

#### 8. What is the mission of the `__str__` method in a Model?
**In-Depth Answer:** The `__str__` method is a "Magic Method" in Python that returns a string representation of an object.
- **Default Behavior:** Without it, Django shows objects as `<Student object (1)>`, which is useless for humans.
- **In Django:** Implementing `def __str__(self): return self.roll_number` makes the object show up as "CS101" in the Django Admin panel, in dropdown selections, and in your logs.
- **Best Practice:** Always return something that uniquely identifies the object or describes it clearly so that admins can distinguish between records easily.

#### 9. Explain `auto_now` vs `auto_now_add` in a DateTimeField.
**In-Depth Answer:** These are automated timestamp handlers.
- **`auto_now_add=True`**: This is for **Creation Date**. It sets the field to the current date/time ONLY when the object is created for the first time. It never changes again. Perfect for things like `joined_at`.
- **`auto_now=True`**: This is for **Last Modified Date**. Every single time you call `object.save()`, Django automatically updates this field to the current time. Perfect for tracking when a record was updated.
- **Constraint:** You cannot manually change these fields in the Django Admin because they are "read-only" by design.

#### 10. What is the `Meta` class used for in a Model?
**In-Depth Answer:** The `Meta` class is used to define "Metadata" — which is "information about the data model itself," rather than a specific field.
- **Common Uses:**
    - **`ordering`**: Tells Django how to sort results by default (e.g., `ordering = ['-date']` for newest first).
    - **`unique_together`**: Enforces that a combination of several fields must be unique.
    - **`verbose_name`**: Changes how the model name appears in the Admin (e.g., change "Absence" to "Student Leaves").
    - **`db_table`**: Allows you to override the default table name that Django creates in SQL.

---

### 🛠️ Advanced Concepts

#### 11. How do migrations work in Django? Explain `makemigrations` vs `migrate`.
**In-Depth Answer:** Migrations are Django's way of propagating changes you make to your models (adding a field, deleting a model, etc.) into your database schema.
- **`makemigrations`**: Django looks at your `models.py`, compares it to the previous version, and generates a new Python file in the `migrations/` folder. This file contains the instructions (e.g., "Add column 'user_type' to table 'core_customuser'"). **It does NOT change the DB yet.**
- **`migrate`**: This command reads those instruction files and actually executes the SQL commands to modify your database tables.
- **Why this system?** It allows you to version-control your database schema just like your code, ensuring that every developer on the team has the exact same database structure.

#### 12. What is a "QuerySet"? Is it lazy?
**In-Depth Answer:** A QuerySet is essentially a list of objects from your database.
- **The "Lazy" nature:** This is the most important concept. When you write `users = CustomUser.objects.filter(is_active=True)`, Django **does not** hit the database yet. It just creates a "plan" for the query.
- **The Trigger:** The database is only contacted when you actually try to use the data (e.g., looping through it with `for user in users`, printing it, or calling `len(users)`).
- **Benefit:** This allows you to "chain" filters together (e.g., `users.filter(...).exclude(...).order_by(...)`) without making multiple expensive trips to the database.

#### 13. What is the difference between `filter()` and `get()`?
**In-Depth Answer:** These are the two primary ways to retrieve data, and they behave very differently when data is missing or duplicated.
- **`filter()`**: Always returns a **QuerySet** (a list-like object). If no records match, it returns an empty list `[]`. It never throws an error.
- **`get()`**: Expects to find **Exactly One** record. 
    - If it finds 0 records, it crashes with a `DoesNotExist` error.
    - If it finds 2 or more records, it crashes with a `MultipleObjectsReturned` error.
- **When to use:** Use `get()` when you are sure there is only one record (like searching by ID or Roll Number). Use `filter()` for everything else.

#### 14. How do you handle a Many-to-Many relationship in Django?
**In-Depth Answer:** You use `models.ManyToManyField`.
- **The Problem:** In SQL, you cannot store a list of items inside a single column.
- **The Django Solution:** When you define a `ManyToManyField` (e.g., `Students` in a `Course`), Django automatically creates a hidden "Intermediate Table" (also called a join table) that stores pairs of IDs (Student_ID and Course_ID).
- **Access:** Django handles all the complex SQL JOINs behind the scenes, allowing you to just write `course.students.all()`.

#### 15. Explain the `unique_together` constraint.
**In-Depth Answer:** This is a `Meta` option that enforces uniqueness across multiple columns simultaneously.
- **Scenario:** In `EventParticipation`, we have a `student` field and an `event` field.
- **The Rule:** `unique_together = ('student', 'event')`.
- **The Result:** The database will allow Student A to join Event 1. It will allow Student B to join Event 1. But if Student A tries to join Event 1 **again**, the database will throw an Integrity Error.
- **Modern Alternative:** In newer Django versions, the `UniqueConstraint` inside the `constraints` list is preferred as it is more flexible, but `unique_together` remains the classic, widely-used method.

---

### 🤖 Logic & Optimization

#### 16. How can you add custom logic/methods to a Django Model?
**In-Depth Answer:** Since Django Models are just Python classes, you can add any method you want!
- **Usage:** In our `ClassLog` model, we added `get_ai_video_links()`. 
- **The Benefit:** This is called "Fat Models, Skinny Views." By putting the logic inside the model, it is available everywhere in your project (Views, Admin, API, Shell) without rewriting the code.
- **Access:** You can access the object's specific data using `self` (e.g., `self.subject`).

#### 17. What is "Select Related" vs "Prefetch Related"?
**In-Depth Answer:** These are the primary tools for solving the "N+1 Problem" (where your code makes hundreds of tiny database queries instead of one big one).
- **`select_related()`**: Used for **Single** relationships (`ForeignKey` or `OneToOne`). It performs a SQL **JOIN** and fetches everything in one query.
- **`prefetch_related()`**: Used for **Many** relationships (`ManyToManyField` or the reverse of a ForeignKey). It performs a separate query for the related items and "stitches" them together in Python memory.
- **Result:** Using these can turn a page that takes 5 seconds to load into one that takes 0.1 seconds.

#### 18. Explain the `Proxy` model.
**In-Depth Answer:** A Proxy model is a model that allows you to change the **Python-side behavior** of a model without changing the **Database-side schema**.
- **How it works:** You create a class that inherits from your model and set `proxy = True` in the `Meta` class. No new table is created in the DB.
- **Use Case:** You want two different views in the Django Admin for the same table (e.g., one Admin for "Active Users" and one for "Banned Users") with different ordering or permissions for each.

#### 19. What is `F()` expressions?
**In-Depth Answer:** `F()` expressions allow you to refer to a model field value and perform database-level operations without actually pulling the data into Python memory.
- **Standard way:** `p.likes += 1; p.save()` (This is slow and has race condition bugs).
- **F() way:** `p.likes = F('likes') + 1; p.save()`
- **Benefit:** The calculation happens entirely inside the database (SQL: `UPDATE table SET likes = likes + 1`). This is much faster and safe if two users click "like" at the exact same split-second.

#### 20. If you change a `help_text` in a model field, do you need a migration?
**In-Depth Answer:** **Yes.** 
- **The Reason:** While `help_text` doesn't change the actual SQL column type (it doesn't turn an INTEGER into a VARCHAR), it is part of the field's definition in Django.
- **Django's Logic:** Django tracks every single attribute of a field in its migration files. To keep the project's "History" accurate, any change to the Model code requires a migration so that the state of your code and the state of your database stay perfectly in sync. I always recommend running `makemigrations` after any change to `models.py`, no matter how small.
