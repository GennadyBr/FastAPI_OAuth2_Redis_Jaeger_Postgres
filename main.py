import re  # регулярка
import uuid
import uvicorn
import settings
from fastapi.routing import APIRouter
from fastapi import FastAPI, HTTPException
from sqlalchemy import Column, Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import psycopg2

#############################################
# BLOCK FOR COMMON INTERATION WITH DATABASE #
#############################################

# create async engine for interaction with database
engine = create_async_engine(settings.REAL_DATABASE_URL, future=True, echo=True)

# create session for interaction with database
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

##############################
# BLOCK WITH DATABASE MODELS #
##############################
# это алхимия
# пайдентик на одной стороне, а алхимия на стороне приложения с базой данных

Base = declarative_base()


# что бы наследовать модели для общения с алхимией

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    login = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean(), default=True)
    hashed_password = Column(String, default='')  # пока строка


###########################################################
# BLOCK FOR INTERACTION WITH DATABASE IN BUSINESS CONTEXT #
###########################################################

class UserDAL:  # User Data Access Layer создание, удаление и все остальные функции взаимодействия с пользователем
    """Data Access Layer for operation user CRUD"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
            self, name: str, surname: str, login: str, email: str) -> User:
        """Create User"""
        new_user = User(
            name=name,
            surname=surname,
            login=login,
            email=email,
        )
        self.db_session.add(new_user)  # добавление в сессию нового пользователя
        await self.db_session.flush()  # добавление в Постгресс нового пользователя
        # сюда позже можно добавить проверки на существование такого пользователя
        return new_user

    async def read_user():
        pass

    async def update_user():
        pass

    async def del_user():
        pass


##################################
# PYDENTIC BLOCK WITH API MODELS #
##################################

LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


# лучше один раз создать регулярное выражение и потом вызывать через match, потому что делать регулярки каждый раз затратно для памяти

class TunedModel(BaseModel):  # наследуется от BaseModel pydentic
    class Config:
        """tells pydentic to conver even non dict obj to json"""
        # это класс для создания настроек которые будут общими во всех моделях
        orm_mode = True  # это будет переводить все подряд в JSON


class ShowUser(TunedModel):
    """это класс ответа для пользователя, поэтому JSON TunedModel"""
    user_id: uuid.UUID  # в алхимии другой UUID из алхимии
    name: str
    surname: str
    login: str
    email: EmailStr
    is_active: bool
    hashed_password: str  #


class UserCreate(BaseModel):
    """это класс обработки входящего запроса поэтому не надо JSON TunedModel"""
    name: str
    surname: str
    login: str
    email: EmailStr

    @validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Name should contains only letters"
            )
        return value

    @validator("surname")
    def validate_surname(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(
                status_code=422, detail="Surname should contains only letters"
            )
        return value


#########################
# BLOCK WITH API ROUTERS #
#########################

# create instance of the app
app = FastAPI(title="luchanos-oxford-university")

user_router = APIRouter()  # инициализируем роутер для "/user"


async def _create_new_user(body: UserCreate) -> ShowUser:
    async with async_session() as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.create_user(  # создаем юзера в алхимии и получаем его обратно с id и is_active
                name=body.name,
                surname=body.surname,
                login=body.login,
                email=body.email,
            )
            return ShowUser(
                user_id=user.user_id,
                name=user.name,
                surname=user.surname,
                login=user.login,
                email=user.email,
                is_active=user.is_active,
                hashed_password=user.hashed_password,  #
            )


@user_router.post("/", response_model=ShowUser)  # роутер пост запрос доступный через "/" а ниже указано "/user"
async def create_user(body: UserCreate) -> ShowUser:
    return await _create_new_user(body)


# create the instance for the routes
main_api_router = APIRouter()  # инициализируем роутер для любых адресов, роутер который будет собирать остальные роутеры

# set routes to the app instance
main_api_router.include_router(user_router, prefix="/user",
                               tags=["user"])  # включаем user_router в main_api_router c путем "/user"
app.include_router(main_api_router)  # даем доступ main_api_router в приложение app FastAPI

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # run app on the host and port
    uvicorn.run(app, host="0.0.0.0", port=8000)  # запускаем приложение app через uvicorn

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
