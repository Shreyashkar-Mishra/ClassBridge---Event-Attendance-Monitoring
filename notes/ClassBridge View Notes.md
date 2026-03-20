# 📄 ClassBridge View Notes

> This file explains the "Logic Center" of ClassBridge—how **Views** process requests, talk to **Models**, and render **Templates**.

---

## 🔷 Section 1 — The Request-Response Cycle

In ClassBridge, every time a user clicks a button or enters a URL, it triggers a **View function**.
1.  **Request**: The browser sends a `HttpRequest` (e.g., "I want to see the dashboard").
2.  **Logic**: The View checks: "Is the user logged in?", "Are they a Student or Faculty?", "Fetch their logs from the DB."
3.  **Response**: The View returns a `HttpResponse` (usually a rendered HTML page).

---

## 🔷 Section 2 — Role-Based Dashboard (`dashboard` view)

This is the most important view in the project. It uses a single URL (`/dashboard/`) but shows different content based on the `user_type`.

```python
@login_required
def dashboard(request):
    user = request.user
    if user.user_type == 'student':
        # Logic for student (recent logs)
        return render(request, 'dashboard_student.html', context)
    elif user.user_type == 'faculty':
        # Logic for faculty (their own logs + student roster)
        return render(request, 'dashboard_faculty.html', context)
```

### 🧠 Key Concepts:
*   **`@login_required`**: A **Decorator**. It acts as a security guard. If a user isn't logged in, it catches them and redirects them to the login page before the function even runs.
*   **`request.user`**: This object is always available. We use `user.user_type` (which we defined in `models.py`) to decide what data to fetch.
*   **Conditional Rendering**: One view can render multiple different templates depending on user logic.

---

## 🔷 Section 3 — Handling Forms in Views (`log_class`)

When a Faculty member logs a class, the view handles two types of requests: **GET** (show empty form) and **POST** (process submitted data).

```python
@login_required
def log_class(request):
    if request.method == 'POST':
        form = ClassLogForm(request.POST) # Bind data
        if form.is_valid():
            new_log = form.save(commit=False) # Create object but don't save yet
            new_log.logged_by = request.user.faculty_profile # Fill in secret data
            new_log.save() # Now save!
            return redirect('dashboard')
    else:
        form = ClassLogForm() # Empty form
    return render(request, 'create_class_log.html', {'form': form})
```

### 🔍 Backend logic explained:
1.  **`request.method == 'POST'`**: Checks if the user clicked "Submit."
2.  **`form.is_valid()`**: Triggers all the validation logic we wrote in `forms.py`.
3.  **`commit=False`**: This is critical. The form doesn't know *who* is logged in. We use this to manually attach the Faculty profile (`logged_by`) before the record hits the database.
4.  **`redirect()` vs `render()`**:
    *   `render` serves a page (stays on current URL).
    *   `redirect` sends the user to a NEW URL (prevents duplicate submissions if they refresh the page).

---

## 🔷 Section 4 — Security & Permissions

We use `PermissionDenied` to block unauthorized actions.

```python
if request.user.user_type != 'coordinator':
    raise PermissionDenied("Only Coordinators can create events.")
```

*   **Middleware**: When you `raise PermissionDenied`, Django's middleware catches it and automatically shows a "403 Forbidden" page.
*   **Object Retrieval**: `get_object_or_404(Event, id=event_id)` is a safety feature. It tries to find the event; if it doesn't exist, it shows a "404 Not Found" instead of the server crashing with an error.

---

## 🔷 Section 5 — External Integrations (Excel & Email)

ClassBridge goes beyond simple HTML. Some views generate files:

*   **Excel**: `HttpResponse(content_type='application/vnd.ms-excel')`. We use `openpyxl` to write data into a binary stream and send it to the browser as a download.
*   **Email**: `EmailMessage(...)`. The view prepares a subject and body, attaches the Excel file, and sends it via the `email.send()` system.

---

## 🔷 Summary: The View's Checklist
Every view you write usually follows this pattern:
1.  **Check security** (Is user logged in? Do they have the right role?).
2.  **Process data** (Is it a POST request? Is the form valid?).
3.  **Perform DB actions** (Save, Update, or Delete).
4.  **Send Feedback** (`messages.success` to show a notification).
5.  **Redirect or Render** (Where does the user go next?).

> ✏️ *This file explains the "Brain" of your application.*
