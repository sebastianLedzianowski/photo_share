import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Picture, User
from src.repository.descriptions import (
    upload_description,
    get_all_descriptions,
    get_one_description,
    update_description,
    delete_description,
)


class TestUnitRepositoryDescriptions(unittest.IsolatedAsyncioTestCase):

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
            user_id=self.user,
            description=None
        )
        self.picture2 = Picture(
            id=2,
            picture_url="http://example22.com",
            created_at="2010-02-02T00:00:00",
            user_id=self.user,
            description="test description no.2"
        )
        self.picture3 = Picture(
            id=3,
            picture_url="http://example333.com",
            created_at="2020-02-02T00:00:00",
            user_id=self.user,
            description="test description no.3"
        )

    async def test_upload_description(self):
        picture = self.picture1
        test_description = "test description no.1"
        result = await upload_description(picture_id=picture.id, description=test_description, db=self.session)
        self.assertEqual(result.description, test_description)
        self.assertTrue(hasattr(result, "id"))

    async def test_get_all_descriptions(self):
        pictures = [self.picture1, self.picture2, self.picture3]
        pictures_descriptions = [picture.description for picture in pictures]

        mock_query = self.session.query.return_value
        mock_offset = mock_query.offset.return_value
        mock_limit = mock_offset.limit.return_value
        mock_limit.all.return_value = pictures

        result = await get_all_descriptions(skip=0, limit=100, db=self.session)

        self.assertEqual(result[0].description, pictures[0].description)
        self.assertEqual(result[1].description, pictures[1].description)
        self.assertEqual(result[2].description, pictures[2].description)
        self.assertEqual(len(result), len(pictures_descriptions))

    async def test_get_one_description_picture_found(self):
        picture = self.picture2
        self.session.query().filter().first.return_value = picture
        result = await get_one_description(picture_id=2, db=self.session)
        self.assertEqual(result.description, picture.description)
        self.assertEqual(result.id, picture.id)

    async def test_get_one_description_picture_not_found(self):
        self.session.query().filter(Picture.id == 999).first.return_value = None
        result = await get_one_description(picture_id=999, db=self.session)
        self.assertIsNone(result)

    async def test_update_description_picture_found(self):
        new_description = "New test description"
        picture_to_update = self.picture1
        self.session.query().filter().first.return_value = picture_to_update
        result = await update_description(picture_id=picture_to_update.id, new_description=new_description, db=self.session)
        self.assertEqual(result.description, new_description)
        self.assertEqual(result.id, picture_to_update.id)

    async def test_update_description_picture_not_found(self):
        new_description = "New test description"
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_description(picture_id=999, new_description=new_description ,db=self.session)
        self.assertIsNone(result)

    async def test_delete_description_picture_found(self):
        picture = self.picture2
        self.session.query().filter().first.return_value = picture
        result = await delete_description(picture_id=picture.id, db=self.session)
        self.assertEqual(result, picture)
        self.assertEqual(result.description, None)

    async def test_delete_description_picture_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await delete_description(picture_id=999, db=self.session)
        self.assertIsNone(result)
