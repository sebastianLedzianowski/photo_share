import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Picture, User
from src.repository.pictures import (
    upload_picture,
    get_all_pictures,
    get_one_picture,
    update_picture,
    delete_picture,
)


class TestUnitRepositoryPictures(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(
            id=1,
            username="Username",
            email="username@example.com",
            password="password",
            created_at="2000-02-02T00:00:00",
            avatar=None,
            refresh_token="refresh_token",
            confirmed=False,
        )
        self.picture1 = Picture(
            id=1,
            picture_url="http://example1.com",
            created_at="2000-02-02T00:00:00",
            user_id=self.user
        )
        self.picture2 = Picture(
            id=2,
            picture_url="http://example22.com",
            created_at="2010-02-02T00:00:00",
            user_id=self.user
        )
        self.picture3 = Picture(
            id=3,
            picture_url="http://example333.com",
            created_at="2020-02-02T00:00:00",
            user_id=self.user
        )

    async def test_upload_picture(self):
        picture = self.picture1
        picture_name = f'picture/{self.user.email}'
        result = await upload_picture(url=picture.picture_url, version="v1", picture_name=picture_name, user=self.user, db=self.session)
        self.assertEqual(result.picture_url, picture.picture_url)
        self.assertTrue(hasattr(result, "id"))

    async def test_get_all_pictures(self):
        pictures = [self.picture1, self.picture2, self.picture3]

        mock_query = self.session.query.return_value
        mock_offset = mock_query.offset.return_value
        mock_limit = mock_offset.limit.return_value
        mock_limit.all.return_value = pictures

        result = await get_all_pictures(skip=0, limit=100, db=self.session)

        self.assertEqual(result, pictures)
        self.assertEqual(result[0].id, self.picture1.id)
        self.assertEqual(result[0].picture_url, self.picture1.picture_url)
        self.assertEqual(result[1].id, self.picture2.id)
        self.assertEqual(result[1].picture_url, self.picture2.picture_url)

    async def test_get_one_picture_found(self):
        picture = self.picture1
        self.session.query().filter().first.return_value = picture
        result = await get_one_picture(picture_id=1, db=self.session)
        self.assertEqual(result, picture)
        self.assertEqual(result.id, picture.id)

    async def test_get_one_picture_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_one_picture(picture_id=1, db=self.session)
        self.assertIsNone(result)

    async def test_update_picture_found(self):
        updated_picture_data = self.picture2
        picture_to_update = self.picture1
        self.session.query().filter().first.return_value = picture_to_update
        result = await update_picture(picture_id=updated_picture_data.id, url=updated_picture_data.picture_url, user=self.user ,db=self.session)
        self.assertEqual(result, picture_to_update)
        self.assertEqual(result.id, picture_to_update.id)

    async def test_update_picture_not_found(self):
        updated_picture_data = self.picture2
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_picture(picture_id=updated_picture_data.id, url=updated_picture_data.picture_url, user=self.user ,db=self.session)
        self.assertIsNone(result)

    async def test_delete_picture_found(self):
        picture = self.picture1
        self.session.query().filter().first.return_value = picture
        result = await delete_picture(picture_id=picture.id, db=self.session)
        self.assertEqual(result, picture)
        self.assertEqual(result.id, picture.id)

    async def test_delete_picture_not_found(self):
        picture = self.picture1
        self.session.query().filter().first.return_value = None
        result = await delete_picture(picture_id=picture.id, db=self.session)
        self.assertIsNone(result)
