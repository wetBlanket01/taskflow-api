from fastapi.testclient import TestClient

from src.main import app
from src.core.security import create_access_token

client = TestClient(app)


def get_token(username: str = 'admin'):
    resp = client.post(url="/auth/register", json={
        "username": username,
        "email": f"{username}@example.com",
        "password": "testpass123"
    })

    response = client.post(url="/auth/token", data={
        "username": username,
        "password": "testpass123"
    })

    return response.json()['access_token']


def test_full_task_crud():
    token_a = get_token('user_a')

    headers_a = {'Authorization': f'Bearer {token_a}'}

    create_response = client.post(url="/tasks", json={
        "title": "test task",
        "description": "test description"
    }, headers=headers_a)

    assert create_response.status_code == 200

    task_data = create_response.json()
    task_id = task_data['id']

    list_response = client.get(f"/tasks", headers=headers_a)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]['title'] == 'test task'

    update_response = client.patch(f"/tasks/{task_id}", json={
        "title": "updated test task",
        "description": "updated test description",
        "completed": True
    }, headers=headers_a)

    assert update_response.status_code == 200
    updated_task = client.get(f"/tasks", headers=headers_a)
    assert updated_task.json()[0]['title'] == 'updated test task'
    assert updated_task.json()[0]['description'] == 'updated test description'
    assert updated_task.json()[0]['completed'] is True

    token_b = get_token('user_b')
    headers_b = {'Authorization': f'Bearer {token_b}'}

    foreign_update = client.patch(f"/tasks/{task_id}", json={
        "title": "hacked"
    }, headers=headers_b)
    assert foreign_update.status_code == 404

    delete_response = client.delete(f"/tasks/{task_id}", headers=headers_a)
    assert delete_response.status_code == 200

    final_list = client.get(f"/tasks", headers=headers_a)
    assert len(final_list.json()) == 0


