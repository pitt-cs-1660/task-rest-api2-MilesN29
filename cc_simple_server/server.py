from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import status
from cc_simple_server.models import TaskCreate
from cc_simple_server.models import TaskRead
from cc_simple_server.database import init_db
from cc_simple_server.database import get_db_connection

# init
init_db()

app = FastAPI()

############################################
# Edit the code below this line
############################################


@app.get("/")
async def read_root():
    """
    This is already working!!!! Welcome to the Cloud Computing!
    """
    return {"message": "Welcome to the Cloud Computing!"}


# POST ROUTE data is sent in the body of the request
@app.post("/tasks/", response_model=TaskRead)
async def create_task(task_data: TaskCreate):
    """
    Create a new task

    Args:
        task_data (TaskCreate): The task data to be created

    Returns:
        TaskRead: The created task data
    """
    task_title = task_data.title
    task_description = task_data.description
    task_completed = task_data.completed
    
    db_conn = get_db_connection()
    with db_conn: #need this to avoid --> sqlite3.OperationalError: database is locked
        cursor = db_conn.cursor()
        
        cursor.execute("INSERT INTO tasks (title, description, completed) VALUES (?, ?, ?)", (task_title, task_description, task_completed))
        
        task_id = cursor.lastrowid
        cursor.close()

    return TaskRead(id=task_id, title=task_title, description= task_description, completed=task_completed)

# GET ROUTE to get all tasks
@app.get("/tasks/", response_model=list[TaskRead])
async def get_tasks():
    """
    Get all tasks in the whole wide database

    Args:
        None

    Returns:
        list[TaskRead]: A list of all tasks in the database
    """
    db_conn = get_db_connection()
    with db_conn:
        cursor = db_conn.cursor()
        cursor.execute("SELECT id, title, description, completed FROM tasks") #need this to get to the actaul database
        tasks = []
        
        for row in cursor.fetchall():
            task = TaskRead(id = row[0], title = row[1], description=row[2],completed=row[3])
            tasks.append(task)
            
        cursor.close()
        
    return tasks


# UPDATE ROUTE data is sent in the body of the request and the task_id is in the URL
@app.put("/tasks/{task_id}/", response_model=TaskRead)
async def update_task(task_id: int, task_data: TaskCreate):
    """
    Update a task by its ID

    Args:
        task_id (int): The ID of the task to be updated
        task_data (TaskCreate): The task data to be updated

    Returns:
        TaskRead: The updated task data
    """
    task_title = task_data.title
    task_description = task_data.description
    task_completed = task_data.completed
    db_conn = get_db_connection()
    with db_conn:
        cursor = db_conn.cursor()
        
        cursor.execute("UPDATE tasks SET title = ? WHERE id = ?", (task_title, task_id))
        cursor.execute("UPDATE tasks SET description = ? WHERE id = ?", (task_description, task_id))
        cursor.execute("UPDATE tasks SET completed = ? WHERE id = ?", (task_completed, task_id))
        
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)) #have to put a extra comma because it needs to be a tuple
        
        row = cursor.fetchone()
        task = TaskRead(id=task_id, title=row[1], description=row[2], completed=row[3])
        return task


# DELETE ROUTE task_id is in the URL
@app.delete("/tasks/{task_id}/")
async def delete_task(task_id: int):
    """
    Delete a task by its ID

    Args:
        task_id (int): The ID of the task to be deleted

    Returns:
        dict: A message indicating that the task was deleted successfully
    """
    db_conn = get_db_connection()
    with db_conn:
        cursor = db_conn.cursor()
        
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,)) #have to put a extra comma because it needs to be a tuple
        
        #maybe shoudl have a more in depth check here?
        return {'message': f"Task {task_id} deleted successfully"}
    return {'message': f'Task {task_id} failed to delete'}
