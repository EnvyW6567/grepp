from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from src.exam.model import Exam
from src.member.model import Member
from src.member.schema import Role
from src.reservation.exception import ReservationNotFound, NotAllowed, ReservationValidationFailed
from src.reservation.model import Reservation, Status
from src.reservation.schema import ReservationCreate, ReservationResponse, ReservationUpdate, ReservationUpdateStatus
from src.reservation.service import ReservationService


@pytest.fixture
def reservation_service():
    service = ReservationService()
    service.repository = MagicMock()
    service.exam_service = MagicMock()
    return service


@pytest.fixture
def db_session():
    return MagicMock(spec=Session)


@pytest.fixture
def test_member():
    member = MagicMock(spec=Member)
    member.id = 1
    member.role = Role.USER
    return member


@pytest.fixture
def test_admin():
    admin = MagicMock(spec=Member)
    admin.id = 2
    admin.role = Role.ADMIN
    return admin


@pytest.fixture
def mock_exam():
    exam = MagicMock(spec=Exam)
    exam.id = 1
    exam.member_id = 1
    exam.description = "Test Exam"
    exam.date = datetime.now() + timedelta(days=10)
    exam.current_people = 10
    exam.max_people = 100
    return exam


@pytest.fixture
def mock_reservation():
    reservation = MagicMock(spec=Reservation)
    reservation.id = 1
    reservation.member_id = 1
    reservation.exam_id = 1
    reservation.people = 5
    reservation.status = Status.PENDING
    reservation.created_at = datetime.now()
    reservation.modified_at = datetime.now()
    return reservation


# 예약 생성 성공 시나리오
def test_create_success(reservation_service, db_session, test_member, mock_exam):
    # Given
    reservation_create = ReservationCreate(
        exam_id=1,
        people=5
    )

    # exam_service.get_by_id 모킹
    reservation_service.exam_service.get_by_id.return_value = mock_exam

    # repository.save 모킹
    mock_saved_reservation = MagicMock(spec=Reservation)
    mock_saved_reservation.id = 1
    mock_saved_reservation.member_id = test_member.id
    mock_saved_reservation.exam_id = mock_exam.id
    mock_saved_reservation.people = 5
    mock_saved_reservation.status = Status.PENDING

    reservation_service.repository.save.return_value = mock_saved_reservation

    # When
    result = reservation_service.create(db_session, test_member, reservation_create)

    # Then
    reservation_service.exam_service.get_by_id.assert_called_once_with(db_session, reservation_create.exam_id)
    reservation_service.repository.save.assert_called_once()
    assert result == mock_saved_reservation


# 날짜 제한으로 인한 예약 생성 실패 시나리오
def test_create_validation_failed(reservation_service, db_session, test_member, mock_exam):
    # Given
    reservation_create = ReservationCreate(
        exam_id=1,
        people=5
    )

    # 시험 날짜가 3일 이내로 설정
    mock_exam.date = datetime.now() + timedelta(days=2)

    # exam_service.get_by_id 모킹
    reservation_service.exam_service.get_by_id.return_value = mock_exam

    # When & Then
    with pytest.raises(ReservationValidationFailed):
        reservation_service.create(db_session, test_member, reservation_create)

    reservation_service.exam_service.get_by_id.assert_called_once_with(db_session, reservation_create.exam_id)
    reservation_service.repository.save.assert_not_called()


# 인원 초과로 인한 예약 생성 실패 시나리오
def test_create_people_exceeded(reservation_service, db_session, test_member, mock_exam):
    # Given
    reservation_create = ReservationCreate(
        exam_id=1,
        people=100  # 시험 남은 인원보다 많음
    )

    # exam_service.get_by_id 모킹
    mock_exam.max_people = 50
    mock_exam.current_people = 10
    reservation_service.exam_service.get_by_id.return_value = mock_exam

    # When & Then
    with pytest.raises(ReservationValidationFailed):
        reservation_service.create(db_session, test_member, reservation_create)

    reservation_service.exam_service.get_by_id.assert_called_once_with(db_session, reservation_create.exam_id)
    reservation_service.repository.save.assert_not_called()


# 사용자 본인 예약 조회 성공 시나리오
def test_get_by_id_success_own(reservation_service, db_session, test_member, mock_reservation):
    # Given
    reservation_id = 1
    mock_reservation.member_id = test_member.id

    reservation_service.repository.find_by_id.return_value = mock_reservation

    # ReservationResponse.model_validate 모킹
    mock_response = MagicMock(spec=ReservationResponse)

    with patch('src.reservation.schema.ReservationResponse.model_validate', return_value=mock_response):
        # When
        result = reservation_service.get_by_id(db_session, test_member, reservation_id)

        # Then
        reservation_service.repository.find_by_id.assert_called_once_with(db_session, reservation_id)
        assert result == mock_response


# 관리자의 타인 예약 조회 성공 시나리오
def test_get_by_id_success_admin(reservation_service, db_session, test_admin, mock_reservation):
    # Given
    reservation_id = 1
    mock_reservation.member_id = 3  # 다른 회원의 예약

    reservation_service.repository.find_by_id.return_value = mock_reservation

    # ReservationResponse.model_validate 모킹
    mock_response = MagicMock(spec=ReservationResponse)

    with patch('src.reservation.schema.ReservationResponse.model_validate', return_value=mock_response):
        # When
        result = reservation_service.get_by_id(db_session, test_admin, reservation_id)

        # Then
        reservation_service.repository.find_by_id.assert_called_once_with(db_session, reservation_id)
        assert result == mock_response


# 존재하지 않는 예약 조회 실패 시나리오
def test_get_by_id_not_found(reservation_service, db_session, test_member):
    # Given
    reservation_id = 999
    reservation_service.repository.find_by_id.return_value = None

    # When & Then
    with pytest.raises(ReservationNotFound):
        reservation_service.get_by_id(db_session, test_member, reservation_id)

    reservation_service.repository.find_by_id.assert_called_once_with(db_session, reservation_id)


# 권한 없는 예약 조회 실패 시나리오
def test_get_by_id_not_allowed(reservation_service, db_session, test_member, mock_reservation):
    # Given
    reservation_id = 1
    mock_reservation.member_id = 999  # 다른 회원의 예약

    reservation_service.repository.find_by_id.return_value = mock_reservation

    # When & Then
    with pytest.raises(NotAllowed):
        reservation_service.get_by_id(db_session, test_member, reservation_id)

    reservation_service.repository.find_by_id.assert_called_once_with(db_session, reservation_id)


# 사용자의 모든 예약 목록 조회 테스트
def test_get_all(reservation_service, db_session, test_member, mock_reservation):
    # Given
    mock_reservations = [mock_reservation]
    reservation_service.repository.find_by_member_id.return_value = mock_reservations

    # ReservationResponse.model_validate 모킹
    mock_response = MagicMock(spec=ReservationResponse)

    with patch('src.reservation.schema.ReservationResponse.model_validate', return_value=mock_response):
        # When
        result = reservation_service.get_all(db_session, test_member)

        # Then
        reservation_service.repository.find_by_member_id.assert_called_once_with(db_session, test_member.id)
        assert len(result) == 1
        assert result[0] == mock_response


# 특정 회원 예약 목록 조회 테스트
def test_get_all_by_member_id(reservation_service, db_session, mock_reservation):
    # Given
    member_id = 1
    mock_reservations = [mock_reservation]
    reservation_service.repository.find_by_member_id.return_value = mock_reservations

    # ReservationResponse.model_validate 모킹
    mock_response = MagicMock(spec=ReservationResponse)

    with patch('src.reservation.schema.ReservationResponse.model_validate', return_value=mock_response):
        # When
        result = reservation_service.get_all_by_member_id(db_session, member_id)

        # Then
        reservation_service.repository.find_by_member_id.assert_called_once_with(db_session, member_id)
        assert len(result) == 1
        assert result[0] == mock_response


# 사용자 본인 예약 수정 성공 시나리오
def test_update_success_own(reservation_service, db_session, test_member, mock_reservation):
    # Given
    reservation_update = ReservationUpdate(
        id=1,
        people=10
    )

    mock_reservation.member_id = test_member.id
    reservation_service.repository.find_by_id.return_value = mock_reservation

    # 저장 메서드 모킹
    mock_updated_reservation = MagicMock(spec=Reservation)
    mock_updated_reservation.people = 10
    reservation_service.repository.save.return_value = mock_updated_reservation

    # ReservationResponse.model_validate 모킹
    mock_response = MagicMock(spec=ReservationResponse)

    with patch('src.reservation.schema.ReservationResponse.model_validate', return_value=mock_response):
        # When
        result = reservation_service.update(db_session, test_member, reservation_update)

        # Then
        reservation_service.repository.find_by_id.assert_called_once_with(
            db_session,
            reservation_update.id
        )
        assert mock_reservation.people == 10
        reservation_service.repository.save.assert_called_once_with(db_session, mock_reservation)
        assert result == mock_response


# 관리자의 타인 예약 수정 성공 시나리오
def test_update_success_admin(reservation_service, db_session, test_admin, mock_reservation):
    # Given
    reservation_update = ReservationUpdate(
        id=1,
        people=10
    )

    reservation_service.repository.find_by_id.return_value = mock_reservation

    # 저장 메서드 모킹
    mock_updated_reservation = MagicMock(spec=Reservation)
    mock_updated_reservation.people = 10
    reservation_service.repository.save.return_value = mock_updated_reservation

    # ReservationResponse.model_validate 모킹
    mock_response = MagicMock(spec=ReservationResponse)

    with patch('src.reservation.schema.ReservationResponse.model_validate', return_value=mock_response):
        # When
        result = reservation_service.update(db_session, test_admin, reservation_update)

        # Then
        reservation_service.repository.find_by_id.assert_called_once_with(
            db_session,
            reservation_update.id
        )
        assert mock_reservation.people == 10
        reservation_service.repository.save.assert_called_once_with(db_session, mock_reservation)
        assert result == mock_response


# 존재하지 않는 예약 수정 실패 시나리오
def test_update_not_found(reservation_service, db_session, test_member):
    # Given
    reservation_update = ReservationUpdate(
        id=1,
        people=10
    )

    reservation_service.repository.find_by_id.return_value = None

    # When & Then
    with pytest.raises(ReservationNotFound):
        reservation_service.update(db_session, test_member, reservation_update)

    reservation_service.repository.find_by_id.assert_called_once_with(
        db_session,
        reservation_update.id
    )
    reservation_service.repository.save.assert_not_called()


# 권한 없는 예약 수정 실패 시나리오
def test_update_not_allowed(reservation_service, db_session, test_member, mock_reservation):
    # Given
    reservation_update = ReservationUpdate(
        id=1,
        people=10
    )

    mock_reservation.member_id = 999
    mock_reservation.role = Role.USER
    reservation_service.repository.find_by_id.return_value = mock_reservation

    # When & Then
    with pytest.raises(NotAllowed):
        reservation_service.update(db_session, test_member, reservation_update)

    reservation_service.repository.find_by_id.assert_called_once_with(
        db_session,
        reservation_update.id
    )
    reservation_service.repository.save.assert_not_called()


# 예약 상태 확정 변경 시나리오
def test_update_status_confirmed(reservation_service, db_session, mock_reservation):
    # Given
    reservation_update_status = ReservationUpdateStatus(
        id=1,
        status=Status.CONFIRMED
    )

    mock_reservation.status = Status.PENDING
    mock_reservation.exam_id = 1
    mock_reservation.people = 5

    reservation_service.repository.find_by_id.return_value = mock_reservation

    # 저장 메서드 모킹
    mock_updated_reservation = MagicMock(spec=Reservation)
    mock_updated_reservation.status = Status.CONFIRMED
    reservation_service.repository.save.return_value = mock_updated_reservation

    # ReservationResponse.model_validate 모킹
    mock_response = MagicMock(spec=ReservationResponse)

    with patch('src.reservation.schema.ReservationResponse.model_validate', return_value=mock_response):
        # When
        result = reservation_service.update_status(db_session, reservation_update_status)

        # Then
        reservation_service.repository.find_by_id.assert_called_once_with(db_session, reservation_update_status.id)
        assert mock_reservation.status == Status.CONFIRMED
        reservation_service.exam_service.update_people.assert_called_once_with(db_session, mock_reservation.exam_id,
                                                                               mock_reservation.people)
        reservation_service.repository.save.assert_called_once_with(db_session, mock_reservation)
        assert result == mock_response


# 예약 상태 거부 변경 시나리오
def test_update_status_denied(reservation_service, db_session, mock_reservation):
    # Given
    reservation_update_status = ReservationUpdateStatus(
        id=1,
        status=Status.DENIED
    )

    mock_reservation.status = Status.PENDING

    reservation_service.repository.find_by_id.return_value = mock_reservation

    # 저장 메서드 모킹
    mock_updated_reservation = MagicMock(spec=Reservation)
    mock_updated_reservation.status = Status.DENIED
    reservation_service.repository.save.return_value = mock_updated_reservation

    # ReservationResponse.model_validate 모킹
    mock_response = MagicMock(spec=ReservationResponse)

    with patch('src.reservation.schema.ReservationResponse.model_validate', return_value=mock_response):
        # When
        result = reservation_service.update_status(db_session, reservation_update_status)

        # Then
        reservation_service.repository.find_by_id.assert_called_once_with(db_session, reservation_update_status.id)
        assert mock_reservation.status == Status.DENIED
        reservation_service.exam_service.update_people.assert_not_called()  # DENIED 상태에서는 호출 안 함
        reservation_service.repository.save.assert_called_once_with(db_session, mock_reservation)
        assert result == mock_response


# 존재하지 않는 예약 상태 변경 실패 시나리오
def test_update_status_not_found(reservation_service, db_session):
    # Given
    reservation_update_status = ReservationUpdateStatus(
        id=999,
        status=Status.CONFIRMED
    )

    reservation_service.repository.find_by_id.return_value = None

    # When & Then
    with pytest.raises(ReservationNotFound):
        reservation_service.update_status(db_session, reservation_update_status)

    reservation_service.repository.find_by_id.assert_called_once_with(db_session, reservation_update_status.id)
    reservation_service.repository.save.assert_not_called()


# 대기중인 본인 예약 삭제 성공 시나리오
def test_delete_success_own_pending(reservation_service, db_session, test_member, mock_reservation):
    # Given
    reservation_id = 1
    mock_reservation.member_id = test_member.id
    mock_reservation.status = Status.PENDING

    reservation_service.repository.find_by_id.return_value = mock_reservation
    reservation_service.repository.delete.return_value = True

    # When
    reservation_service.delete(db_session, test_member, reservation_id)

    # Then
    reservation_service.repository.find_by_id.assert_called_once_with(db_session, reservation_id)
    reservation_service.repository.delete.assert_called_once_with(db_session, mock_reservation)
    reservation_service.exam_service.update_people.assert_not_called()  # PENDING 상태에서는 호출 안 함


# 확정된 본인 예약 삭제 성공 시나리오
def test_delete_success_own_confirmed(reservation_service, db_session, test_member, mock_reservation):
    # Given
    reservation_id = 1
    mock_reservation.member_id = test_member.id
    mock_reservation.status = Status.CONFIRMED
    mock_reservation.exam_id = 1
    mock_reservation.people = 5

    reservation_service.repository.find_by_id.return_value = mock_reservation
    reservation_service.repository.delete.return_value = True

    # When
    reservation_service.delete(db_session, test_member, reservation_id)

    # Then
    reservation_service.repository.find_by_id.assert_called_once_with(db_session, reservation_id)
    reservation_service.repository.delete.assert_called_once_with(db_session, mock_reservation)
    reservation_service.exam_service.update_people.assert_called_once_with(db_session, mock_reservation.exam_id,
                                                                           -mock_reservation.people)


# 관리자의 타인 예약 삭제 성공 시나리오
def test_delete_success_admin(reservation_service, db_session, test_admin, mock_reservation):
    # Given
    reservation_id = 1
    mock_reservation.member_id = 999  # 다른 회원의 예약
    mock_reservation.status = Status.PENDING

    reservation_service.repository.find_by_id.return_value = mock_reservation
    reservation_service.repository.delete.return_value = True

    # When
    reservation_service.delete(db_session, test_admin, reservation_id)

    # Then
    reservation_service.repository.find_by_id.assert_called_once_with(db_session, reservation_id)
    reservation_service.repository.delete.assert_called_once_with(db_session, mock_reservation)


# 존재하지 않는 예약 삭제 시나리오
def test_delete_not_found(reservation_service, db_session, test_member):
    # Given
    reservation_id = 999
    reservation_service.repository.find_by_id.return_value = None

    # When
    result = reservation_service.delete(db_session, test_member, reservation_id)

    # Then
    reservation_service.repository.find_by_id.assert_called_once_with(db_session, reservation_id)
    reservation_service.repository.delete.assert_not_called()
    assert isinstance(result, ReservationNotFound)


# 권한 없는 예약 삭제 실패 시나리오
def test_delete_not_allowed(reservation_service, db_session, test_member, mock_reservation):
    # Given
    reservation_id = 1
    mock_reservation.member_id = 999  # 다른 회원의 예약

    reservation_service.repository.find_by_id.return_value = mock_reservation

    # When & Then
    with pytest.raises(NotAllowed):
        reservation_service.delete(db_session, test_member, reservation_id)

    reservation_service.repository.find_by_id.assert_called_once_with(db_session, reservation_id)
    reservation_service.repository.delete.assert_not_called()
