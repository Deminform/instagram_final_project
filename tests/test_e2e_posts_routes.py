from docutils.nodes import description


def test_create_post(override_get_db, test_user):
    response = override_get_db.post("api/posts", json={
        "description":"Test post description",
        "user_id":test_user.id,
        "original_image_url":"https://res.cloudinary.com/dr0qfbx4m/image/upload/v1735225152/first_app/f283fba11972428993afc5f5fc165ad8.jpg",
        "image_url":"https://res.cloudinary.com/dr0qfbx4m/image/upload/e_sepia/c_fill,h_1200,w_800/v1/first_app/f283fba11972428993afc5f5fc165ad8",
        "tags":("tag_1", "tag_2")
    })

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["description"] == "Test post description"
    assert data["user_id"] == test_user.id