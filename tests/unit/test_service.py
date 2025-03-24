import pytest
import shortuuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock
from src.links import service
from src.models import TShortUrl


@pytest.mark.asyncio
async def test_generate_short_url():
    short_code = shortuuid.uuid()
    assert isinstance(short_code, str)
    assert len(short_code) > 5  # Минимальная длина


@pytest.mark.asyncio
async def test_create_short_link_existing(mocker):
    mock_session = AsyncMock()
    mocker.patch("src.links.service.get_shorturl_by_name",
                 return_value=TShortUrl(short_name="test"))

    with pytest.raises(Exception) as exc_info:
        await service.create_short_url("https://example.com", "test", mock_session)

    assert "уже существует" in str(exc_info.value)
