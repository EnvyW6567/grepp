from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from src.exam.exception import ExamNotFound, ExamCapacityExceededError
from src.exam.model import Exam
from src.exam.schema import ExamCreate, ExamResponse
from src.exam.service import ExamService
from src.member.model import Member


@pytest.fixture
def exam_service():
    service = ExamService()
    service.repository = MagicMock()
    return service


@pytest.fixture
def db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def test_member():
    member = MagicMock(spec=Member)
    member.id = 1
    return member


@pytest.fixture
def mock_exam():
    exam = MagicMock(spec=Exam)
    exam.id = 1
    exam.member_id = 1
    exam.description = "Test Exam"
    exam.date = datetime.now() + timedelta(days=10)
    exam.current_people = 10
    exam.max_people = 100
    exam.created_at = datetime.now()
    exam.modified_at = datetime.now()
    return exam


# 모든 시험 목록 조회 테스트
def test_get_all(exam_service, db_session, mock_exam):
    # Given
    mock_exams = [mock_exam]
    exam_service.repository.find_all.return_value = mock_exams

    # ExamResponse.model_validate 모킹
    mock_response = MagicMock(spec=ExamResponse)

    with patch('src.exam.schema.ExamResponse.model_validate', return_value=mock_response):
        # When
        result = exam_service.get_all(db_session)

        # Then
        exam_service.repository.find_all.assert_called_once_with(db_session)
        assert len(result) == 1
        assert result[0] == mock_response


# ID로 시험 검색 성공 시나리오
def test_get_by_id_success(exam_service, db_session, mock_exam):
    # Given
    exam_id = 1
    exam_service.repository.find_by_id.return_value = mock_exam

    # ExamResponse.model_validate 모킹
    mock_response = MagicMock(spec=ExamResponse)

    with patch('src.exam.schema.ExamResponse.model_validate', return_value=mock_response):
        # When
        result = exam_service.get_by_id(db_session, exam_id)

        # Then
        exam_service.repository.find_by_id.assert_called_once_with(db_session, exam_id)
        assert result == mock_response


# 존재하지 않는 ID로 시험 검색 실패 시나리오
def test_get_by_id_not_found(exam_service, db_session):
    # Given
    exam_id = 999
    exam_service.repository.find_by_id.return_value = None

    # When & Then
    with pytest.raises(ExamNotFound):
        exam_service.get_by_id(db_session, exam_id)

    exam_service.repository.find_by_id.assert_called_once_with(db_session, exam_id)


# 회원 ID로 시험 목록 조회 테스트
def test_get_by_member_id(exam_service, db_session, mock_exam):
    # Given
    member_id = 1
    mock_exams = [mock_exam]
    exam_service.repository.find_by_member_id.return_value = mock_exams

    # ExamResponse.model_validate 모킹
    mock_response = MagicMock(spec=ExamResponse)

    with patch('src.exam.schema.ExamResponse.model_validate', return_value=mock_response):
        # When
        result = exam_service.get_by_member_id(db_session, member_id)

        # Then
        exam_service.repository.find_by_member_id.assert_called_once_with(db_session, member_id)
        assert len(result) == 1
        assert result[0] == mock_response


# 신규 시험 생성 성공 시나리오
def test_create_success(exam_service, db_session, test_member):
    # Given
    exam_date = datetime.now() + timedelta(days=7)
    exam_create = ExamCreate(
        date=exam_date,
        description="New Exam",
        current_people=5,
        max_people=50
    )

    # repository.save 모킹
    mock_saved_exam = MagicMock(spec=Exam)
    mock_saved_exam.id = 1
    mock_saved_exam.member_id = test_member.id
    mock_saved_exam.date = exam_date
    mock_saved_exam.description = "New Exam"
    mock_saved_exam.current_people = 5
    mock_saved_exam.max_people = 50

    exam_service.repository.save.return_value = mock_saved_exam

    # ExamResponse.model_validate 모킹
    mock_response = MagicMock(spec=ExamResponse)

    with patch('src.exam.schema.ExamResponse.model_validate', return_value=mock_response):
        # When
        result = exam_service.create(db_session, test_member, exam_create)

        # Then
        exam_service.repository.save.assert_called_once()
        assert result == mock_response


# 인원 수용량 초과 시 생성 실패 시나리오
def test_create_capacity_exceeded(exam_service, db_session, test_member):
    # Given
    exam_create = ExamCreate(
        date=datetime.now() + timedelta(days=7),
        description="Over Capacity Exam",
        current_people=100,
        max_people=50  # 현재 인원이 최대 인원보다 많음
    )

    # When & Then
    with pytest.raises(ExamCapacityExceededError):
        exam_service.create(db_session, test_member, exam_create)

    exam_service.repository.save.assert_not_called()


# 시험 삭제 성공 시나리오
def test_delete_success(exam_service, db_session, mock_exam):
    # Given
    exam_id = 1
    exam_service.repository.find_by_id.return_value = mock_exam
    exam_service.repository.delete.return_value = True

    # When
    exam_service.delete(db_session, exam_id)

    # Then
    exam_service.repository.find_by_id.assert_called_once_with(db_session, exam_id)
    exam_service.repository.delete.assert_called_once_with(db_session, mock_exam)


# 존재하지 않는 시험 삭제 시나리오
def test_delete_not_found(exam_service, db_session):
    # Given
    exam_id = 999
    exam_service.repository.find_by_id.return_value = None

    # When & Then
    with pytest.raises(ExamNotFound):
        exam_service.delete(db_session, exam_id)

    exam_service.repository.find_by_id.assert_called_once_with(db_session, exam_id)
    exam_service.repository.delete.assert_not_called()


# 인원 업데이트 성공 시나리오
def test_update_people_success(exam_service, db_session, mock_exam):
    # Given
    exam_id = 1
    people_to_add = 5
    mock_exam.current_people = 10
    mock_exam.max_people = 100

    exam_service.repository.find_by_id.return_value = mock_exam
    exam_service.repository.save.return_value = mock_exam

    # When
    result = exam_service.update_people(db_session, exam_id, people_to_add)

    # Then
    exam_service.repository.find_by_id.assert_called_once_with(db_session, exam_id)
    assert mock_exam.current_people == 15  # 10 + 5
    exam_service.repository.save.assert_called_once_with(db_session, mock_exam)
    assert result == mock_exam


# 존재하지 않는 시험 인원 업데이트 시나리오
def test_update_people_not_found(exam_service, db_session):
    # Given
    exam_id = 999
    people_to_add = 5

    exam_service.repository.find_by_id.return_value = None

    # When & Then
    with pytest.raises(ExamNotFound):
        exam_service.update_people(db_session, exam_id, people_to_add)

    exam_service.repository.find_by_id.assert_called_once_with(db_session, exam_id)
    exam_service.repository.save.assert_not_called()


# 용량 초과 시 인원 업데이트 실패 시나리오
def test_update_people_capacity_exceeded(exam_service, db_session, mock_exam):
    # Given
    exam_id = 1
    people_to_add = 100  # 추가하면 용량 초과
    mock_exam.current_people = 10
    mock_exam.max_people = 50

    exam_service.repository.find_by_id.return_value = mock_exam

    # When & Then
    with pytest.raises(ExamCapacityExceededError):
        exam_service.update_people(db_session, exam_id, people_to_add)

    exam_service.repository.find_by_id.assert_called_once_with(db_session, exam_id)
    exam_service.repository.save.assert_not_called()
