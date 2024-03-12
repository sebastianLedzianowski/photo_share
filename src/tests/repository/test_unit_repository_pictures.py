import unittest
from unittest.mock import MagicMock
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException


from src.database.models import Picture, User
from src.repository.pictures import (
    upload_picture,
    get_all_pictures,
    get_one_picture,
    update_picture,
    delete_picture,
    upload_edited_picture,
    validate_edit_parameters,
    parse_transform_effects,
)


class TestUnitRepositoryPictures(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(
            id=1,
            username="Username",
            email="username@example.com",
            password="password",
            created_at=datetime.now(),
            avatar=None,
            refresh_token="refresh_token",
            confirmed=False,
        )
        self.picture1 = Picture(
            id=1,
            picture_url="http://example1.com",
            picture_json={
                "version": "v1",
                "public_id": "picture/123456"
            },
            qr_code_picture="http://example1.com",
            created_at=datetime.now(),
            user_id=self.user
        )
        self.picture2 = Picture(
            id=2,
            picture_url="http://example22.com",
            picture_json={
                "version": "v1",
                "public_id": "picture/123456"
            },
            qr_code_picture="http://example22.com",
            created_at=datetime.now(),
            user_id=self.user
        )
        self.picture3 = Picture(
            id=3,
            picture_url="http://example333.com",
                        picture_json={
                "version": "v1",
                "public_id": "picture/123456"
            },
            qr_code_picture="http://example333.com",
            created_at=datetime.now(),
            user_id=self.user
        )

    async def test_upload_picture(self):
        picture = self.picture1
        result = await upload_picture(picture_url=picture.picture_url, picture_json=picture.picture_json, qr=picture.qr_code_picture, user=self.user, db=self.session)
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

    async def test_validate_edit_parameters_valid(self):
        picture_edit = MagicMock()
        picture_edit.improve = "50"
        picture_edit.contrast = "0"
        picture_edit.unsharp_mask = "500"
        picture_edit.brightness = "10"
        picture_edit.gamma = "50"
        picture_edit.grayscale = False
        picture_edit.redeye = False
        picture_edit.gen_replace = "black"
        picture_edit.gen_remove = "prompt_null"

        await validate_edit_parameters(picture_edit)


    async def test_parse_transform_effects(self):
        picture_edit = MagicMock()
        picture_edit.improve = "0"
        picture_edit.contrast = "0"
        picture_edit.unsharp_mask = "500"
        picture_edit.brightness = "10"
        picture_edit.gamma = "50"
        picture_edit.grayscale = False
        picture_edit.redeye = False
        picture_edit.gen_replace = "from_null;to_null"
        picture_edit.gen_remove = "prompt_null"

        expected_effects = [
            {'effect': 'unsharp_mask:500'},
            {'effect': 'brightness:10'},
            {'effect': 'gamma:50'}
        ]

        result = await parse_transform_effects(picture_edit)
        self.assertEqual(result, expected_effects)

        picture_edit.gen_remove = "prompt_background"

        expected_effects_2 = [
            {'effect': 'gen_remove:prompt_background'},
            {'effect': 'unsharp_mask:500'},
            {'effect': 'brightness:10'},
            {'effect': 'gamma:50'}
        ]

        result_2 = await parse_transform_effects(picture_edit)
        self.assertEqual(result_2, expected_effects_2)
        

    async def test_upload_edited_picture(self):
        picture = MagicMock()
        picture.picture_edited_url = None
        picture.picture_edited_json = None
        picture.qr_code_picture_edited = None

        picture_edited = MagicMock()
        picture_edited_url = "http://edited_picture.com"
        qr = "http://edited_qr_code.com"

        db_session = MagicMock(spec=Session)

        result = await upload_edited_picture(picture, picture_edited, picture_edited_url, qr, db_session)

        self.assertEqual(result["picture_edited_url"], picture_edited_url)
        self.assertEqual(result["qr_code_picture_edited"], qr)

    async def test_validate_edit_parameters_invalid_improve(self):
        # Test dla invalid improve value
        picture_edit = MagicMock()
        picture_edit.improve = "200"

        with self.assertRaises(HTTPException):
            await validate_edit_parameters(picture_edit)

    async def test_validate_edit_parameters_invalid_contrast(self):
        # Test dla invalid contrast value
        picture_edit = MagicMock()
        picture_edit.contrast = "200"

        with self.assertRaises(HTTPException):
            await validate_edit_parameters(picture_edit)

    async def test_validate_edit_parameters_invalid_unsharp_mask(self):
        # Test dla invalid unsharp_mask value
        picture_edit = MagicMock()
        picture_edit.unsharp_mask = "5000"

        with self.assertRaises(HTTPException):
            await validate_edit_parameters(picture_edit)

    async def test_validate_edit_parameters_invalid_brightness(self):
        # Test dla invalid brightness value
        picture_edit = MagicMock()
        picture_edit.brightness = "200"

        with self.assertRaises(HTTPException):
            await validate_edit_parameters(picture_edit)

    async def test_validate_edit_parameters_invalid_gamma(self):
        # Test dla invalid gamma value
        picture_edit = MagicMock()
        picture_edit.gamma = "200"

        with self.assertRaises(HTTPException):
            await validate_edit_parameters(picture_edit)

    async def test_validate_edit_parameters_invalid_grayscale(self):
        # Test dla invalid grayscale value
        picture_edit = MagicMock()
        picture_edit.grayscale = "invalid"

        with self.assertRaises(HTTPException):
            await validate_edit_parameters(picture_edit)

    async def test_validate_edit_parameters_invalid_redeye(self):
        # Test dla invalid redeye value
        picture_edit = MagicMock()
        picture_edit.redeye = "invalid"

        with self.assertRaises(HTTPException):
            await validate_edit_parameters(picture_edit)

    async def test_validate_edit_parameters_invalid_gen_replace_and_gen_remove(self):
        # Test dla invalid gen_replace and gen_remove values
        picture_edit = MagicMock()
        picture_edit.gen_replace = "from_null;to_null"
        picture_edit.gen_remove = "prompt_null"

        with self.assertRaises(HTTPException):
            await validate_edit_parameters(picture_edit)
