from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from src.member.model import Member, Role
from src.member.schema import MemberCreate, MemberUpdate, MemberResponse, LoginResponse
from src.member.service import MemberService


# 테스트용 픽스처 설정
@pytest.fixture
def member_service():
    service = MemberService()
    service.repository = MagicMock()
    return service


@pytest.fixture
def db_session():
    return MagicMock(spec=Session)


# 비밀번호 해싱 테스트
def test_hash_password(member_service):
    # Given
    password = "test_password"

    # When
    hashed = member_service._hash_password(password)

    # Then
    assert ":" in hashed
    salt, hash_part = hashed.split(":")
    assert len(bytes.fromhex(salt)) == 32
    assert len(bytes.fromhex(hash_part)) > 0


# 올바른 비밀번호 검증 테스트
def test_verify_password_success(member_service):
    # Given
    password = "test_password"
    hashed = member_service._hash_password(password)

    # When
    result = member_service._verify_password(hashed, password)

    # Then
    assert result is True


# 잘못된 비밀번호 검증 테스트
def test_verify_password_failure(member_service):
    # Given
    password = "test_password"
    wrong_password = "wrong_password"
    hashed = member_service._hash_password(password)

    # When
    result = member_service._verify_password(hashed, wrong_password)

    # Then
    assert result is False


# ID로 회원 조회 성공 테스트
def test_get_by_id_success(member_service, db_session):
    # Given
    member_id = 1
    mock_member = MagicMock(spec=Member)
    mock_member.id = member_id
    mock_member.username = "test_user"
    mock_member.role = Role.USER

    member_service.repository.find_by_id.return_value = mock_member

    # When
    result = member_service._get_by_id(db_session, member_id)

    # Then
    member_service.repository.find_by_id.assert_called_once_with(db_session, member_id)
    assert result is not None
    assert isinstance(result, MemberResponse)
    assert result.id == member_id


# ID로 회원 조회 실패 테스트
def test_get_by_id_not_found(member_service, db_session):
    # Given
    member_id = 999
    member_service.repository.find_by_id.return_value = None

    # When
    result = member_service._get_by_id(db_session, member_id)

    # Then
    member_service.repository.find_by_id.assert_called_once_with(db_session, member_id)
    assert result is None


# 사용자명으로 회원 조회 테스트
def test_get_by_username(member_service, db_session):
    # Given
    username = "test_user"
    mock_member = MagicMock(spec=Member)
    mock_member.username = username

    member_service.repository.find_by_username.return_value = mock_member

    # When
    result = member_service._get_by_username(db_session, username)

    # Then
    member_service.repository.find_by_username.assert_called_once_with(db_session, username)
    assert result is mock_member


# 회원 생성 성공 테스트
def test_create_success(member_service, db_session):
    # Given
    username = "new_user"
    password = "password123"
    role = Role.USER

    member_create = MemberCreate(username=username, password=password, role=role)

    # 사용자명이 존재하지 않는 경우 모킹
    member_service.repository.find_by_username.return_value = None

    # 저장 메서드 모킹
    mock_saved_member = MagicMock(spec=Member)
    mock_saved_member.id = 1
    mock_saved_member.username = username
    mock_saved_member.role = role
    member_service.repository.save.return_value = mock_saved_member

    # When
    with patch.object(member_service, '_hash_password', return_value="salt:hash"):
        result = member_service.create(db_session, member_create)

    # Then
    member_service.repository.find_by_username.assert_called_once_with(db_session, username=username)
    member_service.repository.save.assert_called_once()
    assert result is not None
    assert isinstance(result, MemberResponse)
    assert result.username == username
    assert result.role.value == role.value


# 회원 생성 실패(사용자명 중복) 테스트
def test_create_username_exists(member_service, db_session):
    # Given
    username = "existing_user"
    password = "password123"

    member_create = MemberCreate(username=username, password=password)

    # 사용자명이 이미 존재하는 경우 모킹
    mock_existing_member = MagicMock(spec=Member)
    mock_existing_member.username = username
    member_service.repository.find_by_username.return_value = mock_existing_member

    # When
    result = member_service.create(db_session, member_create)

    # Then
    member_service.repository.find_by_username.assert_called_once_with(db_session, username=username)
    member_service.repository.save.assert_not_called()
    assert result is None


# 회원 정보 업데이트 성공 테스트
def test_update_success(member_service, db_session):
    # Given
    member_id = 1
    new_username = "updated_user"

    member_update = MemberUpdate(username=new_username)

    # 회원이 존재하는 경우 모킹
    mock_member = MagicMock(spec=Member)
    mock_member.id = 1
    mock_member.username = "old_username"
    mock_member.role = Role.USER

    # 저장 메서드 모킹
    mock_updated_member = MagicMock(spec=Member)
    mock_updated_member.username = new_username
    mock_updated_member.role = Role.USER
    member_service.repository.save.return_value = mock_updated_member

    # When
    result = member_service.update(db_session, mock_member, member_update)

    # Then
    member_service.repository.save.assert_called_once_with(db_session, mock_member)
    assert result is not None
    assert isinstance(result, MemberResponse)
    assert result.username == new_username


# 비밀번호 업데이트 테스트
def test_update_with_password(member_service, db_session):
    # Given
    member_id = 1
    new_password = "new_password"

    member_update = MemberUpdate(password=new_password)

    # 회원이 존재하는 경우 모킹
    mock_member = MagicMock(spec=Member)
    mock_member.id = member_id

    # 저장 메서드 모킹
    mock_updated_member = MagicMock(spec=Member)
    mock_updated_member.id = member_id
    mock_updated_member.username = "test_user"
    mock_updated_member.role = Role.USER
    member_service.repository.save.return_value = mock_updated_member

    # 비밀번호 해싱 메서드 모킹
    hashed_password = "salt:hash"

    # When
    with patch.object(member_service, '_hash_password', return_value=hashed_password):
        result = member_service.update(db_session, mock_member, member_update)

    # Then
    assert mock_member.password == hashed_password
    member_service.repository.save.assert_called_once_with(db_session, mock_member)
    assert result is not None


# 회원 삭제 성공 테스트
def test_delete_success(member_service, db_session):
    # Given
    member_id = 1

    # 회원이 존재하는 경우 모킹
    mock_member = MagicMock(spec=Member)
    mock_member.id = member_id
    member_service.repository.find_by_id.return_value = mock_member

    # 삭제 메서드 모킹
    member_service.repository.delete.return_value = True

    # When
    result = member_service.delete(db_session, member_id)

    # Then
    member_service.repository.find_by_id.assert_called_once_with(db_session, member_id)
    member_service.repository.delete.assert_called_once_with(db_session, mock_member)
    assert result is True


# 존재하지 않는 회원 삭제 테스트
def test_delete_member_not_found(member_service, db_session):
    # Given
    member_id = 999

    # 회원이 존재하지 않는 경우 모킹
    member_service.repository.find_by_id.return_value = None

    # When
    result = member_service.delete(db_session, member_id)

    # Then
    member_service.repository.find_by_id.assert_called_once_with(db_session, member_id)
    member_service.repository.delete.assert_not_called()
    assert result is False


# 로그인 성공 테스트
def test_login_success(member_service, db_session):
    # Given
    username = "test_user"
    password = "password123"

    member_login = MagicMock()
    member_login.username = username
    member_login.password = password

    # 회원이 존재하는 경우 모킹
    mock_member = MagicMock(spec=Member)
    mock_member.id = 1
    mock_member.username = username
    mock_member.password = "salt:hash"
    mock_member.role = Role.USER
    member_service.repository.find_by_username.return_value = mock_member

    # 비밀번호 검증 모킹
    with patch.object(member_service, '_verify_password', return_value=True):
        token = "test.jwt.token"
        with patch('src.core.security.security.create_access_token', return_value=token):
            # When
            result = member_service.login(db_session, member_login)

    # Then
    member_service.repository.find_by_username.assert_called_once_with(db_session, username)
    assert result is not None
    assert isinstance(result, LoginResponse)


# 로그인 실패(잘못된 비밀번호) 테스트
def test_login_wrong_password(member_service, db_session):
    # Given
    username = "test_user"
    password = "wrong_password"

    # OAuth2PasswordRequestForm 모킹
    member_login = MagicMock()
    member_login.username = username
    member_login.password = password

    # 회원이 존재하는 경우 모킹
    mock_member = MagicMock(spec=Member)
    mock_member.username = username
    mock_member.password = "salt:hash"
    member_service.repository.find_by_username.return_value = mock_member

    # 비밀번호 검증 실패 모킹
    with patch.object(member_service, '_verify_password', return_value=False):
        # When
        result = member_service.login(db_session, member_login)

    # Then
    member_service.repository.find_by_username.assert_called_once_with(db_session, username)
    assert result is None


# 로그인 실패(존재하지 않는 사용자) 테스트
def test_login_user_not_found(member_service, db_session):
    # Given
    username = "nonexistent_user"
    password = "password123"

    # OAuth2PasswordRequestForm 모킹
    member_login = MagicMock()
    member_login.username = username
    member_login.password = password

    member_service.repository.find_by_username.return_value = None

    # When
    result = member_service.login(db_session, member_login)

    # Then
    member_service.repository.find_by_username.assert_called_once_with(db_session, username)
    assert result is None
