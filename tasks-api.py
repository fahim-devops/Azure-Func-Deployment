import azure.functions as func
import json
import pymysql



db = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PSWD,
    database=DB_NAME,
    cursorclass=pymysql.cursors.DictCursor,
)
cursor = db.cursor()

def main(req: func.HttpRequest) -> func.HttpResponse:
    method = req.method
    id = req.route_params.get('id')
    title = req.params.get('title')

    if method == "GET" and id:
        resp = get_task(id)
    elif method == "GET":
        resp = get_tasks()
    elif method == "DELETE":
        resp = delete_task(id)
    elif not title_is_valid(title):
        resp = ("", 400)
    elif method == "POST":
        resp = create_task(title)
    elif method == "PUT":
        resp = update_task(id, title)

    return func.HttpResponse(
        body=json.dumps(resp[0]),
        status_code=resp[1],
        mimetype='application/json'
    )

# Create a new task
def create_task(title):
    try:
        cursor.execute("INSERT INTO tasks (title) VALUES (%s)", title)
        db.commit()
        cursor.execute("SELECT MAX(id) AS id FROM tasks")
        row = cursor.fetchone()
        resp = get_task(row["id"])
        return (resp[0], 201)
    except Exception as e:
        return (str(e), 500)

# Get all tasks
def get_tasks():
    try:
        cursor.execute(
            "SELECT id, title, date_format(created, '%Y-%m-%d %H:%i') as created FROM tasks"
        )
        return (cursor.fetchall(), 200)
    except Exception as e:
        return (str(e), 500)

# Get an individual task
def get_task(id):
    try:
        cursor.execute(
            "SELECT id, title, date_format(created, '%Y-%m-%d %H:%i') as created \
            FROM tasks WHERE id=" + str(id)
        )
        row = cursor.fetchone()
        return (row if row is not None else "", 200 if row is not None else 404)
    except Exception as e:
        return ("", 404)

# Update an existing task
def update_task(id, title):
    try:
        cursor.execute("UPDATE tasks SET title=%s WHERE id=%s", (title, id))
        db.commit()
        return get_task(id)
    except Exception as e:
        return (str(e), 500)

# Delete an existing task
def delete_task(id):
    try:
        resp = get_task(id)
        if resp[1] == 200:
            cursor.execute("DELETE FROM tasks WHERE id=%s", id)
            db.commit()
            return ("", 200)
        else:
            return resp
    except Exception as e:
        return (str(e), 500)

# Returns True if title is valid, False otherwise
def title_is_valid(title):
    return True if isinstance(title, str) and 6 <= len(title) <= 255 else False

