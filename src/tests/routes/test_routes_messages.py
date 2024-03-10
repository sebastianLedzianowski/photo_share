def test_user_creation(fake_db_for_message_test):
    user = fake_db_for_message_test["create_user"]("user@example.com", "testuser", "securepassword")
    assert user["id"] == 1
    assert fake_db_for_message_test["users"][1]["email"] == "user@example.com"


def test_message_sending(fake_db_for_message_test):
    sender = fake_db_for_message_test["create_user"]("sender@example.com", "senderuser", "password1")
    receiver = fake_db_for_message_test["create_user"]("receiver@example.com", "receiveruser", "password2")
    message = fake_db_for_message_test["create_message"](sender["id"], receiver["id"], "Hello, Receiver!")
    assert message["id"] == 1
    assert len(fake_db_for_message_test["get_messages_for_user"](receiver["id"])) == 1
    assert fake_db_for_message_test["messages"][1]["content"] == "Hello, Receiver!"
