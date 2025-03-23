from datetime import datetime, timezone, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import AnyUrl
import shortuuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from database import get_async_session
from models import TShortUrl, TEvents, EventType
from links.schemas import ShortUrlParameters, ShortUrlStats, UpdateParameters
from users import TUser, current_active_user
from links import service

router = APIRouter(prefix="/links", tags=["links"])


@router.post("/shorten", description="Создать короткую ссылку")
async def createShorter(
    request: Request,
    url_params: Annotated[ShortUrlParameters, "Параметры создания короткой ссылки"],
    session: AsyncSession = Depends(get_async_session),
    user: TUser = Depends(current_active_user)
):
    if url_params.original_url is None:
        raise HTTPException(
            400,
            "Для создания короткой ссылки необходимо указать original_url"
        )
    if url_params.custom_alias is not None:
        exist = await service.get_shorturl_by_name(url_params.custom_alias, session)
        if exist is not None:
            raise HTTPException(
                400,
                "Такая короткая ссылка уже существует!"
            )
        short_code = url_params.custom_alias
    else:
        short_code = shortuuid.uuid()
    short = TShortUrl(
        short_name=short_code,
        original_url=str(url_params.original_url),
        # использую datetime without time zone, поэтому .utcnow(), а не .now(timezone.utc)
        create_time=datetime.utcnow(),
        modify_time=datetime.utcnow(),
        redirect_count=0,
        user_id=None,
        last_redirect=None
    )
    if user is not None:
        short.user_id = user.id
        # Для авторизованных пользователей можно создавать ссылку бессрочную
        if url_params.expires_at is not None and url_params.expires_at > datetime.now(timezone.utc):
            short.expires_at = url_params.expires_at.utcfromtimestamp(0)
    else:
        # Для неавторизованных пользователей создается ссылка на 12 часов
        short.expires_at = datetime.utcnow() + timedelta(hours=12)
    try:
        session.add(short)

        event = TEvents(
            short_url=short.short_name,
            event_type=EventType.AddShort,
            datetime=datetime.utcnow(),
            description=f"{"Unauthorized" if user is None else user.email} создал короткую ссылку {short.short_name}"
        )
        session.add(event)

        await session.commit()
        # Возвращает созданный короткий URL
        return f"{str(request.base_url)}links/{short.short_name}"
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/my_urls", description="Получить список всех своих ссылок")
async def getUserUrls(session: AsyncSession = Depends(get_async_session), user: TUser = Depends(current_active_user)):
    if user is None:
        raise HTTPException(
            401, "Просмотр ссылок только для авторизованных пользователей!")
    try:
        query = select(TShortUrl).where(
            TShortUrl.user_id == user.id).limit(100)
        result = await session.execute(query)
        urls_result = result.scalars().all()
        if urls_result is not None:
            return urls_result
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/search", description="Поиск ссылки по оригинальному URL")
async def searchUrl(
    original_url: Annotated[AnyUrl, "Оригинальный URL"],
    request: Request,
    session: AsyncSession = Depends(get_async_session)
):
    shorts = await service.get_shorturl_by_original(str(original_url), session)
    # Может быть несколько коротких ссылок для оригинальной
    # Отдаю список коротких ссылок
    return [f"{str(request.base_url)}links/{sh}" for sh in shorts]


@router.get("/{short_code}/stats", description="Статистика по короткой ссылке")
async def getShortUrlStats(
    short_code: Annotated[str, "Короткий код ссылки"],
    session: AsyncSession = Depends(get_async_session)
):
    try:
        short = await service.get_shorturl_by_name(short_code, session)
        if short is None:
            raise HTTPException(404, "Не найден ресурс короткой ссылки")
        else:
            return ShortUrlStats(
                original_url=short.original_url,
                create_time=short.create_time,
                redirect_count=short.redirect_count,
                last_redirect=short.last_redirect
            )
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/{short_code}", description="Перенаправление на оригинальную ссылку")
async def redirectShorter(
    short_code: Annotated[str, "Короткий код ссылки"],
    session: AsyncSession = Depends(get_async_session)
):
    try:
        short = await service.get_shorturl_by_name(short_code, session)
        if short is not None:
            short.redirect_count = short.redirect_count+1
            short.last_redirect = datetime.utcnow()
            await session.commit()
            return RedirectResponse(short.original_url)
        else:
            raise HTTPException(404, "Не найден ресурс короткой ссылки")
    except HTTPException as httpEx:
        raise HTTPException(httpEx.status_code, httpEx.detail)
    except Exception as e:
        raise HTTPException(500, str(e))


@router.delete("/{short_code}", description="Удаление ссылки")
async def removeShorter(
    short_code: Annotated[str, "Короткий код ссылки"],
    session: AsyncSession = Depends(get_async_session),
    user: TUser = Depends(current_active_user)
):
    if user is None:
        raise HTTPException(401)
    short = await service.get_user_shorturl_by_name(short_code, session, user)
    if short is None:
        raise HTTPException(
            400,
            f"Пользователю {user.email} не принадлежит короткая ссылка /{short_code}"
        )
    try:
        await session.delete(short)
        event = TEvents(
            short_url=short.short_name,
            event_type=EventType.RemoveShort,
            datetime=datetime.utcnow(),
            description=f"{user.email} удалил короткую ссылку {short.short_name}"
        )
        session.add(event)
        await session.commit()
        return Response(status_code=200)
    except Exception as e:
        return HTTPException(500, str(e))


@router.put("/{short_code}", description="Обновление оригинальной ссылки, привязанной к короткой")
async def updateShorter(
    updateParams: Annotated[UpdateParameters, "Параметры для обновления короткой ссылки"],
    short_code: Annotated[str, "Короткий код ссылки"],
    session: AsyncSession = Depends(get_async_session),
    user: TUser = Depends(current_active_user)
):
    if user is None:
        raise HTTPException(
            401, "Обновлять ссылки можно только авторизованным пользователям!")
    short = await service.get_user_shorturl_by_name(short_code, session, user)
    if short is None:
        raise HTTPException(
            400,
            f"Пользователю {user.email} не принадлежит короткая ссылка /{short_code}"
        )
    try:
        if updateParams.expires_at is not None and updateParams.expires_at > datetime.now(timezone.utc):
            short.expires_at = updateParams.expires_at.utcfromtimestamp(0)
        short.original_url = str(updateParams.original_url)
        short.modify_time = datetime.utcnow()

        event = TEvents(
            short_url=short.short_name,
            event_type=EventType.UpdateShort,
            datetime=datetime.utcnow(),
            description=f"{user.email} обновил короткую ссылку {short.short_name}"
        )
        session.add(event)

        await session.commit()
        return Response(status_code=200)
    except Exception as e:
        raise HTTPException(500, str(e))
