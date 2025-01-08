import unittest
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.scores.models import Score
from src.scores.repository import ScoreRepository
from src.scores.schemas import ScoreCreate, ScoreUpdate


class TestScoreRepository(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample_score_1 = Score(id=1, user_id=1, post_id=1, score=5)
        cls.sample_score_2 = Score(id=2, user_id=1, post_id=2, score=4)
        cls.sample_score_3 = Score(id=3, user_id=2, post_id=1, score=3)

    def setUp(self):
        self.session = MagicMock(spec=AsyncSession)
        self.session.execute = AsyncMock()
        self.session.add = MagicMock()
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()
        self.score_repository = ScoreRepository(self.session)

    async def test_get_score_by_id(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.sample_score_1
        self.session.execute.return_value = mock_result

        result = await self.score_repository.get_score_by_id(1)
        stmt = self.session.execute.call_args[0][0]
        expected_stmt = select(Score).where(Score.id == 1)

        self.assertEqual(str(stmt), str(expected_stmt))
        self.assertEqual(result, self.sample_score_1)

    async def test_create_score(self):
        score_data = ScoreCreate(post_id=1, user_id=1, score=5)
        new_score = await self.score_repository.create_score(score_data)

        self.session.add.assert_called_once_with(new_score)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(new_score)
        self.assertEqual(new_score.score, score_data.score)

    async def test_update_score(self):
        score_data = ScoreUpdate(score=5)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.sample_score_1
        self.session.execute.return_value = mock_result

        updated_score = await self.score_repository.update_score(1, score_data)
        stmt = self.session.execute.call_args[0][0]
        expected_stmt = select(Score).where(Score.id == 1)

        self.assertEqual(str(stmt), str(expected_stmt))
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(self.sample_score_1)
        self.assertEqual(updated_score.score, 5)

    # async def test_delete_score(self):
    #     mock_result = MagicMock()
    #     mock_result.scalar_one_or_none.return_value = self.sample_score_1
    #     self.session.execute.return_value = mock_result
    #
    #     deleted_score = await self.score_repository.delete_score(1)
    #     stmt = self.session.execute.call_args[0][0]
    #     expected_stmt = select(Score).where(Score.id == 1)
    #
    #     self.assertEqual(str(stmt), str(expected_stmt))
    #     self.session.commit.assert_called_once()
    #     self.assertEqual(deleted_score, self.sample_score_1)

    async def test_get_average_score_by_post_id(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = 4.5
        self.session.execute.return_value = mock_result

        average_score = await self.score_repository.get_average_score_by_post_id(1)
        stmt = self.session.execute.call_args[0][0]
        expected_stmt = select(func.avg(Score.score).label("average_score")).where(Score.post_id == 1)

        self.assertEqual(str(stmt), str(expected_stmt))
        self.assertEqual(average_score, 4.5)

    async def test_score_exists(self):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.sample_score_1
        self.session.execute.return_value = mock_result

        exists = await self.score_repository.score_exists(1, 1)
        stmt = self.session.execute.call_args[0][0]
        expected_stmt = select(Score).where(Score.user_id == 1, Score.post_id == 1)
        
        self.assertEqual(str(stmt), str(expected_stmt))
        self.assertTrue(exists)

        mock_result.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mock_result

        not_exists = await self.score_repository.score_exists(2, 2)
        self.assertFalse(not_exists)
